from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .llm import OpenAICompatibleLLMClient
from .models import (
    ActionPlan,
    CommunicationPlan,
    EquipmentItem,
    EquipmentLibrary,
    LLMEnhancement,
    MarkdownReport,
    ResourcePlan,
    ScenarioCatalog,
    ScenarioInput,
    ScenarioSummary,
    SimulationReport,
    TaskZone,
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

SEVERITY_LABELS = {
    'medium': '中风险',
    'high': '高风险',
    'critical': '极高风险',
}

RESOURCE_LABELS = {
    'fire_robot': '消防机器人',
    'drone': '无人机',
    'mesh_radio': '自组网通信设备',
    'ladder_truck': '举高喷射车',
    'hazmat_team': '危化处置组',
    'decon_unit': '洗消单元',
}

EQUIPMENT_LIBRARY = [
    {
        'id': 'fire_robot',
        'name': '消防机器人',
        'category': '地面无人平台',
        'summary': '适用于高温、浓烟和爆炸风险区域的抵近侦察与控火压制。',
        'supported_scenarios': ['high_rise_fire', 'chemical_leak', 'subway_fire'],
        'capabilities': ['热成像侦察', '远程喷水/喷雾', '有毒环境替代人员抵近'],
        'deployment_roles': ['近距侦察', '控火压制', '危险区替代作业'],
        'models': ['RXR-MC80BGD', 'QX-XF02'],
        'inventory_count': 6,
        'unit_cost_rmb': 680000,
        'recommended_quantity': 2,
        'recommended_tasks': ['着火层抵近侦察', '烟热区控火压制', '危险区替代作业'],
    },
    {
        'id': 'drone',
        'name': '无人机',
        'category': '空中侦察平台',
        'summary': '用于高空观察、外立面侦察、热源定位与现场回传。',
        'supported_scenarios': ['high_rise_fire', 'flood_response', 'earthquake_rescue'],
        'capabilities': ['高点态势回传', '外立面巡检', '搜索热源与受困目标'],
        'deployment_roles': ['空中侦察', '态势建模', '高点通信辅助'],
        'models': ['Matrice 350 RTK', 'FC-30T'],
        'inventory_count': 8,
        'unit_cost_rmb': 145000,
        'recommended_quantity': 2,
        'recommended_tasks': ['高点侦察', '外立面热源扫描', '态势图回传'],
    },
    {
        'id': 'mesh_radio',
        'name': '自组网通信设备',
        'category': '通信保障',
        'summary': '用于复杂建筑、地下空间和断网环境下的多点通信中继。',
        'supported_scenarios': ['high_rise_fire', 'subway_fire', 'earthquake_rescue'],
        'capabilities': ['无线中继', '前后方语音数据回传', '复杂空间覆盖'],
        'deployment_roles': ['通信中继', '前后方联通', '态势共享'],
        'models': ['MeshCom M6', 'E-LINK 5G Relay'],
        'inventory_count': 12,
        'unit_cost_rmb': 32000,
        'recommended_quantity': 4,
        'recommended_tasks': ['楼层通信中继', '电梯前室信号覆盖', '指挥链路保障'],
    },
    {
        'id': 'ladder_truck',
        'name': '举高喷射车',
        'category': '灭火攻坚装备',
        'summary': '用于高层外部攻坚、窗口救援和高位供水喷射。',
        'supported_scenarios': ['high_rise_fire'],
        'capabilities': ['高位喷射', '外部破拆救援', '高空观察'],
        'deployment_roles': ['外围压制', '窗口救援', '高位灭火'],
        'models': ['DG54', 'JP62'],
        'inventory_count': 3,
        'unit_cost_rmb': 4200000,
        'recommended_quantity': 1,
        'recommended_tasks': ['高层外围压制', '窗口救援', '高位供水'],
    },
    {
        'id': 'hazmat_team',
        'name': '危化处置组',
        'category': '专业作战力量',
        'summary': '用于危化识别、堵漏、围控和污染扩散控制。',
        'supported_scenarios': ['chemical_leak'],
        'capabilities': ['介质侦检', '堵漏控源', '围堰与污染控制'],
        'deployment_roles': ['危化侦检', '堵漏处置', '扩散控制'],
        'models': ['A级防化编组', '危化堵漏编组'],
        'inventory_count': 4,
        'unit_cost_rmb': 260000,
        'recommended_quantity': 1,
        'recommended_tasks': ['介质侦检', '泄漏源堵漏', '围堰与污染面控制'],
    },
    {
        'id': 'decon_unit',
        'name': '洗消单元',
        'category': '洗消保障',
        'summary': '用于人员、装备与区域洗消，闭合危化处置链路。',
        'supported_scenarios': ['chemical_leak'],
        'capabilities': ['人员洗消', '装备洗消', '污染区转运保障'],
        'deployment_roles': ['洗消作业', '污染控制', '恢复保障'],
        'models': ['XC-12 洗消帐篷', 'DCU-8 洗消拖车'],
        'inventory_count': 5,
        'unit_cost_rmb': 180000,
        'recommended_quantity': 1,
        'recommended_tasks': ['暴露人员洗消', '装备洗消', '污染区转运保障'],
    },
]


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


@dataclass
class TaskZoneAgent:
    def build(self, scenario: ScenarioInput) -> list[TaskZone]:
        if scenario.scenario_type == 'high_rise_fire':
            floors = sorted(scenario.floors_affected or [12, 13, 14])
            attack_floor = floors[-1]
            search_floor = floors[-2] if len(floors) > 1 else attack_floor - 1
            support_floor = floors[0]
            return [
                TaskZone(
                    zone_name='主攻控火区',
                    target=f'{attack_floor} 楼层',
                    assigned_team='内攻灭火组',
                    priority='P1',
                    tasks=['压制明火', '阻断垂直蔓延', '回传热成像与可燃物分布'],
                    equipment_support=['消防机器人', '举高喷射车', '主攻水枪阵地'],
                ),
                TaskZone(
                    zone_name='搜救疏散区',
                    target=f'{search_floor} 楼层',
                    assigned_team='搜救组',
                    priority='P1',
                    tasks=['搜索被困人员', '引导疏散', '复核防烟楼梯通行性'],
                    equipment_support=['无人机', '破拆器材', '照明装备'],
                ),
                TaskZone(
                    zone_name='供水通信支撑区',
                    target=f'{support_floor} 楼层及避难层',
                    assigned_team='供水排烟组 / 通信保障组',
                    priority='P2',
                    tasks=['部署水带干线', '布设自组网中继', '建立医疗与转运接驳点'],
                    equipment_support=['自组网通信设备', '排烟机', '医疗转运单元'],
                ),
            ]
        if scenario.scenario_type == 'chemical_leak':
            return [
                TaskZone(
                    zone_name='上风向指挥集结区',
                    target='上风向安全区',
                    assigned_team='现场指挥员 / 医疗救护组',
                    priority='P1',
                    tasks=['建立指挥席', '组织伤员转运', '管控进入污染区人员'],
                    equipment_support=['指挥车', '医疗救护包', '通信中继'],
                ),
                TaskZone(
                    zone_name='源头堵漏区',
                    target='泄漏源核心区',
                    assigned_team='危化处置组',
                    priority='P1',
                    tasks=['介质侦检', '堵漏控源', '围堰截流'],
                    equipment_support=['危化处置组', '堵漏工具组', '消防机器人'],
                ),
                TaskZone(
                    zone_name='洗消转运区',
                    target='污染边界外侧',
                    assigned_team='洗消组',
                    priority='P2',
                    tasks=['人员装备洗消', '污染物暂存', '转运闭环管理'],
                    equipment_support=['洗消单元', '转运担架', '洗消帐篷'],
                ),
            ]
        return [
            TaskZone(
                zone_name='核心处置区',
                target='事故核心区',
                assigned_team='主攻组',
                priority='P1',
                tasks=['快速侦察', '主任务处置', '持续回传关键态势'],
                equipment_support=['无人机', '通信设备'],
            ),
            TaskZone(
                zone_name='外围支撑区',
                target='警戒与后勤区',
                assigned_team='后勤保障组',
                priority='P2',
                tasks=['物资补给', '人员轮换', '伤员转运'],
                equipment_support=['后勤车辆', '照明装备'],
            ),
        ]


class SimulationEngine:
    def __init__(self, llm_client: Any | None = None) -> None:
        self.risk_assessor = RiskAssessorAgent()
        self.strategy_agent = StrategyAgent()
        self.action_planner = ActionPlannerAgent()
        self.resource_planner = ResourcePlannerAgent()
        self.communication_agent = CommunicationAgent()
        self.timeline_agent = TimelineAgent()
        self.task_zone_agent = TaskZoneAgent()
        self.llm_client = llm_client or OpenAICompatibleLLMClient()

    def get_catalog(self) -> ScenarioCatalog:
        return ScenarioCatalog(
            version='1.5.0',
            supported_scenarios=SCENARIO_LABELS,
            supported_resources=RESOURCE_LABELS,
            severity_levels=SEVERITY_LABELS,
        )

    def get_equipment_library(self) -> EquipmentLibrary:
        return EquipmentLibrary(
            version='1.5.0',
            items=[EquipmentItem(**item) for item in EQUIPMENT_LIBRARY],
        )

    def run(self, scenario: ScenarioInput) -> SimulationReport:
        risks = self.risk_assessor.evaluate(scenario)
        strategy = self.strategy_agent.recommend(scenario, risks)
        action_plan = self.action_planner.build(scenario)
        resource_plan = self.resource_planner.build(scenario)
        communication_plan = self.communication_agent.build(scenario)
        timeline = self.timeline_agent.build(scenario)
        task_zones = self.task_zone_agent.build(scenario)

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
            task_zones=task_zones,
            assumptions=assumptions,
        )

    def run_with_llm(self, scenario: ScenarioInput) -> SimulationReport:
        report = self.run(scenario)
        try:
            enhancement_payload = self.llm_client.enhance_report(scenario, report)
        except Exception:
            report.llm_status = 'fallback'
            report.llm_enhancement = None
            return report

        report.llm_status = 'enhanced'
        report.llm_enhancement = LLMEnhancement(**enhancement_payload)
        return report

    def render_markdown(self, report: SimulationReport) -> str:
        sections = [
            '# 应急场景推演报告',
            '',
            '## 事件摘要',
            f'- 场景类型：{report.summary.scenario_type_label}',
            f'- 事件等级：{report.summary.incident_level}',
            f'- 推荐总策略：{report.summary.recommended_strategy}',
            '',
            '## 主要风险',
        ]
        sections.extend([f'- {risk}' for risk in report.summary.top_risks])
        sections.extend(['', '## 行动计划', '### 立即行动'])
        sections.extend([f'- {item}' for item in report.action_plan.immediate_actions])
        sections.extend(['', '### 稳定控制'])
        sections.extend([f'- {item}' for item in report.action_plan.stabilization_actions])
        sections.extend(['', '### 后续收尾'])
        sections.extend([f'- {item}' for item in report.action_plan.follow_up_actions])
        sections.extend(['', '## 资源调度'])
        sections.extend([f'- 优先序列：{"、".join(report.resource_plan.dispatch_priority)}'])
        sections.extend([f'- 推荐装备：{"、".join(report.resource_plan.recommended_assets)}'])
        if report.resource_plan.capability_gaps:
            sections.append('- 能力缺口：')
            sections.extend([f'  - {item}' for item in report.resource_plan.capability_gaps])
        sections.extend(['', '## 通信保障'])
        sections.append(f'- 指挥模式：{report.communication_plan.command_mode}')
        sections.append(f'- 报送频率：{report.communication_plan.reporting_frequency}')
        sections.extend([f'- {item}' for item in report.communication_plan.key_actions])
        sections.extend(['', '## 时间线'])
        sections.extend([f'- T+{step.minute} 分钟｜{step.owner}：{step.objective}' for step in report.timeline])
        sections.extend(['', '## 任务分区'])
        for zone in report.task_zones:
            sections.append(f'- {zone.zone_name}｜{zone.target}｜{zone.assigned_team}｜优先级 {zone.priority}')
            sections.extend([f'  - 任务：{item}' for item in zone.tasks])
            sections.extend([f'  - 装备：{item}' for item in zone.equipment_support])
        sections.extend(['', '## 关键假设'])
        sections.extend([f'- {item}' for item in report.assumptions])
        if report.llm_enhancement:
            sections.extend(['', '## 大模型增强建议'])
            sections.append(f'- 摘要：{report.llm_enhancement.executive_summary}')
            sections.extend(['', '### 指挥简报'])
            sections.extend([f'- {item}' for item in report.llm_enhancement.command_brief])
            sections.extend(['', '### 资源优化'])
            sections.extend([f'- {item}' for item in report.llm_enhancement.resource_optimization])
            sections.extend(['', '### 对外沟通'])
            sections.extend([f'- {item}' for item in report.llm_enhancement.public_communication])
        return '\n'.join(sections)

    def render_markdown_response(self, report: SimulationReport) -> MarkdownReport:
        return MarkdownReport(content=self.render_markdown(report))
