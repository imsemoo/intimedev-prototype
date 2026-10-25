(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;

  // Header gains a rule once the page scrolls.
  const head = $("[data-head]");
  if (head) {
    const mark = document.createElement("div");
    mark.setAttribute("aria-hidden", "true");
    document.body.prepend(mark);
    new IntersectionObserver(([e]) => head.classList.toggle("is-scrolled", !e.isIntersecting)).observe(mark);
  }

  // Theme: system by default; the toggle stores an explicit choice.
  $$("[data-theme-toggle]").forEach((btn) => btn.addEventListener("click", () => {
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (e) { /* storage blocked: theme lasts this page */ }
  }));

  // Mobile menu: native modal dialog (focus trap, Escape and inert background come with it).
  const menu = $("[data-menu]");
  const openBtn = $("[data-menu-open]");
  if (menu && openBtn && typeof menu.showModal === "function") {
    openBtn.addEventListener("click", () => menu.showModal());
    $("[data-menu-close]", menu).addEventListener("click", () => menu.close());
    $$("a", menu).forEach((a) => a.addEventListener("click", () => menu.close()));
    menu.addEventListener("close", () => openBtn.focus());
    matchMedia("(min-width: 881px)").addEventListener("change", (m) => { if (m.matches && menu.open) menu.close(); });
  }

  // Sunrise reveal for content entering the viewport.
  const reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    }), { rootMargin: "0px 0px -6% 0px" });
    reveals.forEach((el) => io.observe(el));
  } else reveals.forEach((el) => el.classList.add("is-in"));

  // Day path: steps fill in as they pass the middle of the screen.
  $$("[data-day] li").forEach((li) => new IntersectionObserver(([e]) => { if (e.isIntersecting) li.classList.add("is-lit"); },
    { rootMargin: "0px 0px -45% 0px" }).observe(li));

  // Page loader: shown on internal navigation and kept on the next page until its fonts are ready.
  // It never delays navigation; the browser navigates at once and the loader only covers the wait.
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[href]");
    if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    if ((a.target && a.target !== "_self") || a.hasAttribute("download")) return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || !/^https?:$/.test(url.protocol)) return;
    if (url.pathname === location.pathname && url.search === location.search) return;
    try { sessionStorage.setItem("idv-nav", "1"); } catch (e) { /* storage blocked: no arrival cover */ }
    root.classList.add("is-leaving");
  });
  if (root.classList.contains("is-arriving")) {
    const fonts = document.fonts ? document.fonts.ready : Promise.resolve();
    Promise.race([fonts, new Promise((r) => setTimeout(r, 700))]).then(() => {
      setTimeout(() => root.classList.remove("is-arriving"), Math.max(0, 240 - performance.now()));
    });
  }
  // The back/forward cache can restore a page with the cover still on.
  window.addEventListener("pageshow", (ev) => { if (ev.persisted) root.classList.remove("is-leaving", "is-arriving"); });

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

    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const bad = $$("[required]", form).filter((input) => !check(input));
      if (bad.length) { bad[0].focus(); return; }
      const data = Object.fromEntries(new FormData(form));
      const service = select.value ? select.options[select.selectedIndex].text : "Not specified";
      const subject = `Project estimate request${data.company ? ` from ${data.company}` : ""}`;
      const body = [
        `Name: ${data.name}`, `Company: ${data.company || "-"}`, `Email: ${data.email}`, `Phone: ${data.phone || "-"}`,
        `Service: ${service}`, "", "Project description:", data.description,
      ].join("\n");
      preview.textContent = `To: ${email}\nSubject: ${subject}\n\n${body}`;
      $("[data-wa]", form).href = `https://wa.me/201153886625?text=${encodeURIComponent(`${subject}\n\n${body}`)}`;
      form.classList.add("is-done");
      done.hidden = false;
      done.focus();
      location.href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });

    $("[data-edit]", form).addEventListener("click", () => {
      form.classList.remove("is-done");
      done.hidden = true;
      $("#f-desc", form).focus();
    });
    $("[data-copy]", form).addEventListener("click", async (ev) => {
      const label = ev.currentTarget.querySelector("span");
      try { await navigator.clipboard.writeText(preview.textContent); label.textContent = "Copied"; }
      catch (e) { label.textContent = "Select the text above to copy"; }
    });
  }
})();
