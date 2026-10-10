/* OpenSchool motion helper — vendored GSAP, guarded, offline-first.
   Provides: OSMotion.staggerIn / tabSwap / popIn / shake
   - All helpers are no-ops when window.gsap is absent.
   - All helpers respect prefers-reduced-motion (no-op, CSS fallback handles visibility).
   - Safe to include on every lab; auto-enhances shell without touching physics. */
(function () {
  "use strict";

  function reducedMotion() {
    try {
      return window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) { return false; }
  }

  function hasGsap() {
    return !!(window.gsap && typeof window.gsap.fromTo === "function");
  }

  function canAnimate() {
    return hasGsap() && !reducedMotion();
  }

  function toNodes(target) {
    if (!target) return [];
    if (typeof target === "string") {
      try { return Array.prototype.slice.call(document.querySelectorAll(target)); }
      catch (e) { return []; }
    }
    if (target.nodeType === 1) return [target];
    if (target.length != null && typeof target !== "function") {
      try { return Array.prototype.slice.call(target); } catch (e) { return []; }
    }
    return [];
  }

  /* Stagger-fade/slide entrance for shell panels. */
  function staggerIn(target, opts) {
    var els = toNodes(target || ".os-panel, .os-tabpanel.active");
    if (!els.length || !canAnimate()) return;
    var o = opts || {};
    try {
      window.gsap.fromTo(els,
        { y: o.y != null ? o.y : 10, opacity: 0 },
        {
          y: 0, opacity: 1,
          duration: o.duration || 0.45,
          stagger: o.stagger != null ? o.stagger : 0.07,
          ease: o.ease || "power2.out",
          overwrite: true,
          clearProps: "transform,opacity"
        });
    } catch (e) { /* no-op: CSS keeps content visible */ }
  }

  /* Tab panel swap: fade/slide incoming panel. Old panel hidden by CSS class logic. */
  function tabSwap(incomingPanel) {
    if (!incomingPanel || !canAnimate()) return;
    try {
      window.gsap.fromTo(incomingPanel,
        { y: 8, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.28, ease: "power2.out", overwrite: true, clearProps: "transform,opacity" });
    } catch (e) { /* no-op */ }
  }

  /* Row pop-in (reimplements 02-number-pop-in): scale + fade for new observation rows. */
  function popIn(el) {
    var nodes = toNodes(el);
    if (!nodes.length || !canAnimate()) return;
    try {
      window.gsap.fromTo(nodes,
        { scale: 0.96, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2.2)", overwrite: true, clearProps: "transform,opacity" });
    } catch (e) { /* no-op: CSS .os-pop-in handles fallback */ }
  }

  /* Error shake (reimplements 12-error-state-shake): horizontal shake for empty-save. */
  function shake(el) {
    var nodes = toNodes(el);
    if (!nodes.length || !canAnimate()) return;
    try {
      nodes.forEach(function (n) {
        window.gsap.fromTo(n, { x: 0 },
          { keyframes: [{ x: -7 }, { x: 7 }, { x: -5 }, { x: 5 }, { x: 0 }], duration: 0.38, ease: "power1.inOut", overwrite: true, clearProps: "transform" });
      });
    } catch (e) { /* no-op: CSS .os-shake handles fallback */ }
  }

  window.OSMotion = {
    staggerIn: staggerIn,
    tabSwap: tabSwap,
    popIn: popIn,
    shake: shake,
    enabled: canAnimate
  };

  /* Auto-enhance: entrance + tab wiring + row observer. Idempotent. */
  function autoInit() {
    if (document.body && !document.body.hasAttribute("data-os-motion")) {
      document.body.setAttribute("data-os-motion", "1");
    }
    try { staggerIn(".os-panel"); } catch (e) {}
    /* Tab transitions: hook .os-tabs clicks -> animate incoming panel. */
    document.querySelectorAll(".os-tabs").forEach(function (tabsEl) {
      if (tabsEl.getAttribute("data-os-motion-tabs")) return;
      tabsEl.setAttribute("data-os-motion-tabs", "1");
      tabsEl.addEventListener("click", function (ev) {
        var tab = ev.target && ev.target.closest ? ev.target.closest(".os-tab") : null;
        if (!tab) return;
        /* Let the lab's own selectTab run first, then animate the now-active panel. */
        setTimeout(function () {
          try {
            var sel = tab.getAttribute("data-tab");
            var panel = sel && document.querySelector('.os-tabpanel[data-panel="' + sel + '"]');
            if (panel) tabSwap(panel);
          } catch (e) {}
        }, 0);
      });
    });
    /* Row pop-in: observe observation-table bodies. */
    try {
      var bodies = document.querySelectorAll("#obsTable tbody");
      if (bodies.length && window.MutationObserver) {
        var obs = new MutationObserver(function (muts) {
          muts.forEach(function (m) {
            (m.addedNodes || []).forEach(function (n) {
              if (n.nodeType === 1 && n.tagName === "TR") {
                n.classList.add("os-pop-in");
                popIn(n);
              }
            });
          });
        });
        bodies.forEach(function (b) { obs.observe(b, { childList: true }); });
      }
    } catch (e) {}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoInit);
  } else {
    autoInit();
  }
})();
