import pandas as pd
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------

pdfmetrics.registerFont(TTFont("Archive", "Archive.ttf"))

FONT_NAME = "Archive"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pt(cm_val):
    return cm_val * 28.3465

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

BADGE_W = pt(9.0)
BADGE_H = pt(13.0)

BADGES_PER_ROW  = 2
BADGES_PER_COL  = 2
BADGES_PER_PAGE = BADGES_PER_ROW * BADGES_PER_COL

PAGE_W = BADGES_PER_ROW * BADGE_W
PAGE_H = BADGES_PER_COL * BADGE_H

TEXT_MARGIN_X = pt(2.2)

# Left col shifts right (+), right col shifts left (-)
CENTER_NUDGE  = pt(0.2)

# Blank zone (fractions of badge height from bottom)
TEXT_AREA_TOP    = 0.60
TEXT_AREA_BOTTOM = 0.38

# Vertical offset per row. Positive = shift text downward.
ROW_VERTICAL_OFFSET = {
    0: pt(-0.4),   # top badges: nudge down
    1: pt(0.0),    # bottom badges: no change
}

NAME_FONT_SIZE  = 26
AFFIL_FONT_SIZE = 14
AFFIL_MAX_DELTA = 4

LINE_SPACING_FACTOR = 1.3
GAP_FACTOR          = 0.4

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def shrink_to_fit(c, text, font, max_size, max_width, min_size=6):
    size = max_size
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 1
    return size

def wrap_text(c, text, font, size, max_width):
    words   = text.split()
    lines   = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]

def build_name_lines(c, font, first, surname, max_size, max_width):
    """Always first name on line 1, surname on line 2.
    Font sized so the longest of the two fits."""
    size = max_size
    for word in [first, surname]:
        size = shrink_to_fit(c, word, font, size, max_width, min_size=6)
    return [first, surname], size

def build_affil_lines(c, text, font, max_size, max_width):
    size = shrink_to_fit(c, text, font, max_size, max_width, min_size=6)
    if c.stringWidth(text, font, size) <= max_width:
        return [text], size
    lines = wrap_text(c, text, font, size, max_width)
    return lines, size

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def create_badges(csv_file, png_file, output_file="output.pdf"):
    df = pd.read_csv(csv_file)

    c = canvas.Canvas(output_file, pagesize=(PAGE_W, PAGE_H))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    try:
        Image.open(png_file).save(tmp.name, format="PNG")
        tmp.close()
        bg_path = tmp.name

        total      = len(df)
        page_start = 0

        while page_start < total:

            c.drawImage(bg_path, 0, 0, width=PAGE_W, height=PAGE_H,
                        preserveAspectRatio=False)

            for slot in range(BADGES_PER_PAGE):
                idx = page_start + slot
                if idx >= total:
                    break

                row = df.iloc[idx]

                col     = slot % BADGES_PER_ROW
                row_idx = slot // BADGES_PER_ROW

                bx = col * BADGE_W
                by = PAGE_H - (row_idx + 1) * BADGE_H

                area_top_y    = by + BADGE_H * TEXT_AREA_TOP
                area_bottom_y = by + BADGE_H * TEXT_AREA_BOTTOM
                area_h        = area_top_y - area_bottom_y
                avail_w       = BADGE_W - 2 * TEXT_MARGIN_X

                nudge    = CENTER_NUDGE if col == 0 else -CENTER_NUDGE
                center_x = bx + BADGE_W / 2 + nudge

                v_offset      = ROW_VERTICAL_OFFSET.get(row_idx, 0)
                area_center_y = (area_bottom_y + area_h / 2) + v_offset

                c.setFillColorRGB(0, 0, 0)

                # ── NAME ──────────────────────────────────────────────────
                first   = str(row['name'])
                surname = str(row['surname'])
                name_lines, name_size = build_name_lines(
                    c, FONT_NAME, first, surname, NAME_FONT_SIZE, avail_w)

                # ── AFFILIATION — strictly smaller than name ───────────────
                affil_max = name_size - AFFIL_MAX_DELTA
                affil     = str(row['affiliation'])
                afil_lines, afil_size = build_affil_lines(
                    c, affil, FONT_NAME, min(AFFIL_FONT_SIZE, affil_max), avail_w)

                # ── center block vertically ────────────────────────────────
                name_line_h = name_size * LINE_SPACING_FACTOR
                afil_line_h = afil_size * LINE_SPACING_FACTOR
                gap         = name_size * GAP_FACTOR

                total_h   = (len(name_lines) * name_line_h
                             + gap
                             + len(afil_lines) * afil_line_h)
                block_top = area_center_y + total_h / 2

                y = block_top

                # ── draw name ──────────────────────────────────────────────
                c.setFont(FONT_NAME, name_size)
                for line in name_lines:
                    y -= name_line_h
                    c.drawCentredString(center_x, y, line)

                y -= gap

                # ── draw affiliation ───────────────────────────────────────
                c.setFont(FONT_NAME, afil_size)
                for line in afil_lines:
                    y -= afil_line_h
                    c.drawCentredString(center_x, y, line)

            page_start += BADGES_PER_PAGE
            c.showPage()

    finally:
        os.unlink(tmp.name)

    c.save()
    print(f"Saved → {output_file}")

# ---------------------------------------------------------------------------
create_badges("participants.csv", "background.png")