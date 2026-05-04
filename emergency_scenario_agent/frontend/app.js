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

function setStatus(text, ok = false, err = false) {
  statusEl.textContent = text;
  statusEl.className = 'status' + (ok ? ' ok' : '') + (err ? ' err' : '');
}

function renderList(el, items) {
  el.innerHTML = '';
  (items || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

function fillForm(data) {
  scenarioSelect.value = data.scenario_type;
  form.location_type.value = data.location_type;
  form.severity.value = data.severity;
  form.weather.value = data.weather;
  form.time_of_day.value = data.time_of_day;
  form.people_trapped.value = data.people_trapped;
  form.floors_affected.value = (data.floors_affected || []).join(',');
  form.hazards.value = (data.hazards || []).join(',');
  form.available_resources.value = (data.available_resources || []).join(',');
}

function readPayload() {
  return {
    scenario_type: form.scenario_type.value,
    location_type: form.location_type.value.trim(),
    severity: form.severity.value,
    weather: form.weather.value.trim(),
    time_of_day: form.time_of_day.value.trim(),
    people_trapped: Number(form.people_trapped.value || 0),
    floors_affected: form.floors_affected.value.split(',').map(x => x.trim()).filter(Boolean).map(Number),
    hazards: form.hazards.value.split(',').map(x => x.trim()).filter(Boolean),
    available_resources: form.available_resources.value.split(',').map(x => x.trim()).filter(Boolean),
  };
}

async function fetchCatalog() {
  const res = await fetch('/catalog');
  const data = await res.json();
  scenarioSelect.innerHTML = '';
  Object.entries(data.supported_scenarios).forEach(([value, label]) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = `${label} (${value})`;
    scenarioSelect.appendChild(opt);
  });
  supportedCount.textContent = `${Object.keys(data.supported_scenarios).length} 类`;
}

async function simulate(payload) {
  setStatus('正在生成推演结果...');
  const [jsonRes, mdRes] = await Promise.all([
    fetch('/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
    fetch('/simulate/markdown', {
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

  summaryScenario.textContent = report.summary.scenario_type_label;
  summaryLevel.textContent = report.summary.incident_level;
  summaryStrategy.textContent = report.summary.recommended_strategy;

  renderList(riskList, report.summary.top_risks);
  renderList(immediateList, report.action_plan.immediate_actions);
  renderList(resourceList, report.resource_plan.recommended_assets);
  renderList(commList, report.communication_plan.key_actions);

  markdownOutput.textContent = markdown.content;
  jsonOutput.textContent = JSON.stringify(report, null, 2);
  setStatus('推演完成，可复制 Markdown 或继续修改场景。', true, false);
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

document.getElementById('copy-markdown').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(markdownOutput.textContent);
    setStatus('Markdown 已复制到剪贴板。', true, false);
  } catch {
    setStatus('复制失败，请手动复制。', false, true);
  }
});

document.getElementById('download-markdown').addEventListener('click', () => {
  const blob = new Blob([markdownOutput.textContent], { type: 'text/markdown;charset=utf-8' });
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

(async function init() {
  try {
    await fetchCatalog();
    fillForm(highRiseExample);
    await simulate(highRiseExample);
  } catch (error) {
    console.error(error);
    setStatus('初始化失败，请检查后端服务。', false, true);
  }
})();
