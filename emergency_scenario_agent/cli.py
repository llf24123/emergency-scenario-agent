from __future__ import annotations

import argparse
import json

from .engine import SimulationEngine
from .models import ScenarioInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='应急场景推演 Agent CLI')
    parser.add_argument('--scenario-type', required=True, choices=['high_rise_fire', 'chemical_leak', 'earthquake_rescue', 'flood_response', 'subway_fire'])
    parser.add_argument('--location-type', required=True)
    parser.add_argument('--severity', required=True, choices=['medium', 'high', 'critical'])
    parser.add_argument('--weather', required=True)
    parser.add_argument('--time-of-day', required=True)
    parser.add_argument('--people-trapped', type=int, default=0)
    parser.add_argument('--floors-affected', default='')
    parser.add_argument('--hazards', default='')
    parser.add_argument('--available-resources', default='')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scenario = ScenarioInput(
        scenario_type=args.scenario_type,
        location_type=args.location_type,
        severity=args.severity,
        weather=args.weather,
        time_of_day=args.time_of_day,
        people_trapped=args.people_trapped,
        floors_affected=[int(item) for item in args.floors_affected.split(',') if item],
        hazards=[item for item in args.hazards.split(',') if item],
        available_resources=[item for item in args.available_resources.split(',') if item],
    )
    engine = SimulationEngine()
    report = engine.run(scenario)
    if args.format == 'markdown':
        print(engine.render_markdown(report))
    else:
        print(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
