const el = (id) => document.getElementById(id);

function pretty(v) {
  return JSON.stringify(v, null, 2);
}

function setHealth(ok, payload, ms) {
  el("healthValue").textContent = ok ? "OK" : "Unavailable";
  el("healthValue").className = "mt-2 text-base font-semibold " + (ok ? "text-emerald-300" : "text-rose-300");
  el("healthMeta").textContent = ok ? `Responded in ${ms}ms` : (payload?.detail ? String(payload.detail) : "Could not reach /health");
}

function setStatus(text) {
  el("statusLine").textContent = text;
}

function pathToLabel(method, path) {
  return `${method.toUpperCase()} ${path}`;
}

async function fetchJson(url) {
  const res = await fetch(url, { headers: { accept: "application/json" } });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }
  return { ok: res.ok, status: res.status, data };
}

function flattenOpenApiPaths(openapi) {
  const out = [];
  const paths = openapi.paths || {};
  for (const [path, methods] of Object.entries(paths)) {
    for (const [method, info] of Object.entries(methods)) {
      if (!info || typeof info !== "object") continue;
      if (["get", "post", "put", "delete", "patch"].includes(method)) {
        out.push({
          method,
          path,
          summary: info.summary || "",
          tags: info.tags || [],
          operationId: info.operationId || "",
          requestBody: info.requestBody || null,
          parameters: info.parameters || [],
        });
      }
    }
  }
  out.sort((a, b) => {
    const at = (a.tags[0] || "").localeCompare(b.tags[0] || "");
    if (at !== 0) return at;
    const ap = a.path.localeCompare(b.path);
    if (ap !== 0) return ap;
    return a.method.localeCompare(b.method);
  });
  return out;
}

function renderEndpointExplorer(items) {
  const select = el("endpointSelect");
  select.innerHTML = "";

  for (const it of items) {
    const opt = document.createElement("option");
    opt.value = `${it.method}:${it.path}`;
    opt.textContent = `${(it.tags[0] ? `[${it.tags[0]}] ` : "")}${pathToLabel(it.method, it.path)}`;
    select.appendChild(opt);
  }

  const show = () => {
    const v = select.value;
    const [method, path] = v.split(":");
    const it = items.find((x) => x.method === method && x.path === path);
    if (!it) return;

    el("endpointDetails").textContent = pretty({
      method: it.method.toUpperCase(),
      path: it.path,
      tags: it.tags,
      summary: it.summary,
      operationId: it.operationId,
      parameters: it.parameters,
      requestBody: it.requestBody,
    });
  };

  select.addEventListener("change", show);
  show();
}

async function refresh() {
  setStatus("Refreshing…");

  // health
  const t0 = performance.now();
  const health = await fetchJson("/health");
  const t1 = performance.now();
  setHealth(health.ok, health.data, Math.round(t1 - t0));

  // openapi
  const openapi = await fetchJson("/openapi.json");
  if (openapi.ok) {
    const items = flattenOpenApiPaths(openapi.data);
    el("endpointCount").textContent = `${items.length} operations`;
    renderEndpointExplorer(items);
  } else {
    el("endpointCount").textContent = "Unavailable";
    el("endpointDetails").textContent = pretty({ error: openapi.data });
  }

  setStatus("Ready.");
}

el("refreshBtn").addEventListener("click", refresh);
refresh();
