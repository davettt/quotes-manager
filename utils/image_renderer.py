"""Quote image renderer using Pillow."""

import io
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ASSETS_DIR = Path(__file__).parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# ---------------------------------------------------------------------------
# Aspect ratios  (width, height)
# ---------------------------------------------------------------------------

RATIOS: dict = {
    "square": (1080, 1080),
    "portrait": (1080, 1350),
    "landscape": (1920, 1080),
    "mobile": (1080, 1920),
    "tablet": (1536, 2048),
}

# ---------------------------------------------------------------------------
# Style presets
# ---------------------------------------------------------------------------

PRESETS: dict = {
    "dark": {
        "overlay_color": (0, 0, 0),
        "overlay_alpha": 140,  # ~55 %
        "text_color": (255, 255, 255),
        "author_color": (210, 210, 210),
        "quote_font": "PlayfairDisplay-Regular.ttf",
        "author_font": "PlayfairDisplay-Italic.ttf",
        "quote_bold": False,
        "author_bold": False,
        "decorative_marks": True,
        "shadow": True,
    },
    "light": {
        "overlay_color": (255, 255, 255),
        "overlay_alpha": 175,  # ~69 % — strong white wash for clean legibility
        "text_color": (15, 15, 15),
        "author_color": (65, 65, 65),
        "quote_font": "Lora-Regular.ttf",  # warm serif suits a light palette
        "author_font": "Lora-Regular.ttf",
        "quote_bold": False,
        "author_bold": True,
        "decorative_marks": False,
        "shadow": False,
    },
    "minimal": {
        "overlay_color": (0, 0, 0),
        "overlay_alpha": 77,  # ~30 % — photo breathes through
        "text_color": (255, 255, 255),
        "author_color": (200, 200, 200),
        "quote_font": "Inter-Regular.ttf",
        "author_font": "Inter-Regular.ttf",
        "quote_bold": False,
        "author_bold": False,
        "decorative_marks": False,
        "shadow": True,
    },
    "bold": {
        "overlay_color": (0, 0, 0),
        "overlay_alpha": 195,  # ~76 % — heavier than dark for max contrast
        "text_color": (255, 255, 255),
        "author_color": (170, 170, 170),  # muted so the bold quote is the hero
        "quote_font": "PlayfairDisplay-Regular.ttf",  # same serif as dark
        "author_font": "PlayfairDisplay-Italic.ttf",
        "quote_bold": True,  # bold weight — the key difference from dark
        "author_bold": False,
        "decorative_marks": True,
        "shadow": False,  # overlay is strong enough
    },
}

# ---------------------------------------------------------------------------
# Category → gradient palette  (start_rgb, end_rgb)
# ---------------------------------------------------------------------------

GRADIENTS: dict = {
    "stoicism": ((44, 62, 80), (52, 73, 94)),
    "philosophy": ((44, 62, 80), (74, 35, 90)),
    "motivation": ((180, 50, 30), (220, 100, 20)),
    "inspiration": ((0, 90, 160), (0, 160, 200)),
    "nature": ((30, 80, 40), (60, 130, 90)),
    "love": ((100, 10, 160), (220, 30, 120)),
    "wisdom": ((50, 10, 140), (60, 180, 220)),
    "mindfulness": ((0, 140, 120), (20, 180, 150)),
    "creativity": ((200, 120, 0), (220, 70, 20)),
    "success": ((0, 60, 50), (0, 130, 110)),
    "resilience": ((25, 45, 80), (60, 110, 160)),
    "leadership": ((20, 30, 60), (55, 80, 110)),
    "default": ((20, 30, 48), (36, 59, 85)),
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_font(
    font_filename: str, size: int, bold: bool = False
) -> ImageFont.FreeTypeFont:
    """Load a bundled font, optionally setting bold weight via variable-font axis."""
    path = FONTS_DIR / font_filename
    font = ImageFont.truetype(str(path), size)
    if bold:
        try:
            font.set_variation_by_name("Bold")
        except (OSError, Exception):
            try:
                font.set_variation_by_axes([700])
            except (OSError, Exception):
                pass  # Use default weight — non-critical
    return font


def _text_size(
    text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw
) -> Tuple[int, int]:
    """Return (width, height) of rendered text using textbbox for accuracy."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])


def _wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> List[str]:
    """Word-wrap text to fit within max_width pixels using actual glyph measurements."""
    words = text.split()
    lines: List[str] = []
    current: List[str] = []

    for word in words:
        candidate = " ".join(current + [word])
        w, _ = _text_size(candidate, font, draw)
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines if lines else [text]


def _optimal_font_size(
    text: str,
    max_width: int,
    max_height: int,
    font_filename: str,
    max_size: int = 72,
    min_size: int = 22,
    bold: bool = False,
) -> Tuple[int, List[str]]:
    """Find the largest font size where the wrapped text fits within the given bounds."""
    dummy = Image.new("RGB", (max_width + 200, max_height + 200))
    draw = ImageDraw.Draw(dummy)

    for size in range(max_size, min_size - 1, -2):
        font = _get_font(font_filename, size, bold=bold)
        lines = _wrap_text(text, font, max_width, draw)
        line_h = int(size * 1.45)
        if len(lines) * line_h <= max_height:
            return size, lines

    font = _get_font(font_filename, min_size, bold=bold)
    lines = _wrap_text(text, font, max_width, draw)
    return min_size, lines


def _gradient_background(
    width: int,
    height: int,
    start: Tuple[int, int, int],
    end: Tuple[int, int, int],
) -> Image.Image:
    """Create a top-to-bottom linear gradient background."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / height
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def _fit_image(photo_path: str, width: int, height: int) -> Image.Image:
    """Resize and center-crop a photo to fill the canvas exactly (cover behaviour)."""
    img = Image.open(photo_path).convert("RGB")
    iw, ih = img.size
    scale = max(width / iw, height / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - width) // 2
    top = (nh - height) // 2
    return img.crop((left, top, left + width, top + height))


def _apply_overlay(
    img: Image.Image, color: Tuple[int, int, int], alpha: int
) -> Image.Image:
    """Composite a semi-transparent solid-colour overlay onto the image."""
    overlay = Image.new("RGBA", img.size, (*color, alpha))
    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return result.convert("RGB")


def _gradient_for_categories(
    categories: List[str],
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Return (start, end) gradient colours for the first matching category."""
    for cat in categories:
        cat_lower = cat.lower()
        for key, colors in GRADIENTS.items():
            if key in cat_lower or cat_lower in key:
                return colors
    return GRADIENTS["default"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_quote_image(
    quote_text: str,
    author: str,
    categories: List[str],
    ratio: str = "square",
    style: str = "dark",
    bg_image_path: Optional[str] = None,
    photo_credit: Optional[str] = None,
) -> bytes:
    """
    Render a quote as a PNG image.

    Args:
        quote_text:    The quote body.
        author:        Author name (shown as "— Author").
        categories:    Quote categories, used to choose gradient colours.
        ratio:         One of: square, portrait, landscape, mobile, tablet.
        style:         One of: dark, light, minimal, bold.
        bg_image_path: Optional path to a background photo. Falls back to
                       gradient when None.
        photo_credit:  Optional attribution string embedded in the image
                       (e.g. "Photo by Jane / Unsplash"). Required by
                       Unsplash API ToS when a photo is used.

    Returns:
        Raw PNG bytes.
    """
    width, height = RATIOS.get(ratio, RATIOS["square"])
    preset = PRESETS.get(style, PRESETS["dark"])

    # ------------------------------------------------------------------
    # 1. Background
    # ------------------------------------------------------------------
    if bg_image_path:
        img = _fit_image(bg_image_path, width, height)
    else:
        start, end = _gradient_for_categories(categories)
        img = _gradient_background(width, height, start, end)

    # ------------------------------------------------------------------
    # 2. Overlay
    # ------------------------------------------------------------------
    img = _apply_overlay(img, preset["overlay_color"], preset["overlay_alpha"])

    draw = ImageDraw.Draw(img)

    # ------------------------------------------------------------------
    # 3. Layout measurements
    # ------------------------------------------------------------------
    # Mobile wallpapers need extra inset: iPhone's Perspective Zoom can
    # crop ~15-18 % from each edge, so we use a wider safe margin.
    padding_pct = 0.18 if ratio == "mobile" else 0.10
    padding = int(width * padding_pct)
    text_max_w = int(width * (1 - 2 * padding_pct))
    # Mobile: narrower quote area so the text block stays clear of the status
    # bar, widgets, and dock — and a lower font cap so longer quotes fit more
    # words per line rather than stacking into many short lines.
    if ratio == "mobile":
        quote_area_h = int(height * 0.42)
        max_font = 52
    else:
        quote_area_h = int(height * 0.55)
        max_font = 72

    # ------------------------------------------------------------------
    # 4. Optimal font size + word wrap
    # ------------------------------------------------------------------
    quote_bold = preset.get("quote_bold", False)
    font_size, lines = _optimal_font_size(
        quote_text,
        text_max_w,
        quote_area_h,
        preset["quote_font"],
        max_size=max_font,
        bold=quote_bold,
    )
    quote_font = _get_font(preset["quote_font"], font_size, bold=quote_bold)
    line_h = int(font_size * 1.45)
    total_quote_h = len(lines) * line_h

    # ------------------------------------------------------------------
    # 5. Vertical position: centre the full block (quote + gap + author)
    # ------------------------------------------------------------------
    author_text = f"\u2014 {author}"
    author_size = max(int(font_size * 0.52), 18)
    author_font = _get_font(
        preset["author_font"], author_size, bold=preset["author_bold"]
    )
    author_gap = int(font_size * 0.75)
    total_block_h = total_quote_h + author_gap + author_size

    quote_y = (height - total_block_h) // 2
    quote_y = max(int(height * 0.08), quote_y)

    # ------------------------------------------------------------------
    # 6. Decorative opening quote mark — positioned relative to quote_y
    # ------------------------------------------------------------------
    if preset["decorative_marks"]:
        mark_size = int(min(width, height) * 0.22)
        try:
            mark_font = _get_font(preset["quote_font"], mark_size)
            mark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            mark_draw = ImageDraw.Draw(mark_layer)
            # Sit the mark above the quote — offset by ~80 % of glyph size
            mark_y = quote_y - int(mark_size * 0.80)
            mark_draw.text(
                (padding, mark_y),
                "\u201c",
                font=mark_font,
                fill=(255, 255, 255, 35),
            )
            img = Image.alpha_composite(img.convert("RGBA"), mark_layer).convert("RGB")
            draw = ImageDraw.Draw(img)
        except Exception:
            pass  # Non-critical visual element

    # ------------------------------------------------------------------
    # 7. Draw quote lines
    # ------------------------------------------------------------------
    for i, line in enumerate(lines):
        lw, _ = _text_size(line, quote_font, draw)
        x = (width - lw) // 2
        y = quote_y + i * line_h
        if preset["shadow"]:
            draw.text((x + 2, y + 2), line, font=quote_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=quote_font, fill=preset["text_color"])

    # ------------------------------------------------------------------
    # 8. Author line  (right-aligned within text block)
    # ------------------------------------------------------------------
    author_y = quote_y + total_quote_h + author_gap
    aw, _ = _text_size(author_text, author_font, draw)
    author_x = width - padding - aw

    if preset["shadow"]:
        draw.text(
            (author_x + 1, author_y + 1),
            author_text,
            font=author_font,
            fill=(0, 0, 0),
        )
    draw.text(
        (author_x, author_y), author_text, font=author_font, fill=preset["author_color"]
    )

    # ------------------------------------------------------------------
    # 9. Photo attribution watermark (Unsplash API ToS requirement)
    # ------------------------------------------------------------------
    if photo_credit:
        credit_size = max(int(width * 0.013), 12)
        try:
            credit_font = _get_font("Inter-Regular.ttf", credit_size)
            cw, ch = _text_size(photo_credit, credit_font, draw)
            credit_padding = int(width * 0.03)
            cx = width - credit_padding - cw
            cy = height - credit_padding - ch
            # Choose text colour based on overlay type (light vs dark)
            is_light_preset = preset["overlay_color"] == (255, 255, 255)
            credit_color = (40, 40, 40) if is_light_preset else (220, 220, 220)
            shadow_color = (220, 220, 220) if is_light_preset else (0, 0, 0)
            draw.text(
                (cx + 1, cy + 1), photo_credit, font=credit_font, fill=shadow_color
            )
            draw.text((cx, cy), photo_credit, font=credit_font, fill=credit_color)
        except Exception:
            pass  # Non-critical

    # ------------------------------------------------------------------
    # 10. Return PNG bytes
    # ------------------------------------------------------------------
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
