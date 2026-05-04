from __future__ import annotations

from fastapi import FastAPI

from .engine import SimulationEngine
from .models import ScenarioInput, SimulationReport

app = FastAPI(title='应急场景推演Agent', version='1.0.0')
engine = SimulationEngine()


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/simulate', response_model=SimulationReport)
def simulate(payload: ScenarioInput) -> SimulationReport:
    return engine.run(payload)
