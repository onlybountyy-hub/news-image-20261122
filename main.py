#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026.

Draws a deterministic 1024x1024 front-page poster of the day's world news
with the Python 3.13 standard library only (no PIL, no network, no fonts
from disk: a built-in 5x7 bitmap font). Writes /output/entry.png
(MAKEFUN_OUTPUT_DIR when set). Running it twice produces byte-identical
output: no timestamps, no randomness, fixed zlib level.

Lineup from the verified sources file (~/workspace/makefun/
news-image-20261122-SOURCES.md, research pass ~07:00 WIB 22 Nov),
with two build-time re-checks done by the builder:
- COP31 updated to the Sunday package text (Reuters: new text tabled
  early Sunday, presidency says all parties can agree, plenary to
  approve Sunday morning).
- Trump/Iran (NYT) second-sourced via InvestingLive + Cumhuriyet;
  Trump/Europe call second-sourced via Telegraph + Politico/WaPo
  (call was Thu 19 Nov; White House disputes the "halt" reading);
  Gaza 129 remains second-sourced via Gaza Civil Defense wire
  mirrors (announced Sat 21 Nov, central Gaza).
- Voyager 1 DROPPED: NASA confirms the milestone but it was
  18 Nov (confirmed 19 Nov) - four days old, not 22 Nov news.
- Date traps rejected: ICJ Myanmar ruling (19 Nov), Russian missiles
  on Poland (21 Nov edition's hero), Peru Junin quake (same event as
  the 21 Nov grid item), Anthropic IPO (19 Nov), BepiColombo (21 Nov).
Hero: the Kryvyi Rih double-tap (Fri night 20 Nov, first reported
21 Nov by AP/CNN) - the war story of the weekend, per the sources
file. Sunday-dated items (COP31 package, Hong Kong vote, Myanmar
quake) are front-loaded in the grid.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (178, 34, 28)
TEAL = (14, 74, 90)
TEAL_LT = (24, 104, 122)
GOLD = (212, 160, 32)
WHITE = (255, 255, 255)
GREY = (110, 108, 100)
BLUE = (28, 68, 140)
GREEN = (34, 110, 64)
ORANGE = (196, 94, 20)
PURPLE = (96, 58, 140)
BROWN = (122, 74, 40)
STEEL = (70, 96, 120)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 characters; '#' is ink, '.' is blank.
# Uppercase only (newspaper style), digits and common punctuation.
FONT = {
    'A': ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ':': (".....", ".....", ".##..", ".....", ".##..", ".....", "....."),
    ';': (".....", ".....", ".##..", ".....", ".##..", ".#...", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': ("#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}
SPACE_W = 6  # glyph advance in font units (5 + 1 gap)


def text_w(s, scale):
    """Width in pixels of string s at the given scale."""
    return len(s) * SPACE_W * scale


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            n = (x1 - x0) * 3
            self.px[i:i + n] = bytes(c) * (x1 - x0)

    def hline(self, x0, x1, y, c, t=1):
        self.rect(x0, y, x1, y + t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.rect(x, y0, x + t, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        """Draw uppercase text; unknown chars become spaces."""
        cx = x
        for ch in s:
            g = FONT.get(ch, None)
            if g is None:
                cx += SPACE_W * scale
                continue
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale, y + (row + 1) * scale, c)
            cx += SPACE_W * scale

    def text_center(self, y, s, scale, c):
        self.text((self.w - text_w(s, scale)) // 2, y, s, scale, c)


def png_bytes(cv):
    """Encode the canvas as a deterministic PNG (no ancillary chunks)."""
    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        return out + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', idat) + chunk(b'IEND', b''))


# ------------------------------------------------------------------- icons
def icon(cv, kind, x, y, s, c):
    """Small pictogram drawn in a s x s box at (x, y)."""
    if kind == 'globe':
        cv.circle(x + s // 2, y + s // 2, s // 2 - 2, c)
        cv.line(x + 4, y + s // 2, x + s - 4, y + s // 2, c, 2)
        cv.line(x + s // 2, y + 4, x + s // 2, y + s - 4, c, 2)
    elif kind == 'vote':
        cv.rect(x + 6, y + s - 16, x + s - 6, y + s - 6, c)
        cv.line(x + 6, y + s - 16, x + s // 2, y + 8, c, 3)
        cv.line(x + s // 2, y + 8, x + s - 6, y + s - 16, c, 3)
    elif kind == 'quake':
        cv.line(x + 2, y + s // 2, x + s // 3, y + 6, c, 3)
        cv.line(x + s // 3, y + 6, x + 2 * s // 3, y + s - 8, c, 3)
        cv.line(x + 2 * s // 3, y + s - 8, x + s - 2, y + s // 2, c, 3)
    elif kind == 'shield':
        cv.line(x + s // 2, y + 4, x + s - 4, y + 12, c, 3)
        cv.line(x + s - 4, y + 12, x + s - 4, y + s // 2, c, 3)
        cv.line(x + s - 4, y + s // 2, x + s // 2, y + s - 4, c, 3)
        cv.line(x + s // 2, y + s - 4, x + 4, y + s // 2, c, 3)
        cv.line(x + 4, y + s // 2, x + 4, y + 12, c, 3)
        cv.line(x + 4, y + 12, x + s // 2, y + 4, c, 3)
    elif kind == 'boat':
        cv.line(x + 4, y + s - 12, x + s - 4, y + s - 12, c, 3)
        cv.line(x + 8, y + s - 12, x + s - 8, y + s - 4, c, 3)
        cv.line(x + s // 2, y + s - 12, x + s // 2, y + 6, c, 3)
        cv.line(x + s // 2, y + 6, x + s - 8, y + s - 12, c, 3)
    elif kind == 'wall':
        for r in range(3):
            for col in range(3):
                cv.rect(x + 4 + col * 12 + (r % 2) * 6, y + 6 + r * 12,
                        x + 4 + col * 12 + (r % 2) * 6 + 10, y + 6 + r * 12 + 10, c)
    elif kind == 'talks':
        cv.rect(x + 4, y + 8, x + s // 2 + 6, y + s // 2 + 4, c)
        cv.rect(x + s // 2 - 2, y + s // 2 - 2, x + s - 4, y + s - 8, c)
    elif kind == 'flag':
        cv.vline(x + 6, y + 4, y + s - 4, c, 3)
        cv.line(x + 6, y + 4, x + s - 6, y + 10, c, 3)
        cv.line(x + s - 6, y + 10, x + 6, y + 18, c, 3)
    elif kind == 'plane':
        cv.line(x + 4, y + s // 2, x + s - 4, y + s // 2, c, 3)
        cv.line(x + s // 2, y + 6, x + s // 2 + 6, y + s // 2, c, 3)
        cv.line(x + s // 2, y + s - 6, x + s // 2 + 6, y + s // 2, c, 3)
        cv.line(x + s - 10, y + s // 2 - 8, x + s - 4, y + s // 2, c, 3)
    elif kind == 'bridge':
        cv.line(x + 4, y + s - 10, x + s // 2, y + 6, c, 3)
        cv.line(x + s // 2, y + 6, x + s - 4, y + s - 10, c, 3)
        cv.hline(x + 2, x + s - 2, y + s - 10, c, 3)
    elif kind == 'storm':
        cv.circle(x + 14, y + 12, 8, c, fill=True)
        cv.circle(x + 24, y + 14, 10, c, fill=True)
        cv.line(x + 20, y + 22, x + 14, y + s - 6, c, 3)
        cv.line(x + 14, y + s - 6, x + 20, y + s - 6, c, 3)
        cv.line(x + 20, y + s - 6, x + 16, y + s - 12, c, 3)


# ------------------------------------------------------------------ stories
# (kicker, colour, headline lines, deck, icon)
# Headline lines <= 16 chars (scale 3 = 18 px/char, tile inner 298 px);
# deck wraps to <= 2 lines at 24 chars/line (scale 2).
GRID = [
    ("CLIMATE", TEAL, ["COP31 NEARS", "A DEAL"],
     "NEW PACKAGE TEXT TABLED EARLY SUNDAY.", 'globe'),
    ("HONG KONG", RED, ["HONG KONG", "VOTES"],
     "856 CANDIDATES, 723 SEATS, ONE COMMITTEE.", 'vote'),
    ("MYANMAR", ORANGE, ["QUAKE HITS", "MYANMAR"],
     "M4.1 TREMOR IN THE EARLY HOURS.", 'quake'),
    ("MEXICO", RED, ["EL CHAPO", "ISIDRO HELD"],
     "FBI TOP-10 BOSS SEIZED IN SINALOA.", 'shield'),
    ("BALTIC SEA", STEEL, ["SHIP ABLAZE", "AT SEA"],
     "RUSSIAN CARGO SHIP HIT BY DRONES.", 'boat'),
    ("USA", BLUE, ["TRUMP WEIGHS", "IRAN STRIKES"],
     "ISRAEL PRESSES FOR 4-7 DAY CAMPAIGN.", 'flag'),
    ("EUROPE", PURPLE, ["STOP FUNDING", "UKRAINE"],
     "TRUMP'S ANGRY CALL AFTER SUMMIT.", 'talks'),
    ("GAZA", BROWN, ["129 BODIES", "FROM RUBBLE"],
     "39 HOMES SEARCHED IN CENTRAL GAZA.", 'wall'),
    ("UKRAINE", BLUE, ["NATO IS THE", "GUARANTEE"],
     "ZELENSKYY: ALLIANCE IS THE SHIELD.", 'shield'),
    ("ISRAEL", GREEN, ["COALITION", "TALKS"],
     "EISENKOT INVITES LIKUD TO TABLE.", 'talks'),
    ("KYIV", STEEL, ["KYIV HIT", "OVERNIGHT"],
     "3 KILLED, BRIDGES DAMAGED, POWER CUT.", 'storm'),
]

NUMBERS = [
    "2 / 60 KRYVYI RIH",
    "11 KILLED IN SINALOA",
    "$5M EL CHAPO REWARD",
    "0 FOSSIL FUELS IN DRAFT",
    "35% POWER BY 2035",
    "M4.1 MYANMAR QUAKE",
]


def build():
    cv = Canvas(W, H, PAPER)

    # ------------------------------------------------------------ masthead
    cv.text_center(16, "SUNDAY 22 NOVEMBER 2026", 2, INK)
    cv.text_center(42, "THE WORLD TODAY", 9, INK)
    cv.rect(24, 118, W - 24, 123, RED)
    cv.rect(24, 127, W - 24, 129, INK)

    # ---------------------------------------------------------------- hero
    cv.rect(24, 136, W - 24, 440, TEAL)
    cv.rect(24, 136, W - 24, 140, GOLD)
    # globe motif
    gx, gy, gr = 168, 294, 102
    cv.circle(gx, gy, gr, WHITE)
    cv.circle(gx, gy, gr - 14, GOLD)
    cv.line(gx - gr, gy, gx + gr, gy, WHITE, 3)
    cv.line(gx, gy - gr, gx, gy + gr, WHITE, 3)
    cv.circle(gx, gy, gr // 2, WHITE)
    cv.line(gx - 60, gy - 58, gx + 60, gy + 58, GOLD, 3)
    cv.line(gx + 60, gy - 58, gx - 60, gy + 58, GOLD, 3)
    # hero text
    tx = 316
    cv.text(tx, 168, "UKRAINE - KRYVYI RIH", 2, GOLD)
    cv.text(tx, 200, "DOUBLE-TAP", 5, WHITE)
    cv.text(tx, 240, "ON KRYVYI RIH", 5, WHITE)
    deck = ("TWO MISSILES HIT ZELENSKYY'S HOMETOWN ON FRIDAY NIGHT. AS "
            "RESCUERS RUSHED IN, DRONES STRUCK AGAIN. A BOY OF 7 AND A "
            "PARAMEDIC OF 20 ARE DEAD; 60 WOUNDED.")
    y = 306
    for ln in wrap(deck, 660, 2):
        cv.text(tx, y, ln, 2, WHITE)
        y += 22
    cv.text(tx, y + 8, "28 STILL IN HOSPITAL, 5 IN INTENSIVE CARE.", 2, GOLD)

    # ---------------------------------------------------------------- grid
    x0, gap, cw = 24, 10, 318
    y0, rh = 452, 116
    for i, (kick, col, head, deck, ic) in enumerate(GRID):
        r, c = divmod(i, 3)
        x, y = x0 + c * (cw + gap), y0 + r * (rh + gap)
        cv.rect(x, y, x + cw, y + rh, WHITE)
        cv.rect(x, y, x + cw, y + 2, INK)
        cv.rect(x, y + rh - 2, x + cw, y + rh, INK)
        cv.rect(x, y, x + 2, y + rh, INK)
        cv.rect(x + cw - 2, y, x + cw, y + rh, INK)
        cv.rect(x + 2, y + 2, x + cw - 2, y + 26, col)
        cv.text(x + 10, y + 9, kick, 2, WHITE)
        icon(cv, ic, x + cw - 52, y + 32, 40, col)
        hy = y + 36
        for ln in head:
            cv.text(x + 10, hy, ln, 3, INK)
            hy += 22
        dy = y + rh - 36
        for ln in wrap(deck, cw - 20, 2)[:2]:
            cv.text(x + 10, dy, ln, 2, GREY)
            dy += 16

    # numbers tile (12th slot)
    r, c = 3, 2
    x, y = x0 + c * (cw + gap), y0 + r * (rh + gap)
    cv.rect(x, y, x + cw, y + rh, INK)
    cv.text(x + 10, y + 9, "THE DAY IN NUMBERS", 2, GOLD)
    ny = y + 28
    for ln in NUMBERS:
        cv.text(x + 10, ny, ln, 2, WHITE)
        ny += 14

    # -------------------------------------------------------------- footer
    cv.rect(0, 958, W, H, INK)
    cv.text(24, 974, "ALSO TODAY: JAPAN TO HOLD LIVE-FIRE DRILLS IN INDIA, A FIRST", 2, WHITE)
    cv.text(24, 996, "CUMMINS KEEPS AUSTRALIA'S TEST CAPTAINCY - CHAHAL JOINS BJP - OIL FALLS 3%+", 2, GOLD)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (os.path.join(out_dir, "entry.png"), len(data)))


if __name__ == "__main__":
    main()
