# core/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ThumbnailBrief(BaseModel):
    scene_type: str = Field(default="unknown", description="courtroom / street / house / interrogation / etc.")
    visible_elements: List[str] = Field(default_factory=list)
    vibe: List[str] = Field(default_factory=list)
    hook_angle: str = Field(default="", description="1-line hook angle implied by thumbnail")
    composition_notes: List[str] = Field(default_factory=list)
    text_on_thumbnail: Optional[str] = Field(default=None, description="Any text visible on the thumbnail (manual entry)")
    colors: Dict[str, str] = Field(default_factory=dict, description="dominant colors in hex")
    brightness: str = Field(default="unknown", description="low / medium / high")
    contrast: str = Field(default="unknown", description="low / medium / high")
    user_hint: str = Field(default="", description="Optional hint you typed in the UI")

    def to_dict(self) -> dict:
        return self.model_dump()
