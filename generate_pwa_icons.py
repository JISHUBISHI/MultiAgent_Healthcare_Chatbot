"""Generate the HealthBuddy desktop and PWA icon set."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BASE_DIR = Path(__file__).resolve().parent
LOGO_JPEG = BASE_DIR / "healthbuddy-logo.jpeg"
APP_ICON = BASE_DIR / "healthbuddy-app.ico"
OUT_192 = BASE_DIR / "icon-192.png"
OUT_512 = BASE_DIR / "icon-512.png"
MASKABLE_512 = BASE_DIR / "icon-512-maskable.png"

PRIMARY = (79, 140, 255)
ACCENT = (43, 215, 163)
CYAN = (53, 210, 255)
SURFACE = (7, 16, 30)
SURFACE_ALT = (12, 28, 48)
WHITE = (233, 247, 255)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
    ]
    for name in candidates:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def vertical_gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    gradient = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(gradient)
    for y in range(size):
        mix = y / max(size - 1, 1)
        color = tuple(int(top[i] * (1 - mix) + bottom[i] * mix) for i in range(3)) + (255,)
        draw.line((0, y, size, y), fill=color)
    return gradient


def make_symbol_icon(size: int) -> Image.Image:
    icon = Image.new("RGBA", (size, size), SURFACE + (255,))
    icon.alpha_composite(vertical_gradient(size, (9, 23, 40), (4, 12, 24)))

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((size * 0.12, size * 0.1, size * 0.88, size * 0.86), fill=(67, 228, 255, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(8, size // 20)))
    icon.alpha_composite(glow)

    inner_margin = int(size * 0.11)
    inner = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner_draw = ImageDraw.Draw(inner)
    inner_draw.rounded_rectangle(
        (inner_margin, inner_margin, size - inner_margin, size - inner_margin),
        radius=int(size * 0.18),
        fill=SURFACE_ALT + (255,),
        outline=(119, 223, 255, 70),
        width=max(2, size // 80),
    )
    icon.alpha_composite(inner)

    draw = ImageDraw.Draw(icon)
    trace = [
        (0.2, 0.53), (0.34, 0.53), (0.41, 0.42), (0.49, 0.65),
        (0.58, 0.35), (0.67, 0.56), (0.8, 0.56),
    ]
    points = [(int(size * x), int(size * y)) for x, y in trace]
    draw.line(points, fill=CYAN + (255,), width=max(6, size // 26), joint="curve")

    cx = int(size * 0.34)
    cy = int(size * 0.36)
    arm = max(16, size // 7)
    stroke = max(12, size // 12)
    draw.rounded_rectangle((cx - stroke // 2, cy - arm, cx + stroke // 2, cy + arm), radius=stroke // 2, fill=WHITE + (255,))
    draw.rounded_rectangle((cx - arm, cy - stroke // 2, cx + arm, cy + stroke // 2), radius=stroke // 2, fill=WHITE + (255,))
    return icon


def make_logo_banner(width: int = 1600, height: int = 900) -> Image.Image:
    image = Image.new("RGB", (width, height), SURFACE)
    background = vertical_gradient(height, (6, 14, 28), (3, 9, 18)).resize((width, height))
    image.paste(background, (0, 0))

    symbol = make_symbol_icon(420).resize((420, 420), Image.LANCZOS)
    image.paste(symbol, (120, 240), symbol)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((60, 180, 760, 820), fill=(36, 176, 255, 24))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(image)
    title_font = load_font(160, bold=True)
    subtitle_font = load_font(56, bold=True)
    text_x = 610
    draw.text((text_x, 340), "HealthBuddy", font=title_font, fill=WHITE)
    draw.text((text_x + 8, 520), "AI MEDICAL ASSISTANT", font=subtitle_font, fill=(137, 180, 204), spacing=8)
    draw.line((text_x + 10, 620, text_x + 520, 620), fill=CYAN, width=8)
    pulse = [(text_x + 520, 620), (text_x + 580, 620), (text_x + 610, 560), (text_x + 646, 670), (text_x + 700, 470), (text_x + 758, 620), (text_x + 860, 620)]
    draw.line(pulse, fill=CYAN, width=10, joint="curve")
    return image


def make_maskable_icon() -> Image.Image:
    canvas = Image.new("RGBA", (512, 512), SURFACE + (255,))
    symbol = make_symbol_icon(360)
    canvas.alpha_composite(symbol, dest=((512 - 360) // 2, (512 - 360) // 2))
    return canvas


def save_png(image: Image.Image, path: Path, size: int) -> None:
    image.resize((size, size), Image.LANCZOS).save(path, format="PNG")


def main():
    make_logo_banner().save(LOGO_JPEG, format="JPEG", quality=94)

    app_icon = make_symbol_icon(512)
    save_png(app_icon, OUT_512, 512)
    save_png(app_icon, OUT_192, 192)
    make_maskable_icon().save(MASKABLE_512, format="PNG")
    app_icon.save(APP_ICON, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])


if __name__ == "__main__":
    main()
