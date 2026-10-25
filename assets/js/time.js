/* Time in Cairo drives the identity: the dial, the cast shadows, the hour rules and the clocks.
   Everything here is optional: without it the page shows a correct static 10:00 dial. */
(function () {
  "use strict";

  const CAIRO = "Africa/Cairo";
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;

  // Run once the arrival cover has lifted (or at once if there is none).
  const afterCover = (fn) => {
    if (!root.classList.contains("is-arriving")) return fn();
    const mo = new MutationObserver(() => {
      if (!root.classList.contains("is-arriving")) { mo.disconnect(); fn(); }
    });
    mo.observe(root, { attributes: true, attributeFilter: ["class"] });
  };

  // Intl formatters are expensive to build; keep one per zone and purpose.
  const FMT = new Map();
  const formatter = (key, make) => FMT.get(key) || FMT.set(key, make()).get(key);

  // Minutes a zone is ahead of UTC at a given moment.
  function offset(tz, date) {
    const parts = formatter("o" + tz, () => new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    })).formatToParts(date);
    const v = (t) => Number(parts.find((p) => p.type === t).value);
    const asUTC = Date.UTC(v("year"), v("month") - 1, v("day"), v("hour"), v("minute"), v("second"));
    return Math.round((asUTC - date.getTime()) / 60000);
  }

  function zoneNow(tz, date = new Date()) {
    const parts = formatter("z" + tz, () => new Intl.DateTimeFormat("en-GB", {
      timeZone: tz, hourCycle: "h23", hour: "2-digit", minute: "2-digit", weekday: "short",
    })).formatToParts(date);
    const get = (t) => parts.find((p) => p.type === t).value;
    const h = Number(get("hour")), m = Number(get("minute"));
    return { hours: h + m / 60, label: `${get("hour")}:${get("minute")}`, weekday: get("weekday") };
  }

  const pad = (n) => String(n).padStart(2, "0");
  const fmt = (hours) => {
    const total = Math.round((((hours % 24) + 24) % 24) * 60) % 1440;
    return `${pad(Math.floor(total / 60))}:${pad(total % 60)}`;
  };
  const put = (el, v) => { if (el && el.textContent !== v) el.textContent = v; };
  const q = (n) => (Math.round(n * 2) / 2).toFixed(1);

  // ---------------------------------------------------------------- global "now"

  // Sun angle on the sky arc: 180 deg at 06:00 (east, left), 0 deg at 18:00 (west, right).
  const sunAngle = (t) => 180 - (Math.min(18, Math.max(6, t)) - 6) * 15;

  // The head script sets these on :root before first paint. Later minute updates go only to the
  // elements that use them, so the whole document is not restyled.
  const casters = document.querySelectorAll(".btn-primary, .layer, .market");
  const rules = document.querySelectorAll(".hour-rule");
  const setVar = (els, n, v) => els.forEach((el) => { if (el.style.getPropertyValue(n) !== v) el.style.setProperty(n, v); });

  function applyNow() {
    const cairo = zoneNow(CAIRO);
    const t = cairo.hours;
    const day = t >= 6 && t < 18;
    // Cast shadows fall away from the sun; longer near the horizon. Flat at night.
    const a = (sunAngle(t) * Math.PI) / 180;
    const len = 2.5 + 3 * Math.abs(Math.cos(a));
    setVar(casters, "--cast-x", day ? `${q(-Math.cos(a) * len)}px` : "0px");
    setVar(casters, "--cast-y", day ? `${q(Math.sin(a) * len + 1.5)}px` : "0px");
    setVar(rules, "--now-pos", q(((Math.min(18, Math.max(6, t)) - 6) / 12) * 100));
    setVar(rules, "--now-on", day ? "1" : "0");
    const daylight = day ? "day" : "night";
    if (root.dataset.daylight !== daylight) root.dataset.daylight = daylight;
    document.querySelectorAll("[data-sun-arc]").forEach((c) => {
      const r = +c.dataset.r;
      c.setAttribute("cx", (+c.dataset.cx + r * Math.cos(a)).toFixed(1));
      c.setAttribute("cy", (+c.dataset.cy - r * Math.sin(a)).toFixed(1));
    });

    document.querySelectorAll("[data-now]").forEach((el) => put(el, cairo.label));
    document.querySelectorAll("[data-clock]").forEach((el) => put(el.querySelector("time"), zoneNow(el.dataset.clock).label));
    document.querySelectorAll("[data-market]").forEach((el) => {
      const z = zoneNow(el.dataset.market);
      const weekend = (el.dataset.weekend || "Sat Sun").split(" ").includes(z.weekday);
      const on = !weekend && z.hours >= 9 && z.hours < 17;
      put(el.querySelector(".time"), z.label);
      put(el.querySelector(".state"), weekend ? "Weekend" : on ? "Open now" : "After hours");
      el.classList.toggle("is-on", on);
    });
    return t;
  }

  // ---------------------------------------------------------------- dial

  const CX = 280, CY = 280, SKY_RX = 236, SKY_RY = 236;
  const BAND_R = { cairo: 202, sydney: 180, london: 158 };
  const polar = (r, deg) => {
    const a = (deg * Math.PI) / 180;
    return [CX + r * Math.cos(a), CY - r * Math.sin(a)];
  };
  const shadowAngle = (t) => -(t - 6) * 15;
  const sky = (deg) => {
    const a = (deg * Math.PI) / 180;
    return [CX + SKY_RX * Math.cos(a), CY - SKY_RY * Math.sin(a)];
  };
  const easeOut = (k) => 1 - Math.pow(1 - k, 3);
  const inOut = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2); // = --ease-sweep

  function arcPath(r, t1, t2, steps = 24) {
    let d = "";
    for (let i = 0; i <= steps; i++) {
      const [x, y] = polar(r, shadowAngle(t1 + ((t2 - t1) * i) / steps));
      d += `${i ? " L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return d;
  }

  function shadowPath(t) {
    const a = (shadowAngle(t) * Math.PI) / 180;
    const len = 120 + 100 * Math.abs(Math.cos((sunAngle(t) * Math.PI) / 180));
    const ux = Math.cos(a), uy = -Math.sin(a), px = -uy, py = ux;
    const tip = [CX + ux * len, CY + uy * len];
    const f = (n) => n.toFixed(1);
    return `M${f(CX + px * 7)} ${f(CY + py * 7)} L${f(tip[0] + px * 3)} ${f(tip[1] + py * 3)} ` +
      `A3 3 0 0 1 ${f(tip[0] - px * 3)} ${f(tip[1] - py * 3)} L${f(CX - px * 7)} ${f(CY - py * 7)} Z`;
  }

  function initDial(block) {
    const svg = block.querySelector(".dial");
    const sun = svg.querySelector(".sun");
    const hit = svg.querySelector(".sun-hit");
    const ring = svg.querySelector(".sun-ring");
    const shadow = svg.querySelector(".shadow");
    const bands = [...svg.querySelectorAll(".band")];
    const cities = [...block.querySelectorAll(".city")];
    const note = block.querySelector("[data-dial-note]");
    const nowBtn = block.querySelector("[data-dial-now]");
    const status = block.querySelector("[data-dial-status]");
    let mode = "live";
    let t = 10;
    let tween = 0;

    // Hours each city is ahead of Cairo (handles daylight saving). Bands redraw only when a delta changes.
    const deltas = {};
    function refreshDeltas() {
      const now = new Date();
      const c = offset(CAIRO, now);
      cities.forEach((el) => {
        const d = (offset(el.dataset.tz, now) - c) / 60;
        if (deltas[el.dataset.tz] === d) return;
        deltas[el.dataset.tz] = d;
        const key = el.querySelector(".label").textContent.trim().toLowerCase();
        const band = bands.find((b) => b.dataset.city === key);
        if (!band) return;
        const segs = [];
        for (const shift of [-24, 0, 24]) {
          const lo = Math.max(9 - d + shift, 6), hi = Math.min(17 - d + shift, 18);
          if (hi > lo) segs.push(arcPath(BAND_R[key], lo, hi));
        }
        band.setAttribute("d", segs.join(" "));
        band.dataset.tz = el.dataset.tz;
      });
    }

    // Geometry only: cheap enough for every animation frame.
    function place(time) {
      const s = Math.min(18, Math.max(6, time));
      const [x, y] = sky(sunAngle(s));
      for (const el of [sun, hit, ring]) { el.setAttribute("cx", x.toFixed(1)); el.setAttribute("cy", y.toFixed(1)); }
      shadow.setAttribute("d", shadowPath(s));
    }

    // Geometry plus readings. Readings round to 5 minutes so a drag reads cleanly while the sun moves freely.
    function render(time, live) {
      t = time;
      const day = time >= 6 && time < 18;
      svg.classList.toggle("is-night", live && !day);
      place(live && !day ? 18 : time);   // at night the sun has set in the west
      const read = Math.round(time * 12) / 12;
      const shown = Math.min(18, Math.max(6, read));
      const cairoDay = zoneNow(CAIRO).weekday;
      const texts = [];
      cities.forEach((el) => {
        const local = read + (deltas[el.dataset.tz] || 0);
        const label = el.querySelector(".label").textContent.trim();
        // Weekday: today's in live mode; in scrub mode assume the same calendar day as Cairo now.
        const weekday = live ? zoneNow(el.dataset.tz).weekday : (local >= 24 || local < 0 ? null : cairoDay);
        const weekend = weekday && (el.dataset.weekend || "Sat Sun").split(" ").includes(weekday);
        const lh = ((local % 24) + 24) % 24;
        const on = !weekend && lh >= 9 && lh < 17;
        put(el.querySelector(".time"), fmt(local));
        put(el.querySelector(".state"), weekend ? "Weekend" : on ? "Open now" : "After hours");
        el.classList.toggle("is-on", on);
        bands.forEach((b) => { if (b.dataset.tz === el.dataset.tz) b.classList.toggle("is-on", on); });
        texts.push(`${fmt(local)} in ${label}`);
      });
      hit.setAttribute("aria-valuenow", shown.toFixed(2));
      hit.setAttribute("aria-valuetext", texts.join(", "));
      put(note, live ? (day ? "Live: drag the sun to compare working hours." : "After hours in Cairo. Drag the sun to plan a call.")
        : `If it is ${fmt(read)} in Cairo:`);
      nowBtn.hidden = live;
    }

    function live() { cancelAnimationFrame(tween); mode = "live"; render(applyNow(), true); }

    // Sweep: a state change moves like a dial hand (Back to now, Escape). At night it sets in the west.
    function sweepTo(to, done) {
      cancelAnimationFrame(tween);
      const from = Math.min(18, Math.max(6, t)), end = (to < 6 || to >= 18) ? 18 : to;
      if (reduced || Math.abs(end - from) < 0.25) return done();
      const dur = Math.min(600, 240 + 30 * Math.abs(end - from));
      let t0 = null;
      mode = "sweep";
      const step = (now) => {
        if (mode !== "sweep") return;
        if (t0 === null) t0 = now;
        const k = Math.min(1, (now - t0) / dur);
        place(from + (end - from) * inOut(k));
        if (k < 1) tween = requestAnimationFrame(step); else done();
      };
      tween = requestAnimationFrame(step);
    }
    const backToNow = () => sweepTo(applyNow(), live);

    // Pointer: the inverse screen matrix is cached and dropped on scroll/resize, so a drag forces no layout.
    let inv = null;
    const toLocal = (ev) => new DOMPoint(ev.clientX, ev.clientY).matrixTransform(inv || (inv = svg.getScreenCTM().inverse()));
    addEventListener("scroll", () => { inv = null; }, { passive: true });
    addEventListener("resize", () => { inv = null; });
    function fromPointer(ev) {
      const p = toLocal(ev);
      let deg = (Math.atan2((CY - p.y) / SKY_RY, (p.x - CX) / SKY_RX) * 180) / Math.PI;
      if (deg < 0) deg = p.x < CX ? 180 : 0;       // below the horizon: clamp to the nearest end
      return 6 + (180 - deg) / 15;
    }

    let dragging = false, pending = null, queued = false;
    function start(ev) {
      if (ev.button !== undefined && ev.button !== 0) return;
      cancelAnimationFrame(tween);
      inv = svg.getScreenCTM().inverse();
      dragging = true; mode = "scrub";
      svg.classList.add("is-dragging");
      svg.setPointerCapture(ev.pointerId);
      render(fromPointer(ev), false);
    }
    svg.addEventListener("pointerdown", (ev) => {
      const p = ev.target;
      // Touch starts a drag only on the sun itself, so a vertical swipe over the dial still scrolls the page.
      if (p === hit || p.closest(".sun-hit") || (ev.pointerType !== "touch" && toLocal(ev).y < CY)) start(ev);
    });
    hit.addEventListener("touchstart", (e) => e.preventDefault(), { passive: false });
    svg.addEventListener("pointermove", (ev) => {
      if (!dragging) return;
      pending = fromPointer(ev);
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; if (dragging) render(pending, false); });
    });
    const stop = () => {
      if (dragging && status) status.textContent = hit.getAttribute("aria-valuetext");
      dragging = false;
      svg.classList.remove("is-dragging");
    };
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);

    hit.addEventListener("keydown", (ev) => {
      const steps = { ArrowRight: 0.25, ArrowUp: 0.25, ArrowLeft: -0.25, ArrowDown: -0.25, PageUp: 1, PageDown: -1 };
      const base = Math.min(18, Math.max(6, t));
      let next = null;
      if (ev.key in steps) next = Math.min(18, Math.max(6, base + steps[ev.key]));
      else if (ev.key === "Home") next = 6;
      else if (ev.key === "End") next = 18;
      else if (ev.key === "Escape") { backToNow(); ev.preventDefault(); return; }
      if (next === null) return;
      ev.preventDefault();
      cancelAnimationFrame(tween);
      mode = "scrub";
      render(next, false);
    });
    nowBtn.addEventListener("click", () => { hit.focus(); backToNow(); });

    // Sunrise: once the headline has risen, the sun leaves the east horizon and lands on now.
    // Duration scales with distance; on narrow screens it waits until the dial is in view.
    function startSunrise() {
      if (mode !== "live" && mode !== "armed") return;
      refreshDeltas();
      const target = applyNow();
      if (reduced || target < 6 || target >= 18) { live(); svg.classList.add("is-live"); return; }
      render(target, true);
      place(6);
      svg.classList.add("is-live");
      const dur = Math.min(1300, 500 + 70 * (target - 6));
      let t0 = null;
      mode = "rise";
      const step = (now) => {
        if (mode !== "rise") return;
        if (t0 === null) t0 = now;
        const k = Math.min(1, (now - t0) / dur);
        place(6 + (target - 6) * easeOut(k));
        if (k < 1) tween = requestAnimationFrame(step); else live();
      };
      tween = requestAnimationFrame(step);
    }
    const go = () => {
      if (!matchMedia("(max-width: 900px)").matches || !("IntersectionObserver" in window)) return startSunrise();
      refreshDeltas();
      render(applyNow(), true);
      place(6);
      mode = "armed";
      svg.classList.add("is-armed");
      const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); startSunrise(); } }, { threshold: 0.3 });
      io.observe(block);
    };
    refreshDeltas();
    if (reduced) { live(); svg.classList.add("is-live"); }
    else afterCover(() => setTimeout(go, 200));

    return { tick(now) { refreshDeltas(); if (mode === "live") render(now, true); } };
  }

  // Clocks flip on the minute, like a real clock, and skip work in hidden tabs.
  function everyMinute(fn) {
    const next = () => setTimeout(() => { if (!document.hidden) fn(); next(); }, 60000 - (Date.now() % 60000) + 50);
    next();
    document.addEventListener("visibilitychange", () => { if (!document.hidden) fn(); });
  }

  applyNow();
  const dials = [...document.querySelectorAll("[data-dial]")].map(initDial);
  everyMinute(() => { const t = applyNow(); dials.forEach((d) => d.tick(t)); });
})();
