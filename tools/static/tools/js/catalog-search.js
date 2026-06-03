(() => {
  const API_URL = "/api/search-catalog/";
  const CACHE_KEY = "amrxhub.searchCatalog.v1";
  const CACHE_TS_KEY = "amrxhub.searchCatalog.v1.ts";
  const CACHE_TTL = 24 * 60 * 60 * 1000;
  const MIN_QUERY_LENGTH = 3;
  const DEBOUNCE_MS = 300;

  const state = {
    catalog: [],
    searchTimer: null,
  };

  const els = {};

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function normalize(value) {
    return String(value ?? "").trim().toLowerCase();
  }

  function getCachedCatalog() {
    try {
      const cachedAt = Number(localStorage.getItem(CACHE_TS_KEY) || 0);
      const cachedPayload = localStorage.getItem(CACHE_KEY);
      if (!cachedPayload || !cachedAt) {
        return null;
      }
      if (Date.now() - cachedAt > CACHE_TTL) {
        return null;
      }
      return JSON.parse(cachedPayload);
    } catch {
      return null;
    }
  }

  function setCachedCatalog(catalog) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(catalog));
      localStorage.setItem(CACHE_TS_KEY, String(Date.now()));
    } catch {
      // Ignore storage failures and continue with in-memory search.
    }
  }

  async function fetchCatalog() {
    const response = await fetch(API_URL, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Catalog request failed with status ${response.status}`);
    }

    return response.json();
  }

  async function loadCatalog() {
    const cached = getCachedCatalog();
    if (cached) {
      return cached;
    }

    const freshCatalog = await fetchCatalog();
    setCachedCatalog(freshCatalog);
    return freshCatalog;
  }

  function collectUniqueValues(field, predicate = () => true) {
    const seen = new Map();
    state.catalog.filter(predicate).forEach((item) => {
      const value = item[field];
      if (!value) {
        return;
      }
      const key = normalize(value);
      if (!seen.has(key)) {
        seen.set(key, value);
      }
    });
    return Array.from(seen.values()).sort((left, right) => left.localeCompare(right));
  }

  function populateSelect(selectEl, values) {
    const currentValue = selectEl.value || "all";
    selectEl.innerHTML = `<option value="all">All</option>`;
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = normalize(value);
      option.textContent = value;
      selectEl.appendChild(option);
    });
    selectEl.value = values.some((value) => normalize(value) === currentValue) ? currentValue : "all";
  }

  function populateFilters() {
    populateSelect(els.typeFilter, collectUniqueValues("type"));
    populateSelect(els.categoryFilter, collectUniqueValues("category"));
    populateSelect(els.subcategoryFilter, collectUniqueValues("subcategory"));
    populateSelect(els.organismFilter, collectUniqueValues("organism"));
  }

  function matchesQuery(item, query) {
    if (query.length < MIN_QUERY_LENGTH) {
      return true;
    }

    const haystack = [
      item.name,
      item.description,
      item.category,
      item.subcategory,
      item.organism,
    ]
      .map(normalize)
      .join(" ");

    return haystack.includes(query);
  }

  function matchesFilters(item) {
    const typeValue = normalize(els.typeFilter.value);
    const categoryValue = normalize(els.categoryFilter.value);
    const subcategoryValue = normalize(els.subcategoryFilter.value);
    const organismValue = normalize(els.organismFilter.value);

    if (typeValue !== "all" && normalize(item.type) !== typeValue) {
      return false;
    }
    if (categoryValue !== "all" && normalize(item.category) !== categoryValue) {
      return false;
    }
    if (subcategoryValue !== "all" && normalize(item.subcategory) !== subcategoryValue) {
      return false;
    }
    if (organismValue !== "all" && normalize(item.organism) !== organismValue) {
      return false;
    }

    return true;
  }

  function filteredCatalog() {
    const query = normalize(els.searchInput.value);
    return state.catalog.filter((item) => matchesQuery(item, query) && matchesFilters(item));
  }

  function renderStatus(items) {
    if (!els.status) {
      return;
    }

    const query = normalize(els.searchInput.value);
    if (!state.catalog.length) {
      els.status.textContent = "No catalog data loaded.";
      return;
    }

    if (query.length > 0 && query.length < MIN_QUERY_LENGTH) {
      els.status.textContent = "Type at least 3 characters to search.";
      return;
    }

    els.status.textContent = `${items.length} result${items.length === 1 ? "" : "s"} found.`;
  }

  function renderResults(items) {
    if (!els.results) {
      return;
    }

    if (!items.length) {
      els.results.innerHTML = `
        <div class="no-categories">
          <i class="fas fa-search"></i>
          <h3>No matches found</h3>
          <p>Try a different keyword or adjust the filters.</p>
        </div>
      `;
      renderStatus(items);
      return;
    }

    els.results.innerHTML = `
      <div class="categories-grid">
        ${items.map((item) => `
          <div class="category-card" style="background: #f8f9fa; color: #222; text-align: left;">
            <div style="display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:10px;">
              <span class="category-badge">${escapeHtml(item.type)}</span>
              ${item.url ? `<a href="${escapeHtml(item.url)}" class="admin-btn">Open</a>` : ""}
            </div>
            <h3 style="margin-top:0;">${escapeHtml(item.name)}</h3>
            <p>${escapeHtml(item.description || "")}</p>
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;">
              <span class="tool-count">${escapeHtml(item.category || "Uncategorized")}</span>
              ${item.subcategory ? `<span class="tool-count">${escapeHtml(item.subcategory)}</span>` : ""}
              ${item.organism ? `<span class="tool-count">${escapeHtml(item.organism)}</span>` : ""}
            </div>
          </div>
        `).join("")}
      </div>
    `;

    renderStatus(items);
  }

  function scheduleRender() {
    clearTimeout(state.searchTimer);
    state.searchTimer = setTimeout(() => {
      renderResults(filteredCatalog());
    }, DEBOUNCE_MS);
  }

  function bindEvents() {
    els.searchInput.addEventListener("input", scheduleRender);

    [els.typeFilter, els.categoryFilter, els.subcategoryFilter, els.organismFilter].forEach((selectEl) => {
      selectEl.addEventListener("change", () => {
        renderResults(filteredCatalog());
      });
    });

    els.clearButton.addEventListener("click", () => {
      els.searchInput.value = "";
      els.typeFilter.value = "all";
      els.categoryFilter.value = "all";
      els.subcategoryFilter.value = "all";
      els.organismFilter.value = "all";
      renderResults(state.catalog);
    });
  }

  async function init() {
    els.searchInput = $("tool-search");
    els.typeFilter = $("filter-type");
    els.categoryFilter = $("filter-category");
    els.subcategoryFilter = $("filter-subcategory");
    els.organismFilter = $("filter-organism");
    els.results = $("catalog-results");
    els.status = $("catalog-status");
    els.clearButton = $("clear-search");

    if (!els.searchInput || !els.typeFilter || !els.categoryFilter || !els.subcategoryFilter || !els.organismFilter || !els.results) {
      return;
    }

    try {
      state.catalog = await loadCatalog();
      populateFilters();
      renderResults(state.catalog);
      bindEvents();
    } catch (error) {
      if (els.status) {
        els.status.textContent = "Unable to load catalog data.";
      }
      console.error(error);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();