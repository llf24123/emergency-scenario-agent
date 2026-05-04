# 应急场景推演 Agent

一个面向 **消防 / 应急 / 安全处置** 场景的多 Agent 推演系统。它将输入的事故信息结构化后，交给多个职责清晰的 Agent 协同分析，输出可直接用于汇报、值守研判、演练准备或系统集成的推演结果。

> 当前版本：**v1.1.0**

---

## 核心能力

- **多 Agent 协同推演**
  - 风险评估 Agent
  - 战术策略 Agent
  - 行动计划 Agent
  - 资源调度 Agent
  - 通信保障 Agent
  - 时间线 Agent
- **支持 API 与 CLI 双入口**
- **支持 JSON / Markdown 两种输出**
- **内置场景目录接口**，方便前端或第三方系统对接
- **内置测试、Dockerfile、GitHub Actions CI**

---

## 当前支持的场景

- `high_rise_fire`：高层火灾
- `chemical_leak`：危化品泄漏
- `earthquake_rescue`：地震救援
- `flood_response`：城市内涝
- `subway_fire`：地铁火灾

---

## 输出内容

每次推演会输出：

- 事件摘要
- 主要风险
- 推荐总策略
- 行动计划（立即行动 / 稳定控制 / 后续收尾）
- 资源调度建议
- 通信保障建议
- 时间线
- 关键假设

这使它不只是一个“回答问题的聊天机器人”，而是一个 **可生成结构化推演报告** 的引擎。

---

## 项目结构

```text
emergency_scenario_agent/
├── .github/workflows/ci.yml
├── emergency_scenario_agent/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── engine.py
│   └── models.py
├── examples/
│   ├── chemical_leak.json
│   └── high_rise_fire.json
├── tests/
│   ├── test_api.py
│   └── test_engine.py
├── .gitignore
├── Dockerfile
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## 安装

### 本地开发安装

```bash
git clone https://github.com/llf24123/emergency-scenario-agent.git
cd emergency-scenario-agent
python3 -m pip install -e .[dev]
```

### 最小安装

```bash
python3 -m pip install -e .
```

---

## 启动 API

```bash
python3 -m uvicorn emergency_scenario_agent.api:app --host 0.0.0.0 --port 8000
```

启动后可访问：

- 健康检查：`GET /health`
- 场景目录：`GET /catalog`
- JSON 推演：`POST /simulate`
- Markdown 推演：`POST /simulate/markdown`
- Swagger 文档：`http://127.0.0.1:8000/docs`

---

## API 示例

### 1）查看支持的场景目录

```bash
curl http://127.0.0.1:8000/catalog
```

### 2）生成 JSON 推演报告

```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  -d @examples/high_rise_fire.json
```

### 3）生成 Markdown 推演报告

```bash
curl -X POST http://127.0.0.1:8000/simulate/markdown \
  -H 'Content-Type: application/json' \
  -d @examples/chemical_leak.json
```

---

## CLI 示例

### JSON 输出

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

### Markdown 输出

```bash
python3 -m emergency_scenario_agent.cli \
  --scenario-type chemical_leak \
  --location-type industrial_park \
  --severity critical \
  --weather rainy \
  --time-of-day night \
  --people-trapped 2 \
  --hazards toxic_gas,corrosive_material \
  --available-resources hazmat_team,decon_unit,fire_robot \
  --format markdown
```

---

## 设计架构

### Agent 分工

- `RiskAssessorAgent`：识别关键风险
- `StrategyAgent`：给出总体处置策略
- `ActionPlannerAgent`：生成分阶段行动建议
- `ResourcePlannerAgent`：生成资源调度与缺口分析
- `CommunicationAgent`：生成通信与指挥链建议
- `TimelineAgent`：生成分钟级推演时间线
- `SimulationEngine`：编排多个 Agent 并输出报告

### 为什么这样设计

这种拆分方式便于后续扩展：

- 替换某个 Agent 的实现逻辑
- 将规则引擎升级为“规则 + LLM”混合架构
- 接入装备数据库、地图系统、建筑图纸、实时气象
- 单独测试每类推演能力

---

## 测试

```bash
python3 -m pytest -q
```

当前测试覆盖：

- 高层火灾推演主流程
- 危化品泄漏洗消逻辑
- Markdown 报告渲染
- API 返回结构
- 场景目录接口

---

## Docker 运行

### 构建镜像

```bash
docker build -t emergency-scenario-agent .
```

### 启动容器

```bash
docker run --rm -p 8000:8000 emergency-scenario-agent
```

---

## 后续建议

你可以基于这个项目继续扩展：

1. **接入大模型**：生成更贴近真实指挥口径的研判说明
2. **接入装备库**：从“推荐装备类别”升级到“推荐型号 + 数量 + 成本”
3. **接入地图/建筑图纸**：做空间化推演
4. **接入前端页面**：形成完整的态势推演平台
5. **增加推演评分机制**：用于培训、演练与复盘
6. **增加导出 Word / PDF**：直接形成汇报材料

---

## License

MIT
