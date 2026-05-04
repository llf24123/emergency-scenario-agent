from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import yaml

from .models import LLMEnhancement, ScenarioInput, SimulationReport


@dataclass
class LLMConfig:
    enabled: bool
    model: str | None
    base_url: str | None
    api_key: str | None
    timeout: int = 60


def load_llm_config() -> LLMConfig:
    env_enabled = os.getenv('SCENARIO_AGENT_LLM_ENABLED', '').lower()
    enabled = env_enabled in {'1', 'true', 'yes', 'on'} if env_enabled else True
    model = os.getenv('SCENARIO_AGENT_LLM_MODEL')
    base_url = os.getenv('SCENARIO_AGENT_LLM_BASE_URL')
    api_key = os.getenv('SCENARIO_AGENT_LLM_API_KEY')
    timeout = int(os.getenv('SCENARIO_AGENT_LLM_TIMEOUT', '60'))

    config_path = Path('/root/.hermes/config.yaml')
    if config_path.exists() and (not model or not base_url or not api_key):
        data = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
        model_block = data.get('model', {})
        model = model or model_block.get('default')
        base_url = base_url or model_block.get('base_url')
        api_key = api_key or model_block.get('api_key')

    return LLMConfig(
        enabled=enabled and bool(model and base_url and api_key),
        model=model,
        base_url=base_url.rstrip('/') if base_url else None,
        api_key=api_key,
        timeout=timeout,
    )


class OpenAICompatibleLLMClient:
    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or load_llm_config()

    def is_available(self) -> bool:
        return self.config.enabled

    def enhance_report(self, scenario: ScenarioInput, report: SimulationReport) -> dict[str, Any]:
        if not self.is_available():
            raise RuntimeError('llm unavailable')

        prompt = self._build_prompt(scenario, report)
        payload = {
            'model': self.config.model,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        '你是一名消防与应急指挥专家。请基于已有规则推演结果，进一步输出更适合汇报和指挥简报的增强内容。'
                        '必须只返回 JSON 对象，不要输出 markdown 代码块。'
                    ),
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.4,
            'response_format': {'type': 'json_object'},
        }
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
        }
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    response = client.post(f'{self.config.base_url}/chat/completions', headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                content = data['choices'][0]['message']['content']
                parsed = json.loads(content)
                return LLMEnhancement(**parsed).model_dump()
            except Exception as exc:  # pragma: no cover - exercised indirectly by fallback tests
                last_error = exc
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise last_error

    def _build_prompt(self, scenario: ScenarioInput, report: SimulationReport) -> str:
        return json.dumps(
            {
                'instruction': '请输出 executive_summary、command_brief、resource_optimization、public_communication 四个字段，后 3 个字段为中文字符串数组，每个数组 2-4 条。',
                'scenario': scenario.model_dump(),
                'rule_report': report.model_dump(exclude={'llm_enhancement'}),
            },
            ensure_ascii=False,
            indent=2,
        )
