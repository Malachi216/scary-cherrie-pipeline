def score_act_bundle(acts: dict) -> dict:
    # TODO: Replace with rubric-based scoring (LLM + deterministic checks).
    return {k: {"cold_open": 4, "bridge": 4, "timeline": 4, "sentencing": 3} for k in acts.keys()}

# some comment test
