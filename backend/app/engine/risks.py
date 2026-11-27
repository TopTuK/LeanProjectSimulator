"""Deterministic managed-risk outcomes and response effects."""

import hashlib

from app.engine import rules
from app.engine.scenario import RiskDef, ScenarioData


def response_settings(option: dict | None) -> dict:
    return (option or {}).get("effects", {}).get("risk_response", {})


def probability(risk: RiskDef, option: dict | None, cfg: dict) -> float:
    multiplier = response_settings(option).get("probability", 1.0)
    return min(0.95, max(0.0, risk.probability * rules.difficulty(cfg, "risk") * multiplier))


def impact_multiplier(option: dict | None) -> float:
    return response_settings(option).get("impact", 1.0)


def draw(session_id: str, risk_key: str) -> float:
    digest = hashlib.sha256(f"{session_id}:{risk_key}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / (2**64 - 1)


def scaled_impact(impact: dict, multiplier: float) -> dict:
    result = {}
    for key, value in impact.items():
        if key == "effort":
            result[key] = {no: hours * multiplier for no, hours in value.items()}
        elif key in ("cost", "quality", "motivation"):
            result[key] = value * multiplier
        elif multiplier > 0:
            result[key] = value
    return result


def occur(
    scn: ScenarioData, state: dict, risk: RiskDef, option: dict | None,
    cfg: dict, session_id: str, minute: float,
) -> dict:
    roll = draw(session_id, risk.key)
    chance = probability(risk, option, cfg)
    multiplier = impact_multiplier(option)
    occurred = roll < chance
    if occurred:
        rules.apply_effects(scn, state, scaled_impact(risk.impact, multiplier), cfg, minute)
    return {
        "occurred": occurred,
        "roll": roll,
        "probability": chance,
        "impact_multiplier": multiplier,
        "response": option["key"] if option else None,
        "minute": minute,
    }
