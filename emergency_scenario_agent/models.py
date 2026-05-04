from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ScenarioType = Literal[
    'high_rise_fire',
    'chemical_leak',
    'earthquake_rescue',
    'flood_response',
    'subway_fire',
]
SeverityLevel = Literal['medium', 'high', 'critical']


class ScenarioInput(BaseModel):
    scenario_type: ScenarioType
    location_type: str = Field(..., description='场景地点类型，如 residential_tower / industrial_park')
    severity: SeverityLevel
    weather: str
    time_of_day: str
    people_trapped: int = Field(0, ge=0)
    floors_affected: list[int] = Field(default_factory=list)
    hazards: list[str] = Field(default_factory=list)
    available_resources: list[str] = Field(default_factory=list)


class ScenarioSummary(BaseModel):
    scenario_type_label: str
    incident_level: str
    recommended_strategy: str
    top_risks: list[str]


class ActionPlan(BaseModel):
    immediate_actions: list[str]
    stabilization_actions: list[str]
    follow_up_actions: list[str]


class ResourcePlan(BaseModel):
    dispatch_priority: list[str]
    recommended_assets: list[str]
    capability_gaps: list[str]


class CommunicationPlan(BaseModel):
    command_mode: str
    key_actions: list[str]
    reporting_frequency: str


class TimelineStep(BaseModel):
    minute: int
    objective: str
    owner: str


class TaskZone(BaseModel):
    zone_name: str
    target: str
    assigned_team: str
    priority: str
    tasks: list[str]
    equipment_support: list[str]


class SimulationReport(BaseModel):
    summary: ScenarioSummary
    action_plan: ActionPlan
    resource_plan: ResourcePlan
    communication_plan: CommunicationPlan
    timeline: list[TimelineStep]
    task_zones: list[TaskZone]
    assumptions: list[str]
    equipment_budget_plan: 'ScenarioEquipmentBudgetPlan'
    llm_status: str = 'not_requested'
    llm_enhancement: 'LLMEnhancement | None' = None


class LLMEnhancement(BaseModel):
    executive_summary: str
    command_brief: list[str]
    resource_optimization: list[str]
    public_communication: list[str]


class ScenarioCatalog(BaseModel):
    version: str
    supported_scenarios: dict[str, str]
    supported_resources: dict[str, str]
    severity_levels: dict[str, str]


class EquipmentItem(BaseModel):
    id: str
    name: str
    category: str
    summary: str
    supported_scenarios: list[str]
    capabilities: list[str]
    deployment_roles: list[str]
    models: list[str]
    inventory_count: int = Field(..., ge=0)
    unit_cost_rmb: int = Field(..., ge=0)
    recommended_quantity: int = Field(..., ge=1)
    recommended_tasks: list[str]


class ScenarioEquipmentPlanItem(BaseModel):
    id: str
    name: str
    category: str
    models: list[str]
    recommended_quantity: int = Field(..., ge=1)
    unit_cost_rmb: int = Field(..., ge=0)
    estimated_budget_rmb: int = Field(..., ge=0)
    reason: str
    recommended_tasks: list[str]


class ScenarioEquipmentBudgetPlan(BaseModel):
    scenario_type: ScenarioType
    scenario_type_label: str
    total_recommended_quantity: int = Field(..., ge=0)
    total_estimated_budget_rmb: int = Field(..., ge=0)
    items: list[ScenarioEquipmentPlanItem]
    procurement_advice: list[str]


class EquipmentLibrary(BaseModel):
    version: str
    items: list[EquipmentItem]


class MarkdownReport(BaseModel):
    format: str = 'markdown'
    content: str
