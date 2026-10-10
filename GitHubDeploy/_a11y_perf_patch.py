"""Batch a11y + perf patch for OpenSchool GitHubDeploy site. Zero-deps, idempotent."""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(ROOT, 'labs', '**', '*.html'), recursive=True))
files.append(os.path.join(ROOT, 'index.html'))

stats = {'skip': 0, 'canvas': 0, 'tab': 0, 'input': 0, 'perf_src': 0, 'draw': 0, 'files_touched': set()}

SKIP_SNIPPET = '<a class="os-skip-link" href="#main-content">Skip to main content</a>'

def rel_prefix(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel == 'index.html':
        return 'assets/js/perf.js'
    depth = rel.count('/')  # labs/x.html -> 1, labs/class9/x.html -> 2, labs/class11/physics/x.html -> 3
    return '../' * depth + 'assets/js/perf.js'

def ensure_skip(t, f):
    if 'os-skip-link' in t:
        return t, False
    nt, n = re.subn(r'(<body[^>]*>)', r'\1\n' + SKIP_SNIPPET, t, count=1)
    if n:
        stats['skip'] += 1
        return nt, True
    return t, False

def ensure_main_id(t):
    # add id="main-content" to first <main> lacking an id
    def repl(m):
        tag = m.group(0)
        if 'id=' in tag:
            return tag
        return tag.replace('<main', '<main id="main-content"', 1)
    nt = re.sub(r'<main[^>]*>', repl, t, count=1)
    return (nt, nt != t)

def patch_canvas(t):
    changed = False
    def repl(m):
        nonlocal changed
        tag = m.group(0)
        if 'aria-label' in tag:
            return tag
        changed = True
        extra = ' role="img" aria-label="Interactive experiment simulation canvas. Use the on-page controls to change the plotted scene."'
        return tag.replace('<canvas', '<canvas' + extra, 1)
    nt = re.sub(r'<canvas[^>]*>', repl, t)
    if changed:
        stats['canvas'] += 1
    return nt, changed

def patch_tabs(t):
    changed = False
    # container: <div class="os-tabs" ...> -> add role=tablist aria-label if missing
    def repl_tabs(m):
        nonlocal changed
        tag = m.group(0)
        if 'role=' in tag:
            return tag
        changed = True
        return tag.replace('class="os-tabs"', 'class="os-tabs" role="tablist" aria-label="Lab information tabs"', 1)
    t = re.sub(r'<div[^>]*class="os-tabs"[^>]*>', repl_tabs, t)
    # tab buttons: <button class="os-tab..."> -> role=tab + aria-selected
    def repl_tab(m):
        nonlocal changed
        tag = m.group(0)
        if 'role="tab"' in tag:
            return tag
        changed = True
        sel = 'true' if 'active' in tag else 'false'
        if tag.endswith('>'):
            tag = tag[:-1] + ' role="tab" aria-selected="%s">' % sel
        return tag
    t = re.sub(r'<button[^>]*class="os-tab[^"]*"[^>]*>', repl_tab, t)
    # panels: <div class="os-tabpanel..."> -> role=tabpanel tabindex + labelledby if missing
    def repl_panel(m):
        nonlocal changed
        tag = m.group(0)
        if 'role="tabpanel"' in tag:
            return tag
        changed = True
        mm = re.search(r'data-panel="([^"]+)"', tag)
        name = mm.group(1) if mm else 'panel'
        return tag.replace('class="os-tabpanel', 'role="tabpanel" tabindex="0" class="os-tabpanel', 1)
    t = re.sub(r'<div[^>]*class="os-tabpanel[^"]*"[^>]*>', repl_panel, t)
    if changed:
        stats['tab'] += 1
    return t, changed

def patch_inputs(t):
    # collect label-for ids and bare label texts in order
    labels_for = set(re.findall(r'<label[^>]*for="([^"]+)"', t))
    # bare <label>TEXT</label> (no for=) followed eventually by input/select
    changed = False
    # 1) bare labels: add for= pointing at next input/select id if it has one
    def repl_bare(m):
        nonlocal changed
        full, text, rest = m.group(0), m.group(1), m.group(2)
        if 'for=' in full.split('>')[0]:
            return full
        mid = m.group(0)
        nxt = re.search(r'<(input|select|textarea)[^>]*id="([^"]+)"', rest[:800])
        if nxt:
            changed = True
            new_open = re.sub(r'<label', '<label for="%s"' % nxt.group(2), full.split('>')[0], count=1)
            return new_open + '>' + text + '</label>'
        return full
    # operate on label + following chunk
    t = re.sub(r'<label([^>]*)>([^<]{1,120})</label>(\s*(?:<[^>]+>\s*){0,4}<(?:input|select|textarea)[^>]*>)',
               lambda m: repl_bare_label(m), t)
    # 2) inputs without any accessible name -> aria-label from placeholder or nearby text
    def repl_input(m):
        nonlocal changed
        tag = m.group(0)
        if 'aria-label' in tag or 'aria-labelledby' in tag:
            return tag
        mm = re.search(r'id="([^"]+)"', tag)
        if mm and mm.group(1) in labels_for:
            return tag
        ph = re.search(r'placeholder="([^"]+)"', tag)
        if ph:
            changed = True
            return tag.replace('<input', '<input aria-label="%s"' % ph.group(1).replace('"', ''), 1)
        return tag
    t2 = re.sub(r'<input[^>]*>', repl_input, t)
    if t2 != t:
        changed = True
        t = t2
    if changed:
        stats['input'] += 1
    return t, changed

def repl_bare_label(m):
    open_attrs, text, rest = m.group(1), m.group(2).strip(), m.group(3)
    if 'for=' in open_attrs:
        return m.group(0)
    nxt = re.search(r'<(?:input|select|textarea)[^>]*id="([^"]+)"', rest)
    if nxt:
        return '<label for="%s">%s</label>%s' % (nxt.group(1), m.group(2), rest)
    return m.group(0)

def ensure_perf_src(t, f):
    if 'perf.js' in t:
        return t, False
    prefix = rel_prefix(f)
    tag = '<script src="%s"></script>' % prefix
    # insert after ai-examiner.js script tag, else after storage.js, else before first inline <script>
    if 'ai-examiner.js' in t:
        nt = re.sub(r'(<script src="[^"]*ai-examiner\.js"></script>)', r'\1\n' + tag, t, count=1)
    elif 'storage.js' in t:
        nt = re.sub(r'(<script src="[^"]*storage\.js"></script>)', r'\1\n' + tag, t, count=1)
    else:
        return t, False
    stats['perf_src'] += 1
    return nt, True

SHIM = ('<script>window.scheduleDraw=(window.OSPerf&&window.OSPerf.rafThrottle)?'
        'window.OSPerf.rafThrottle(function(){try{if(typeof drawScene==="function")drawScene();}catch(e){}'
        'try{if(typeof draw==="function")draw();}catch(e){}'
        'try{if(typeof updateReadout==="function")updateReadout();}catch(e){}}):'
        'function(){try{if(typeof drawScene==="function")drawScene();}catch(e){}'
        'try{if(typeof draw==="function")draw();}catch(e){}'
        'try{if(typeof updateReadout==="function")updateReadout();}catch(e){}};</script>')

def patch_draw(t):
    if 'scheduleDraw' in t or 'OSPerf' in t:
        return t, False
    # only patch files with an "input" listener that calls draw
    if 'addEventListener' not in t or 'draw(' not in t:
        return t, False
    has_input_draw = bool(re.search(r'addEventListener\(\s*["\']input["\']', t))
    if not has_input_draw:
        return t, False
    changed = False
    # replace draw-call sequences inside input handlers with scheduleDraw();
    # handle common combos: drawScene(); draw(); updateReadout(); | draw(); updateReadout(); | draw();
    def repl_handler(m):
        nonlocal changed
        head, body, tail = m.group(1), m.group(2), m.group(3)
        new_body, n1 = re.subn(r'drawScene\(\);\s*draw\(\);\s*updateReadout\(\);', 'scheduleDraw();', body)
        new_body, n2 = re.subn(r'(?<![A-Za-z_])draw\(\);', 'scheduleDraw();', new_body)
        if n1 or n2:
            changed = True
        return head + new_body + tail
    t = re.sub(r'(addEventListener\(\s*["\']input["\']\s*,\s*function\s*\([^)]*\)\s*\{)(.*?)(\}\s*\);)',
               repl_handler, t, flags=re.S)
    if changed:
        # insert shim right after perf.js script tag
        t = t.replace('perf.js"></script>', 'perf.js"></script>\n' + SHIM, 1)
        stats['draw'] += 1
    return t, changed

aria_before = sum(t.count('aria-label') for t in
                  (open(f, encoding='utf-8', errors='ignore').read() for f in files))

for f in files:
    t = open(f, encoding='utf-8', errors='ignore').read()
    orig = t
    t, _ = ensure_skip(t, f)
    t, _ = ensure_main_id(t)
    t, _ = patch_canvas(t)
    t, _ = patch_tabs(t)
    t, _ = patch_inputs(t)
    t, _ = ensure_perf_src(t, f)
    t, _ = patch_draw(t)
    if t != orig:
        open(f, 'w', encoding='utf-8', newline='').write(t)
        stats['files_touched'].add(f)

aria_after = sum(open(f, encoding='utf-8', errors='ignore').read().count('aria-label') for f in files)
print('FILES SCANNED:', len(files))
print('skip-link added:', stats['skip'])
print('canvas labelled:', stats['canvas'])
print('tab roles patched (files):', stats['tab'])
print('input labels patched (files):', stats['input'])
print('perf.js src added:', stats['perf_src'])
print('draw->scheduleDraw (files):', stats['draw'])
print('files modified:', len(stats['files_touched']))
print('aria-label count: %d -> %d' % (aria_before, aria_after))
print('perf.js exists:', os.path.exists(os.path.join(ROOT, 'assets', 'js', 'perf.js')))
# no-CDN check on touched lines
import subprocess
bad = []
for f in files:
    tt = open(f, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'src="https?://[^"]+"|href="https?://[^"]+"', tt):
        bad.append((f, m.group(0)))
print('CDN refs (should be none):', bad if bad else 'NONE')
