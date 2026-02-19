from PIL import Image

def build_thumbnail_brief(img: Image.Image, hint: str = "") -> dict:
    # Minimal starter: you can later replace with a vision model call.
    return {
        "scene_type": "courtroom",
        "visible_elements": ["defendant", "face paint", "tattoos", "court setting"],
        "vibe": ["menacing", "public judgment", "shock reveal"],
        "hook_angle": "judge thinks defendant is violent; truth is worse",
        "user_hint": hint.strip() if hint else ""
    }
