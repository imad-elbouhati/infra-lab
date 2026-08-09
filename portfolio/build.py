#!/usr/bin/env python3
"""
Build the portfolio page.

Takes src/page.html (markup + CSS, with a __FONTS__ placeholder), subsets each
font to only the glyphs the page actually uses, converts it to WOFF2, inlines it
as a data URI, and writes a standalone self-contained index.html.

    pip install fonttools brotli
    python3 build.py --fonts /path/to/ttf-directory

The font directory must contain the TTFs listed in FACES below. All six are
open-source (SIL OFL): Bricolage Grotesque, Instrument Sans and Geist Mono.
"""
import argparse
import base64
import html
import io
import pathlib
import re

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

HERE = pathlib.Path(__file__).resolve().parent

FACES = [
    ("Bricolage Grotesque", "BricolageGrotesque-Bold.ttf", 700, "normal"),
    ("Instrument Sans",     "InstrumentSans-Regular.ttf",  400, "normal"),
    ("Instrument Sans",     "InstrumentSans-Bold.ttf",     700, "normal"),
    ("Instrument Sans",     "InstrumentSans-Italic.ttf",   400, "italic"),
    ("Geist Mono",          "GeistMono-Regular.ttf",       400, "normal"),
    ("Geist Mono",          "GeistMono-Bold.ttf",          700, "normal"),
]

TITLE = "Imad El Bouhati — DevOps &amp; SRE Engineer"
DESC = (
    "Freelance DevOps and SRE engineer. Kubernetes operators in Go, "
    "Terraform-managed AWS, and Ansible-automated Linux infrastructure — "
    "every claim backed by public source code."
)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Imad El Bouhati">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='%230B1116'/><text y='23' x='16' text-anchor='middle' font-family='monospace' font-size='19' font-weight='700' fill='%23E3B05A'>I</text></svg>">
<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}img{{max-width:100%}}</style>
</head>
<body>
{body}
</body>
</html>
"""


def needed_glyphs(markup):
    """Printable ASCII + Latin-1, plus every character the page actually uses."""
    visible = re.sub(r"<style>.*?</style>|<script>.*?</script>|<!--.*?-->", "", markup, flags=re.S)
    visible = html.unescape(re.sub(r"<[^>]+>", " ", visible))
    charset = {chr(c) for c in range(0x20, 0x7F)}
    charset |= {chr(c) for c in range(0xA0, 0x100)}
    charset |= set(visible)
    return {c for c in charset if c.isprintable() or c == " "}


def face_css(font_dir, family, filename, weight, style, charset, quiet=False):
    src = font_dir / filename
    if not src.exists():
        raise SystemExit("missing font: %s\n(pass --fonts <dir> containing the TTFs)" % src)

    font = TTFont(src)
    opts = Options()
    opts.layout_features = ["kern", "liga", "calt", "tnum", "ccmp", "locl", "mark", "mkmk"]
    opts.desubroutinize = True
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]

    sub = Subsetter(options=opts)
    sub.populate(text="".join(sorted(charset)))
    sub.subset(font)

    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()

    if not quiet:
        print("  %-30s %6.1f KB -> woff2 %5.1f KB"
              % (filename, src.stat().st_size / 1024, len(data) / 1024))

    return (
        "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;"
        "src:url(data:font/woff2;base64,%s) format('woff2');}"
        % (family, style, weight, base64.b64encode(data).decode("ascii"))
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fonts", type=pathlib.Path, default=HERE / "fonts",
                    help="directory holding the source TTF files (default: ./fonts)")
    ap.add_argument("--src", type=pathlib.Path, default=HERE / "src" / "page.html")
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "index.html")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()

    body = args.src.read_text(encoding="utf-8")
    if "__FONTS__" not in body:
        raise SystemExit("%s has no __FONTS__ placeholder" % args.src)

    charset = needed_glyphs(body)
    if not args.quiet:
        print("subsetting %d faces to %d glyphs:" % (len(FACES), len(charset)))

    fonts = "\n".join(
        face_css(args.fonts, fam, fn, w, st, charset, args.quiet) for fam, fn, w, st in FACES
    )
    body = body.replace("__FONTS__", fonts)

    args.out.write_text(TEMPLATE.format(title=TITLE, desc=DESC, body=body), encoding="utf-8")
    print("wrote %s (%.1f KB)" % (args.out, args.out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
