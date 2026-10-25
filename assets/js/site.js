(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Run once the arrival cover has lifted (or at once if there is none).
  const afterCover = (fn) => {
    if (!root.classList.contains("is-arriving")) return fn();
    const mo = new MutationObserver(() => {
      if (!root.classList.contains("is-arriving")) { mo.disconnect(); fn(); }
    });
    mo.observe(root, { attributes: true, attributeFilter: ["class"] });
  };

  // Reveals first, so a later error cannot leave content hidden. The head script removes .js
  // after 2.5s if this flag never appears.
  root.classList.add("io");
  const reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    // Items that appear together stagger in reading order; anything entering from above just fades.
    // On pages with a hero headline the first batch waits for the headline to land.
    let base = $(".hero-copy") ? 240 : 0;
    const io = new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting)
        .sort((a, b) => (a.boundingClientRect.top - b.boundingClientRect.top) || (a.boundingClientRect.left - b.boundingClientRect.left))
        .forEach((e, k) => {
          const el = e.target, above = e.boundingClientRect.top < 0;
          el.style.setProperty("--d", above ? "0ms" : `${base + Math.min(k, 4) * 50}ms`);
          el.classList.toggle("no-rise", above);
          el.classList.add("is-in");
          io.unobserve(el);
          el.addEventListener("transitionend", () => { el.style.removeProperty("--d"); }, { once: true });
        });
      base = 0;
    }, { rootMargin: "0px 0px -6% 0px" });
    afterCover(() => reveals.forEach((el) => io.observe(el)));
    // Keyboard focus never lands on content that is still fading in.
    document.addEventListener("focusin", (ev) => {
      const el = ev.target.closest && ev.target.closest(".reveal:not(.is-in)");
      if (el) { el.classList.add("is-in"); io.unobserve(el); }
    });
  } else reveals.forEach((el) => el.classList.add("is-in"));

  // Day path: the line runs and each step fills as the reader reaches it.
  const steps = $$("[data-day] li");
  if ("IntersectionObserver" in window) {
    const dayIO = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("is-lit");
      e.target.parentElement.classList.add("is-run");
      dayIO.unobserve(e.target);
    }), { rootMargin: "0px 0px -45% 0px" });
    steps.forEach((li) => dayIO.observe(li));
  } else steps.forEach((li) => li.classList.add("is-lit"));

  // Header gains a rule once the page scrolls.
  const head = $("[data-head]");
  if (head) {
    const mark = document.createElement("div");
    mark.setAttribute("aria-hidden", "true");
    document.body.prepend(mark);
    new IntersectionObserver(([e]) => head.classList.toggle("is-scrolled", !e.isIntersecting)).observe(mark);
  }

  // Theme: system by default; the toggle stores an explicit choice. The light changes with a short crossfade.
  $$("[data-theme-toggle]").forEach((btn) => btn.addEventListener("click", () => {
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    const next = dark ? "light" : "dark";
    const apply = () => {
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) { /* storage blocked: theme lasts this page */ }
    };
    if (document.startViewTransition && !reduced()) document.startViewTransition(apply); else apply();
  }));

  // Mobile menu: native modal dialog (focus trap, Escape and inert background come with it).
  const menu = $("[data-menu]");
  const openBtn = $("[data-menu-open]");
  if (menu && openBtn && typeof menu.showModal === "function") {
    openBtn.addEventListener("click", () => menu.showModal());
    const closeBtn = $("[data-menu-close]", menu);
    if (closeBtn) closeBtn.addEventListener("click", () => menu.close());
    $$("a", menu).forEach((a) => a.addEventListener("click", () => menu.close()));
    menu.addEventListener("close", () => openBtn.focus());
    matchMedia("(min-width: 881px)").addEventListener("change", (m) => { if (m.matches && menu.open) menu.close(); });
  }

  // Page loader. It never delays navigation: the browser navigates at once. CSS shows the cover only
  // if the next page has not committed after 240ms, so fast clicks never flash it. The next page keeps
  // the cover only when it was actually visible here.
  let leaveTimer;
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[href]");
    if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    if ((a.target && a.target !== "_self") || a.hasAttribute("download")) return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || !/^https?:$/.test(url.protocol)) return;
    if (url.pathname === location.pathname && url.search === location.search) return;
    root.style.setProperty("--ld-phase", `${-(Date.now() % 1400)}ms`);
    root.classList.add("is-leaving");
    clearTimeout(leaveTimer);
    leaveTimer = setTimeout(() => root.classList.remove("is-leaving"), 3000);   // aborted or slow: never a dead end
  });
  addEventListener("keydown", (e) => { if (e.key === "Escape") root.classList.remove("is-leaving"); });
  addEventListener("pagehide", () => {
    const l = $(".loader");
    if (root.classList.contains("is-leaving") && l && +getComputedStyle(l).opacity > 0.5) {
      try { sessionStorage.setItem("idv-nav", "1"); } catch (e) { /* storage blocked: no arrival cover */ }
    }
  });
  if (root.classList.contains("is-arriving")) {
    const fonts = document.fonts
      ? Promise.all([document.fonts.load('700 1em "Funnel Display"'), document.fonts.load('400 1em "Funnel Sans"')])
      : Promise.resolve();
    Promise.race([fonts, new Promise((r) => setTimeout(r, 700))]).then(() => root.classList.remove("is-arriving"));
  }
  // The back/forward cache can restore a page with the cover still on.
  addEventListener("pageshow", (ev) => {
    if (ev.persisted) { clearTimeout(leaveTimer); root.classList.remove("is-leaving", "is-arriving"); }
  });

  $$("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });

  // Estimate form: validate, then compose an email to the team (no server endpoint yet).
  const form = $("[data-estimate]");
  if (form) {
    const email = "info@intimedev.com";
    const select = $("#f-service", form);
    const wanted = new URLSearchParams(location.search).get("service");
    if (wanted && select.querySelector(`option[value="${CSS.escape(wanted)}"]`)) select.value = wanted;

    const done = $("[data-done]", form);
    const preview = $("[data-preview]", form);
    const rules = {
      name: (v) => v.trim().length > 1,
      email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()),
      description: (v) => v.trim().length > 9,
    };
    const check = (input) => {
      const ok = rules[input.name] ? rules[input.name](input.value) : true;
      input.closest(".field").classList.toggle("is-invalid", !ok);
      input.setAttribute("aria-invalid", String(!ok));
      return ok;
    };
    $$("[required]", form).forEach((input) => input.addEventListener("blur", () => { if (input.value) check(input); }));
    form.addEventListener("input", (ev) => { if (ev.target.closest(".is-invalid")) check(ev.target); });

    // With an endpoint the request is sent as JSON; without one (or if sending fails) the visitor's
    // email app opens with the message ready.
    const sent = $("[data-sent]", form);
    const alertBox = $("[data-send-error]", form);
    const submit = $("[data-submit]", form);
    const submitLabel = $("[data-submit-label]", form);
    const submitText = submitLabel.textContent;
    let lastMessage = null;

    const compose = (data) => {
      const service = select.value ? select.options[select.selectedIndex].text : "Not specified";
      const subject = `Project estimate request${data.company ? ` from ${data.company}` : ""}`;
      const body = [
        `Name: ${data.name}`, `Company: ${data.company || "-"}`, `Email: ${data.email}`, `Phone: ${data.phone || "-"}`,
        `Service: ${service}`, "", "Project description:", data.description,
      ].join("\n");
      return { service, subject, body };
    };
    const openEmail = ({ subject, body }) => {
      preview.textContent = `To: ${email}\nSubject: ${subject}\n\n${body}`;
      $("[data-wa]", form).href = `https://wa.me/201153886625?text=${encodeURIComponent(`${subject}\n\n${body}`)}`;
      alertBox.hidden = true;
      form.classList.add("is-done");
      done.hidden = false;
      done.focus();
      location.href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    };
    const showSent = () => {
      alertBox.hidden = true;
      form.classList.add("is-done");
      sent.hidden = false;
      sent.focus();
    };
    const busy = (on) => {
      submit.disabled = on;
      submit.setAttribute("aria-busy", String(on));
      submitLabel.textContent = on ? "Sending" : submitText;
    };

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      if (submit.disabled) return;
      const bad = $$("[required]", form).filter((input) => !check(input));
      if (bad.length) { bad[0].focus(); return; }
      const data = Object.fromEntries(new FormData(form));
      const honey = data._honey;
      delete data._honey;
      const message = compose(data);
      lastMessage = message;
      const endpoint = form.dataset.endpoint;
      if (!endpoint) { openEmail(message); return; }
      if (honey) { showSent(); return; }            // a bot filled the hidden field: accept quietly, send nothing
      alertBox.hidden = true;
      busy(true);
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 15000);
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ ...data, service: message.service, _subject: message.subject, _replyto: data.email }),
          signal: ctrl.signal,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        showSent();
      } catch (e) {
        alertBox.hidden = false;
      } finally {
        clearTimeout(timer);
        busy(false);
      }
    });

    $("[data-fallback]", form).addEventListener("click", () => { if (lastMessage) openEmail(lastMessage); });
    $("[data-again]", form).addEventListener("click", () => {
      form.reset();
      form.classList.remove("is-done");
      sent.hidden = true;
      $("#f-name", form).focus();
    });

    $("[data-edit]", form).addEventListener("click", () => {
      form.classList.remove("is-done");
      done.hidden = true;
      sent.hidden = true;
      $("#f-desc", form).focus();
    });
    const copyBtn = $("[data-copy]", form);
    const copyLabel = copyBtn.querySelector("span");
    const copyText = copyLabel.textContent;
    let copyTimer;
    copyBtn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(preview.textContent); copyLabel.textContent = "Copied"; }
      catch (e) { copyLabel.textContent = "Select the text above to copy"; }
      if (!reduced()) copyLabel.animate([{ opacity: 0, transform: "translateY(4px)" }, { opacity: 1, transform: "none" }], { duration: 160, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
      clearTimeout(copyTimer);
      copyTimer = setTimeout(() => { copyLabel.textContent = copyText; }, 2000);
    });
  }
})();
