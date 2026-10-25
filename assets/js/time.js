/* Time in Cairo drives the identity: the dial, the cast shadows, the hour rules and the clocks.
   Everything here is optional: without it the page shows a correct static 10:00 dial. */
(function () {
  "use strict";

  const CAIRO = "Africa/Cairo";
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;

  // Minutes a zone is ahead of UTC at a given moment.
  function offset(tz, date) {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    }).formatToParts(date);
    const v = (t) => Number(parts.find((p) => p.type === t).value);
    const asUTC = Date.UTC(v("year"), v("month") - 1, v("day"), v("hour"), v("minute"), v("second"));
    return Math.round((asUTC - date.getTime()) / 60000);
  }

  function zoneNow(tz, date = new Date()) {
    const parts = new Intl.DateTimeFormat("en-GB", { timeZone: tz, hourCycle: "h23", hour: "2-digit", minute: "2-digit", weekday: "short" }).formatToParts(date);
    const get = (t) => parts.find((p) => p.type === t).value;
    const h = Number(get("hour")), m = Number(get("minute"));
    return { hours: h + m / 60, label: `${get("hour")}:${get("minute")}`, weekday: get("weekday") };
  }

  const pad = (n) => String(n).padStart(2, "0");
  const fmt = (hours) => {
    const total = Math.round((((hours % 24) + 24) % 24) * 60) % 1440;
    return `${pad(Math.floor(total / 60))}:${pad(total % 60)}`;
  };

  // ---------------------------------------------------------------- global "now"

  // Sun angle on the sky arc: 180 deg at 06:00 (east, left), 0 deg at 18:00 (west, right).
  const sunAngle = (t) => 180 - (Math.min(18, Math.max(6, t)) - 6) * 15;

  function applyNow() {
    const cairo = zoneNow(CAIRO);
    const t = cairo.hours;
    const day = t >= 6 && t < 18;
    // Cast shadows fall away from the sun; longer near the horizon. Flat at night.
    if (day) {
      const a = (sunAngle(t) * Math.PI) / 180;
      const len = 2.5 + 3 * Math.abs(Math.cos(a));
      root.style.setProperty("--cast-x", `${(-Math.cos(a) * len).toFixed(1)}px`);
      root.style.setProperty("--cast-y", `${(Math.sin(a) * len + 1.5).toFixed(1)}px`);
    } else {
      root.style.setProperty("--cast-x", "0px");
      root.style.setProperty("--cast-y", "0px");
    }
    root.style.setProperty("--now-pos", (((Math.min(18, Math.max(6, t)) - 6) / 12) * 100).toFixed(2));
    root.style.setProperty("--now-on", day ? "1" : "0");
    root.dataset.daylight = day ? "day" : "night";
    document.querySelectorAll("[data-sun-arc]").forEach((c) => {
      const a = (sunAngle(t) * Math.PI) / 180, r = +c.dataset.r;
      c.setAttribute("cx", (+c.dataset.cx + r * Math.cos(a)).toFixed(1));
      c.setAttribute("cy", (+c.dataset.cy - r * Math.sin(a)).toFixed(1));
    });

    document.querySelectorAll("[data-now]").forEach((el) => { el.textContent = cairo.label; });
    document.querySelectorAll("[data-clock]").forEach((el) => { el.querySelector("time").textContent = zoneNow(el.dataset.clock).label; });
    document.querySelectorAll("[data-market]").forEach((el) => {
      const z = zoneNow(el.dataset.market);
      const weekend = (el.dataset.weekend || "Sat Sun").split(" ").includes(z.weekday);
      const on = !weekend && z.hours >= 9 && z.hours < 17;
      el.querySelector(".time").textContent = z.label;
      el.querySelector(".state").textContent = weekend ? "Weekend" : on ? "Business hours" : "After hours";
      el.classList.toggle("is-on", on);
    });
    return t;
  }

  // ---------------------------------------------------------------- dial

  const CX = 280, CY = 280, R_SKY = 250;
  const BAND_R = { cairo: 202, sydney: 180, london: 158 };
  const polar = (r, deg) => {
    const a = (deg * Math.PI) / 180;
    return [CX + r * Math.cos(a), CY - r * Math.sin(a)];
  };
  const shadowAngle = (t) => -(t - 6) * 15;

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
    let mode = "live";
    let t = 10;

    // Hours each city is ahead of Cairo, refreshed every minute (handles daylight saving).
    let deltas = {};
    function refreshDeltas() {
      const now = new Date();
      const c = offset(CAIRO, now);
      cities.forEach((el) => { deltas[el.dataset.tz] = (offset(el.dataset.tz, now) - c) / 60; });
      bands.forEach((band) => {
        const tz = cities.find((el) => el.querySelector(".label").textContent.trim().toLowerCase() === band.dataset.city).dataset.tz;
        const d = deltas[tz];
        const segs = [];
        for (const shift of [-24, 0, 24]) {
          const lo = Math.max(9 - d + shift, 6), hi = Math.min(17 - d + shift, 18);
          if (hi > lo) segs.push(arcPath(BAND_R[band.dataset.city], lo, hi));
        }
        band.setAttribute("d", segs.join(" "));
        band.dataset.tz = tz;
      });
    }

    function render(time, live) {
      t = time;
      const day = time >= 6 && time < 18;
      svg.classList.toggle("is-night", live && !day);
      const shown = Math.min(18, Math.max(6, time));
      const [sx, sy] = polar(R_SKY, sunAngle(shown));
      for (const el of [sun, hit, ring]) { el.setAttribute("cx", sx.toFixed(1)); el.setAttribute("cy", sy.toFixed(1)); }
      shadow.setAttribute("d", shadowPath(shown));

      const cairoDay = zoneNow(CAIRO).weekday;
      const texts = [];
      cities.forEach((el) => {
        const d = deltas[el.dataset.tz] || 0;
        const local = time + d;
        const label = el.querySelector(".label").textContent.trim();
        // Weekday: today's in live mode; in scrub mode assume the same calendar day as Cairo now.
        const weekday = live ? zoneNow(el.dataset.tz).weekday : (local >= 24 || local < 0 ? null : cairoDay);
        const weekend = weekday && (el.dataset.weekend || "Sat Sun").split(" ").includes(weekday);
        const lh = ((local % 24) + 24) % 24;
        const on = !weekend && lh >= 9 && lh < 17;
        el.querySelector(".time").textContent = fmt(local);
        el.querySelector(".state").textContent = weekend ? "Weekend" : on ? "Business hours" : "After hours";
        el.classList.toggle("is-on", on);
        bands.forEach((b) => { if (b.dataset.tz === el.dataset.tz) b.classList.toggle("is-on", on); });
        texts.push(`${fmt(local)} in ${label}`);
      });
      hit.setAttribute("aria-valuenow", shown.toFixed(2));
      hit.setAttribute("aria-valuetext", texts.join(", "));
      if (live) note.textContent = day ? "Live: drag the sun to compare working hours." : "After hours in Cairo. Drag the sun to plan a call.";
      else note.textContent = `If it is ${fmt(time)} in Cairo:`;
      nowBtn.hidden = live;
    }

    function live() { mode = "live"; render(applyNow(), true); }

    function fromPointer(ev) {
      const pt = svg.createSVGPoint();
      pt.x = ev.clientX; pt.y = ev.clientY;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      let deg = (Math.atan2(CY - p.y, p.x - CX) * 180) / Math.PI;
      if (deg < 0) deg = p.x < CX ? 180 : 0;       // below the horizon: clamp to the nearest end
      return 6 + (180 - deg) / 15;
    }

    let dragging = false;
    function start(ev) {
      if (ev.button !== undefined && ev.button !== 0) return;
      dragging = true; mode = "scrub";
      svg.classList.add("is-dragging");
      svg.setPointerCapture(ev.pointerId);
      render(Math.round(fromPointer(ev) * 4) / 4, false);
    }
    svg.addEventListener("pointerdown", (ev) => {
      const p = ev.target;
      if (p === hit || p.closest(".sun-hit") || ev.offsetY < svg.getBoundingClientRect().height * 0.55) start(ev);
    });
    svg.addEventListener("pointermove", (ev) => { if (dragging) render(Math.round(fromPointer(ev) * 4) / 4, false); });
    const stop = () => { dragging = false; svg.classList.remove("is-dragging"); };
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);

    hit.addEventListener("keydown", (ev) => {
      const steps = { ArrowRight: 0.25, ArrowUp: 0.25, ArrowLeft: -0.25, ArrowDown: -0.25, PageUp: 1, PageDown: -1 };
      let next = null;
      if (ev.key in steps) next = Math.min(18, Math.max(6, (mode === "live" ? Math.min(18, Math.max(6, t)) : t) + steps[ev.key]));
      else if (ev.key === "Home") next = 6;
      else if (ev.key === "End") next = 18;
      else if (ev.key === "Escape") { live(); ev.preventDefault(); return; }
      if (next === null) return;
      ev.preventDefault();
      mode = "scrub";
      render(next, false);
    });
    nowBtn.addEventListener("click", () => { live(); hit.focus(); });

    refreshDeltas();
    // Sunrise: the sun travels from the horizon to now once, then the dial runs live.
    const target = applyNow();
    if (reduced || target < 6 || target >= 18) { live(); }
    else {
      const t0 = performance.now(), dur = 1400;
      const ease = (k) => 1 - Math.pow(1 - k, 3);
      const step = (now) => {
        if (mode !== "live") return;
        const k = Math.min(1, (now - t0) / dur);
        render(6 + (target - 6) * ease(k), true);
        if (k < 1) requestAnimationFrame(step); else live();
      };
      requestAnimationFrame(step);
    }
    setInterval(() => { refreshDeltas(); if (mode === "live") live(); }, 30000);
  }

  applyNow();
  setInterval(applyNow, 30000);
  document.querySelectorAll("[data-dial]").forEach(initDial);
})();
