"""OS-FLUID-SHELL batch: HTML-hook-only, idempotent, no physics/canvas/data changes.
Adds CSS/JS-choreography targets that motion.js sibling drives.
Zero CDN (inline script only, no new src). Run from GitHubDeploy/.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
files = sorted((ROOT / 'labs').rglob('*.html'))

ACTIONBAR = '''
    <!-- OS-ACTIONBAR: sticky mobile quick actions (proxies, no duplicate ids) -->
    <div class="os-actionbar" data-os-actionbar role="toolbar" aria-label="Quick actions">
      <button class="os-btn primary" type="button" data-os-proxy="btnRecord">Record Reading</button>
      <button class="os-btn success" type="button" data-os-proxy="btnSave">Save to Notebook</button>
      <button class="os-btn" type="button" data-os-proxy="btnReport">Print Report</button>
    </div>

'''

TOAST_DIV = '\n<!-- OS-FLUID-SHELL hooks: toast stack + alert routing + proxy/fader/indicator targets.\n     CSS lives in lab-theme.css; motion.js sibling drives animation. Idempotent. -->\n<div class="os-toasts os-toast-stack" id="osToasts" role="status" aria-live="polite" aria-atomic="false"></div>\n'

TOAST_JS = '''<script>/* OS-TOAST: toast system replacing window.alert (guarded, idempotent). */
(function(){
  if(window.OSToast&&window.OSToast.__osFluid)return;
  function host(){
    var h=document.getElementById("osToasts");
    if(h)return h;
    h=document.createElement("div");
    h.className="os-toasts os-toast-stack";h.id="osToasts";
    h.setAttribute("role","status");h.setAttribute("aria-live","polite");h.setAttribute("aria-atomic","false");
    document.body.appendChild(h);return h;
  }
  function show(msg,type){
    try{
      var h=host();
      var t=document.createElement("div");
      var kind=(type==="ok"||type==="success")?"ok":(type==="danger"||type==="error")?"danger":(type==="warn"?"warn":"");
      t.className=("os-toast "+kind).trim();
      var dot=document.createElement("span");dot.className="os-toast-dot";dot.setAttribute("aria-hidden","true");
      var m=document.createElement("span");m.className="os-toast-msg";m.textContent=String(msg==null?"":msg);
      var x=document.createElement("button");x.className="os-toast-close";x.type="button";x.textContent="×";x.setAttribute("aria-label","Dismiss");
      x.addEventListener("click",function(){dismiss(t);});
      t.appendChild(dot);t.appendChild(m);t.appendChild(x);
      h.appendChild(t);
      while(h.children.length>4)h.removeChild(h.firstChild);
      setTimeout(function(){dismiss(t);},4200);
      return t;
    }catch(e){try{window.__osNativeAlert(String(msg));}catch(_){}return null;}
  }
  function dismiss(t){
    if(!t||!t.parentNode||t.classList.contains("is-leaving"))return;
    try{
      t.classList.add("is-leaving");
      setTimeout(function(){if(t.parentNode)t.parentNode.removeChild(t);},200);
    }catch(e){if(t.parentNode)t.parentNode.removeChild(t);}
  }
  window.OSToast={show:show,dismiss:dismiss,__osFluid:true};
  if(!window.__osNativeAlert){
    try{window.__osNativeAlert=window.alert;}catch(e){}
    try{window.alert=function(m){return show(m,"warn");};}catch(e){}
  }
  /* Sticky action-bar proxies: [data-os-proxy] clicks forward to #id buttons. */
  document.addEventListener("click",function(ev){
    var p=ev.target&&ev.target.closest?ev.target.closest("[data-os-proxy]"):null;
    if(!p)return;
    var target=document.getElementById(p.getAttribute("data-os-proxy"));
    if(target&&target!==p&&typeof target.click==="function"){ev.preventDefault();target.click();}
  });
})();</script>
'''

counts = dict(total=len(files), changed=0, tablist=0, indicator=0,
              ledger=0, rolling=0, fader=0, actionbar=0, toastdiv=0,
              toastjs=0, collapsible=0, tabaria=0, panelaria=0, roving=0)
changed_files = []

for f in files:
    s = f.read_text(encoding='utf-8')
    orig = s
    rel = str(f.relative_to(ROOT))

    # 1. data-os-tablist on #tabs
    def _tablist(m):
        tag = m.group(0)
        if 'data-os-tablist' in tag:
            return tag
        return tag[:-1] + ' data-os-tablist>'
    s2, n = re.subn(r'<div[^>]*id="tabs"[^>]*>', _tablist, s, count=1)
    if n and s2 != s:
        s = s2; counts['tablist'] += 1

    # 2. tab indicator span inside #tabs (first </div> after tabs open)
    if 'os-tab-indicator' not in s:
        m = re.search(r'<div[^>]*id="tabs"[^>]*>', s)
        if m:
            close = s.find('</div>', m.end())
            # sanity: tabs block should contain data-tab buttons before close
            block = s[m.end():close] if close != -1 else ''
            if close != -1 and 'data-tab=' in block:
                s = (s[:close]
                     + '\n        <span class="os-tab-indicator" id="tabIndicator" aria-hidden="true"></span>\n      '
                     + s[close:])
                counts['indicator'] += 1

    # 3. generic tab aria + ids for EVERY data-tab value (covers proc outlier too)
    for m in re.finditer(r'<button[^>]*data-tab="([a-z]+)"[^>]*>', s):
        pass
    def _fix_all_tabs(m):
        tag = m.group(0)
        tn = re.search(r'data-tab="([a-z]+)"', tag).group(1)
        new = tag
        if 'aria-controls' not in tag:
            new = new[:-1] + ' aria-controls="panel-%s">' % tn
        if 'id="tab-' not in tag:
            new = new[:-1] + ' id="tab-%s">' % tn
        return new
    s2, n = re.subn(r'<button[^>]*data-tab="[a-z]+"[^>]*>', _fix_all_tabs, s)
    if s2 != s:
        # count files touched (approx: compare)
        counts['tabaria'] += 1; s = s2

    # 4. generic panels: every data-panel value gets id + aria-labelledby
    def _fix_all_panels(m):
        tag = m.group(0)
        pn = re.search(r'data-panel="([a-z]+)"', tag).group(1)
        new = tag
        if 'id="panel-' not in tag:
            new = new[:-1] + ' id="panel-%s">' % pn
        if 'aria-labelledby' not in tag:
            new = new[:-1] + ' aria-labelledby="tab-%s">' % pn
        return new
    s2, n = re.subn(r'<div[^>]*data-panel="[a-z]+"[^>]*>', _fix_all_panels, s)
    if s2 != s:
        counts['panelaria'] += 1; s = s2

    # 5. theory collapsible hook (fallback: first active panel when no theory panel)
    # NOTE: match markup only — report-wiring JS strings also mention data-panel="theory".
    if re.search(r'<div[^>]*data-panel="theory"', s):
        def _theory(m):
            tag = m.group(0)
            if 'data-os-collapsible' in tag:
                return tag
            return tag[:-1] + ' data-os-collapsible>'
        s2, n = re.subn(r'<div[^>]*data-panel="theory"[^>]*>', _theory, s, count=9)
        if s2 != s:
            counts['collapsible'] += 1; s = s2
    else:
        def _first_active(m):
            tag = m.group(0)
            if 'data-os-collapsible' in tag:
                return tag
            return tag[:-1] + ' data-os-collapsible>'
        s2, n = re.subn(r'<div[^>]*class="[^"]*os-tabpanel[^"]*active[^"]*"[^>]*>', _first_active, s, count=1)
        if s2 != s:
            counts['collapsible'] += 1; s = s2

    # 6. roving tabindex for .os-tab buttons missing tabindex
    def _roving(m):
        tag = m.group(0)
        if 'tabindex' in tag.lower():
            return tag
        active = 'active' in tag
        return tag[:-1] + (' tabindex="0">' if active else ' tabindex="-1">')
    s2, n = re.subn(r'<button[^>]*class="[^"]*os-tab[^"]*"[^>]*>', _roving, s)
    if s2 != s:
        counts['roving'] += 1; s = s2

    # 7. ledger hook on obs table wrap
    def _ledger(m):
        tag = m.group(0)
        if 'data-os-ledger' in tag or 'os-obs' not in tag:
            return tag
        return tag[:-1] + ' data-os-ledger>'
    s2, n = re.subn(r'<div[^>]*class="[^"]*os-table-wrap[^"]*"[^>]*>', _ledger, s)
    if s2 != s:
        counts['ledger'] += 1; s = s2

    # 8. readout rolling digits: <b id="roXxx">
    def _rolling(m):
        pre, bid, post = m.group(1), m.group(2), m.group(3)
        tag = '<b' + pre + 'id="' + bid + '"' + post + '>'
        new = tag
        if 'data-os-rolling' not in tag:
            new = new[:-1] + ' data-os-rolling>'
        if 'os-rolling' not in tag:
            # inject class (or append)
            if 'class="' in new:
                new = re.sub(r'class="([^"]*)"', lambda c: 'class="%s os-rolling"' % c.group(1).strip() if 'os-rolling' not in c.group(1) else c.group(0), new, count=1)
            else:
                new = new[:-1] + ' class="os-rolling">'
        return new
    s2, n = re.subn(r'<b([^>]*?)id="(ro[A-Za-z]*)"([^>]*?)>', _rolling, s)
    if s2 != s:
        counts['rolling'] += 1; s = s2

    # 9. fader wrap: only when file has zero wraps (first conversion wraps ALL ranges)
    if 'os-range-wrap' not in s and 'os-range' in s:
        def _wrap(m):
            tag = m.group(0)
            return ('<div class="os-range-wrap" data-os-fader>'
                    '<span class="os-range-bubble" data-os-bubble aria-hidden="true"></span>'
                    + tag +
                    '<span class="os-ticks" aria-hidden="true"></span></div>')
        s2, n = re.subn(r'<input[^>]*class="[^"]*os-range[^"]*"[^>]*>', _wrap, s)
        if n and s2 != s:
            counts['fader'] += 1; s = s2

    # 10. sticky mobile actionbar before bottom-tabs anchor
    if 'data-os-actionbar' not in s:
        anchor = None
        for a in ('<!-- ============================ BOTTOM TABS',
                  '<section class="os-panel" style="margin-top:18px">',
                  'id="tabs"'):
            i = s.find(a)
            if i != -1:
                anchor = i; break
        if anchor is None:
            anchor = s.find('</main>')
        if anchor != -1 and anchor is not None:
            s = s[:anchor] + ACTIONBAR + s[anchor:]
            counts['actionbar'] += 1

    # 11. toast container + toast/alert-routing script before </body>
    if 'id="osToasts"' not in s:
        i = s.rfind('</body>')
        if i != -1:
            s = s[:i] + TOAST_DIV + s[i:]
            counts['toastdiv'] += 1
    if 'OS-TOAST' not in s:
        i = s.rfind('</body>')
        if i != -1:
            s = s[:i] + TOAST_JS + s[i:]
            counts['toastjs'] += 1

    if s != orig:
        f.write_text(s, encoding='utf-8')
        counts['changed'] += 1
        changed_files.append(rel)

print('COUNTS:', counts)
print('CHANGED_FILES:', len(changed_files))
for c in changed_files:
    print('  +', c)
