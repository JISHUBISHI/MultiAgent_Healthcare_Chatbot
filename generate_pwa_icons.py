"""
Generate PWA icon sizes from the HealthBuddy logo.
"""

from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "healthbuddy-logo.jpeg"
OUT_192 = BASE_DIR / "icon-192.png"
OUT_512 = BASE_DIR / "icon-512.png"
MASKABLE_512 = BASE_DIR / "icon-512-maskable.png"


def main():
    with Image.open(SOURCE) as image:
        image = image.convert("RGBA")
        image.resize((192, 192), Image.LANCZOS).save(OUT_192, format="PNG")
        image.resize((512, 512), Image.LANCZOS).save(OUT_512, format="PNG")

        canvas = Image.new("RGBA", (512, 512), (11, 23, 32, 255))
        foreground = image.resize((360, 360), Image.LANCZOS)
        canvas.paste(foreground, ((512 - 360) // 2, (512 - 360) // 2), foreground)
        canvas.save(MASKABLE_512, format="PNG")


if __name__ == "__main__":
    main()
