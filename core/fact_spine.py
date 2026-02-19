def build_fact_spine(chosen_case: dict) -> dict:
    # This is the “real spine” + allowed fictionalization rules.
    return {
        "case_title": chosen_case.get("title", ""),
        "real_spine": {
            "timeline": [],
            "key_events": [],
            "outcome": "",
            "evidence": [],
            "sources": chosen_case.get("sources", [])
        },
        "fiction_layer_rules": {
            "names_are_fictional": True,
            "dialogue_is_recreated": True,
            "juicy_details_allowed": True,
            "must_not_contradict_real_spine": True
        }
    }
