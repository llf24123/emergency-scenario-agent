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
    assert result.task_zones
    assert any("楼层" in zone.target for zone in result.task_zones)


def test_equipment_library_includes_cost_and_quantity_metadata():
    engine = SimulationEngine()
    library = engine.get_equipment_library()

    first = library.items[0]
    assert first.models
    assert first.inventory_count > 0
    assert first.unit_cost_rmb > 0
    assert first.recommended_quantity > 0
    assert first.recommended_tasks
    assert len(library.items) >= 18
    assert len({item.category for item in library.items}) >= 8


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


def test_high_rise_fire_generates_equipment_budget_plan():
    engine = SimulationEngine()
    scenario = ScenarioInput(
        scenario_type="high_rise_fire",
        location_type="residential_tower",
        severity="high",
        weather="windy",
        time_of_day="night",
        people_trapped=10,
        floors_affected=[18, 19, 20],
        hazards=["smoke", "power_outage"],
        available_resources=["fire_robot", "mesh_radio", "drone"],
    )

    result = engine.run(scenario)

    assert result.equipment_budget_plan.scenario_type == "high_rise_fire"
    assert result.equipment_budget_plan.scenario_type_label == "高层火灾"
    assert result.equipment_budget_plan.total_estimated_budget_rmb > 0
    assert result.equipment_budget_plan.total_recommended_quantity >= 3
    assert len(result.equipment_budget_plan.items) >= 3
    assert any(item.name == "消防机器人" for item in result.equipment_budget_plan.items)
    fire_robot = next(item for item in result.equipment_budget_plan.items if item.name == "消防机器人")
    assert fire_robot.estimated_budget_rmb == fire_robot.unit_cost_rmb * fire_robot.recommended_quantity
    assert fire_robot.reason
    assert result.equipment_budget_plan.procurement_advice


def test_report_can_render_markdown():
    engine = SimulationEngine()
    scenario = ScenarioInput(
        scenario_type="subway_fire",
        location_type="metro_station",
        severity="medium",
        weather="cloudy",
        time_of_day="rush_hour",
        people_trapped=30,
        hazards=["smoke"],
        available_resources=["drone", "mesh_radio"],
    )

    report = engine.run(scenario)
    markdown = engine.render_markdown(report)

    assert "# 应急场景推演报告" in markdown
    assert "地铁火灾" in markdown
    assert "## 行动计划" in markdown
    assert "## 时间线" in markdown
    assert "## 任务分区" in markdown


class FakeLLMClient:
    def enhance_report(self, scenario, report):
        return {
            "executive_summary": "大模型增强摘要",
            "command_brief": ["建议建立单一指挥链", "加强高风险区轮换"],
            "resource_optimization": ["优先前推通信中继"],
            "public_communication": ["对外统一口径，避免恐慌"],
        }


class FailingLLMClient:
    def enhance_report(self, scenario, report):
        raise RuntimeError("llm offline")


def test_llm_enhancement_can_be_attached_to_report():
    engine = SimulationEngine(llm_client=FakeLLMClient())
    scenario = ScenarioInput(
        scenario_type="high_rise_fire",
        location_type="residential_tower",
        severity="high",
        weather="windy",
        time_of_day="night",
        people_trapped=12,
        floors_affected=[25, 26],
        hazards=["smoke"],
        available_resources=["fire_robot", "mesh_radio"],
    )

    report = engine.run_with_llm(scenario)

    assert report.llm_enhancement is not None
    assert report.llm_enhancement.executive_summary == "大模型增强摘要"
    assert any("指挥链" in item for item in report.llm_enhancement.command_brief)


def test_llm_failure_falls_back_to_rule_report():
    engine = SimulationEngine(llm_client=FailingLLMClient())
    scenario = ScenarioInput(
        scenario_type="chemical_leak",
        location_type="industrial_park",
        severity="critical",
        weather="rainy",
        time_of_day="night",
        people_trapped=1,
        hazards=["toxic_gas"],
        available_resources=["hazmat_team"],
    )

    report = engine.run_with_llm(scenario)

    assert report.summary.scenario_type_label == "危化品泄漏"
    assert report.llm_enhancement is None
    assert report.llm_status == "fallback"
