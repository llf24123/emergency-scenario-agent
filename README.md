# 应急场景推演 Agent

一个可直接运行的 **多 Agent 应急推演系统**。它不是单纯的聊天机器人，而是把场景输入结构化后，交给多个职责清晰的 Agent 协同输出：

- 风险评估
- 行动方案
- 资源调度建议
- 通信保障建议
- 分钟级时间线
- 关键假设条件

## 1. 适用场景

当前内置：

- `high_rise_fire` 高层火灾
- `chemical_leak` 危化品泄漏
- `earthquake_rescue` 地震救援
- `flood_response` 城市内涝
- `subway_fire` 地铁火灾

## 2. 项目结构

```text
emergency_scenario_agent/
├── emergency_scenario_agent/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── engine.py
│   └── models.py
├── tests/
│   ├── test_api.py
│   └── test_engine.py
└── pyproject.toml
```

## 3. 安装

```bash
cd emergency_scenario_agent
python3 -m pip install -e . --break-system-packages
python3 -m pip install -e .[dev] --break-system-packages
```

## 4. 启动 API

```bash
python3 -m uvicorn emergency_scenario_agent.api:app --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 5. API 调用示例

```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario_type": "high_rise_fire",
    "location_type": "residential_tower",
    "severity": "high",
    "weather": "windy",
    "time_of_day": "night",
    "people_trapped": 8,
    "floors_affected": [18, 19, 20],
    "hazards": ["smoke", "power_outage"],
    "available_resources": ["fire_robot", "drone", "mesh_radio"]
  }'
```

## 6. CLI 调用示例

```bash
python3 -m emergency_scenario_agent.cli \
  --scenario-type high_rise_fire \
  --location-type residential_tower \
  --severity high \
  --weather windy \
  --time-of-day night \
  --people-trapped 8 \
  --floors-affected 18,19,20 \
  --hazards smoke,power_outage \
  --available-resources fire_robot,drone,mesh_radio
```

## 7. 架构说明

### Agent 分工

- `RiskAssessorAgent`：识别风险
- `StrategyAgent`：输出总战术
- `ActionPlannerAgent`：生成行动计划
- `ResourcePlannerAgent`：生成资源配置建议
- `CommunicationAgent`：输出通信保障策略
- `TimelineAgent`：生成时间线
- `SimulationEngine`：作为总控 Orchestrator，汇总结果

## 8. 后续扩展方向

你可以继续加：

1. 接入 LLM，把规则推演升级成“规则 + 大模型”混合推演
2. 接入地图/建筑图纸/实时气象
3. 增加装备数据库和成本测算
4. 增加可视化前端（态势图、任务卡、时间轴）
5. 增加推演评分与复盘模块

## 9. 测试

```bash
python3 -m pytest -q
```
