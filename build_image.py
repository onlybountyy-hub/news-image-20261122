#!/usr/bin/env python3
"""
THE WORLD TODAY - Sunday 22 November 2026 edition.

Renders the one-page newspaper image (entry.png, 1024x1024) for the
make.fun news-image-20261122 competition. Every story on the page is an
event that happened, or was first reported, on Sunday 22 November 2026;
see SOURCES.md for the wire reports behind each item.

Pure Pillow drawing: flat shapes, rules and type. No photographs, no
external assets.
"""

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)      # warm newsprint
PANEL = (255, 253, 246)      # story cell background
INK = (26, 26, 26)           # body ink
FAINT = (110, 102, 90)       # secondary text
RULE = (138, 131, 120)       # hairlines
RED = (179, 35, 42)          # section red
BLUE = (29, 78, 137)         # section blue
GREEN = (30, 110, 76)        # section green
GOLD = (176, 124, 32)        # section gold
DARK = (30, 36, 46)          # hero / figures background
DARKTXT = (247, 242, 231)
GOLDBRIGHT = (232, 177, 60)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap using real glyph widths."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, leading):
    x, y = xy
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
# Tiny flat glyphs drawn in a 30x30 box whose top-left corner is (x, y).

def icon_ship(d, x, y, c):
    d.polygon([(x + 3, y + 19), (x + 27, y + 19), (x + 23, y + 26), (x + 7, y + 26)], fill=c)
    d.rectangle([x + 9, y + 13, x + 21, y + 19], fill=c)
    d.rectangle([x + 13, y + 7, x + 17, y + 13], fill=c)
    d.line([(x + 2, y + 28), (x + 28, y + 28)], fill=c, width=2)


def icon_building(d, x, y, c):
    d.rectangle([x + 6, y + 4, x + 24, y + 27], outline=c, width=2)
    for r in range(3):
        for col in range(2):
            d.rectangle([x + 10 + col * 7, y + 8 + r * 6, x + 13 + col * 7, y + 11 + r * 6], fill=c)
    d.polygon([(x + 18, y + 14), (x + 24, y + 20), (x + 24, y + 27), (x + 18, y + 27)], fill=RED)


def icon_capitol(d, x, y, c):
    d.arc([x + 8, y + 3, x + 22, y + 17], start=180, end=0, fill=c, width=2)
    d.rectangle([x + 14, y + 1, x + 16, y + 5], fill=c)
    d.line([(x + 4, y + 17), (x + 26, y + 17)], fill=c, width=2)
    for i in range(4):
        d.line([(x + 6 + i * 6, y + 19), (x + 6 + i * 6, y + 25)], fill=c, width=2)
    d.line([(x + 3, y + 27), (x + 27, y + 27)], fill=c, width=2)


def icon_missile(d, x, y, c):
    d.polygon([(x + 20, y + 3), (x + 27, y + 10), (x + 14, y + 23), (x + 10, y + 19)], fill=c)
    d.polygon([(x + 10, y + 19), (x + 5, y + 27), (x + 12, y + 25)], fill=GOLD)
    d.polygon([(x + 10, y + 19), (x + 3, y + 21), (x + 8, y + 26)], fill=RED)


def icon_flame(d, x, y, c):
    d.polygon([(x + 15, y + 2), (x + 21, y + 12), (x + 24, y + 18), (x + 21, y + 27),
               (x + 9, y + 27), (x + 6, y + 18), (x + 10, y + 11)], fill=c)
    d.polygon([(x + 15, y + 13), (x + 19, y + 19), (x + 17, y + 26), (x + 12, y + 26),
               (x + 11, y + 19)], fill=GOLDBRIGHT)


def icon_tanker(d, x, y, c):
    d.polygon([(x + 2, y + 17), (x + 28, y + 17), (x + 24, y + 24), (x + 6, y + 24)], fill=c)
    d.rectangle([x + 5, y + 12, x + 22, y + 17], fill=c)
    d.rectangle([x + 22, y + 8, x + 26, y + 17], fill=c)
    d.arc([x + 2, y + 22, x + 12, y + 30], start=0, end=180, fill=BLUE, width=2)
    d.arc([x + 14, y + 22, x + 24, y + 30], start=0, end=180, fill=BLUE, width=2)


def icon_drone(d, x, y, c):
    for cx, cy in [(6, 6), (24, 6), (6, 24), (24, 24)]:
        d.ellipse([x + cx - 4, y + cy - 4, x + cx + 4, y + cy + 4], outline=c, width=2)
    d.line([(x + 9, y + 9), (x + 21, y + 21)], fill=c, width=2)
    d.line([(x + 21, y + 9), (x + 9, y + 21)], fill=c, width=2)
    d.rectangle([x + 12, y + 12, x + 18, y + 18], fill=c)


def icon_factory(d, x, y, c):
    d.polygon([(x + 3, y + 27), (x + 3, y + 15), (x + 12, y + 20), (x + 12, y + 15),
               (x + 21, y + 20), (x + 21, y + 27)], fill=c)
    d.rectangle([x + 23, y + 6, x + 27, y + 27], fill=c)
    d.polygon([(x + 25, y + 1), (x + 29, y + 6), (x + 22, y + 6)], fill=RED)


def icon_crowd(d, x, y, c):
    for cx in (8, 15, 22):
        d.ellipse([x + cx - 3, y + 5, x + cx + 3, y + 11], fill=c)
        d.arc([x + cx - 5, y + 11, x + cx + 5, y + 23], start=180, end=0, fill=c, width=3)
    d.line([(x + 3, y + 26), (x + 27, y + 26)], fill=c, width=2)


def icon_plane(d, x, y, c):
    d.polygon([(x + 2, y + 18), (x + 26, y + 6), (x + 18, y + 20), (x + 13, y + 15)], fill=c)
    d.polygon([(x + 13, y + 15), (x + 18, y + 20), (x + 12, y + 24), (x + 9, y + 19)], fill=c)
    d.line([(x + 3, y + 27), (x + 15, y + 27)], fill=c, width=2)


def icon_ball(d, x, y, c):
    d.ellipse([x + 3, y + 3, x + 27, y + 27], outline=c, width=2)
    d.polygon([(x + 15, y + 10), (x + 20, y + 14), (x + 18, y + 20), (x + 12, y + 20), (x + 10, y + 14)], fill=c)
    for a, b in [(15, 4), (25, 12), (21, 24), (9, 24), (5, 12)]:
        d.line([(x + 15, y + 15), (x + a, y + b)], fill=c, width=1)


# ---------------------------------------------------------------- stories
# (kicker, kicker colour, headline, dek, icon)
HERO_KICKER = "CLIMATE · ANTALYA, TÜRKIYE"
HERO_HEADLINE = "COP31 COLLAPSES"
HERO_DEK = (
    "After two weeks of talks and a record 44 hours of overtime, the UN climate "
    "summit ended with no deal: the EU and its allies rejected a final text that "
    "never mentioned fossil fuels. The “Antalya Pact” falls."
)

ROW1 = [
    ("CONFLICT · BENGHAZI", RED,
     "SEA DRONES SINK RUSSIAN CORVETTE",
     "Suspected Ukrainian sea drones hit the Merkury at Benghazi naval base; "
     "it capsized at its berth. Ten hurt; a merchant ship was also struck.",
     icon_ship),
    ("CONFLICT · DYMER", RED,
     "DRONE LEVELS FLATS NEAR KYIV",
     "A Russian drone collapsed a five-storey block overnight: at least two "
     "dead, four wounded, more feared under the rubble.",
     icon_building),
    ("POLITICS · WASHINGTON", BLUE,
     "DEMOCRATS CLINCH 258 HOUSE SEATS",
     "A North Carolina call delivered the largest House majority since 1992. "
     "Four races are still uncalled.",
     icon_capitol),
    ("EUROPE · WARSAW", BLUE,
     "POLAND: ALL 3 WERE RUSSIAN MISSILES",
     "Prosecutors say Friday's debris was three Kh-101 cruise missiles made "
     "weeks ago in Dubna. NATO meets Monday.",
     icon_missile),
]

ROW2 = [
    ("MIDDLE EAST · RAMALLAH", RED,
     "SETTLERS TORCH WEST BANK VILLAGES",
     "Cars and homes burned in four villages overnight; “Revenge” daubed on "
     "walls. Israel's opposition chief: “Jewish terrorism.”",
     icon_flame),
    ("MIDDLE EAST · THE GULF", RED,
     "MISSILES OVER THE GULF AGAIN",
     "Bahrain: an Iranian strike wounds two at a plant. Saudis down a Houthi "
     "missile; Iran says two tankers afire in Hormuz.",
     icon_tanker),
    ("AFRICA · KHARTOUM", RED,
     "DRONES HIT UN BUILDING IN KHARTOUM",
     "Pre-dawn strikes on homes across the capital damaged a UN premises with "
     "staff inside. Four people were killed.",
     icon_drone),
    ("DISASTER · BANTEN", GOLD,
     "37 MISSING IN CANDY FACTORY FIRE",
     "Rescuers combed a burned-out candy factory for 37 missing workers after "
     "Saturday's blaze killed at least three.",
     icon_factory),
]

ROW3 = [
    ("LABOUR · GAZIPUR", GOLD,
     "TEAR GAS ON THE HIGHWAY",
     "Garment workers seeking a Tk 30,000 wage blocked the Dhaka–Mymensingh "
     "road; police fired tear gas.",
     icon_crowd),
    ("DIPLOMACY · NEW DELHI", BLUE,
     "NEPAL'S PM OPENS INDIA VISIT",
     "Balendra Shah's first state visit since taking office: a 34-member "
     "team, Modi talks on Monday.",
     icon_plane),
    ("SPORT · ANFIELD", GREEN,
     "LIVERPOOL 4–0 MAN UNITED",
     "Pochettino's debut: Yoro off in 8 minutes, then Szoboszlai, Wirtz, "
     "Ngumoha and Muñoz ran riot.",
     icon_ball),
]

FIGURES = [
    ("194", "nations at COP31"),
    ("44 hrs", "of overtime in Antalya"),
    ("258", "House seats for Democrats"),
    ("3", "Kh-101 missiles in Poland"),
    ("37", "workers missing in Banten"),
    ("8 min", "to Anfield's red card"),
]


# ---------------------------------------------------------------- drawing
def masthead(d, W):
    f_title = font(SERIF, 52)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 14), title, font=f_title, fill=INK)
    d.line([(28, 78), (W - 28, 78)], fill=INK, width=3)
    # date band - the day, named large
    d.rectangle([28, 86, W - 28, 132], fill=INK)
    f_date = font(SANS_B, 30)
    date = "SUNDAY · 22 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 94), date, font=f_date, fill=PAPER)
    f_tag = font(SANS, 13)
    tag = "ONE DAY · ONE PAGE · THE WHOLE WORLD"
    tw2 = d.textlength(tag, font=f_tag)
    d.text(((W - tw2) / 2, 140), tag, font=f_tag, fill=FAINT)


def hero_art(d, x, y, w, h):
    """Globe, rising thermometer, and the pact torn in two."""
    # globe
    cx, cy, r = x + 122, y + 150, 98
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 84, 124))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLDBRIGHT, width=3)
    for blob in [(-44, -40, 34, 20), (10, -56, 26, 16), (36, 8, 38, 24),
                 (-18, 36, 30, 18), (-60, 10, 20, 14), (52, -30, 18, 13)]:
        bx, by, bw, bh = blob
        d.ellipse([cx + bx, cy + by, cx + bx + bw, cy + by + bh], fill=(64, 142, 92))
    # crack across the globe
    d.line([(cx - 68, cy - 76), (cx - 26, cy - 20), (cx - 46, cy + 18), (cx - 6, cy + 72)],
           fill=(20, 26, 34), width=5)
    # thermometer
    tx = x + 246
    d.rounded_rectangle([tx, y + 42, tx + 20, y + 186], radius=10, fill=(214, 219, 226))
    d.rectangle([tx + 5, y + 84, tx + 15, y + 178], fill=RED)
    d.ellipse([tx - 6, y + 174, tx + 26, y + 206], fill=RED)
    for i in range(5):
        d.line([(tx + 24, y + 62 + i * 24), (tx + 34, y + 62 + i * 24)], fill=DARKTXT, width=2)
    # torn pact document
    px, py = x + 292, y + 88
    d.polygon([(px, py), (px + 62, py + 8), (px + 40, py + 44), (px + 58, py + 84),
               (px + 2, py + 76)], fill=(238, 233, 218))
    d.polygon([(px + 70, py + 2), (px + 128, py + 12), (px + 122, py + 88),
               (px + 66, py + 80), (px + 48, py + 42)], fill=(222, 216, 198))
    for i in range(3):
        d.line([(px + 12, py + 24 + i * 16), (px + 44, py + 28 + i * 16)], fill=FAINT, width=3)
        d.line([(px + 76, py + 28 + i * 16), (px + 112, py + 32 + i * 16)], fill=FAINT, width=3)
    f_doc = font(SANS_B, 14)
    d.text((px + 2, y + 234), "THE ANTALYA PACT", font=f_doc, fill=DARKTXT)
    # red X over the document
    d.line([(px + 8, py + 6), (px + 120, py + 84)], fill=RED, width=7)
    d.line([(px + 120, py + 6), (px + 8, py + 84)], fill=RED, width=7)


def hero(d, W):
    top, bot = 162, 470
    d.rectangle([28, top, W - 28, bot], fill=DARK)
    hero_art(d, 28, top, 452, bot - top)
    tx = 472
    d.text((tx, top + 22), HERO_KICKER, font=font(SANS_B, 17), fill=GOLDBRIGHT)
    y = text_block(d, (tx, top + 52), HERO_HEADLINE, font(SERIF, 54), DARKTXT, W - tx - 28, 62)
    d.line([(tx, y + 6), (tx + 120, y + 6)], fill=RED, width=5)
    text_block(d, (tx, y + 22), HERO_DEK, font(SANS, 15), (216, 220, 226), W - tx - 28, 22)
    # contents strip along the hero's foot
    d.line([(tx, bot - 40), (W - 28, bot - 40)], fill=(90, 98, 110), width=1)
    d.text((tx, bot - 30), "ALSO INSIDE:  LIBYA · KYIV FLATS · THE GULF · ANFIELD ROUT",
           font=font(SANS_B, 12), fill=GOLDBRIGHT)


def story_cell(d, x, y, w, h, story):
    kicker, kc, headline, dek, icon = story
    d.rectangle([x, y, x + w, y + h], fill=PANEL)
    d.rectangle([x, y, x + w, y + 5], fill=kc)
    icon(d, x + w - 40, y + 14, kc)
    text_block(d, (x + 10, y + 14), kicker, font(SANS_B, 11), kc, w - 56, 14)
    y2 = text_block(d, (x + 10, y + 36), headline, font(SERIF, 17), INK, w - 20, 21)
    text_block(d, (x + 10, y2 + 4), dek, font(SANS, 12), (52, 50, 46), w - 20, 16)


def grid_row(d, W, y, h, stories):
    cols, gut, mx = 4, 14, 28
    cw = (W - 2 * mx - (cols - 1) * gut) // cols
    for i, s in enumerate(stories):
        story_cell(d, mx + i * (cw + gut), y, cw, h, s)
    return cw


def figures_box(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=DARK)
    d.text((x + 10, y + 10), "THE DAY IN NUMBERS", font=font(SANS_B, 12), fill=GOLDBRIGHT)
    fy = y + 32
    f_num, f_lab = font(SERIF, 15), font(SANS, 10)
    for num, lab in FIGURES:
        d.text((x + 10, fy), num, font=f_num, fill=DARKTXT)
        nw = d.textlength(num, font=f_num)
        d.text((x + 16 + nw, fy + 3), lab, font=f_lab, fill=(190, 196, 204))
        fy += 17


def footer(d, W):
    d.line([(28, 976), (W - 28, 976)], fill=INK, width=2)
    f = font(SANS, 11)
    line = ("Compiled from wire reports published Sunday 22 November 2026 · "
            "Reuters · AP · AFP · CNN · Al Jazeera · UN OCHA · IANS · TBS News")
    lw = d.textlength(line, font=f)
    d.text(((W - lw) / 2, 984), line, font=f, fill=FAINT)


def main():
    W = H = 1024
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d, W)
    hero(d, W)
    grid_row(d, W, 482, 156, ROW1)
    grid_row(d, W, 650, 156, ROW2)
    cw = grid_row(d, W, 818, 144, ROW3)
    figures_box(d, 28 + 3 * (cw + 14), 818, cw, 144)
    footer(d, W)
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
