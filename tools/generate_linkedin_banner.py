#!/usr/bin/env python3
"""Render the LinkedIn profile banner (1584x396 PNG) in the README's style.

Layout rules the composition follows:
- 1584x396 px. On desktop the profile photo covers about 568x264 px of the
  lower-left corner, so that area only carries faint decoration.
- Mobile shows roughly the central 60% of the width (x = 317..1267): the value
  proposition and the call to action live there. The right column is decoration.
- LinkedIn prints the name right below the banner, so the banner spends its
  space on one outcome statement readable in two seconds, not on the name.

Usage:
    pip install pillow
    python3 tools/build_linkedin_banner.py

On the first run it downloads JetBrains Mono into .fonts/. If the download
fails it falls back to a monospace font already installed on the system.
Output: assets/linkedin-banner.png
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "linkedin-banner.png"
FONT_CACHE = ROOT / ".fonts"

W, H = 1584, 396
S = 2  # supersampling: draw at 2x and downscale for smooth edges

# Palette
BG = "#0b0f14"
PANEL = "#111820"
GREEN = "#39ff14"
CYAN = "#00e5ff"
WHITE = "#e6edf3"
TEXT = "#c9d1d9"
DIM = "#6e7681"
CARD = "#0d1117"

# Copy
HEADLINE = ("SECURE BY", "DESIGN.")
SUB = ("Backend, DevOps and cloud engineering", "with security built in from the first commit.")
CTA = "github.com/maldoA10"
LOGS = ["[ ok ] jwt.verify(token)", "[ ok ] otp.challenge(user)", "[ ok ] npm audit --omit=dev"]
PIPELINE = ["build", "test", "audit", "deploy"]  # the last stage is highlighted

# Fonts
FONT_URLS = {
    "bold": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Bold.ttf",
    "regular": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf",
}
FALLBACKS = {  # (path, collection index)
    "bold": [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 0),
        ("/System/Library/Fonts/Menlo.ttc", 1),
        ("C:/Windows/Fonts/consolab.ttf", 0),
    ],
    "regular": [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0),
        ("/System/Library/Fonts/Menlo.ttc", 0),
        ("C:/Windows/Fonts/consola.ttf", 0),
    ],
}
_font_paths: dict[str, tuple[Path, int]] = {}


def resolve_fonts() -> None:
    FONT_CACHE.mkdir(exist_ok=True)
    for key, url in FONT_URLS.items():
        target = FONT_CACHE / url.rsplit("/", 1)[1]
        if not target.exists():
            try:
                urllib.request.urlretrieve(url, target)
            except Exception:
                target.unlink(missing_ok=True)
        candidates = [(target, 0)] if target.exists() else []
        candidates += [(Path(p), i) for p, i in FALLBACKS[key] if Path(p).exists()]
        for path, index in candidates:
            try:
                ImageFont.truetype(str(path), 20, index=index)
            except OSError:
                continue
            _font_paths[key] = (path, index)
            break
        else:
            raise SystemExit(f"No usable {key} monospace font found. Put a .ttf in {FONT_CACHE}")


def font(key: str, size: float) -> ImageFont.FreeTypeFont:
    path, index = _font_paths[key]
    return ImageFont.truetype(str(path), round(size * S), index=index)


def sc(v: float) -> int:
    return round(v * S)


# Drawing helpers (all coordinates are in banner pixels)
def text(d: ImageDraw.ImageDraw, x: float, y: float, s: str, f, fill) -> float:
    """Draw text with its baseline at y. Returns the x where it ends."""
    d.text((sc(x), sc(y)), s, font=f, fill=fill, anchor="ls")
    return x + f.getlength(s) / S


def glow(img: Image.Image, painter, radius: float, passes: int = 2) -> None:
    """painter(draw, glow_only): blur a copy of the shape under the crisp one."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer), True)
    blurred = layer.filter(ImageFilter.GaussianBlur(sc(radius)))
    for _ in range(passes):
        img.alpha_composite(blurred)
    painter(ImageDraw.Draw(img), False)


def blob(img: Image.Image, cx: int, cy: int, radius: int, color: str, strength: float) -> None:
    """Soft radial light, used for the background ambience."""
    r = sc(radius)
    mask = ImageOps.invert(Image.radial_gradient("L").resize((2 * r, 2 * r)))
    mask = mask.point(lambda v: int(v * v / 255 * strength))
    solid = Image.new("RGBA", (2 * r, 2 * r), color)
    solid.putalpha(mask)
    img.alpha_composite(solid, (sc(cx) - r, sc(cy) - r))


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


# Scene
def background() -> Image.Image:
    img = Image.new("RGBA", (sc(W), sc(H)), BG)
    blob(img, 1020, 230, 560, GREEN, 0.13)
    blob(img, 1500, 340, 380, CYAN, 0.12)
    blob(img, 260, 40, 320, GREEN, 0.06)

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, W, 44):  # faint blueprint grid
        d.line([(sc(x), 0), (sc(x), sc(H))], fill=(255, 255, 255, 9), width=sc(1))
    for y in range(0, H, 44):
        d.line([(0, sc(y)), (sc(W), sc(y))], fill=(255, 255, 255, 9), width=sc(1))
    for x in range(22, 590, 22):  # dotted "desk" under the profile photo
        for y in range(66, H, 22):
            d.ellipse([sc(x) - 2, sc(y) - 2, sc(x) + 2, sc(y) + 2], fill=rgba(GREEN, 60))
    for y in range(0, H, 4):  # scanlines
        d.line([(0, sc(y)), (sc(W), sc(y))], fill=(255, 255, 255, 7), width=sc(1))
    img.alpha_composite(layer)
    return img


def title_bar(img: Image.Image) -> None:
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, sc(W), sc(44)], fill=PANEL)
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        cx = 30 + i * 24
        d.ellipse([sc(cx - 7), sc(15), sc(cx + 7), sc(29)], fill=c)
    f = font("regular", 15)
    label = "andres@maldonado: ~/linkedin"
    d.text((sc(W / 2), sc(28)), label, font=f, fill=DIM, anchor="ms")
    d.line([(0, sc(44)), (sc(W), sc(44))], fill=rgba(GREEN, 70), width=sc(1))


def left_logs(img: Image.Image) -> None:
    d = ImageDraw.Draw(img)
    f = font("regular", 15)
    for i, line in enumerate(LOGS):  # stays above the profile photo (y < 132)
        y = 72 + i * 22
        x = text(d, 36, y, "[ ok ]", f, rgba(GREEN, 150))
        text(d, x, y, line[6:], f, rgba(TEXT, 95))


def copy_block(img: Image.Image) -> None:
    X = 610
    d = ImageDraw.Draw(img)

    # Prompt line with a blinking-style cursor
    f20 = font("regular", 20)
    x = X
    for s, c in (("andres@maldonado", GREEN), (":", DIM), ("~", CYAN), (" $ ", TEXT), ("ship --secure", WHITE)):
        x = text(d, x, 96, s, f20, c)

    def cursor(dr: ImageDraw.ImageDraw, glow_only: bool) -> None:
        dr.rectangle([sc(x + 6), sc(79), sc(x + 18), sc(100)], fill=GREEN)

    glow(img, cursor, 5)

    # Headline: first line plain, second line neon
    f_head = font("bold", 84)
    d = ImageDraw.Draw(img)
    text(d, X, 178, HEADLINE[0], f_head, WHITE)

    def neon(dr: ImageDraw.ImageDraw, glow_only: bool) -> None:
        text(dr, X, 258, HEADLINE[1], f_head, GREEN)

    glow(img, neon, 12, passes=3)

    # Sub copy and call to action
    d = ImageDraw.Draw(img)
    f22 = font("regular", 22)
    text(d, X, 298, SUB[0], f22, WHITE)
    text(d, X, 326, SUB[1], f22, TEXT)

    d.rectangle([sc(X), sc(349), sc(X + 9), sc(358)], fill=CYAN)
    text(d, X + 22, 360, CTA, font("bold", 20), CYAN)


def pipeline(img: Image.Image) -> None:
    X, Y0, PW, PH, GAP = 1340, 84, 190, 44, 22
    d = ImageDraw.Draw(img)
    text(d, X, 70, "// ci pipeline", font("regular", 14), DIM)

    for i, label in enumerate(PIPELINE):
        y = Y0 + i * (PH + GAP)
        color = CYAN if i == len(PIPELINE) - 1 else GREEN

        if i:  # connector from the previous stage
            cx = X + PW / 2
            d.line([(sc(cx), sc(y - GAP)), (sc(cx), sc(y))], fill=rgba(GREEN, 150), width=sc(2))

        def pill(dr: ImageDraw.ImageDraw, glow_only: bool, y=y, color=color) -> None:
            box = [sc(X), sc(y), sc(X + PW), sc(y + PH)]
            if not glow_only:
                dr.rounded_rectangle(box, radius=sc(22), fill=CARD)
            dr.rounded_rectangle(box, radius=sc(22), outline=color, width=sc(2))

        glow(img, pill, 7, passes=1)

        d = ImageDraw.Draw(img)
        pts = [(X + 20, y + 23), (X + 27, y + 30), (X + 40, y + 15)]  # check mark
        d.line([(sc(a), sc(b)) for a, b in pts], fill=color, width=sc(3), joint="curve")
        text(d, X + 58, y + 29, label, font("bold", 20), WHITE)

    text(d, X, 356, "on every push", font("regular", 14), DIM)


def frame(img: Image.Image) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle(
        [sc(1), sc(1), sc(W - 2), sc(H - 2)], outline=rgba(GREEN, 150), width=sc(3)
    )
    img.alpha_composite(layer)


def build() -> Image.Image:
    img = background()
    title_bar(img)
    left_logs(img)
    copy_block(img)
    pipeline(img)
    frame(img)
    return img.convert("RGB").resize((W, H), Image.LANCZOS)


def main() -> None:
    resolve_fonts()
    OUTPUT.parent.mkdir(exist_ok=True)
    build().save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
