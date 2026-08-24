(() => {
  const flow = JSON.parse(document.querySelector('#flow-contract').textContent);
  const expected = JSON.parse(document.querySelector('#expected-contract').textContent);
  const resultNode = document.querySelector('#harness-result');
  const stateMap = new Map(flow.states.map((item) => [item.state_id, item]));
  const transitions = flow.transitions || [];
  const visited = [];
  const errors = [];
  let currentState = new URLSearchParams(location.search).get('harness_state') || flow.initial_state;
  let autoTimer = null;
  let timeoutTimer = null;

  const pushError = (type, objectRef, evidence) => {
    const key = `${type}|${objectRef}|${evidence}`;
    if (!errors.some((item) => item.key === key)) errors.push({ key, type, object_ref: objectRef, evidence });
  };

  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };

  const rectsOverlap = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;

  const auditScreen = (screen) => {
    const stateId = screen.dataset.stateId;
    const primary = [...screen.querySelectorAll('[data-level="primary"]')].filter(visible);
    if (primary.length !== 1) pushError('PRIMARY_ACTION_INVALID', stateId, `visible primary actions: ${primary.length}`);

    const p0 = [...screen.querySelectorAll('[data-priority="P0"]')];
    if (!p0.length || p0.some((item) => !visible(item))) pushError('STATE_MISSING', stateId, 'P0 content missing or invisible');

    const regions = [...screen.querySelectorAll('.prototype-region')].filter(visible);
    for (const region of regions) {
      const rect = region.getBoundingClientRect();
      if (rect.left < -0.5 || rect.top < -0.5 || rect.right > innerWidth + 0.5 || rect.bottom > innerHeight + 0.5) {
        pushError('LAYOUT_OVERFLOW', region.dataset.regionId, `${rect.left},${rect.top},${rect.right},${rect.bottom} outside ${innerWidth}x${innerHeight}`);
      }
    }
    for (let i = 0; i < regions.length; i += 1) {
      for (let j = i + 1; j < regions.length; j += 1) {
        const a = regions[i];
        const b = regions[j];
        const allowed = (a.dataset.allowedOverlap || '').split(',').filter(Boolean);
        const isOverlay = a.dataset.positionMode === 'overlay' || b.dataset.positionMode === 'overlay';
        if (!isOverlay && !allowed.includes(b.dataset.regionId) && rectsOverlap(a.getBoundingClientRect(), b.getBoundingClientRect())) {
          pushError('REGION_OVERLAP', `${a.dataset.regionId}/${b.dataset.regionId}`, `unexpected overlap in ${stateId}`);
        }
      }
    }

    if (screen.scrollWidth > innerWidth || screen.scrollHeight > innerHeight) {
      pushError('LAYOUT_OVERFLOW', stateId, `screen scroll size ${screen.scrollWidth}x${screen.scrollHeight}`);
    }
    if (screen.querySelector('img,svg,canvas,video,audio,[style*="background-image"]')) {
      pushError('ASSET_POLICY_VIOLATION', stateId, 'forbidden visual/media element found');
    }
  };

  const auditAllScreens = () => {
    const screens = [...document.querySelectorAll('.prototype-screen')];
    const previous = screens.map((item) => item.hidden);
    screens.forEach((screen, index) => {
      screens.forEach((item) => { item.hidden = item !== screen; });
      auditScreen(screen);
      screen.hidden = previous[index];
    });
  };

  const findTransition = (event) => transitions.find((item) => item.from === currentState && item.event === event);

  const activate = (stateId) => {
    clearTimeout(autoTimer);
    clearTimeout(timeoutTimer);
    currentState = stateId;
    visited.push(stateId);
    document.querySelectorAll('.prototype-screen').forEach((screen) => {
      screen.hidden = screen.dataset.stateId !== stateId;
    });
    const state = stateMap.get(stateId);
    if (!state) {
      pushError('STATE_MISSING', stateId, 'flow state has no definition');
      return;
    }
    const auto = transitions.find((item) => item.from === stateId && item.trigger === 'auto');
    if (auto) autoTimer = setTimeout(() => activate(auto.to), Number(auto.delay_ms || 60));
    if (state.type === 'async') {
      const timeout = transitions.find((item) => item.from === stateId && item.trigger === 'timeout');
      if (timeout) timeoutTimer = setTimeout(() => activate(timeout.to), Number(timeout.timeout_ms || flow.async_policy?.required_timeout_ms || 3000));
    }
  };

  document.addEventListener('click', (event) => {
    const action = event.target.closest('[data-action-id]');
    if (!action) return;
    const transition = findTransition(action.dataset.actionId);
    if (!transition) {
      pushError('FLOW_UNREACHABLE', action.dataset.actionId, `no transition from ${currentState}`);
      return;
    }
    activate(transition.to);
  });

  const waitForAction = async (actionId, timeoutMs = 1200) => {
    const started = performance.now();
    while (performance.now() - started < timeoutMs) {
      const node = document.querySelector(`.prototype-screen:not([hidden]) [data-action-id="${CSS.escape(actionId)}"]`);
      if (node) return node;
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
    return null;
  };

  const publish = (taskPassed = null) => {
    const bodyOverflow = document.documentElement.scrollWidth > innerWidth || document.documentElement.scrollHeight > innerHeight;
    if (bodyOverflow) pushError('LAYOUT_OVERFLOW', 'document', `${document.documentElement.scrollWidth}x${document.documentElement.scrollHeight}`);
    const payload = {
      browser: true,
      viewport: { width: innerWidth, height: innerHeight },
      current_state: currentState,
      visited_states: visited,
      task_passed: taskPassed,
      errors: errors.map(({ key, ...item }) => item),
      passed: errors.length === 0 && taskPassed !== false,
    };
    resultNode.textContent = JSON.stringify(payload);
  };

  const runAuto = async () => {
    for (const actionId of expected.action_sequence || []) {
      const action = await waitForAction(actionId);
      if (!action) {
        pushError('FLOW_UNREACHABLE', actionId, `action unavailable from ${currentState}`);
        publish(false);
        return;
      }
      action.click();
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    const expectedState = expected.terminal_state;
    const passed = !expectedState || currentState === expectedState;
    if (!passed) pushError('FLOW_UNREACHABLE', expectedState, `ended at ${currentState}`);
    publish(passed);
  };

  auditAllScreens();
  activate(currentState);
  publish(null);
  if (new URLSearchParams(location.search).get('harness_auto') === '1') runAuto();
})();
