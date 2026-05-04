# 应急场景推演 Agent

一个面向 **消防 / 应急 / 安全处置** 场景的多 Agent 推演系统。它将输入的事故信息结构化后，交给多个职责清晰的 Agent 协同分析，输出可直接用于汇报、值守研判、演练准备或系统集成的推演结果。

> 当前版本：**v1.5.0**

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
- **内置 Web 前端控制台**，可直接填写场景并查看结果
- **新增前端态势总览页**，可查看预警、时间线、楼层任务分区与资源缺口
- **新增装备库**，按场景查看装备能力、适用任务、型号、库存、参考单价与建议投送数量
- **支持 JSON / Markdown 两种输出**
- **支持大模型增强模式**，可补充指挥简报、资源优化和对外沟通建议
- **内置场景目录接口与装备库接口**，方便前端或第三方系统对接
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
│   ├── frontend/
│   │   ├── app.js
│   │   └── index.html
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

- 前端控制台：`GET /`
- 健康检查：`GET /health`
- 场景目录：`GET /catalog`
- 装备库：`GET /equipment-library`
- JSON 推演：`POST /simulate`
- LLM 增强推演：`POST /simulate/llm`
- Markdown 推演：`POST /simulate/markdown`
- LLM 增强 Markdown：`POST /simulate/llm/markdown`
- Swagger 文档：`http://127.0.0.1:8000/docs`

### 前端控制台说明

打开 `http://127.0.0.1:8000/` 后，你可以：

- 直接填写场景参数
- 一键载入高层火灾 / 危化泄漏示例
- 查看“推演结果”页：摘要、风险、行动建议、资源建议、通信保障
- 查看“态势总览”页：关键预警、行动时间线、楼层任务分区、资源缺口
- 查看“装备库”页：按场景筛选装备能力、部署角色、型号、库存与参考成本
- 复制或下载 Markdown 报告
- 实时查看 JSON 原始响应，便于系统联调

---

## API 示例

### 1）查看支持的场景目录

```bash
curl http://127.0.0.1:8000/catalog
```

### 2）查看装备库

```bash
curl http://127.0.0.1:8000/equipment-library
```

### 3）生成 JSON 推演报告

```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  -d @examples/high_rise_fire.json
```

### 4）生成 LLM 增强推演报告

```bash
curl -X POST http://127.0.0.1:8000/simulate/llm \
  -H 'Content-Type: application/json' \
  -d @examples/high_rise_fire.json
```

### 5）生成 Markdown 推演报告

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

## 大模型配置

默认情况下，系统会优先读取以下环境变量：

- `SCENARIO_AGENT_LLM_ENABLED`
- `SCENARIO_AGENT_LLM_MODEL`
- `SCENARIO_AGENT_LLM_BASE_URL`
- `SCENARIO_AGENT_LLM_API_KEY`
- `SCENARIO_AGENT_LLM_TIMEOUT`

如果这些变量未配置，系统会尝试回退读取 `~/.hermes/config.yaml` 中的主模型配置，并以 OpenAI 兼容 `/chat/completions` 协议调用。

### 示例

```bash
export SCENARIO_AGENT_LLM_ENABLED=true
export SCENARIO_AGENT_LLM_MODEL=gpt-5.4
export SCENARIO_AGENT_LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
export SCENARIO_AGENT_LLM_API_KEY=sk-xxxx
```

### 回退策略

- 大模型调用成功：返回 `llm_status = enhanced`
- 大模型调用失败：自动回退规则推演，返回 `llm_status = fallback`

这意味着即使上游模型偶发超时，系统也能继续输出可用结果。

### Agent 如何接入大模型

项目采用“**规则主链先跑，再由大模型做增强**”的接入方式：

1. `SimulationEngine.run()` 先完成风险评估、策略研判、行动计划、资源调度、通信保障、时间线生成。
2. `SimulationEngine.run_with_llm()` 再把 `scenario` 与 `rule_report` 交给 `OpenAICompatibleLLMClient`。
3. `OpenAICompatibleLLMClient` 通过 OpenAI 兼容 `POST /chat/completions` 调用上游模型。
4. 大模型只返回结构化增强字段：`executive_summary`、`command_brief`、`resource_optimization`、`public_communication`。
5. 如果上游失败，系统自动回退到纯规则结果，不影响主流程。

简化调用关系如下：

```text
结构化场景输入
  -> SimulationEngine.run()
  -> 规则报告 rule_report
  -> OpenAICompatibleLLMClient.enhance_report()
  -> llm_enhancement
  -> 最终 JSON / Markdown / 前端态势页展示
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
- `OpenAICompatibleLLMClient`：在增强模式下生成指挥简报、资源优化和对外沟通建议

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
- 装备库接口与装备元数据
- 楼层任务分区生成与 Markdown 渲染
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

1. **接入地图/建筑图纸**：做空间化推演
2. **增加推演评分机制**：用于培训、演练与复盘
3. **增加导出 Word / PDF / PPT**：直接形成汇报材料
4. **接入实时装备状态**：从静态装备库升级到库存、位置、数量联动
5. **接入实时气象与视频流**：增强现场态势感知
6. **增加高层灭火专项模型**：强化供水、排烟、机器人协同与自组网布点

---

## License

MIT
