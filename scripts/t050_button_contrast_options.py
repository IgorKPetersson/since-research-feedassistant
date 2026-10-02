"""T-050: render the Ask button's contrast options side by side, with each option's
measured WCAG contrast ratio, so the choice can be made by eye. Writes one PNG.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("docs/screenshots/t050-ask-button-options.png")
AMBER = (0xC1, 0x7F, 0x1A)
WHITE = (255, 255, 255)
DARK = (0x1A, 0x1A, 0x1A)
PAGE = (255, 255, 255)
TEXT = (0x26, 0x26, 0x26)
MUTED = (0x6B, 0x6B, 0x6B)


def luminance(rgb: tuple[int, int, int]) -> float:
    def channel(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def darkest_amber_passing() -> tuple[int, int, int]:
    """The lightest shade of the same amber hue on which white text reaches 4.5:1."""
    for percent in range(100, 0, -1):
        shade = tuple(round(v * percent / 100) for v in AMBER)
        if contrast(WHITE, shade) >= 4.5:
            return shade
    raise ValueError("no shade passes")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", size)


def main() -> None:
    darker = darkest_amber_passing()
    options = [
        ("Nu", AMBER, WHITE, AMBER),
        ("A: mörk text, samma gula", AMBER, DARK, AMBER),
        ("B: mörkare gul, vit text", darker, WHITE, darker),
    ]
    col, height = 420, 330
    image = Image.new("RGB", (col * len(options), height), PAGE)
    draw = ImageDraw.Draw(image)
    for i, (title, fill, label, accent) in enumerate(options):
        x = i * col + 40
        draw.text((x, 28), title, font=font(24, bold=True), fill=TEXT)
        ratio = contrast(label, fill)
        verdict = "klarar kravet 4,5" if ratio >= 4.5 else "under kravet 4,5"
        draw.text((x, 64), f"kontrast {ratio:.2f}:1, {verdict}".replace(".", ","), font=font(18), fill=MUTED)
        draw.rounded_rectangle((x, 110, x + 150, 166), radius=10, fill=fill)
        draw.text((x + 75, 138), "Ask", font=font(24, bold=True), fill=label, anchor="mm")
        # the accent as it appears elsewhere in the app: logo dot and a source link
        draw.ellipse((x, 205, x + 22, 227), fill=accent)
        draw.text((x + 34, 199), "Since", font=font(26, bold=True), fill=TEXT)
        draw.text((x, 256), "NeoHorse-1: Towards Recursive…", font=font(18), fill=TEXT)
        draw.line((x, 284, x + 262, 284), fill=accent, width=3)
        draw.text((x, 294), "#%02X%02X%02X" % accent, font=font(16), fill=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT)
    print(OUT, [("%s %.2f" % (t, contrast(l, f))) for t, f, l, _ in options], "#%02X%02X%02X" % darker)


if __name__ == "__main__":
    main()
