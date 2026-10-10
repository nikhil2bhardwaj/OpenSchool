"""Batch-patch all labs with i18n chrome (idempotent).

Adds per lab (where missing):
1. <script> include for assets/js/i18n.js (correct relative depth)
2. EN/hi toggle buttons in topbar before hub link
3. data-i18n / data-i18n-ph attributes mirroring labs/template_lab.html
4. i18n-aware trialCount + obsHead '#' + guarded os-lang-change chrome hook
Zero-dep, no CDN. Run: python3 os_patch_i18n.py
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pathlib
import re

ROOT = pathlib.Path("labs")
files = sorted(ROOT.rglob("*.html"))

TOGGLE_HTML = (
    '<span class="os-row" role="group" aria-label="Language">\n'
    '      <button class="os-filter-pill" data-os-lang-toggle="en">EN</button>\n'
    '      <button class="os-filter-pill" data-os-lang-toggle="hi">\u0939\u093f\u0902</button>\n'
    "    </span>\n    "
)

HOOK = (
    '<script>/* OS-I18N-CHROME: re-render dynamic chrome on language toggle (guarded, idempotent). */\n'
    "(function(){function rr(){try{if(typeof renderHead===\"function\"&&document.getElementById(\"obsHead\"))renderHead();}catch(e){}"
    "try{if(typeof renderTable===\"function\"&&document.getElementById(\"obsTable\"))renderTable();}catch(e){}"
    "try{if(typeof recompute===\"function\")recompute();}catch(e){}}"
    "if(window.__osI18nChromeWired)return;window.__osI18nChromeWired=true;"
    "document.addEventListener(\"os-lang-change\",rr);})();</script>"
)

BTN_KEYS = {
    "btnRecord": "btn.record",
    "btnReset": "btn.reset",
    "btnSave": "btn.save",
    "btnExport": "btn.export",
    "btnClear": "btn.clear",
    "btnReport": "btn.report",
}
TAB_KEYS = {
    "theory": "tabs.theory",
    "errors": "tabs.errors",
    "viva": "tabs.viva",
    "procedure": "tabs.procedure",
    "quiz": "tabs.quiz",
}
VIVA_KEYS = {
    "modeOffline": "viva.offline",
    "modeAI": "viva.ai",
    "vivaStart": "viva.startOffline",
    "aiStart": "viva.startAI",
    "aiSend": "viva.send",
}
STAT_KEYS = {"Mean y": "stats.mean", "Std. Error": "stats.stderr", "Trials": "stats.trials"}

stats = {
    "i18n_include": 0,
    "toggles": 0,
    "dbchip_fix": 0,
    "hub_attr": 0,
    "kicker_attr": 0,
    "chip_attr": 0,
    "btn_attr": 0,
    "stat_attr": 0,
    "tab_attr": 0,
    "viva_attr": 0,
    "aireply_attr": 0,
    "trialcount": 0,
    "obshead": 0,
    "hook": 0,
}


def add_attr_id(text, tag, idname, attr, key):
    """Add data attr to <tag ... id="idname" ...> if missing. Returns (text, changed)."""

    def rep(m):
        if "data-i18n" in m.group(0):
            return m.group(0)
        stats_key = "viva_attr" if idname in VIVA_KEYS else ("tab_attr" if False else None)
        return m.group(0)[:-1] + ' %s="%s">' % (attr, key)

    pat = re.compile(r"<%s\b[^>]*\bid=\"%s\"[^>]*>" % (tag, idname))
    new, n = pat.subn(rep, text)
    return new, n


for f in files:
    t = f.read_text(encoding="utf-8")
    orig = t
    rel = f.relative_to(ROOT)
    prefix = "../" * len(rel.parts)  # template: ../, class9/10 root: ../../, nested: ../../../

    # 1. i18n.js include after bookmarks.js
    if "assets/js/i18n.js" not in t:
        anchor = 'src="%sassets/js/bookmarks.js"></script>' % prefix
        if anchor in t:
            t = t.replace(
                anchor,
                anchor + '\n<script src="%sassets/js/i18n.js"></script>' % prefix,
                1,
            )
            stats["i18n_include"] += 1
        else:  # fallback: before perf.js
            anchor2 = 'src="%sassets/js/perf.js"></script>' % prefix
            assert anchor2 in t, "no anchor in %s" % f
            t = t.replace(
                anchor2,
                '<script src="%sassets/js/i18n.js"></script>\n' % prefix + anchor2,
                1,
            )
            stats["i18n_include"] += 1

    # 2a. dbChip restructure to template form (fixes boot overwrite + enables label i18n)
    m = re.search(
        r'<span class="os-chip" id="dbChip">\s*Notebook:\s*<b>(.*?)</b>\s*</span>', t, re.S
    )
    if m:
        t = t[: m.start()] + (
            '<span class="os-chip"><span data-i18n="topbar.notebook">Notebook:</span> '
            '<b id="dbChip">%s</b></span>' % m.group(1)
        ) + t[m.end():]
        stats["dbchip_fix"] += 1
    else:
        m2 = re.search(
            r'<span class="os-chip">\s*Notebook:\s*<b id="dbChip">(.*?)</b>\s*</span>', t
        )
        if m2 and "topbar.notebook" not in t[max(0, m2.start() - 0): m2.end()]:
            t = t[: m2.start()] + (
                '<span class="os-chip"><span data-i18n="topbar.notebook">Notebook:</span> '
                '<b id="dbChip">%s</b></span>' % m2.group(1)
            ) + t[m2.end():]
            stats["dbchip_fix"] += 1

    # 2b. toggles before hub link
    if "data-os-lang-toggle" not in t:
        pat = re.compile(r'<a class="os-btn ghost sm" href="[^"]*index\.html"')
        assert pat.search(t), "no hub link in %s" % f
        t = pat.sub(TOGGLE_HTML + r"\g<0>", t, count=1)
        stats["toggles"] += 1

    # 3a. hub link attr
    def hub_rep(m):
        if "data-i18n" in m.group(0):
            return m.group(0)
        stats["hub_attr"] += 1
        return m.group(0)[:-1] + ' data-i18n="lab.back">'

    t = re.sub(r'<a class="os-btn ghost sm" href="[^"]*index\.html"[^>]*>', hub_rep, t)

    # 3b. kickers: Apparatus* -> lab.apparatus, Observation* -> lab.observation
    def kick_rep(m):
        full, inner = m.group(0), m.group(1)
        if "data-i18n" in full:
            return full
        if "Apparatus" in inner:
            stats["kicker_attr"] += 1
            return full.replace(">", ' data-i18n="lab.apparatus">', 1)
        if inner.startswith("Observation"):
            stats["kicker_attr"] += 1
            return full.replace(">", ' data-i18n="lab.observation">', 1)
        return full

    t = re.sub(r'<span class="os-kicker">([^<]*)</span>', kick_rep, t)

    # 3c. engine/live chips
    def chip_rep(m):
        if "data-i18n" in m.group(0):
            return m.group(0)
        stats["chip_attr"] += 1
        return m.group(0)[:-1] + ' data-i18n="lab.engineReady">'

    t = re.sub(r'<span class="os-chip" id="(liveChip|engineChip)"[^>]*>', chip_rep, t)

    # 3d. buttons by id
    for bid, key in BTN_KEYS.items():
        def b_rep(m, key=key):
            if "data-i18n" in m.group(0):
                return m.group(0)
            stats["btn_attr"] += 1
            return m.group(0)[:-1] + ' data-i18n="%s">' % key

        t = re.sub(r'<button\b[^>]*\bid="%s"[^>]*>' % bid, b_rep, t)

    # 3e. stat spans (exact generic text only)
    def stat_rep(m):
        full, label = m.group(0), m.group(1)
        if "data-i18n" in full or label not in STAT_KEYS:
            return full
        stats["stat_attr"] += 1
        return full.replace("<span>", '<span data-i18n="%s">' % STAT_KEYS[label], 1)

    t = re.sub(r'<div class="os-stat"><span>([^<]*)</span>', stat_rep, t)

    # 3f. tabs by data-tab
    for tab, key in TAB_KEYS.items():
        def t_rep(m, key=key):
            if "data-i18n" in m.group(0):
                return m.group(0)
            stats["tab_attr"] += 1
            return m.group(0)[:-1] + ' data-i18n="%s">' % key

        t = re.sub(r'<button\b[^>]*\bdata-tab="%s"[^>]*>' % tab, t_rep, t)

    # 3g. viva buttons by id
    for bid, key in VIVA_KEYS.items():
        def v_rep(m, key=key):
            if "data-i18n" in m.group(0):
                return m.group(0)
            stats["viva_attr"] += 1
            return m.group(0)[:-1] + ' data-i18n="%s">' % key

        t = re.sub(r'<button\b[^>]*\bid="%s"[^>]*>' % bid, v_rep, t)

    # 3h. aiReply placeholder
    def ai_rep(m):
        if "data-i18n-ph" in m.group(0):
            return m.group(0)
        stats["aireply_attr"] += 1
        return m.group(0)[:-1] + ' data-i18n-ph="viva.answerPh">'

    t = re.sub(r'<input\b[^>]*\bid="aiReply"[^>]*>', ai_rep, t)

    # 4a. trialCount i18n
    def tc_rep(m):
        stats["trialcount"] += 1
        return (
            m.group(1)
            + m.group(2)
            + ' + " " + ((window.OS_I18N&&window.OS_I18N.t)?window.OS_I18N.t("trials.unit"):"trials");'
        )

    t = re.sub(
        r'(document\.getElementById\("trialCount"\)\.textContent\s*=\s*)([A-Za-z0-9_.()$]+)\s*\+\s*" (trials|tests)"\s*;',
        tc_rep,
        t,
    )

    # 4b. obsHead '#' i18n
    if '"<th>#</th>"' in t:
        t = t.replace(
            '"<th>#</th>"',
            '"<th>"+((window.OS_I18N&&window.OS_I18N.t)?window.OS_I18N.t("th.num"):"#")+"</th>"',
        )
        stats["obshead"] += 1

    # 4c. chrome hook before </body>
    if "OS-I18N-CHROME" not in t:
        assert "</body>" in t, "no body in %s" % f
        t = t.replace("</body>", HOOK + "\n</body>", 1)
        stats["hook"] += 1

    if t != orig:
        f.write_text(t, encoding="utf-8")

print("files:", len(files))
for k, v in stats.items():
    print(k, v)
