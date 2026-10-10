"""Idempotent batch patch for OpenSchool lab pages (F9 TTS + F10 bookmarks).
Skips files already patched (marker checks). Computes asset prefix by depth.
Run: python os_patch_labs.py  (cwd = GitHubDeploy)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(ROOT, "labs")

TTS_BTN = ('<button class="os-btn sm ghost" type="button" data-os-tts-btn '
           'data-os-tts-label="Theory">\U0001F50A Read aloud</button>')
BM_BTN = ('<button class="os-btn sm ghost" type="button" data-os-bookmark-btn '
          'aria-pressed="false">\u2606 Bookmark</button>')

H3_THEORY = re.compile(r"(<h3[^>]*>\s*Theory[^<]*</h3>)")
H3_QUIZ = re.compile(r"(<h3[^>]*>\s*Quiz[^<]*</h3>)")
SCRIPT_RE = re.compile(r'<script\s+src="([^"]*assets/js/(quiz|storage)\.js)"></script>')


def asset_prefix(html_path):
    d = os.path.dirname(html_path)
    rel = os.path.relpath(os.path.join(ROOT, "assets", "js"), d)
    return rel.replace(os.sep, "/")


def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    orig = html
    changed = []

    # 1. script includes (tts.js + bookmarks.js), idempotent
    if "assets/js/tts.js" not in html or "assets/js/bookmarks.js" not in html:
        prefix = asset_prefix(path)
        tags = ""
        if "assets/js/tts.js" not in html:
            tags += '<script src="%s/tts.js"></script>\n' % prefix
        if "assets/js/bookmarks.js" not in html:
            tags += '<script src="%s/bookmarks.js"></script>\n' % prefix
        m = None
        for m in SCRIPT_RE.finditer(html):
            pass  # take the LAST quiz/storage script line
        if m:
            html = html[: m.end()] + "\n" + tags.rstrip("\n") + html[m.end():]
            changed.append("scripts")
        # else: no anchor; leave scripts out (page lacks storage/quiz wiring)

    # 2. TTS speaker button after Theory h3, idempotent
    if "data-os-tts-btn" not in html:
        m = H3_THEORY.search(html)
        if m:
            html = html[: m.end()] + "\n        " + TTS_BTN + html[m.end():]
            changed.append("tts-btn")

    # 3. Bookmark star after Quiz h3, idempotent
    if "data-os-bookmark-btn" not in html:
        m = H3_QUIZ.search(html)
        if m:
            html = html[: m.end()] + "\n        " + BM_BTN + html[m.end():]
            changed.append("bookmark-btn")

    if html != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    return changed


def main():
    total, patched, details = 0, 0, []
    for dirpath, _dirs, files in os.walk(LABS):
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            if fn == "template_lab.html":
                continue
            total += 1
            p = os.path.join(dirpath, fn)
            ch = patch(p)
            if ch:
                patched += 1
                details.append("%s: %s" % (os.path.relpath(p, ROOT), ",".join(ch)))
    print("scanned=%d patched=%d" % (total, patched))
    for d in details[:50]:
        print("  " + d)
    if len(details) > 50:
        print("  ... +%d more" % (len(details) - 50))


if __name__ == "__main__":
    sys.exit(main())
