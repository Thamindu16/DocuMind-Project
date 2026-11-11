from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PUBLIC = Path("public")
AVATARS = PUBLIC / "avatars"
AVATARS.mkdir(parents=True, exist_ok=True)

FONT_PATHS = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
ACCENT = (37, 99, 235, 255)
WHITE = (255, 255, 255, 255)


def load_font(size):
    """Use a bold Windows font, falling back to the default font."""
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_logo(filename):
    """Draw 'DocuMind' as white text on a blue rounded pill, readable on any background."""
    font = load_font(96)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = probe.textbbox((0, 0), "DocuMind", font=font)
    text_w, text_h = box[2] - box[0], box[3] - box[1]

    pad_x, pad_y = 56, 36
    image = Image.new("RGBA", (text_w + 2 * pad_x, text_h + 2 * pad_y), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=44, fill=ACCENT)
    draw.text((pad_x - box[0], pad_y - box[1]), "DocuMind", font=font, fill=WHITE)
    image.save(PUBLIC / filename)


def make_icon(path):
    """Draw a blue rounded square with a white 'D' for the favicon and chat avatar."""
    image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, 127, 127), radius=28, fill=ACCENT)

    font = load_font(84)
    box = draw.textbbox((0, 0), "D", font=font)
    x = (128 - (box[2] - box[0])) / 2 - box[0]
    y = (128 - (box[3] - box[1])) / 2 - box[1]
    draw.text((x, y), "D", font=font, fill=WHITE)
    image.save(path)


# The same logo is used for both themes
make_logo("logo_dark.png")
make_logo("logo_light.png")
make_icon(PUBLIC / "favicon.png")
make_icon(AVATARS / "documind.png")
print("Logo files created in public/")