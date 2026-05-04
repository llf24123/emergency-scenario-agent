from emergency_scenario_agent.engine import SimulationEngine
from emergency_scenario_agent.models import ScenarioInput


def test_high_rise_fire_generates_core_sections():
    engine = SimulationEngine()
    scenario = ScenarioInput(
        scenario_type="high_rise_fire",
        location_type="residential_tower",
        severity="high",
        weather="windy",
        time_of_day="night",
        people_trapped=8,
        floors_affected=[18, 19, 20],
        hazards=["smoke", "power_outage"],
        available_resources=["fire_robot", "drone", "mesh_radio"],
    )

    result = engine.run(scenario)

    assert result.summary.incident_level in {"重大", "较大"}
    assert result.summary.recommended_strategy
    assert any("疏散" in item for item in result.action_plan.immediate_actions)
    assert any("机器人" in item for item in result.resource_plan.recommended_assets)
    assert any("通信" in item for item in result.communication_plan.key_actions)
    assert result.timeline[0].minute == 0


def test_chemical_leak_adds_decontamination_action():
    engine = SimulationEngine()
    scenario = ScenarioInput(
        scenario_type="chemical_leak",
        location_type="industrial_park",
        severity="critical",
        weather="rainy",
        time_of_day="day",
        people_trapped=2,
        floors_affected=[],
        hazards=["toxic_gas", "corrosive_material"],
        available_resources=["hazmat_team", "decon_unit", "fire_robot"],
    )

    result = engine.run(scenario)

    combined_actions = result.action_plan.immediate_actions + result.action_plan.stabilization_actions
    assert any("洗消" in item for item in combined_actions)
    assert any("警戒" in item for item in result.action_plan.immediate_actions)
