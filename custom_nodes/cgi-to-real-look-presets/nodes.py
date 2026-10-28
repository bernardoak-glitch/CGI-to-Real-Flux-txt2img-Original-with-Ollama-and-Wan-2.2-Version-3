from pathlib import Path

import numpy as np
import torch
from PIL import Image

from .presets import CAMERA, COLOR, LIGHTING

CATEGORY = "CGI to Real"
THUMBS = Path(__file__).resolve().parent / "web" / "thumbs"
_CACHE = {}


def _slug(label):
    chars = []
    for ch in str(label).lower():
        chars.append(ch if ch.isalnum() else "-")
    text = "".join(chars)
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "none"


def _load_thumb(kind, label):
    key = (kind, label)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    path = THUMBS / kind / f"{_slug(label)}.png"
    if path.is_file():
        arr = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0)
    else:
        tensor = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
    _CACHE[key] = tensor
    return tensor


class _LookPreset:
    PRESETS = {}
    KIND = ""
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("STRING", "preview")
    FUNCTION = "pick"
    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(cls):
        labels = list(cls.PRESETS.keys())
        return {"required": {"preset": (labels,)}}

    def pick(self, preset):
        return (self.PRESETS.get(preset, ""), _load_thumb(self.KIND, preset))


class CGILightingSetup(_LookPreset):
    PRESETS = LIGHTING
    KIND = "lighting"
    DESCRIPTION = "Dropdown of lighting setups. Outputs a photography sentence and a picture of that light on a mannequin."


class CGICameraLens(_LookPreset):
    PRESETS = CAMERA
    KIND = "camera"
    DESCRIPTION = "Dropdown of camera and lens setups. Outputs a photography sentence and a picture of that framing."


class CGIColorAesthetic(_LookPreset):
    PRESETS = COLOR
    KIND = "color"
    DESCRIPTION = "Dropdown of color grades. Outputs a photography sentence and a picture of that grade."


NODE_CLASS_MAPPINGS = {
    "CGILightingSetup": CGILightingSetup,
    "CGICameraLens": CGICameraLens,
    "CGIColorAesthetic": CGIColorAesthetic,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CGILightingSetup": "Lighting Setup",
    "CGICameraLens": "Camera & Lens Specifications",
    "CGIColorAesthetic": "Color Palette & Aesthetic Style",
}
