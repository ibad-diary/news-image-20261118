#!/usr/bin/env python3
"""Render entry.png (1024x1024) for make.fun news-image-20261118.

Reads stories.json next to this file and draws a newspaper front page:
masthead, a big date line, and seven stories, each with a region tag,
a one-line headline and a two-line summary. Layout is measured first:
font sizes shrink step by step until every story fits above the footer,
so text can never overlap. Only Pillow + stdlib are used.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (168, 32, 26)
MUTED = (90, 86, 78)
RULE = (150, 145, 132)
TAG_BG = (18, 18, 18)
TAG_FG = (250, 247, 238)
ACCENT = (36, 68, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, width, max_lines=None):
    """Greedy word wrap; optionally cap lines, adding an ellipsis."""
    lines = []
    line = ""
    for word in text.split(" "):
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1] + " ..."
    return lines


def measure_stories(draw, stories, f_head, f_sum, width):
    """Return per-story (headline lines, summary lines) and total height."""
    total = 0
    laid = []
    for s in stories:
        hl = wrap(draw, s["headline"], f_head, width, max_lines=1)
        sm = wrap(draw, s["summary"], f_sum, width, max_lines=2)
        laid.append((hl, sm))
        total += 22 + 4 + len(hl) * (f_head.size + 4) + len(sm) * (f_sum.size + 4) + 8
    return laid, total


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font("DejaVuSerif-Bold.ttf", 54)
    f_date = font("DejaVuSans-Bold.ttf", 40)
    f_sub = font("DejaVuSans.ttf", 22)
    f_tag = font("DejaVuSans-Bold.ttf", 16)
    f_foot = font("DejaVuSans.ttf", 15)

    margin = 46
    x0 = margin
    x1 = W - margin
    width = x1 - x0

    # ---- Masthead ----
    y = 22
    d.text((W // 2, y), data["title"], font=f_title, fill=INK, anchor="ma")
    y += 66
    d.text((W // 2, y), data["subtitle"], font=f_sub, fill=MUTED, anchor="ma")
    y += 36
    d.line([(x0, y), (x1, y)], fill=INK, width=3)
    y += 10

    # ---- Big date line ----
    d.text((W // 2, y), data["date_label"], font=f_date, fill=RED, anchor="ma")
    y += 54
    d.line([(x0, y), (x1, y)], fill=INK, width=3)
    y += 14

    stories_top = y
    footer_top = H - 58
    avail = footer_top - stories_top

    # ---- Auto-fit: shrink headline/summary fonts until all stories fit ----
    head_size, sum_size = 25, 18
    while True:
        f_head = font("DejaVuSans-Bold.ttf", head_size)
        f_sum = font("DejaVuSans.ttf", sum_size)
        laid, total = measure_stories(d, data["stories"], f_head, f_sum, width)
        if total <= avail or (head_size <= 20 and sum_size <= 15):
            break
        head_size -= 1
        sum_size -= 1
    print("fit: headline", head_size, "summary", sum_size,
          "total", total, "avail", avail)

    # ---- Stories ----
    y = stories_top
    for i, story in enumerate(data["stories"]):
        hl, sm = laid[i]
        top = y
        tag = story["tag"]
        tw = d.textlength(tag, font=f_tag) + 18
        th = 22
        d.rounded_rectangle([x0, top, x0 + tw, top + th], radius=4, fill=TAG_BG)
        d.text((x0 + 9, top + 2), tag, font=f_tag, fill=TAG_FG)
        d.text((x1, top + 0), str(story["n"]),
               font=font("DejaVuSans-Bold.ttf", 22), fill=ACCENT, anchor="ra")

        ty = top + th + 4
        for line in hl:
            d.text((x0, ty), line, font=f_head, fill=INK)
            ty += head_size + 4
        for line in sm:
            d.text((x0, ty), line, font=f_sum, fill=(52, 50, 46))
            ty += sum_size + 4
        y = ty + 8
        if i < len(data["stories"]) - 1:
            d.line([(x0, y - 4), (x1, y - 4)], fill=RULE, width=1)

    # ---- Footer ----
    d.line([(x0, footer_top), (x1, footer_top)], fill=INK, width=2)
    d.text((W // 2, footer_top + 8), data["footer"], font=f_foot,
           fill=MUTED, anchor="ma")
    d.text((W // 2, footer_top + 28),
           "Sources: Reuters  ·  AP  ·  PAHO  ·  WHO/UN News  ·  CNN  ·  "
           "TechCrunch  ·  Times of India  ·  Horizon",
           font=f_foot, fill=MUTED, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
