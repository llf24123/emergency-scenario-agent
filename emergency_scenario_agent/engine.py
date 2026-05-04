from __future__ import annotations

from dataclasses import dataclass

from .models import (
    ActionPlan,
    CommunicationPlan,
    ResourcePlan,
    ScenarioInput,
    ScenarioSummary,
    SimulationReport,
    TimelineStep,
)


SCENARIO_LABELS = {
    'high_rise_fire': '高层火灾',
    'chemical_leak': '危化品泄漏',
    'earthquake_rescue': '地震救援',
    'flood_response': '城市内涝',
    'subway_fire': '地铁火灾',
}

SEVERITY_TO_INCIDENT = {
    'medium': '一般',
    'high': '较大',
    'critical': '重大',
}

RESOURCE_LABELS = {
    'fire_robot': '消防机器人',
    'drone': '无人机',
    'mesh_radio': '自组网通信设备',
    'ladder_truck': '举高喷射车',
    'hazmat_team': '危化处置组',
    'decon_unit': '洗消单元',
}


@dataclass
class RiskAssessorAgent:
    def evaluate(self, scenario: ScenarioInput) -> list[str]:
        risks = []
        if scenario.people_trapped > 0:
            risks.append(f'存在 {scenario.people_trapped} 名被困人员，需优先搜救与疏散。')
        if scenario.scenario_type == 'high_rise_fire':
            risks.extend([
                '高层垂直蔓延快，烟气上升导致楼梯间与前室失效风险高。',
                '供电中断和电梯停运会影响人员疏散与装备投送。',
            ])
        if scenario.scenario_type == 'chemical_leak':
            risks.extend([
                '有毒/腐蚀介质扩散可能造成二次伤害。',
                '雨天可能导致污染面扩大，需控制外泄路径。',
            ])
        if 'smoke' in scenario.hazards:
            risks.append('浓烟会降低可视性并影响热成像识别效果。')
        if 'toxic_gas' in scenario.hazards:
            risks.append('有毒气体要求前线人员分级防护并进行风向研判。')
        return risks or ['现场信息有限，建议先组织侦察再扩大战术行动。']


@dataclass
class StrategyAgent:
    def recommend(self, scenario: ScenarioInput, risks: list[str]) -> str:
        if scenario.scenario_type == 'high_rise_fire':
            return '采取“先控烟、后搜救、分层灭火、保障通信”的高层建筑攻坚策略。'
        if scenario.scenario_type == 'chemical_leak':
            return '采取“先警戒隔离、后堵漏控源、同步侦检洗消”的危化处置策略。'
        if scenario.scenario_type == 'earthquake_rescue':
            return '采取“先生命搜索、后结构清障、滚动评估余震风险”的救援策略。'
        return '采取“快速侦察、分区处置、动态复盘”的综合应急处置策略。'


@dataclass
class ActionPlannerAgent:
    def build(self, scenario: ScenarioInput) -> ActionPlan:
        immediate = [
            '建立现场警戒区，明确指挥席、作战区、医疗区和后勤区。',
            '启动先遣侦察，收集火点/泄漏点、被困人员和主要通道信息。',
        ]
        stabilization = [
            '根据侦察结果组织主攻与掩护力量，持续修正战术部署。',
            '对高风险区域进行轮换作业，控制人员暴露时间。',
        ]
        follow_up = [
            '形成处置复盘，归档风险点、关键决策与装备表现。',
            '组织现场恢复与次生灾害监测。',
        ]

        if scenario.scenario_type == 'high_rise_fire':
            immediate.extend([
                '优先组织楼层疏散与被困人员搜救，必要时启用避难层转移。',
                '消防机器人进入烟热区域执行近距侦察和控火压制。',
            ])
            stabilization.extend([
                '建立分层供水与排烟协同，保证楼梯间与前室可通行。',
                '在着火层上下一层设置水枪阵地，防止火势垂直蔓延。',
            ])
        elif scenario.scenario_type == 'chemical_leak':
            immediate.extend([
                '第一时间划定上风向安全区并设置警戒隔离。',
                '组织侦检确认泄漏物性质和扩散方向。',
            ])
            stabilization.extend([
                '对暴露人员和装备开展洗消处置。',
                '使用堵漏、围堰、吸附等方式控制污染扩散。',
            ])
        return ActionPlan(
            immediate_actions=immediate,
            stabilization_actions=stabilization,
            follow_up_actions=follow_up,
        )


@dataclass
class ResourcePlannerAgent:
    def build(self, scenario: ScenarioInput) -> ResourcePlan:
        mapped_resources = [RESOURCE_LABELS.get(item, item) for item in scenario.available_resources]
        recommended = list(mapped_resources)
        dispatch_priority = []
        gaps = []

        if scenario.scenario_type == 'high_rise_fire':
            dispatch_priority.extend(['侦察组', '搜救组', '内攻灭火组', '供水排烟组', '通信保障组'])
            for needed, label in [('fire_robot', '消防机器人'), ('mesh_radio', '自组网通信设备')]:
                if needed not in scenario.available_resources:
                    gaps.append(f'缺少{label}，会削弱烟热区侦察/通信保障能力。')
            if '消防机器人' not in recommended:
                recommended.append('消防机器人')
            if '自组网通信设备' not in recommended:
                recommended.append('自组网通信设备')
        elif scenario.scenario_type == 'chemical_leak':
            dispatch_priority.extend(['警戒疏散组', '侦检组', '堵漏组', '洗消组', '医疗救护组'])
            for needed, label in [('hazmat_team', '危化处置组'), ('decon_unit', '洗消单元')]:
                if needed not in scenario.available_resources:
                    gaps.append(f'缺少{label}，危化控制闭环不完整。')
            if '洗消单元' not in recommended:
                recommended.append('洗消单元')
        else:
            dispatch_priority.extend(['侦察组', '主攻组', '医疗组', '后勤保障组'])

        return ResourcePlan(
            dispatch_priority=dispatch_priority,
            recommended_assets=recommended,
            capability_gaps=gaps,
        )


@dataclass
class CommunicationAgent:
    def build(self, scenario: ScenarioInput) -> CommunicationPlan:
        mode = '现场前后方一体化指挥'
        actions = [
            '建立统一通信口令和分组呼号。',
            '每 10 分钟滚动回传风险变化、资源消耗和人员安全状态。',
        ]
        if scenario.scenario_type == 'high_rise_fire':
            actions.extend([
                '在楼层拐点、避难层、电梯前室布设通信中继，保障高层通信。',
                '机器人、无人机、前线班组共用一张态势图，减少信息断层。',
            ])
        if scenario.scenario_type == 'chemical_leak':
            actions.extend([
                '同步通报风向、扩散边界与洗消状态，避免误入污染区。',
                '危化侦检数据与医疗处置组实时共享。',
            ])
        return CommunicationPlan(
            command_mode=mode,
            key_actions=actions,
            reporting_frequency='核心态势 10 分钟一报，重大变化随时上报',
        )


@dataclass
class TimelineAgent:
    def build(self, scenario: ScenarioInput) -> list[TimelineStep]:
        if scenario.scenario_type == 'high_rise_fire':
            return [
                TimelineStep(minute=0, objective='完成警戒分区、先遣侦察与初始战术判断', owner='现场指挥员'),
                TimelineStep(minute=10, objective='机器人和搜救组进入重点楼层，实施疏散与控火', owner='内攻灭火组'),
                TimelineStep(minute=30, objective='建立稳定供水排烟链路，压制垂直蔓延', owner='供水排烟组'),
                TimelineStep(minute=60, objective='转入残火清理与风险复盘', owner='综合保障组'),
            ]
        if scenario.scenario_type == 'chemical_leak':
            return [
                TimelineStep(minute=0, objective='划定警戒范围并完成上风向集结', owner='现场指挥员'),
                TimelineStep(minute=10, objective='完成侦检与堵漏前准备', owner='侦检组'),
                TimelineStep(minute=30, objective='控制泄漏源并组织洗消', owner='堵漏组'),
                TimelineStep(minute=60, objective='持续监测污染边界并评估恢复条件', owner='洗消组'),
            ]
        return [
            TimelineStep(minute=0, objective='完成侦察与分区', owner='现场指挥员'),
            TimelineStep(minute=15, objective='主力量展开', owner='作战组'),
            TimelineStep(minute=45, objective='风险复核和策略调整', owner='指挥席'),
        ]


class SimulationEngine:
    def __init__(self) -> None:
        self.risk_assessor = RiskAssessorAgent()
        self.strategy_agent = StrategyAgent()
        self.action_planner = ActionPlannerAgent()
        self.resource_planner = ResourcePlannerAgent()
        self.communication_agent = CommunicationAgent()
        self.timeline_agent = TimelineAgent()

    def run(self, scenario: ScenarioInput) -> SimulationReport:
        risks = self.risk_assessor.evaluate(scenario)
        strategy = self.strategy_agent.recommend(scenario, risks)
        action_plan = self.action_planner.build(scenario)
        resource_plan = self.resource_planner.build(scenario)
        communication_plan = self.communication_agent.build(scenario)
        timeline = self.timeline_agent.build(scenario)

        assumptions = [
            '默认当地消防救援力量可在常规响应时间内到场。',
            '如建筑图纸、危化品 MSDS 或监控视频缺失，需先补全信息。',
            f'当前天气条件为 {scenario.weather}，时间为 {scenario.time_of_day}。',
        ]
        if scenario.floors_affected:
            assumptions.append(f'重点影响楼层/区域：{", ".join(map(str, scenario.floors_affected))}。')

        summary = ScenarioSummary(
            scenario_type_label=SCENARIO_LABELS[scenario.scenario_type],
            incident_level=SEVERITY_TO_INCIDENT[scenario.severity],
            recommended_strategy=strategy,
            top_risks=risks,
        )
        return SimulationReport(
            summary=summary,
            action_plan=action_plan,
            resource_plan=resource_plan,
            communication_plan=communication_plan,
            timeline=timeline,
            assumptions=assumptions,
        )
