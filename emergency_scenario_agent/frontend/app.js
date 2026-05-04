const form = document.getElementById('scenario-form');
const statusEl = document.getElementById('status');
const summaryScenario = document.getElementById('summary-scenario');
const summaryLevel = document.getElementById('summary-level');
const summaryStrategy = document.getElementById('summary-strategy');
const riskList = document.getElementById('risk-list');
const immediateList = document.getElementById('immediate-list');
const resourceList = document.getElementById('resource-list');
const commList = document.getElementById('comm-list');
const markdownOutput = document.getElementById('markdown-output');
const jsonOutput = document.getElementById('json-output');
const scenarioSelect = document.getElementById('scenario_type');
const supportedCount = document.getElementById('supported-count');
const equipmentCount = document.getElementById('equipment-count');
const useLLM = document.getElementById('use_llm');
const severitySelect = document.getElementById('severity');
const weatherSelect = document.getElementById('weather');
const timeOfDaySelect = document.getElementById('time_of_day');
const floorsGroup = document.getElementById('floors-group');
const floorsLabel = document.getElementById('floors-label');
const llmStatus = document.getElementById('llm-status');
const llmStatusHero = document.getElementById('llm-status-hero');
const llmSummary = document.getElementById('llm-summary');
const llmCommandList = document.getElementById('llm-command-list');
const llmResourceList = document.getElementById('llm-resource-list');
const llmPublicList = document.getElementById('llm-public-list');
const statusScenario = document.getElementById('status-scenario');
const scenarioGuidanceTitle = document.getElementById('scenario-guidance-title');
const scenarioGuidanceDesc = document.getElementById('scenario-guidance-desc');
const scenarioFocusList = document.getElementById('scenario-focus-list');
const heroPeople = document.getElementById('hero-people');
const heroAffected = document.getElementById('hero-affected');
const situationCommandMode = document.getElementById('situation-command-mode');
const situationReporting = document.getElementById('situation-reporting');
const situationGapCount = document.getElementById('situation-gap-count');
const alertList = document.getElementById('alert-list');
const timelineGrid = document.getElementById('timeline-grid');
const taskZoneGrid = document.getElementById('task-zone-grid');
const gapList = document.getElementById('gap-list');
const equipmentFilter = document.getElementById('equipment-filter');
const equipmentGrid = document.getElementById('equipment-grid');

const highRiseExample = {
  scenario_type: 'high_rise_fire',
  location_type: 'residential_tower',
  severity: 'high',
  weather: 'windy',
  time_of_day: 'night',
  people_trapped: 8,
  floors_affected: [18, 19, 20],
  hazards: ['smoke', 'power_outage'],
  available_resources: ['fire_robot', 'drone', 'mesh_radio'],
};

const chemicalExample = {
  scenario_type: 'chemical_leak',
  location_type: 'industrial_park',
  severity: 'critical',
  weather: 'rainy',
  time_of_day: 'night',
  people_trapped: 2,
  floors_affected: [],
  hazards: ['toxic_gas', 'corrosive_material'],
  available_resources: ['hazmat_team', 'decon_unit', 'fire_robot'],
};

let latestPayload = highRiseExample;
let latestReport = null;
let latestEquipment = [];
let catalogMap = {};
let markdownCache = '';

const severityOptions = [
  ['medium', '中等'],
  ['high', '高'],
  ['critical', '极高'],
];

const weatherOptions = [
  ['sunny', '晴天'],
  ['cloudy', '多云'],
  ['rainy', '雨天'],
  ['windy', '大风'],
  ['storm', '暴雨/强对流'],
  ['foggy', '雾天'],
];

const timeOfDayOptions = [
  ['early_morning', '凌晨'],
  ['morning', '上午'],
  ['afternoon', '下午'],
  ['evening', '傍晚'],
  ['night', '夜间'],
  ['rush_hour', '早晚高峰'],
];

const scenarioFieldRules = {
  high_rise_fire: { showFloors: true, floorsLabel: '影响楼层（逗号分隔）', floorsPlaceholder: '18,19,20' },
  subway_fire: { showFloors: true, floorsLabel: '影响站层 / 区域（逗号分隔）', floorsPlaceholder: '1,2' },
  flood_response: { showFloors: false, floorsLabel: '影响区域（逗号分隔）', floorsPlaceholder: '低洼路段,A区地下车库' },
  chemical_leak: { showFloors: false, floorsLabel: '重点区域（逗号分隔）', floorsPlaceholder: '储罐区,装卸区' },
  earthquake_rescue: { showFloors: false, floorsLabel: '重点区域（逗号分隔）', floorsPlaceholder: '1号楼东侧,地下空间' },
};

const scenarioProfiles = {
  high_rise_fire: {
    title: '高层火灾场景专属引导',
    description: '重点关注起火楼层、烟气蔓延、人员疏散、供水排烟和通信中继。',
    focus: ['优先填写受影响楼层', '关注是否停电、浓烟、电梯停运', '资源建议优先消防机器人、举高喷射车、自组网'],
    defaults: { weather: 'windy', time_of_day: 'night', severity: 'high' },
  },
  chemical_leak: {
    title: '危化泄漏场景专属引导',
    description: '重点关注泄漏源、风向、污染扩散边界、堵漏与洗消闭环。',
    focus: ['楼层字段自动隐藏', '建议填写重点区域而不是楼层', '资源建议优先危化处置组、洗消单元'],
    defaults: { weather: 'rainy', time_of_day: 'night', severity: 'critical' },
  },
  flood_response: {
    title: '城市内涝场景专属引导',
    description: '重点关注积水区域、地下空间、受困车辆、排水与转移路线。',
    focus: ['不需要填写影响楼层', '建议填写低洼路段、地下车库、隧道等区域', '天气通常与暴雨、大风、早晚高峰更相关'],
    defaults: { weather: 'storm', time_of_day: 'rush_hour', severity: 'high' },
  },
  earthquake_rescue: {
    title: '地震救援场景专属引导',
    description: '重点关注倒塌区域、被困空间、余震风险、生命搜索与医疗转运。',
    focus: ['不需要填写影响楼层', '建议填写楼栋、地下空间、坍塌点位', '优先关注搜索、破拆、转运协同'],
    defaults: { weather: 'cloudy', time_of_day: 'afternoon', severity: 'high' },
  },
  subway_fire: {
    title: '地铁火灾场景专属引导',
    description: '重点关注站厅层、站台层、排烟组织、疏散路径和通信覆盖。',
    focus: ['建议填写受影响站层', '优先关注烟气控制和客流疏散', '资源建议优先通信中继、无人机、照明设备'],
    defaults: { weather: 'cloudy', time_of_day: 'rush_hour', severity: 'high' },
  },
};

function setStatus(text, ok = false, err = false) {
  statusEl.textContent = text;
  statusEl.className = `status${ok ? ' ok' : ''}${err ? ' err' : ''}`;
}

function renderList(el, items) {
  el.innerHTML = '';
  (items || []).forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

function fillSelectOptions(selectEl, options, selectedValue) {
  selectEl.innerHTML = '';
  options.forEach(([value, label]) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = label;
    if (value === selectedValue) opt.selected = true;
    selectEl.appendChild(opt);
  });
}

function updateScenarioSpecificFields(scenarioType) {
  const rule = scenarioFieldRules[scenarioType] || { showFloors: true, floorsLabel: '影响区域（逗号分隔）', floorsPlaceholder: '' };
  const profile = scenarioProfiles[scenarioType];
  floorsGroup.style.display = rule.showFloors ? 'block' : 'none';
  floorsLabel.textContent = rule.floorsLabel;
  form.floors_affected.placeholder = rule.floorsPlaceholder || '';
  if (!rule.showFloors) {
    form.floors_affected.value = '';
  }
  if (profile) {
    scenarioGuidanceTitle.textContent = profile.title;
    scenarioGuidanceDesc.textContent = profile.description;
    renderList(scenarioFocusList, profile.focus || []);
    if (profile.defaults) {
      if (profile.defaults.severity) severitySelect.value = profile.defaults.severity;
      if (profile.defaults.weather) weatherSelect.value = profile.defaults.weather;
      if (profile.defaults.time_of_day) timeOfDaySelect.value = profile.defaults.time_of_day;
    }
  }
}

function renderCardList(el, items, formatter) {
  el.innerHTML = '';
  (items || []).forEach((item, index) => {
    const node = document.createElement('div');
    node.className = formatter.className || 'alert-item';
    node.innerHTML = formatter(item, index);
    el.appendChild(node);
  });
}

function fillForm(data) {
  scenarioSelect.value = data.scenario_type;
  form.location_type.value = data.location_type;
  severitySelect.value = data.severity;
  weatherSelect.value = data.weather;
  timeOfDaySelect.value = data.time_of_day;
  form.people_trapped.value = data.people_trapped;
  form.floors_affected.value = (data.floors_affected || []).join(',');
  form.hazards.value = (data.hazards || []).join(',');
  form.available_resources.value = (data.available_resources || []).join(',');
  updateScenarioSpecificFields(data.scenario_type);
  syncEquipmentFilter();
}

function readPayload() {
  return {
    scenario_type: form.scenario_type.value,
    location_type: form.location_type.value.trim(),
    severity: form.severity.value,
    weather: form.weather.value.trim(),
    time_of_day: form.time_of_day.value.trim(),
    people_trapped: Number(form.people_trapped.value || 0),
    floors_affected: form.floors_affected.value.split(',').map((x) => x.trim()).filter(Boolean).map(Number),
    hazards: form.hazards.value.split(',').map((x) => x.trim()).filter(Boolean),
    available_resources: form.available_resources.value.split(',').map((x) => x.trim()).filter(Boolean),
  };
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.tab === name);
  });
  document.querySelectorAll('.view').forEach((view) => {
    view.classList.toggle('active', view.dataset.view === name);
  });
}

function syncEquipmentFilter() {
  if (!equipmentFilter.value || equipmentFilter.value === 'recommended') {
    equipmentFilter.value = latestPayload?.scenario_type || 'all';
  }
}

async function fetchCatalog() {
  const res = await fetch('/catalog');
  const data = await res.json();
  scenarioSelect.innerHTML = '';
  catalogMap = data.supported_scenarios || {};
  Object.entries(catalogMap).forEach(([value, label]) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = `${label} (${value})`;
    scenarioSelect.appendChild(opt);
  });
  supportedCount.textContent = `${Object.keys(catalogMap).length} 类`;
  fillSelectOptions(severitySelect, severityOptions, 'high');
  fillSelectOptions(weatherSelect, weatherOptions, highRiseExample.weather);
  fillSelectOptions(timeOfDaySelect, timeOfDayOptions, highRiseExample.time_of_day);

  equipmentFilter.innerHTML = '';
  const defaults = [
    ['all', '全部装备'],
    ...Object.entries(catalogMap).map(([value, label]) => [value, `${label} 场景`]),
  ];
  defaults.forEach(([value, label]) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = label;
    equipmentFilter.appendChild(opt);
  });
}

async function fetchEquipmentLibrary() {
  const res = await fetch('/equipment-library');
  const data = await res.json();
  latestEquipment = data.items || [];
  equipmentCount.textContent = `${latestEquipment.length} 条`;
  renderEquipmentLibrary('all');
}

function renderEquipmentLibrary(mode = equipmentFilter.value || 'all') {
  const payload = latestPayload || highRiseExample;
  const report = latestReport;
  let items = [...latestEquipment];

  if (mode === 'recommended' && report) {
    const names = new Set(report.resource_plan.recommended_assets || []);
    items = items.filter((item) => names.has(item.name) || names.has(item.id));
  } else if (mode !== 'all') {
    items = items.filter((item) => item.supported_scenarios.includes(mode));
  } else if (payload?.scenario_type) {
    items.sort((a, b) => {
      const aScore = a.supported_scenarios.includes(payload.scenario_type) ? 1 : 0;
      const bScore = b.supported_scenarios.includes(payload.scenario_type) ? 1 : 0;
      return bScore - aScore;
    });
  }

  equipmentGrid.innerHTML = '';
  items.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'equipment-card';
    const scenarioTags = item.supported_scenarios.map((key) => `<span class="tag warn">${catalogMap[key] || key}</span>`).join('');
    const roleTags = item.deployment_roles.map((role) => `<span class="tag">${role}</span>`).join('');
    const capabilities = item.capabilities.map((cap) => `<li>${cap}</li>`).join('');
    const taskTags = (item.recommended_tasks || []).map((task) => `<span class="tag">${task}</span>`).join('');
    const modelText = (item.models || []).join(' / ');
    card.innerHTML = `
      <strong>${item.name}</strong>
      <div class="subtle">${item.category}</div>
      <p style="color: var(--muted); line-height:1.75; margin:10px 0 0;">${item.summary}</p>
      <div class="equipment-tags">${scenarioTags}</div>
      <div class="role-tags">${roleTags}</div>
      <div class="meta-box" style="margin-top:12px;">
        <div class="k">型号 / 库存 / 建议投送</div>
        <div class="v">${modelText}<br>库存：${item.inventory_count} 台/套 · 建议投送：${item.recommended_quantity} 台/套</div>
      </div>
      <div class="meta-box" style="margin-top:12px;">
        <div class="k">参考单价</div>
        <div class="v">¥ ${Number(item.unit_cost_rmb || 0).toLocaleString('zh-CN')}</div>
      </div>
      <div class="role-tags" style="margin-top:12px;">${taskTags}</div>
      <ul class="list" style="margin-top:10px;">${capabilities}</ul>
    `;
    equipmentGrid.appendChild(card);
  });
}

function renderSituation(report, payload) {
  statusScenario.textContent = report.summary.scenario_type_label;
  heroPeople.textContent = `${payload.people_trapped || 0} 人`;
  heroAffected.textContent = payload.floors_affected?.length ? payload.floors_affected.join(' / ') : '未录入';
  situationCommandMode.textContent = report.communication_plan.command_mode;
  situationReporting.textContent = report.communication_plan.reporting_frequency;
  situationGapCount.textContent = `${(report.resource_plan.capability_gaps || []).length} 项`;

  const alerts = [
    ...report.summary.top_risks.slice(0, 4).map((item) => ({
      title: '风险预警',
      text: item,
    })),
    ...(payload.hazards || []).slice(0, 2).map((item) => ({
      title: '现场危险因素',
      text: item,
    })),
  ];
  renderCardList(alertList, alerts, (item) => `
    <strong>${item.title}</strong>
    <div class="subtle">${item.text}</div>
  `);

  renderCardList(timelineGrid, report.timeline || [], (step) => `
    <strong>T+${step.minute} 分钟</strong>
    <div class="subtle">${step.owner}</div>
    <div style="margin-top:8px;color:var(--muted);line-height:1.7;">${step.objective}</div>
  `);

  renderCardList(taskZoneGrid, report.task_zones || [], (zone) => `
    <strong>${zone.zone_name}</strong>
    <div class="subtle">${zone.target} · ${zone.assigned_team} · ${zone.priority}</div>
    <div style="margin-top:8px;color:var(--muted);line-height:1.7;">任务：${(zone.tasks || []).join('；')}</div>
    <div style="margin-top:8px;color:var(--muted);line-height:1.7;">装备：${(zone.equipment_support || []).join('、')}</div>
  `);

  const gapItems = report.resource_plan.capability_gaps?.length
    ? report.resource_plan.capability_gaps.map((item) => ({ title: '能力缺口', text: item }))
    : [{ title: '当前判断', text: '当前输入未发现明显能力缺口，但仍建议动态复核资源消耗。' }];
  renderCardList(gapList, gapItems, (item) => `
    <strong>${item.title}</strong>
    <div class="subtle">${item.text}</div>
  `);
}

async function simulate(payload) {
  latestPayload = payload;
  syncEquipmentFilter();
  const endpoint = useLLM.checked ? '/simulate/llm' : '/simulate';
  const markdownEndpoint = useLLM.checked ? '/simulate/llm/markdown' : '/simulate/markdown';
  setStatus(useLLM.checked ? '正在生成大模型增强推演结果...' : '正在生成规则推演结果...');

  const [jsonRes, mdRes] = await Promise.all([
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
    fetch(markdownEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  ]);

  if (!jsonRes.ok || !mdRes.ok) {
    throw new Error('后端返回错误，请检查输入参数。');
  }

  const report = await jsonRes.json();
  const markdown = await mdRes.json();
  latestReport = report;
  markdownCache = markdown.content;

  summaryScenario.textContent = report.summary.scenario_type_label;
  summaryLevel.textContent = report.summary.incident_level;
  summaryStrategy.textContent = report.summary.recommended_strategy;

  renderList(riskList, report.summary.top_risks);
  renderList(immediateList, report.action_plan.immediate_actions);
  renderList(resourceList, report.resource_plan.recommended_assets);
  renderList(commList, report.communication_plan.key_actions);

  llmStatus.textContent = report.llm_status || 'not_requested';
  llmStatusHero.textContent = report.llm_status || 'not_requested';
  llmSummary.textContent = report.llm_enhancement?.executive_summary || '当前未返回大模型增强摘要';
  renderList(llmCommandList, report.llm_enhancement?.command_brief || []);
  renderList(llmResourceList, report.llm_enhancement?.resource_optimization || []);
  renderList(llmPublicList, report.llm_enhancement?.public_communication || []);

  markdownOutput.textContent = markdown.content;
  jsonOutput.textContent = JSON.stringify(report, null, 2);
  renderSituation(report, payload);
  renderEquipmentLibrary(equipmentFilter.value || payload.scenario_type || 'all');
  setStatus(useLLM.checked ? '推演完成，已尝试接入大模型增强。' : '规则推演完成。', true, false);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await simulate(readPayload());
  } catch (error) {
    console.error(error);
    setStatus(error.message || '生成失败，请稍后重试。', false, true);
  }
});

document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

document.getElementById('copy-markdown').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(markdownCache || markdownOutput.textContent);
    setStatus('Markdown 已复制到剪贴板。', true, false);
  } catch {
    setStatus('复制失败，请手动复制。', false, true);
  }
});

document.getElementById('download-markdown').addEventListener('click', () => {
  const blob = new Blob([markdownCache || markdownOutput.textContent], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `emergency-simulation-${Date.now()}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  setStatus('Markdown 文件已下载。', true, false);
});

document.getElementById('load-highrise').addEventListener('click', () => fillForm(highRiseExample));
document.getElementById('load-chemical').addEventListener('click', () => fillForm(chemicalExample));
document.getElementById('show-recommended-equipment').addEventListener('click', () => renderEquipmentLibrary('recommended'));
document.getElementById('show-all-equipment').addEventListener('click', () => renderEquipmentLibrary('all'));
equipmentFilter.addEventListener('change', (event) => renderEquipmentLibrary(event.target.value));
scenarioSelect.addEventListener('change', () => {
  latestPayload = { ...latestPayload, scenario_type: scenarioSelect.value };
  updateScenarioSpecificFields(scenarioSelect.value);
  renderEquipmentLibrary(scenarioSelect.value);
});

(async function init() {
  try {
    await Promise.all([fetchCatalog(), fetchEquipmentLibrary()]);
    fillForm(highRiseExample);
    await simulate(highRiseExample);
  } catch (error) {
    console.error(error);
    setStatus('初始化失败，请检查后端服务。', false, true);
  }
})();
