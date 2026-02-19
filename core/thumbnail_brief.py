# core/thumbnail_brief.py
from PIL import Image, ImageStat
from collections import Counter
from typing import Dict, List, Tuple
import math

from .schemas import ThumbnailBrief

def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def _dominant_colors(img: Image.Image, k: int = 5) -> Dict[str, str]:
    """
    Fast dominant-color estimation:
    - downsample
    - quantize to reduce palette
    - count top colors
    """
    small = img.copy()
    small.thumbnail((256, 256))
    quant = small.convert("P", palette=Image.Palette.ADAPTIVE, colors=64).convert("RGB")
    pixels = list(quant.getdata())
    counts = Counter(pixels).most_common(k)

    out = {}
    for i, (rgb, _) in enumerate(counts, start=1):
        out[f"color_{i}"] = _rgb_to_hex(rgb)
    return out

def _brightness_contrast(img: Image.Image) -> Tuple[str, str]:
    """
    Heuristic brightness + contrast:
    - brightness: mean luminance
    - contrast: stddev luminance
    """
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    mean = stat.mean[0]          # 0..255
    std = stat.stddev[0]         # 0..~80

    # Brightness buckets
    if mean < 85:
        brightness = "low"
    elif mean < 170:
        brightness = "medium"
    else:
        brightness = "high"

    # Contrast buckets
    if std < 30:
        contrast = "low"
    elif std < 55:
        contrast = "medium"
    else:
        contrast = "high"

    return brightness, contrast

def _guess_scene_type(elements: List[str], hint: str) -> str:
    text = " ".join(elements + [hint]).lower()

    if any(w in text for w in ["court", "courtroom", "judge", "trial", "sentencing"]):
        return "courtroom"
    if any(w in text for w in ["cell", "prison", "inmate", "guards", "block"]):
        return "prison"
    if any(w in text for w in ["cctv", "footage", "camera", "bodycam", "dashcam"]):
        return "footage"
    if any(w in text for w in ["house", "basement", "room", "apartment"]):
        return "residential"
    if any(w in text for w in ["interrogation", "interview", "station"]):
        return "interrogation"
    return "unknown"

def _suggest_vibe(brightness: str, contrast: str) -> List[str]:
    vibe = []
    if brightness == "low":
        vibe.append("ominous")
    if contrast in ("medium", "high"):
        vibe.append("high tension")
    if brightness == "high" and contrast == "high":
        vibe.append("harsh clarity")
    if not vibe:
        vibe.append("uneasy")
    return vibe

def build_thumbnail_brief(img: Image.Image, hint: str = "") -> dict:
    """
    Produces a structured thumbnail brief using lightweight heuristics.
    You can later swap this function to call Gemini Vision, but keep this output shape.
    """
    img = img.convert("RGB")

    brightness, contrast = _brightness_contrast(img)
    colors = _dominant_colors(img, k=5)

    # Minimal baseline elements (user can edit)
    visible_elements = []
    composition_notes = []

    # Heuristic composition notes
    w, h = img.size
    if w > h:
        composition_notes.append("landscape thumbnail")
    else:
        composition_notes.append("portrait/vertical thumbnail")

    if brightness == "low":
        composition_notes.append("dark lighting suggests danger/unknown")
    if contrast == "high":
        composition_notes.append("high contrast increases dramatic emphasis")

    # Add elements based on hint keywords (since we’re not doing heavy vision yet)
    hint_l = (hint or "").lower()
    if "court" in hint_l or "judge" in hint_l:
        visible_elements += ["courtroom", "defendant"]
    if "clown" in hint_l or "face paint" in hint_l:
        visible_elements += ["face paint"]
    if "tattoo" in hint_l:
        visible_elements += ["tattoos"]
    if "hoodie" in hint_l:
        visible_elements += ["hoodie"]

    # If user didn’t provide hint, keep elements generic
    if not visible_elements:
        visible_elements = ["person", "close-up/headshot style", "dramatic framing"]

    scene_type = _guess_scene_type(visible_elements, hint or "")
    vibe = _suggest_vibe(brightness, contrast)

    # Default hook angle — user can edit
    hook_angle = "Authority misreads what they’re seeing; the truth is worse than it looks."

    brief = ThumbnailBrief(
        scene_type=scene_type,
        visible_elements=sorted(list(set(visible_elements))),
        vibe=vibe,
        hook_angle=hook_angle,
        composition_notes=composition_notes,
        text_on_thumbnail=None,
        colors=colors,
        brightness=brightness,
        contrast=contrast,
        user_hint=hint or "",
    )

    return brief.to_dict()
