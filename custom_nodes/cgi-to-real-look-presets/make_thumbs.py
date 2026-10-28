"""Render a thumbnail for every look preset.

The scene is a clay mannequin in a plain room. Camera choices move the camera.
Lighting choices move the lights. Color choices grade one neutral frame.
"""

import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from presets import CAMERA, COLOR, LIGHTING

ROOT = Path(__file__).resolve().parent / "web" / "thumbs"
W, H = 288, 192


def slug(label):
    chars = []
    for ch in label.lower():
        chars.append(ch if ch.isalnum() else "-")
    text = "".join(chars)
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "none"


def norm(v, axis=-1):
    return v / np.maximum(np.linalg.norm(v, axis=axis, keepdims=True), 1e-8)


def sdf_parts(p, two=False, cup=False, shoulder=False):
    floor = p[..., 1]
    back = p[..., 2] + 1.35
    left = p[..., 0] + 2.15
    right = -p[..., 0] + 2.15
    head = np.linalg.norm(p - np.array([0.0, 1.66, 0.36]), axis=-1) - 0.22
    neck_a = np.array([0.0, 1.38, 0.34])
    neck_b = np.array([0.0, 1.52, 0.35])
    neck_ba = neck_b - neck_a
    neck_pa = p - neck_a
    neck_h = np.clip(np.sum(neck_pa * neck_ba, axis=-1) / float(np.dot(neck_ba, neck_ba)), 0.0, 1.0)
    neck = np.linalg.norm(neck_pa - neck_ba * neck_h[..., None], axis=-1) - 0.07
    ba = np.array([0.0, 0.62, 0.0])
    pa = p - np.array([0.0, 0.72, 0.32])
    h = np.clip(np.sum(pa * ba, axis=-1) / float(np.dot(ba, ba)), 0.0, 1.0)
    body = np.linalg.norm(pa - ba * h[..., None], axis=-1) - 0.26
    fig = np.minimum(np.minimum(head, neck), body)
    for side in (-1.0, 1.0):
        arm_a = np.array([side * 0.24, 1.22, 0.34])
        arm_b = np.array([side * 0.38, 0.78, 0.42])
        arm_ba = arm_b - arm_a
        arm_pa = p - arm_a
        arm_h = np.clip(np.sum(arm_pa * arm_ba, axis=-1) / float(np.dot(arm_ba, arm_ba)), 0.0, 1.0)
        fig = np.minimum(fig, np.linalg.norm(arm_pa - arm_ba * arm_h[..., None], axis=-1) - 0.055)
    for side in (-0.1, 0.1):
        a = np.array([side, 0.02, 0.30])
        b = np.array([side * 0.85, 0.62, 0.32])
        ba = b - a
        pa = p - a
        h = np.clip(np.sum(pa * ba, axis=-1) / float(np.dot(ba, ba)), 0.0, 1.0)
        fig = np.minimum(fig, np.linalg.norm(pa - ba * h[..., None], axis=-1) - 0.075)
    if two:
        head2 = np.linalg.norm(p - np.array([0.62, 1.52, 0.55]), axis=-1) - 0.18
        a = np.array([0.62, 0.55, 0.5])
        b = np.array([0.62, 1.35, 0.52])
        ba = b - a
        pa = p - a
        h = np.clip(np.sum(pa * ba, axis=-1) / float(np.dot(ba, ba)), 0.0, 1.0)
        fig = np.minimum(fig, np.minimum(head2, np.linalg.norm(pa - ba * h[..., None], axis=-1) - 0.2))
    if cup:
        fig = np.minimum(fig, np.linalg.norm(p - np.array([0.42, 0.72, 0.85]), axis=-1) - 0.09)
    if shoulder:
        fig = np.minimum(fig, np.linalg.norm(p - np.array([0.38, 1.25, 1.85]), axis=-1) - 0.34)
    dists = np.stack([floor, back, left, right, fig], axis=-1)
    return dists.min(axis=-1), dists.argmin(axis=-1)


def march(ro, rd, flags):
    t = np.full(rd.shape[:2], 0.02, np.float32)
    hit = np.zeros(rd.shape[:2], np.bool_)
    alive = np.ones(rd.shape[:2], np.bool_)
    for _ in range(36):
        if not alive.any():
            break
        p = ro + rd * t[..., None]
        dist, _ = sdf_parts(p, flags["two"], flags["cup"], flags["shoulder"])
        near = alive & (dist < 0.006)
        lost = alive & (t > 16.0)
        hit |= near
        alive &= ~(near | lost)
        t = np.where(alive, t + np.maximum(dist, 0.0), t)
    return t, hit


def shade(ro, rd, t, hit, light):
    p = ro + rd * t[..., None]
    eps = 0.012
    axes = np.eye(3, dtype=np.float32) * eps
    grads = []
    for i in range(3):
        dp, _ = sdf_parts(p + axes[i], light["two"], light["cup"], light["shoulder"])
        dm, _ = sdf_parts(p - axes[i], light["two"], light["cup"], light["shoulder"])
        grads.append(dp - dm)
    n = norm(np.stack(grads, axis=-1))
    _, mat = sdf_parts(p, light["two"], light["cup"], light["shoulder"])
    albedo = np.zeros(p.shape, np.float32)
    albedo[mat == 0] = (0.45, 0.44, 0.42)
    albedo[mat == 1] = (0.62, 0.60, 0.57)
    albedo[mat == 2] = (0.55, 0.56, 0.58)
    albedo[mat == 3] = (0.58, 0.55, 0.52)
    albedo[mat == 4] = (0.72, 0.56, 0.46)
    # Floor checkers so wide lenses show the ground stretching away.
    checker = ((np.floor(p[..., 0] * 2.0) + np.floor(p[..., 2] * 2.0)) % 2) == 0
    albedo[mat == 0] = np.where(checker[..., None], 0.52, 0.34)[mat == 0]
    key = norm(np.asarray(light["key_dir"], np.float32))
    fill = norm(np.asarray(light["fill_dir"], np.float32))
    ndk = np.sum(n * key, axis=-1)
    wrap = np.clip((ndk + light["wrap"]) / (1.0 + light["wrap"]), 0.0, 1.0)
    if light.get("dapple"):
        dap = 0.55 + 0.45 * np.sin(p[..., 0] * 9.0) * np.sin(p[..., 2] * 7.0)
        wrap *= np.clip(dap, 0.15, 1.0)
    if light.get("spot"):
        axis = norm(np.array([0.15, -1.0, 0.35], np.float32))
        spot_from = np.array([0.0, 3.4, 1.6], np.float32)
        to_pt = norm(p - spot_from)
        cone = np.clip((np.sum(to_pt * axis, axis=-1) - 0.82) / 0.12, 0.0, 1.0)
        wrap *= cone
    fill_l = np.clip(np.sum(n * fill, axis=-1), 0.0, 1.0)
    view = norm(-rd)
    half = norm(key + view)
    spec = np.clip(np.sum(n * half, axis=-1), 0.0, 1.0) ** light["gloss"]
    rim = np.clip(np.sum(n * norm(np.asarray(light["rim_dir"], np.float32)), axis=-1), 0.0, 1.0) ** 2
    key_c = np.asarray(light["key_color"], np.float32)
    fill_c = np.asarray(light["fill_color"], np.float32)
    rgb = albedo * (
        light["ambient"]
        + wrap[..., None] * key_c * light["key"]
        + fill_l[..., None] * fill_c * light["fill"]
    )
    rgb += spec[..., None] * key_c * light["spec"]
    rgb += rim[..., None] * np.asarray(light["rim_color"], np.float32) * light["rim"]
    # Left-wall window, so practical daylight has a visible source.
    on_left = mat == 2
    in_window = on_left & (p[..., 1] > 1.15) & (p[..., 1] < 2.35) & (p[..., 2] > -0.55) & (p[..., 2] < 0.85)
    rgb[in_window] = light["window"]
    sky = np.asarray(light["sky_horizon"], np.float32) * (1.0 - np.clip(rd[..., 1], 0, 1))[..., None]
    sky = sky + np.asarray(light["sky_zenith"], np.float32) * np.clip(rd[..., 1], 0, 1)[..., None]
    rgb = np.where(hit[..., None], rgb, sky)
    return np.clip(rgb, 0.0, 8.0), t


def rays(cam):
    pos = np.asarray(cam["pos"], np.float32)
    target = np.asarray(cam["target"], np.float32)
    forward = norm(target - pos)
    right = norm(np.cross(forward, np.array([0.0, 1.0, 0.0], np.float32)))
    up = np.cross(right, forward)
    roll = np.deg2rad(cam.get("roll", 0.0))
    cr, sr = np.cos(roll), np.sin(roll)
    right, up = right * cr + up * sr, up * cr - right * sr
    ys, xs = np.mgrid[0:H, 0:W]
    u = ((xs + 0.5) / W * 2.0 - 1.0).astype(np.float32)
    v = (1.0 - (ys + 0.5) / H * 2.0).astype(np.float32)
    if cam.get("fisheye"):
        r = np.sqrt(u * u + v * v)
        scale = np.where(r > 1e-4, np.sin(r * 1.15) / r, 1.0)
        u, v = u * scale, v * scale
    fov = np.deg2rad(cam["fov"])
    aspect = W / H
    stretch = 1.55 if cam.get("anamorphic") else 1.0
    u = u * aspect * np.tan(fov * 0.5) * stretch
    v = v * np.tan(fov * 0.5)
    rd = norm(forward + right * u[..., None] + up * v[..., None])
    return pos, rd


def apply_dof(rgb, depth, cam):
    aperture = cam.get("fstop", 8.0)
    if aperture >= 8.0:
        return rgb
    focus = cam.get("focus", float(np.linalg.norm(np.asarray(cam["target"]) - np.asarray(cam["pos"]))))
    coc = np.clip(np.abs(depth - focus) / (aperture * 1.6), 0.0, 1.0)
    if cam.get("tilt"):
        band = np.exp(-((np.linspace(-1, 1, H)[:, None]) ** 2) / 0.08)
        coc = np.maximum(coc, 1.0 - band)
    sharp = Image.fromarray(np.clip(rgb * 255.0, 0, 255).astype(np.uint8))
    radius = 1.2 + (6.0 / max(aperture, 0.7))
    blurred = np.asarray(sharp.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0
    return rgb * (1.0 - coc[..., None]) + blurred * coc[..., None]


def grade(rgb, name):
    x = np.clip(rgb, 0.0, 1.0)
    lum = x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722
    if name in ("(none)", "Natural documentary", "Daylight neutral", "Clinical clean"):
        out = x
    elif name == "Teal and orange":
        out = x.copy()
        out[..., 0] = x[..., 0] * 1.15 + (1.0 - lum) * 0.02
        out[..., 1] = x[..., 1] * 0.95
        out[..., 2] = x[..., 2] * 0.75 + (1.0 - lum) * 0.18
        out += (lum[..., None] ** 1.4) * np.array([0.12, 0.04, -0.02])
    elif name == "Kodak Portra warmth":
        out = x * np.array([1.08, 1.0, 0.9]) + 0.03
        out = out * 0.92 + 0.04
    elif name == "Fuji cool greens":
        out = x * np.array([0.9, 1.05, 1.02])
        out[..., 1] += (1.0 - lum) * 0.06
    elif name == "Bleach bypass":
        out = lum[..., None] * 0.65 + x * 0.45
        out = (out - 0.5) * 1.35 + 0.5
    elif name == "Desaturated":
        out = lum[..., None] * 0.72 + x * 0.28
    elif name == "High-contrast film":
        out = (x - 0.5) * 1.45 + 0.5
        out *= np.array([1.05, 0.98, 0.94])
    elif name == "Soft pastel":
        out = x * 0.72 + 0.22
    elif name == "Muted earth":
        out = x * np.array([0.85, 0.78, 0.62]) * 0.85 + np.array([0.08, 0.06, 0.03])
    elif name == "Black and white":
        out = np.repeat(lum[..., None], 3, axis=-1)
    elif name == "Sepia":
        out = lum[..., None] * np.array([1.15, 0.9, 0.62])
    elif name == "Cyberpunk neon":
        out = np.clip((x - 0.45) * 1.5 + 0.45, 0, 1)
        out = out * np.array([1.2, 0.75, 1.25])
        out[..., 2] += (1.0 - lum) * 0.25
        out[..., 0] += lum * 0.15
    elif name == "Golden luxury":
        out = x * np.array([1.2, 0.95, 0.7]) + np.array([0.04, 0.02, 0.0])
    elif name == "1970s vintage":
        out = (x * np.array([1.1, 0.98, 0.8]) + 0.04) * 0.9
        out[..., 1] += (1.0 - lum) * 0.04
    elif name == "Moody noir":
        lifted = np.clip((x - 0.08) * 1.15, 0, 1)
        out = (lum[..., None] * 0.82 + lifted * 0.18) * np.array([0.85, 0.9, 1.0])
        out = out ** 1.2
    elif name == "Sun-faded summer":
        out = np.clip(x * np.array([1.1, 1.02, 0.9]) + 0.08, 0, 1)
        out = out * 0.85 + 0.12
    elif name == "Forest green":
        out = x * np.array([0.8, 1.0, 0.78])
        out[..., 1] += (1.0 - lum) * 0.08
    elif name == "Arctic blue":
        out = x * np.array([0.82, 0.92, 1.12]) + np.array([0.0, 0.01, 0.03])
    elif name == "Rose gold":
        out = x * np.array([1.15, 0.92, 0.9]) + np.array([0.04, 0.02, 0.02])
    elif name == "Cross-processed":
        out = x.copy()
        out[..., 0] = x[..., 2] * 0.3 + x[..., 0] * 0.9
        out[..., 1] = x[..., 1] * 1.05 + lum * 0.08
        out[..., 2] = x[..., 0] * 0.25 + x[..., 2] * 1.1 + (1 - lum) * 0.15
    elif name == "Technicolor":
        out = (x - 0.5) * 1.4 + 0.5
        out *= np.array([1.15, 1.05, 1.1])
    elif name == "Matte cinema":
        out = x * 0.82 + 0.08
    elif name == "Warm tungsten interior":
        out = x * np.array([1.18, 0.95, 0.72])
    elif name == "Autumn amber":
        out = x * np.array([1.2, 0.85, 0.55]) + np.array([0.03, 0.01, 0.0])
    elif name == "Midnight blue":
        out = x * np.array([0.55, 0.65, 0.95]) * 0.85
        out[..., 0] += lum * 0.08
    elif name == "Dusty western":
        out = (x * np.array([1.05, 0.92, 0.75]) + 0.05) * 0.9
    elif name == "Editorial fashion":
        out = (x - 0.5) * 1.12 + 0.48
        out *= np.array([1.02, 0.98, 1.04])
    elif name == "Painterly":
        small = Image.fromarray(np.clip(x * 255, 0, 255).astype(np.uint8)).resize((72, 48), Image.Resampling.BILINEAR)
        soft = np.asarray(small.resize((W, H), Image.Resampling.BILINEAR), np.float32) / 255.0
        out = soft * 0.65 + x * 0.35
    elif name == "HDR crisp":
        blur = np.asarray(
            Image.fromarray(np.clip(x * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)),
            np.float32,
        ) / 255.0
        out = np.clip(x + (x - blur) * 0.9, 0, 1)
    else:
        out = x
    return np.clip(out, 0.0, 1.0)


def finish(rgb, vignette=0.35):
    rgb = np.clip(rgb, 0.0, 1.0) ** (1.0 / 2.2)
    ys, xs = np.mgrid[0:H, 0:W]
    u = (xs / W * 2 - 1) * (W / H)
    v = ys / H * 2 - 1
    vig = 1.0 - vignette * np.clip(u * u + v * v, 0, 1)
    return np.clip(rgb * vig[..., None], 0.0, 1.0)


def save(rgb, folder, label):
    path = ROOT / folder
    path.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(np.clip(rgb * 255.0, 0, 255).astype(np.uint8), "RGB")
    img = img.resize((576, 384), Image.Resampling.LANCZOS)
    img.save(path / f"{slug(label)}.png", optimize=True)


def base_light(**over):
    light = dict(
        key_dir=(-0.45, 0.55, 0.65),
        fill_dir=(0.4, 0.2, 0.7),
        rim_dir=(-0.2, 0.4, -0.8),
        key_color=(1.0, 0.97, 0.93),
        fill_color=(0.85, 0.9, 1.0),
        rim_color=(1.0, 0.95, 0.9),
        key=0.85,
        fill=0.28,
        rim=0.12,
        ambient=0.18,
        wrap=0.45,
        gloss=40.0,
        spec=0.18,
        window=(1.6, 1.7, 1.75),
        sky_horizon=(0.72, 0.76, 0.8),
        sky_zenith=(0.45, 0.55, 0.7),
        two=False,
        cup=False,
        shoulder=False,
        dapple=False,
        spot=False,
    )
    light.update(over)
    return light


def base_cam(**over):
    cam = dict(pos=(0.0, 1.25, 3.15), target=(0.0, 1.15, 0.3), fov=42, roll=0, fstop=8, fisheye=False, tilt=False, anamorphic=False)
    cam.update(over)
    focus = float(np.linalg.norm(np.asarray(cam["target"]) - np.asarray(cam["pos"])))
    cam.setdefault("focus", focus)
    return cam


CAMERA_RIG = {
    "Full view": base_cam(),
    "Extreme close-up, 100mm": base_cam(pos=(0.05, 1.6, 0.95), target=(0.0, 1.6, 0.35), fov=14, fstop=2.8),
    "Beauty close-up, 100mm f/2": base_cam(pos=(0.0, 1.58, 1.15), target=(0.0, 1.58, 0.35), fov=16, fstop=2.0),
    "Close-up, 85mm f/1.4": base_cam(pos=(0.08, 1.55, 1.35), target=(0.0, 1.56, 0.35), fov=18, fstop=1.4),
    "Head and shoulders, 85mm f/1.8": base_cam(pos=(0.1, 1.48, 1.7), target=(0.0, 1.45, 0.35), fov=20, fstop=1.8),
    "Medium close-up, 50mm f/1.8": base_cam(pos=(0.05, 1.4, 2.15), target=(0.0, 1.35, 0.32), fov=27, fstop=1.8),
    "Medium shot, 50mm f/2.8": base_cam(pos=(0.0, 1.3, 2.55), target=(0.0, 1.2, 0.32), fov=32, fstop=2.8),
    "Cowboy shot, 35mm": base_cam(pos=(0.15, 1.15, 2.7), target=(0.0, 1.0, 0.32), fov=40, fstop=4),
    "Full body, 35mm f/4": base_cam(pos=(0.0, 1.15, 3.35), target=(0.0, 0.95, 0.3), fov=46, fstop=4),
    "Wide environmental, 24mm f/8": base_cam(pos=(0.2, 1.35, 3.6), target=(0.0, 1.1, 0.2), fov=68, fstop=8),
    "Ultra wide, 16mm": base_cam(pos=(0.15, 1.2, 2.4), target=(0.0, 1.15, 0.3), fov=92, fstop=8),
    "Establishing wide, 18mm": base_cam(pos=(-0.4, 1.6, 4.3), target=(0.2, 1.0, 0.0), fov=84, fstop=8),
    "Low angle, 24mm": base_cam(pos=(0.25, 0.38, 2.5), target=(0.0, 1.45, 0.3), fov=62, fstop=4),
    "High angle, 35mm": base_cam(pos=(0.35, 2.55, 2.35), target=(0.0, 0.7, 0.3), fov=48, fstop=4),
    "Overhead, 35mm": base_cam(pos=(0.05, 3.6, 0.45), target=(0.0, 0.4, 0.35), fov=42, fstop=5.6),
    "Worm's-eye, 20mm": base_cam(pos=(0.15, 0.08, 1.9), target=(0.0, 1.5, 0.25), fov=78, fstop=4),
    "Dutch angle, 35mm": base_cam(pos=(0.2, 1.3, 2.6), target=(0.0, 1.25, 0.3), fov=46, roll=16, fstop=2.8),
    "Over the shoulder, 50mm": base_cam(pos=(0.15, 1.42, 2.05), target=(-0.05, 1.5, 0.35), fov=34, fstop=2.2, shoulder=True),
    "Point of view, 24mm": base_cam(pos=(0.0, 1.58, 0.15), target=(0.0, 1.35, -1.2), fov=70, fstop=5.6),
    "Profile, 85mm f/2": base_cam(pos=(2.4, 1.5, 0.55), target=(0.0, 1.52, 0.35), fov=18, fstop=2.0),
    "Three-quarter view, 50mm": base_cam(pos=(1.15, 1.4, 2.15), target=(0.0, 1.4, 0.35), fov=30, fstop=2.8),
    "Two-shot, 35mm": base_cam(pos=(0.35, 1.3, 3.1), target=(0.3, 1.2, 0.4), fov=48, fstop=4, two=True),
    "Anamorphic widescreen, 40mm": base_cam(pos=(0.0, 1.25, 3.0), target=(0.0, 1.2, 0.3), fov=36, fstop=2.8, anamorphic=True),
    "Telephoto compression, 135mm f/2": base_cam(pos=(0.05, 1.5, 6.4), target=(0.0, 1.5, 0.35), fov=9, fstop=2.0),
    "Tilt-shift": base_cam(pos=(0.0, 1.7, 3.4), target=(0.0, 0.8, 0.2), fov=40, fstop=1.4, tilt=True),
    "Shallow depth of field, 85mm f/1.2": base_cam(pos=(0.0, 1.45, 1.9), target=(0.0, 1.42, 0.35), fov=22, fstop=1.2),
    "Deep focus, 35mm f/11": base_cam(pos=(0.1, 1.3, 3.2), target=(0.0, 1.15, 0.2), fov=48, fstop=11),
    "Handheld documentary, 28mm": base_cam(pos=(0.22, 1.32, 2.15), target=(-0.05, 1.25, 0.3), fov=60, roll=-4, fstop=2.8),
    "Locked-off tripod, 50mm": base_cam(pos=(0.0, 1.35, 2.7), target=(0.0, 1.25, 0.32), fov=30, fstop=5.6),
    "Aerial, 24mm": base_cam(pos=(1.6, 6.5, 5.2), target=(0.0, 0.2, 0.2), fov=52, fstop=5.6),
    "Fisheye, 8mm": base_cam(pos=(0.1, 1.25, 2.2), target=(0.0, 1.15, 0.3), fov=90, fstop=8, fisheye=True),
    "Medium format, 80mm f/2.8": base_cam(pos=(0.0, 1.42, 2.05), target=(0.0, 1.35, 0.35), fov=22, fstop=2.8),
    "Vintage lens, 58mm f/2": base_cam(pos=(0.12, 1.38, 2.2), target=(0.0, 1.32, 0.32), fov=28, fstop=2.0),
    "Side tracking, 35mm": base_cam(pos=(2.3, 1.2, 1.7), target=(0.0, 1.15, 0.35), fov=44, fstop=2.8),
    "Insert detail, 90mm macro": base_cam(pos=(0.55, 0.78, 1.35), target=(0.42, 0.72, 0.85), fov=16, fstop=2.8, cup=True),
    "Long-lens silhouette, 200mm": base_cam(pos=(0.0, 1.55, 7.5), target=(0.0, 1.5, 0.35), fov=6.5, fstop=4),
}

LIGHT_RIG = {
    "(none)": base_light(),
    "Soft window light": base_light(key_dir=(-1.0, 0.35, 0.25), key=0.7, fill=0.4, wrap=0.9, spec=0.05, ambient=0.22),
    "Golden hour": base_light(key_dir=(0.9, 0.15, -0.3), key_color=(1.0, 0.62, 0.28), key=1.3, fill=0.12, rim=0.45, rim_color=(1.0, 0.7, 0.35), ambient=0.08, wrap=0.15, sky_horizon=(0.95, 0.55, 0.3), sky_zenith=(0.35, 0.4, 0.65), window=(1.8, 1.1, 0.55)),
    "Blue hour": base_light(key_dir=(-0.2, 0.8, 0.2), key_color=(0.55, 0.7, 1.0), key=0.45, fill_dir=(0.8, 0.1, 0.4), fill_color=(1.0, 0.7, 0.4), fill=0.18, ambient=0.16, sky_horizon=(0.4, 0.5, 0.75), sky_zenith=(0.15, 0.2, 0.4), window=(0.7, 0.85, 1.3)),
    "Overcast sky": base_light(key_dir=(0.1, 1.0, 0.2), key=0.55, fill=0.45, wrap=1.1, spec=0.02, ambient=0.28, sky_horizon=(0.7, 0.72, 0.74), sky_zenith=(0.55, 0.58, 0.62)),
    "Hard noon sun": base_light(key_dir=(0.05, 1.0, 0.05), key=1.6, fill=0.08, wrap=0.02, spec=0.35, ambient=0.06, gloss=80),
    "Rembrandt": base_light(key_dir=(-0.85, 0.55, 0.45), key=1.25, fill=0.08, wrap=0.05, ambient=0.05, spec=0.2),
    "Butterfly lighting": base_light(key_dir=(0.0, 0.85, 0.55), key=1.15, fill=0.22, wrap=0.25, ambient=0.1),
    "Split lighting": base_light(key_dir=(-1.0, 0.05, 0.05), key=1.3, fill=0.02, wrap=0.0, ambient=0.03, spec=0.15),
    "Loop lighting": base_light(key_dir=(-0.55, 0.5, 0.7), key=1.1, fill=0.16, wrap=0.12, ambient=0.08),
    "Rim light": base_light(key_dir=(0.2, 0.45, -1.0), key=1.5, fill_dir=(0.0, 0.2, 1.0), fill=0.22, rim=0.8, rim_dir=(0.1, 0.3, -1.0), ambient=0.04),
    "Three-point studio": base_light(key=1.0, fill=0.4, rim=0.55, wrap=0.3, ambient=0.1),
    "Warm practical lamps": base_light(key_dir=(0.8, -0.15, 0.4), key_color=(1.0, 0.62, 0.3), key=1.1, fill=0.05, ambient=0.04, wrap=0.2, sky_horizon=(0.25, 0.18, 0.14), sky_zenith=(0.08, 0.07, 0.08), window=(1.4, 0.7, 0.3)),
    "Neon practicals": base_light(key_dir=(-1.0, 0.1, 0.3), key_color=(0.2, 0.85, 1.0), fill_dir=(1.0, 0.0, 0.2), fill_color=(1.0, 0.15, 0.7), fill=0.7, key=0.9, ambient=0.03, sky_horizon=(0.15, 0.05, 0.2), sky_zenith=(0.02, 0.02, 0.05), window=(0.3, 0.9, 1.2)),
    "Candlelight": base_light(key_dir=(0.4, -0.7, 0.5), key_color=(1.0, 0.5, 0.15), key=1.2, fill=0.02, ambient=0.02, wrap=0.35, sky_horizon=(0.08, 0.04, 0.02), sky_zenith=(0.01, 0.01, 0.01), window=(0.4, 0.2, 0.08)),
    "Moonlight": base_light(key_dir=(-0.4, 0.8, -0.3), key_color=(0.65, 0.75, 1.0), key=0.7, fill=0.04, ambient=0.03, sky_horizon=(0.15, 0.18, 0.28), sky_zenith=(0.04, 0.05, 0.12), window=(0.5, 0.6, 0.9)),
    "Cool rain": base_light(key_dir=(0.1, 0.6, 0.4), key_color=(0.75, 0.82, 0.9), key=0.4, fill=0.35, wrap=1.0, ambient=0.2, spec=0.04, sky_horizon=(0.55, 0.58, 0.62), sky_zenith=(0.4, 0.45, 0.5)),
    "God rays": base_light(key_dir=(-0.8, 0.7, -0.2), key_color=(1.0, 0.9, 0.7), key=1.8, fill=0.05, ambient=0.04, wrap=0.05, window=(2.4, 2.2, 1.8), sky_horizon=(0.8, 0.75, 0.6), sky_zenith=(0.4, 0.5, 0.7)),
    "High-key": base_light(key=0.7, fill=0.7, ambient=0.45, wrap=1.0, spec=0.08, sky_horizon=(0.9, 0.92, 0.94), sky_zenith=(0.8, 0.85, 0.9), window=(2.0, 2.0, 2.0)),
    "Low-key chiaroscuro": base_light(key_dir=(-0.7, 0.4, 0.4), key=1.5, fill=0.0, ambient=0.015, wrap=0.0, spec=0.25, sky_horizon=(0.02, 0.02, 0.025), sky_zenith=(0.0, 0.0, 0.0), window=(0.15, 0.15, 0.16)),
    "Fluorescent office": base_light(key_dir=(0.0, 1.0, 0.1), key_color=(0.75, 1.0, 0.85), key=0.8, fill=0.35, wrap=0.8, ambient=0.2, spec=0.05, sky_horizon=(0.6, 0.7, 0.65), window=(0.8, 1.1, 0.9)),
    "Golden rim, cool fill": base_light(key_dir=(0.2, 0.3, 0.9), key_color=(0.75, 0.85, 1.0), key=0.55, rim_dir=(0.5, 0.2, -1.0), rim_color=(1.0, 0.65, 0.25), rim=1.1, fill=0.15, ambient=0.06),
    "On-camera flash": base_light(key_dir=(0.0, 0.05, 1.0), key=1.7, fill=0.0, wrap=0.0, spec=0.55, gloss=90, ambient=0.03, sky_horizon=(0.05, 0.05, 0.06), sky_zenith=(0.01, 0.01, 0.02)),
    "Beauty dish": base_light(key_dir=(0.05, 0.45, 0.9), key=1.15, fill=0.2, wrap=0.22, spec=0.28, ambient=0.08),
    "Ring light": base_light(key_dir=(0.0, 0.0, 1.0), key=0.9, fill=0.55, wrap=0.8, spec=0.4, gloss=120, ambient=0.12),
    "Sunset backlight": base_light(key_dir=(0.3, 0.25, -1.0), key_color=(1.0, 0.55, 0.2), key=1.6, fill=0.12, rim=0.9, rim_color=(1.0, 0.6, 0.25), ambient=0.05, sky_horizon=(1.0, 0.5, 0.25), sky_zenith=(0.3, 0.35, 0.6), window=(2.0, 1.0, 0.4)),
    "Firelight": base_light(key_dir=(0.9, -0.45, 0.2), key_color=(1.0, 0.42, 0.1), key=1.25, fill=0.03, ambient=0.025, wrap=0.25, sky_horizon=(0.12, 0.04, 0.02), sky_zenith=(0.02, 0.01, 0.01)),
    "Forest canopy": base_light(key_dir=(0.2, 1.0, 0.1), key_color=(0.7, 0.9, 0.55), key=0.9, fill=0.2, wrap=0.4, ambient=0.08, dapple=True, sky_horizon=(0.35, 0.45, 0.3), sky_zenith=(0.15, 0.25, 0.18)),
    "Stage spotlight": base_light(key_dir=(0.1, -0.2, 0.7), key=1.6, fill=0.0, ambient=0.012, wrap=0.02, spot=True, sky_horizon=(0.01, 0.01, 0.015), sky_zenith=(0.0, 0.0, 0.0), window=(0.05, 0.05, 0.06)),
    "Open shade": base_light(key_dir=(-0.2, 0.8, 0.3), key_color=(0.8, 0.88, 1.0), key=0.45, fill=0.4, wrap=1.0, ambient=0.25, spec=0.03),
    "Mixed color gels": base_light(key_dir=(0.1, 0.4, 0.9), key_color=(1.0, 0.98, 0.95), key=0.9, fill_dir=(-1.0, 0.1, 0.2), fill_color=(0.3, 0.45, 1.0), fill=0.55, rim_dir=(1.0, 0.1, -0.3), rim_color=(1.0, 0.45, 0.15), rim=0.7, ambient=0.05),
    "Dawn fog": base_light(key_dir=(-0.3, 0.25, 0.8), key_color=(1.0, 0.78, 0.6), key=0.55, fill=0.45, wrap=1.2, ambient=0.32, spec=0.02, sky_horizon=(0.85, 0.7, 0.6), sky_zenith=(0.65, 0.7, 0.78), window=(1.5, 1.3, 1.15)),
}


def flags_from(cam, light):
    return dict(
        two=bool(cam.get("two") or light.get("two")),
        cup=bool(cam.get("cup") or light.get("cup")),
        shoulder=bool(cam.get("shoulder") or light.get("shoulder")),
    )


def render_pair(cam, light):
    flags = flags_from(cam, light)
    light = dict(light)
    light.update(flags)
    cam = dict(cam)
    ro, rd = rays(cam)
    t, hit = march(ro, rd, flags)
    rgb, depth = shade(ro, rd, t, hit, light)
    rgb = apply_dof(rgb, depth, cam)
    if cam.get("anamorphic"):
        streak = Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=6))
        streak = streak.resize((W, max(1, H // 8)), Image.Resampling.BILINEAR).resize((W, H), Image.Resampling.BILINEAR)
        rgb = np.clip(rgb + np.asarray(streak, np.float32) / 255.0 * 0.18, 0, 8)
    return rgb


def main():
    missing_cam = [k for k in CAMERA if k not in CAMERA_RIG]
    missing_light = [k for k in LIGHTING if k not in LIGHT_RIG]
    if missing_cam or missing_light:
        raise SystemExit(f"missing rigs cam={missing_cam} light={missing_light}")
    neutral_cam = CAMERA_RIG["Full view"]
    neutral_light = LIGHT_RIG["(none)"]
    print("rendering cameras", flush=True)
    for i, label in enumerate(CAMERA, 1):
        rgb = render_pair(CAMERA_RIG[label], neutral_light)
        if label == "Vintage lens, 58mm f/2":
            glow = Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
            rgb = np.clip(rgb * 0.8 + np.asarray(glow, np.float32) / 255.0 * 0.35, 0, 8)
        if label == "Long-lens silhouette, 200mm":
            rgb = render_pair(
                CAMERA_RIG[label],
                base_light(key_dir=(0.0, 0.2, -1.0), key=2.0, key_color=(1.0, 0.85, 0.7), fill=0.0, ambient=0.01, sky_horizon=(0.9, 0.75, 0.6), sky_zenith=(0.4, 0.5, 0.7)),
            )
        save(finish(grade(rgb, "Natural documentary"), 0.28), "camera", label)
        print(f"  camera {i}/{len(CAMERA)} {label}", flush=True)
    print("rendering lights", flush=True)
    for i, label in enumerate(LIGHTING, 1):
        rgb = render_pair(neutral_cam, LIGHT_RIG[label])
        save(finish(grade(rgb, "Natural documentary"), 0.28), "lighting", label)
        print(f"  light {i}/{len(LIGHTING)} {label}", flush=True)
    print("rendering grades", flush=True)
    base = render_pair(neutral_cam, neutral_light)
    for i, label in enumerate(COLOR, 1):
        save(finish(grade(base, label), 0.22), "color", label)
        print(f"  color {i}/{len(COLOR)} {label}", flush=True)
    print("done", ROOT)


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    main()
