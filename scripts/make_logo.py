from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PUBLIC = Path("public")
AVATARS = PUBLIC / "avatars"
AVATARS.mkdir(parents=True, exist_ok=True)

WORD = "documind"
FONT_PATHS = [
    "C:/Windows/Fonts/segoeuib.ttf",  # Segoe UI Bold
    "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
    "C:/Windows/Fonts/seguibl.ttf",   # Segoe UI Black (very heavy, melts too much)
]
FONT_SIZE = 360       # draw big, shrink at the end for smooth edges
OVERLAP = 0.035       # how far neighbouring letters overlap (fraction of font size)
GOO = 0.02          # blur radius that melts touching letters together (lower = less melting)
THRESHOLD = 128       # 0-255, higher keeps the holes inside o, d and a open
LEFT, RIGHT = (99, 102, 241), (168, 85, 247)   # indigo to purple, readable on dark and light themes


def load_font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise SystemExit("No bold font found. Edit FONT_PATHS at the top of scripts/make_logo.py.")


def fused_mask(text, size):
    """Draw overlapping letters, then blur and threshold so touching letters melt into one shape."""
    font = load_font(size)
    pad = int(size * 0.4)
    advances = [font.getlength(ch) for ch in text]
    step_back = OVERLAP * size
    width = int(sum(advances) - step_back * (len(text) - 1)) + 2 * pad
    height = int(size * 1.6) + 2 * pad

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    x = pad
    for char, advance in zip(text, advances):
        draw.text((x, pad), char, font=font, fill=255)
        x += advance - step_back

    blurred = mask.filter(ImageFilter.GaussianBlur(GOO * size))
    fused = blurred.point(lambda value: 255 if value > THRESHOLD else 0)
    return fused.crop(fused.getbbox())


def gradient(size, left, right):
    """Horizontal colour gradient image."""
    width, height = size
    row = Image.new("RGB", (width, 1))
    for x in range(width):
        t = x / max(width - 1, 1)
        row.putpixel((x, 0), tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3)))
    return row.resize((width, height), Image.NEAREST)


def make_logo(filename, left, right=None):
    """Save the fused wordmark on a transparent background."""
    mask = fused_mask(WORD, FONT_SIZE)
    margin = int(FONT_SIZE * 0.2)
    canvas = Image.new("L", (mask.width + 2 * margin, mask.height + 2 * margin), 0)
    canvas.paste(mask, (margin, margin))

    logo = gradient(canvas.size, left, right or left).convert("RGBA")
    logo.putalpha(canvas)
    final_width = 900
    logo = logo.resize((final_width, int(logo.height * final_width / logo.width)), Image.LANCZOS)
    logo.save(PUBLIC / filename)


def make_icon(path, pixels):
    """Rounded gradient square with a fused white 'd', used for the favicon and the chat avatar."""
    size = 1024
    icon = gradient((size, size), LEFT, RIGHT).convert("RGBA")
    corners = Image.new("L", (size, size), 0)
    ImageDraw.Draw(corners).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.23), fill=255)
    icon.putalpha(corners)

    letter = fused_mask("d", FONT_SIZE)
    target = int(size * 0.6)
    letter = letter.resize((int(letter.width * target / letter.height), target), Image.LANCZOS)
    layer = Image.new("RGBA", letter.size, (255, 255, 255, 255))
    layer.putalpha(letter)
    overlay = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    overlay.paste(layer, ((size - letter.width) // 2, (size - letter.height) // 2))
    icon = Image.alpha_composite(icon, overlay)
    icon.resize((pixels, pixels), Image.LANCZOS).save(path)


make_logo("logo.png", LEFT, RIGHT)          # used by the chat UI on both themes
make_logo("logo_dark.png", LEFT, RIGHT)
make_logo("logo_light.png", LEFT, RIGHT)
make_logo("logo_black.png", (17, 24, 39))   # plain versions for documents and slides
make_logo("logo_white.png", (255, 255, 255))
make_icon(PUBLIC / "favicon.png", 64)
make_icon(AVATARS / "documind.png", 128)
print("Logo files created in public/")