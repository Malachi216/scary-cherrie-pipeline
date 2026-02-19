import re

def split_into_acts(script_text: str) -> dict:
    # If your scripts have explicit ACT markers, parse them.
    # Otherwise, split by headings like "ACT 1", "ACT 2", etc.
    acts = {}
    pattern = r"(ACT\s+\d+[:\s].*?)(?=ACT\s+\d+[:\s]|$)"
    matches = re.findall(pattern, script_text, flags=re.DOTALL|re.IGNORECASE)
    if matches:
        for m in matches:
            head = re.match(r"(ACT\s+\d+)", m, flags=re.IGNORECASE)
            key = head.group(1).upper() if head else f"ACT_{len(acts)+1}"
            acts[key] = m.strip()
    else:
        # fallback: treat as one act
        acts["ACT 1"] = script_text.strip()
    return acts
