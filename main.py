"""The World Today - 20 November 2026. One image, 30 stories.

Draws a 1024x1024 newspaper front page with PIL only. Deterministic:
no randomness, no timestamps, no network. Run twice, same bytes.
Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py  -> out/entry.png
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
GREY = (107, 107, 107)
OCEAN = (207, 227, 242)
LAND = (203, 185, 138)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, fnt, max_w, max_lines, min_size, path):
    """Wrap text; shrink font until it fits max_lines, else raise."""
    size = fnt.size
    while size >= min_size:
        f = font(path, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    raise SystemExit("TEXT OVERFLOW: %r needs %d lines" % (text, len(lines)))


STORIES = [
    dict(n=1, kicker="SUMMIT / SHENZHEN",
         head="Three presidents, one table",
         summ="Trump, Xi and Putin meet for the first time in Shenzhen "
              "— Ukraine, nuclear arms and trade on the table.",
         pin=(114.1, 22.5), pastel=(253, 232, 216), illo="summit"),
    dict(n=2, kicker="WAR / TEHRAN",
         head="Trump: no rush on Iran",
         summ="The US president pushes any Iran war decision to 2027: "
              "“We’ll see what happens” after Jan 1.",
         pin=(51.4, 35.7), pastel=(226, 232, 240), illo="clock"),
    dict(n=3, kicker="MARKETS / NEW YORK",
         head="Anthropic’s $2tn flash, then the fall",
         summ="ANT opens at $111.50, closes $97.17; the Dow sinks 1,101 "
              "points as the Nasdaq drops 2.25%.",
         pin=(-74.0, 40.7), pastel=(220, 252, 231), illo="chart"),
    dict(n=4, kicker="WAR / RIYADH",
         head="Missile scars Riyadh’s tallest tower",
         summ="A Houthi strike damages the 80-storey PIF Tower, home of "
              "the $900bn wealth fund; no injuries.",
         pin=(46.7, 24.7), pastel=(254, 243, 199), illo="tower"),
    dict(n=5, kicker="ENERGY / WORLD",
         head="Hormuz: “largest energy shock ever”",
         summ="The IEA says the Strait crisis is the biggest energy "
              "supply shock in history; Brent holds near $89.",
         pin=(56.5, 26.6), pastel=(219, 234, 254), illo="tanker"),
    dict(n=6, kicker="SPACE / DEEP SPACE",
         head="Voyager 1, a light-day away",
         summ="NASA confirms the 49-year-old probe has reached one "
              "light-day from Earth — and still phones home.",
         pin=(-118.2, 34.2), pastel=(237, 233, 254), illo="dish"),
    dict(n=7, kicker="WEATHER / ODISHA",
         head="Cyclone Akvan bears down",
         summ="300,000 evacuated in Odisha as the cyclone nears landfall; "
              "423 rescue teams deployed.",
         pin=(85.8, 20.3), pastel=(207, 250, 254), illo="storm"),
    dict(n=8, kicker="COURT / THE HAGUE",
         head="Myanmar guilty of genocide",
         summ="The UN’s top court rules Myanmar committed genocide "
              "against the Rohingya minority.",
         pin=(4.3, 52.1), pastel=(252, 231, 243), illo="scales"),
    dict(n=9, kicker="GAMES / WORLD",
         head="GTA 6 passes $1.8bn in sales",
         summ="Rockstar’s epic has already outsold The Odyssey’s global "
              "run; early reviews put it at 99 on Metacritic.",
         pin=(174.8, -36.8), pastel=(236, 252, 203), illo="city"),
    dict(n=10, kicker="DIPLOMACY / BERLIN",
         head="Europe seeks a Russia talks seat",
         summ="Leaders meet in Berlin to press for a place at Ukraine "
              "peace talks — and to fund Kyiv.",
         pin=(13.4, 52.5), pastel=(255, 237, 213), illo="table"),
]

ALSO = [
    "Hayabusa2 engine trouble ends asteroid landing plan",
    "Nvidia halts H200 chip shipments to China",
    "Fed minutes point to more rate hikes ahead",
    "Hang Seng −2.78%, FTSE 100 −1.3% on AI fears",
    "Seoul court clears ex-PM Han over martial law",
    "Fiji declares national disaster as drought bites",
    "North Korea expands Yongbyon enrichment site",
    "US and Venezuela restore military cooperation",
    "Ukraine hits Crimean Bridge; trains halted",
    "Modi meets the Prince and Princess of Wales",
    "Nicholls 113* as NZ reach 243/5 vs India",
    "Sensex +1.21% to 83,022; Nifty past 25,500",
    "Fire at Yunus ancestral home in Bangladesh",
    "Hamas planner of Oct 7 attacks killed by IDF",
    "Trump lands in Manila for Quad summit",
    "SpaceX Starship caught by launch pad",
    "US officials grilled over tech outages",
    "Japan PM Takaichi seeks dialogue with China",
    "Australia sanctions Israeli West Bank settlers",
    "APEC leaders talk trade as Xi urges openness",
]

TICKER = ("DOW 49,097  −2.2%    •    S&P 500  −2.0%    •    NASDAQ  −2.25%    •    "
          "BRENT $89    •    HANG SENG  −2.78%    •    FTSE 100  −1.3%    •    "
          "SENSEX  +1.21%")


# ---- flat illustrations (all drawn with PIL shapes, no photos) ----

def _rr(d, box, fill):
    d.rounded_rectangle(box, radius=8, fill=fill)


def illo_summit(d, x, y):
    # three flags over a table
    for i, c in enumerate([(185, 28, 28), (30, 58, 95), (21, 128, 61)]):
        px = x + 10 + i * 20
        d.line([px + 6, y + 14, px + 6, y + 52], fill=INK, width=2)
        d.rectangle([px + 6, y + 14, px + 20, y + 26], fill=c)
    d.rectangle([x + 8, y + 52, x + 64, y + 58], fill=INK)


def illo_clock(d, x, y):
    d.ellipse([x + 16, y + 10, x + 56, y + 50], outline=INK, width=3,
              fill=WHITE)
    d.line([x + 36, y + 30, x + 36, y + 16], fill=INK, width=2)
    d.line([x + 36, y + 30, x + 48, y + 36], fill=INK, width=2)
    d.ellipse([x + 33, y + 27, x + 39, y + 33], fill=RED)
    d.rectangle([x + 12, y + 58, x + 60, y + 64], fill=GREY)


def illo_chart(d, x, y):
    bars = [(14, 22, (21, 128, 61)), (28, 34, (21, 128, 61)),
            (42, 46, (21, 128, 61)), (56, 26, (185, 28, 28))]
    for bx, bh, c in bars:
        d.rectangle([x + bx, y + 58 - bh, x + bx + 8, y + 58], fill=c)
    d.line([x + 10, y + 58, x + 62, y + 58], fill=INK, width=2)


def illo_tower(d, x, y):
    d.rectangle([x + 26, y + 8, x + 46, y + 60], fill=NAVY)
    for wy in (16, 26, 36, 46):
        d.rectangle([x + 30, y + wy, x + 42, y + wy + 4], fill=(207, 227, 242))
    d.polygon([(x + 26, y + 8), (x + 36, y + 2), (x + 46, y + 8)], fill=RED)
    for dx, dy in ((-14, -8), (14, -8), (-16, 6), (16, 6)):
        d.line([x + 36 + dx, y + 20 + dy, x + 36, y + 20], fill=RED, width=2)
    d.rectangle([x + 12, y + 60, x + 60, y + 64], fill=INK)


def illo_tanker(d, x, y):
    d.polygon([(x + 10, y + 40), (x + 62, y + 40), (x + 56, y + 52),
               (x + 16, y + 52)], fill=(120, 53, 15))
    for i, c in enumerate([(185, 28, 28), (30, 58, 95), (21, 128, 61)]):
        d.rectangle([x + 14 + i * 14, y + 28, x + 24 + i * 14, y + 40], fill=c)
    for wx in (8, 26, 44):
        d.arc([x + wx, y + 54, x + wx + 16, y + 64], 0, 180, fill=NAVY, width=2)


def illo_dish(d, x, y):
    for sx, sy in ((12, 12), (58, 10), (52, 52), (16, 54), (36, 8)):
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=INK)
    d.arc([x + 14, y + 18, x + 58, y + 56], 300, 60, fill=NAVY, width=4)
    d.line([x + 36, y + 38, x + 52, y + 58], fill=INK, width=3)
    d.line([x + 36, y + 38, x + 20, y + 58], fill=INK, width=3)
    for i in range(4):
        d.ellipse([x + 56 - i * 4, y + 12 + i * 4, x + 59 - i * 4,
                   y + 15 + i * 4], fill=RED)


def illo_storm(d, x, y):
    for r in (26, 18, 10):
        d.arc([x + 36 - r, y + 30 - r, x + 36 + r, y + 30 + r],
              200, 200 + 260, fill=NAVY, width=3)
    for dx in (-18, -6, 6, 18):
        d.line([x + 36 + dx, y + 54, x + 34 + dx, y + 62], fill=NAVY, width=2)


def illo_scales(d, x, y):
    d.line([x + 36, y + 12, x + 36, y + 52], fill=INK, width=3)
    d.line([x + 14, y + 16, x + 58, y + 16], fill=INK, width=3)
    for cx in (16, 56):
        d.line([x + cx, y + 16, x + cx, y + 30], fill=INK, width=2)
        d.polygon([(x + cx - 9, y + 30), (x + cx + 9, y + 30),
                   (x + cx, y + 42)], fill=RED)
    d.rectangle([x + 28, y + 52, x + 44, y + 58], fill=INK)
    d.rectangle([x + 20, y + 58, x + 52, y + 62], fill=INK)


def illo_city(d, x, y):
    d.ellipse([x + 44, y + 8, x + 62, y + 26], fill=(234, 179, 8))
    for bx, bw, bh in ((8, 12, 34), (22, 10, 46), (34, 12, 28), (48, 10, 40)):
        d.rectangle([x + bx, y + 58 - bh, x + bx + bw, y + 58], fill=NAVY)
    d.rectangle([x + 8, y + 58, x + 64, y + 62], fill=INK)


def illo_table(d, x, y):
    d.ellipse([x + 10, y + 30, x + 62, y + 44], fill=(120, 53, 15))
    d.rectangle([x + 16, y + 44, x + 20, y + 60], fill=INK)
    d.rectangle([x + 52, y + 44, x + 56, y + 60], fill=INK)
    for fx, c in ((16, (185, 28, 28)), (36, (30, 58, 95)), (54, (21, 128, 61))):
        d.ellipse([x + fx - 5, y + 18, x + fx + 5, y + 28], fill=c)


ILLOS = {"summit": illo_summit, "clock": illo_clock, "chart": illo_chart,
         "tower": illo_tower, "tanker": illo_tanker, "dish": illo_dish,
         "storm": illo_storm, "scales": illo_scales, "city": illo_city,
         "table": illo_table}

# Simplified continent outlines, equirectangular (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-75, 62), (-70, 45), (-75, 35), (-80, 25), (-85, 30),
     (-90, 21), (-97, 26), (-105, 20), (-110, 23), (-120, 34), (-125, 48),
     (-135, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -15), (-40, -25), (-50, -30), (-60, -35), (-70, -40),
     (-72, -50), (-70, -55), (-75, -45), (-80, -30), (-80, -15), (-80, 5)],
    [(-10, 36), (-5, 44), (0, 50), (5, 55), (10, 58), (15, 60), (20, 65),
     (25, 70), (30, 70), (35, 65), (40, 60), (35, 55), (30, 50), (25, 45),
     (20, 40), (15, 38), (10, 38), (5, 40), (0, 38), (-5, 36)],
    [(-10, 35), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 20),
     (45, 11), (50, 10), (48, 0), (42, -10), (38, -20), (32, -28),
     (25, -33), (18, -35), (12, -25), (10, -15), (8, 0), (0, 5), (-8, 5),
     (-15, 12), (-17, 20), (-15, 28)],
    [(40, 70), (60, 72), (80, 73), (100, 76), (120, 76), (140, 72),
     (160, 70), (170, 66), (178, 65), (170, 60), (162, 55), (158, 50),
     (150, 45), (140, 40), (135, 35), (130, 33), (127, 35), (122, 38),
     (120, 30), (115, 22), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (85, 20), (80, 15), (75, 10), (72, 20), (68, 25), (60, 25),
     (55, 28), (50, 30), (48, 35), (45, 40), (42, 45), (40, 50), (42, 55),
     (45, 60), (40, 65)],
    [(113, -22), (122, -15), (130, -12), (136, -12), (142, -11),
     (146, -15), (150, -22), (153, -28), (150, -37), (140, -38),
     (132, -32), (124, -33), (115, -35), (113, -26)],
    [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-40, 78), (-55, 75),
     (-58, 70), (-55, 62)],
]


# ---- page assembly ----

def draw_cell(d, s, x, y, w, h):
    n = s["n"]
    # number badge
    d.ellipse([x + 1, y + 5, x + 27, y + 31], fill=RED)
    nb = font(F_BOLD, 15)
    t = str(n)
    d.text((x + 14 - d.textlength(t, font=nb) / 2, y + 9), t,
           font=nb, fill=WHITE)
    # illustration
    ix, iy = x + 34, y + 8
    _rr(d, [ix, iy, ix + 72, iy + 72], s["pastel"])
    ILLOS[s["illo"]](d, ix, iy)
    # text block
    tx, tw = x + 116, w - 116 - 8
    kf = font(F_BOLD, 10)
    d.text((tx, y + 8), s["kicker"], font=kf, fill=RED)
    hf, hl = fit_lines(d, s["head"], font(F_BOLD, 15), tw, 2, 11, F_BOLD)
    yy = y + 23
    for line in hl:
        d.text((tx, yy), line, font=hf, fill=INK)
        yy += 18
    sf, sl = fit_lines(d, s["summ"], font(F_REG, 12), tw, 2, 10, F_REG)
    yy += 2
    for line in sl:
        d.text((tx, yy), line, font=sf, fill=INK)
        yy += 15


def draw_map(d):
    mx0, my0, mw, mh = 24, 680, 976, 130
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=OCEAN)
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], outline=INK, width=1)

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (75 - lat) / 130 * mh)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(160, 140, 90))
    # pins: nudge apart when centres would collide (<30 px)
    placed = []
    pf = font(F_BOLD, 11)
    for s in STORIES:
        px, py = proj(*s["pin"])
        qx, qy = px, py
        for dx, dy in [(0, 0), (30, 0), (-30, 0), (0, 30), (0, -30),
                       (30, 30), (-30, 30), (30, -30), (-30, -30),
                       (44, 0), (-44, 0), (0, 44), (44, 22), (-44, 22)]:
            cx, cy = px + dx, py + dy
            if all((cx - ax) ** 2 + (cy - ay) ** 2 >= 30 ** 2
                   for ax, ay in placed):
                qx, qy = cx, cy
                break
        placed.append((qx, qy))
        if (qx, qy) != (px, py):
            d.line([qx, qy, px, py], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([qx - 11, qy - 11, qx + 11, qy + 11], fill=RED,
                  outline=WHITE, width=2)
        t = str(s["n"])
        d.text((qx - d.textlength(t, font=pf) / 2, qy - 8), t,
               font=pf, fill=WHITE)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=6)

    # masthead
    tf = font(F_BOLD, 54)
    title = "THE WORLD TODAY"
    d.text(((W - d.textlength(title, font=tf)) / 2, 20), title,
           font=tf, fill=INK)
    df = font(F_BOLD, 20)
    date = "FRIDAY, 20 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=df)) / 2, 88), date,
           font=df, fill=INK)
    d.line([24, 114, 1000, 114], fill=INK, width=2)

    # red banner
    d.rectangle([24, 120, 1000, 146], fill=RED)
    bf = font(F_BOLD, 19)
    ban = "30 STORIES  •  6 CONTINENTS  •  ONE PAGE"
    d.text(((W - d.textlength(ban, font=bf)) / 2, 123), ban,
           font=bf, fill=WHITE)

    # markets ticker
    d.rectangle([24, 152, 1000, 174], fill=NAVY)
    tk = font(F_REG, 13)
    if d.textlength(TICKER, font=tk) > 968:
        tk = font(F_REG, 12)
    d.text(((W - d.textlength(TICKER, font=tk)) / 2, 156), TICKER,
           font=tk, fill=WHITE)

    # main stories grid: 2 cols x 5 rows
    cols = [24, 528]
    for i, s in enumerate(STORIES):
        x = cols[i % 2]
        y = 182 + (i // 2) * 96
        draw_cell(d, s, x, y, 472, 88)

    # map strip
    mf = font(F_BOLD, 15)
    d.text((24, 662), "WHERE IT HAPPENED", font=mf, fill=INK)
    draw_map(d)

    # also on this day
    af = font(F_BOLD, 15)
    d.text((24, 820), "ALSO ON THIS DAY", font=af, fill=INK)
    d.line([24, 840, 1000, 840], fill=RED, width=2)
    lf = font(F_REG, 12)
    for i, item in enumerate(ALSO):
        col = i // 10
        row = i % 10
        x = 24 if col == 0 else 528
        y = 848 + row * 13
        line = "•  " + item
        if d.textlength(line, font=lf) > 468:
            raise SystemExit("ALSO OVERFLOW: %r" % item)
        d.text((x, y), line, font=lf, fill=INK)

    # footer
    ff = font(F_REG, 11)
    f1 = ("Sources: Reuters  •  BBC  •  Bloomberg  •  Financial Times  •  AP  •  "
          "The Hindu  •  WSJ — 20 Nov 2026. Illustrations are original flat "
          "drawings; no photographs.")
    d.text(((W - d.textlength(f1, font=ff)) / 2, 984), f1, font=ff, fill=GREY)
    f2 = "Every story happened, or was first reported, on Friday 20 November 2026."
    d.text(((W - d.textlength(f2, font=ff)) / 2, 999), f2, font=ff, fill=GREY)
    return img


def main():
    img = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    img.save(path, "PNG")
    print("wrote %s (%dx%d)" % (path, W, H))


if __name__ == "__main__":
    main()
