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



def test_frontend_javascript_is_served():
    response = client.get('/static/app.js')
    assert response.status_code == 200
    assert 'application/javascript' in response.headers['content-type'] or 'text/javascript' in response.headers['content-type']
    assert 'simulate' in response.text
