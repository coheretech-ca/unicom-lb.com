const menuButton = document.querySelector("[data-menu-toggle]");
const siteNav = document.querySelector("[data-site-nav]");

if (menuButton && siteNav) {
  menuButton.addEventListener("click", () => {
    const isOpen = siteNav.dataset.open === "true";
    siteNav.dataset.open = String(!isOpen);
    menuButton.setAttribute("aria-expanded", String(!isOpen));
  });
}

const demoTabs = [...document.querySelectorAll("[data-preview-tab]")];
const demoPanels = [...document.querySelectorAll("[data-preview-panel]")];

demoTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    demoTabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
    demoPanels.forEach((panel) => {
      panel.hidden = panel.id !== tab.getAttribute("aria-controls");
    });
  });
});

const manualSearch = document.querySelector("#manual-search");
const manualEntries = [...document.querySelectorAll("[data-manual-entry]")];
const manualCount = document.querySelector("#manual-search-count");
const clearSearch = document.querySelector("#clear-manual-search");

if (manualSearch && manualEntries.length) {
  const searchInput = manualSearch.querySelector("input[name='q']");
  const updateManualResults = (value) => {
    const query = value.trim().toLocaleLowerCase();
    let visible = 0;

    manualEntries.forEach((entry) => {
      const matches = !query || entry.dataset.search.includes(query);
      entry.hidden = !matches;
      if (matches) visible += 1;
    });

    if (manualCount) {
      manualCount.textContent = query
        ? `${visible} matching manual ${visible === 1 ? "page" : "pages"}`
        : `${manualEntries.length} pages from the 2019 manual`;
    }
  };

  searchInput.addEventListener("input", () => updateManualResults(searchInput.value));
  manualSearch.addEventListener("submit", (event) => {
    event.preventDefault();
    updateManualResults(searchInput.value);
  });
  clearSearch?.addEventListener("click", () => {
    searchInput.value = "";
    updateManualResults("");
    searchInput.focus();
  });

  const initialQuery = new URLSearchParams(window.location.search).get("q") || "";
  searchInput.value = initialQuery;
  updateManualResults(initialQuery);
}

const contactForm = document.querySelector("#contact-form");

if (contactForm) {
  contactForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!contactForm.reportValidity()) return;

    const formData = new FormData(contactForm);
    const subject = `UNICOM website inquiry: ${formData.get("topic")}`;
    const body = [
      `Name: ${formData.get("name")}`,
      `Email: ${formData.get("email")}`,
      `Topic: ${formData.get("topic")}`,
      "",
      formData.get("message"),
    ].join("\n");
    window.location.href = `mailto:info@unicom-lb.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
}
