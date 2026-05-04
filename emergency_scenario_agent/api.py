from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .engine import SimulationEngine
from .models import MarkdownReport, ScenarioCatalog, ScenarioInput, SimulationReport

app = FastAPI(title='应急场景推演Agent', version='1.2.0')
engine = SimulationEngine()
frontend_dir = Path(__file__).parent / 'frontend'
app.mount('/static', StaticFiles(directory=frontend_dir), name='static')


@app.get('/')
def frontend_home() -> FileResponse:
    return FileResponse(frontend_dir / 'index.html')


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/catalog', response_model=ScenarioCatalog)
def catalog() -> ScenarioCatalog:
    return engine.get_catalog()


@app.post('/simulate', response_model=SimulationReport)
def simulate(payload: ScenarioInput) -> SimulationReport:
    return engine.run(payload)


@app.post('/simulate/markdown', response_model=MarkdownReport)
def simulate_markdown(payload: ScenarioInput) -> MarkdownReport:
    report = engine.run(payload)
    return engine.render_markdown_response(report)
