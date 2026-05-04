from fastapi.testclient import TestClient

from emergency_scenario_agent.api import app


client = TestClient(app)


def test_simulate_endpoint_returns_report():
    payload = {
        "scenario_type": "high_rise_fire",
        "location_type": "commercial_complex",
        "severity": "high",
        "weather": "hot",
        "time_of_day": "day",
        "people_trapped": 5,
        "floors_affected": [12, 13],
        "hazards": ["smoke", "glass_fall"],
        "available_resources": ["fire_robot", "ladder_truck", "mesh_radio"]
    }

    response = client.post('/simulate', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['summary']['scenario_type_label'] == '高层火灾'
    assert len(data['timeline']) >= 3
    assert data['resource_plan']['dispatch_priority'][0]
    assert data['equipment_budget_plan']['scenario_type'] == 'high_rise_fire'
    assert data['equipment_budget_plan']['total_estimated_budget_rmb'] > 0
    assert data['equipment_budget_plan']['items']


def test_catalog_endpoint_lists_supported_scenarios():
    response = client.get('/catalog')
    assert response.status_code == 200
    data = response.json()
    assert 'high_rise_fire' in data['supported_scenarios']
    assert 'chemical_leak' in data['supported_scenarios']
    assert data['version']


def test_simulate_markdown_endpoint_returns_text_report():
    payload = {
        "scenario_type": "chemical_leak",
        "location_type": "industrial_park",
        "severity": "critical",
        "weather": "rainy",
        "time_of_day": "night",
        "people_trapped": 2,
        "floors_affected": [],
        "hazards": ["toxic_gas"],
        "available_resources": ["hazmat_team", "decon_unit"]
    }

    response = client.post('/simulate/markdown', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['format'] == 'markdown'
    assert '危化品泄漏' in data['content']


def test_frontend_homepage_is_served():
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert '应急场景推演 Agent 控制台' in response.text
    assert '生成推演报告' in response.text
    assert '态势总览' in response.text
    assert '装备库' in response.text
    assert '楼层任务分区' in response.text
    assert '严重等级' in response.text
    assert '天气情况' in response.text
    assert '影响楼层 / 区域' in response.text
    assert '场景专属引导' in response.text
    assert '关键关注点' in response.text
    assert '场景专属参数' in response.text
    assert '积水深度' in response.text
    assert '泄漏介质' in response.text
    assert '运行总览' in response.text
    assert '核心指标' in response.text
    assert '指挥态势大屏' in response.text
    assert '装备检索' in response.text
    assert '预算汇总' in response.text
    assert '类别筛选' in response.text
    assert '任务筛选' in response.text
    assert '场景推荐清单' in response.text
    assert '采购建议' in response.text
    assert '危险因素研判' in response.text
    assert '资源配置（高级）' in response.text
    assert '显示高级资源配置' in response.text
    assert 'select option' in response.text



def test_frontend_javascript_is_served():
    response = client.get('/static/app.js')
    assert response.status_code == 200
    assert 'application/javascript' in response.headers['content-type'] or 'text/javascript' in response.headers['content-type']
    assert 'simulate' in response.text
    assert 'equipment-library' in response.text
    assert 'updateScenarioSpecificFields' in response.text
    assert 'weatherOptions' in response.text
    assert 'timeOfDayOptions' in response.text
    assert 'scenarioProfiles' in response.text
    assert 'scenario-guidance-title' in response.text
    assert 'buildScenarioSpecificPayload' in response.text
    assert 'renderScenarioFields' in response.text
    assert 'dashboard-kpi' in response.text
    assert 'signal-card' in response.text
    assert 'renderEquipmentSummary' in response.text
    assert 'equipment-search' in response.text
    assert 'equipment-category-filter' in response.text
    assert 'equipment-task-filter' in response.text
    assert 'renderScenarioEquipmentPlan' in response.text
    assert 'scenario-budget-plan' in response.text
    assert 'hazardOptionsMap' in response.text
    assert 'resourceOptions' in response.text
    assert 'toggleAdvancedResources' in response.text
    assert 'renderHazardOptions' in response.text



def test_equipment_library_endpoint_returns_catalog():
    response = client.get('/equipment-library')
    assert response.status_code == 200
    data = response.json()
    assert data['version']
    assert data['items']
    assert len(data['items']) >= 18
    first_item = data['items'][0]
    assert 'name' in first_item
    assert 'category' in first_item
    assert 'supported_scenarios' in first_item
    assert 'models' in first_item
    assert 'inventory_count' in first_item
    assert 'unit_cost_rmb' in first_item
    assert 'recommended_quantity' in first_item
    assert 'recommended_tasks' in first_item
    assert len({item['category'] for item in data['items']}) >= 8


def test_simulate_llm_endpoint_returns_enhanced_payload(monkeypatch):
    from emergency_scenario_agent import api as api_module
    from emergency_scenario_agent.models import LLMEnhancement

    def fake_run_with_llm(payload):
        report = api_module.engine.run(payload)
        report.llm_status = 'enhanced'
        report.llm_enhancement = LLMEnhancement(
            executive_summary='增强版摘要',
            command_brief=['建议单点突破'],
            resource_optimization=['优先部署通信中继'],
            public_communication=['统一对外发布口径'],
        )
        return report

    monkeypatch.setattr(api_module.engine, 'run_with_llm', fake_run_with_llm)
    payload = {
        "scenario_type": "high_rise_fire",
        "location_type": "residential_tower",
        "severity": "high",
        "weather": "windy",
        "time_of_day": "night",
        "people_trapped": 6,
        "floors_affected": [18, 19],
        "hazards": ["smoke"],
        "available_resources": ["fire_robot", "mesh_radio"]
    }

    response = client.post('/simulate/llm', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['llm_status'] == 'enhanced'
    assert data['llm_enhancement']['executive_summary'] == '增强版摘要'



def test_simulate_llm_markdown_endpoint_returns_enhanced_markdown(monkeypatch):
    from emergency_scenario_agent import api as api_module
    from emergency_scenario_agent.models import LLMEnhancement

    def fake_run_with_llm(payload):
        report = api_module.engine.run(payload)
        report.llm_status = 'enhanced'
        report.llm_enhancement = LLMEnhancement(
            executive_summary='增强版摘要',
            command_brief=['建议单点突破'],
            resource_optimization=['优先部署通信中继'],
            public_communication=['统一对外发布口径'],
        )
        return report

    monkeypatch.setattr(api_module.engine, 'run_with_llm', fake_run_with_llm)
    payload = {
        "scenario_type": "high_rise_fire",
        "location_type": "residential_tower",
        "severity": "high",
        "weather": "windy",
        "time_of_day": "night",
        "people_trapped": 6,
        "floors_affected": [18, 19],
        "hazards": ["smoke"],
        "available_resources": ["fire_robot", "mesh_radio"]
    }

    response = client.post('/simulate/llm/markdown', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['format'] == 'markdown'
    assert '大模型增强建议' in data['content']
