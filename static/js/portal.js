(() => {
  // Home slideshow: crossfades every 6s, pauses on hover/focus, honours reduced motion.
  const slider = document.querySelector("[data-slider]");
  if (slider) {
    const slides = [...slider.querySelectorAll(".slide")];
    const dots = [...slider.querySelectorAll(".dots button")];
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let index = 0;
    let timer;

    const show = (n) => {
      index = (n + slides.length) % slides.length;
      slides.forEach((s, k) => {
        s.classList.toggle("is-active", k === index);
        s.inert = k !== index;
      });
      dots.forEach((d, k) => (k === index ? d.setAttribute("aria-current", "true") : d.removeAttribute("aria-current")));
    };
    const play = () => {
      clearInterval(timer);
      if (!reduce && slides.length > 1) timer = setInterval(() => show(index + 1), 6000);
    };
    const pause = () => clearInterval(timer);

    dots.forEach((d, k) => d.addEventListener("click", () => { show(k); play(); }));
    slider.addEventListener("mouseenter", pause);
    slider.addEventListener("mouseleave", play);
    slider.addEventListener("focusin", pause);
    slider.addEventListener("focusout", play);
    document.addEventListener("visibilitychange", () => (document.hidden ? pause() : play()));
    show(0);
    play();
  }

  // Confirm destructive dashboard actions.
  for (const f of document.querySelectorAll("form[data-confirm]")) {
    f.addEventListener("submit", (e) => { if (!confirm(f.dataset.confirm)) e.preventDefault(); });
  }

  // Top-bar Services menu: close on outside click or Escape.
  const navMenu = document.querySelector("[data-nav-menu]");
  if (navMenu) {
    document.addEventListener("click", (e) => { if (!navMenu.contains(e.target)) navMenu.open = false; });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && navMenu.open) { navMenu.open = false; navMenu.querySelector("summary").focus(); }
    });
  }

  // Toasts fade after a few seconds.
  for (const t of document.querySelectorAll("[data-toast]")) {
    setTimeout(() => t.remove(), 6000);
  }
})();
