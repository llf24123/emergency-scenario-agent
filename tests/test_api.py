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
