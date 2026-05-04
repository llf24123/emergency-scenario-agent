FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY emergency_scenario_agent ./emergency_scenario_agent

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "emergency_scenario_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
