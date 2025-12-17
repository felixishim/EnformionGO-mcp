/* Modern, minimal UI logic (no build step). */

const ENDPOINTS = [
  {
    id: "contact-enrichment",
    label: "Contact Enrichment",
    method: "POST",
    path: "/contact-enrichment",
    help: "Requires at least two criteria: name, phone, address, or email.",
    schema: [
      { key: "first_name", label: "First name", type: "text" },
      { key: "middle_name", label: "Middle name", type: "text" },
      { key: "last_name", label: "Last name", type: "text" },
      { key: "dob", label: "DOB", type: "text", placeholder: "MM/DD/YYYY" },
      { key: "age", label: "Age", type: "number" },
      { key: "phone", label: "Phone", type: "text" },
      { key: "email", label: "Email", type: "text" },
      { key: "address.address_line_1", label: "Address line 1", type: "text" },
      { key: "address.address_line_2", label: "Address line 2", type: "text" },
    ],
    sample: {
      FirstName: "John",
      LastName: "Smith",
      Phone: "(555) 555-5555",
    },
  },
  {
    id: "person-search",
    label: "Person Search",
    method: "POST",
    path: "/person-search",
    help: "Set galaxy-search-type header to Person or Teaser (default Person).",
    schema: [
      { key: "first_name", label: "First name", type: "text" },
      { key: "middle_name", label: "Middle name", type: "text" },
      { key: "last_name", label: "Last name", type: "text" },
      { key: "dob", label: "DOB", type: "text", placeholder: "MM/DD/YYYY" },
      { key: "ssn", label: "SSN", type: "text" },
      { key: "email", label: "Email", type: "text" },
      { key: "phone", label: "Phone", type: "text" },
      { key: "addresses.0.address_line_1", label: "Address line 1", type: "text" },
      { key: "addresses.0.address_line_2", label: "Address line 2", type: "text" },
      { key: "addresses.0.county", label: "County", type: "text" },
    ],
    sample: {
      FirstName: "Test",
      LastName: "Test",
      Phone: "(123) 456-7890",
    },
  },
  {
    id: "reverse-phone-search",
    label: "Reverse Phone Search",
    method: "POST",
    path: "/reverse-phone-search",
    help: "Body uses PhoneNumber per docs. (Legacy Phone is accepted too.)",
    schema: [{ key: "phone_number", label: "PhoneNumber", type: "text", placeholder: "(123) 456-7890" }],
    sample: { PhoneNumber: "(123) 456-7890" },
  },
  {
    id: "caller-id",
    label: "Caller ID",
    method: "POST",
    path: "/caller-id",
    help: "Phone enrichment.",
    schema: [{ key: "phone", label: "Phone", type: "text" }],
    sample: { Phone: "(123) 456-7890" },
  },
  {
    id: "email-id",
    label: "Email ID",
    method: "POST",
    path: "/email-id",
    help: "Email enrichment.",
    schema: [{ key: "email", label: "Email", type: "text" }],
    sample: { Email: "test@example.com" },
  },
  {
    id: "contact-id",
    label: "Contact ID",
    method: "POST",
    path: "/contact-id",
    help: "Lookup by PersonId.",
    schema: [{ key: "person_id", label: "PersonId", type: "text" }],
    sample: { PersonId: "G###############" },
  },
  {
    id: "address-autocomplete",
    label: "Address AutoComplete",
    method: "POST",
    path: "/address-autocomplete",
    help: "Search type defaults to AddressSearch.",
    schema: [{ key: "input_str", label: "Input", type: "text", placeholder: "1821 Q St Merced" }],
    sample: { Input: "1821 Q St Merced" },
  },
  {
    id: "property-search-v2",
    label: "Property V2 Search",
    method: "POST",
    path: "/property-search-v2",
    help: "Defaults galaxy-search-type to PropertyV2Search.",
    schema: [
      { key: "address_line_1", label: "addressLine1", type: "text" },
      { key: "address_line_2", label: "addressLine2", type: "text" },
      { key: "city", label: "city", type: "text" },
      { key: "state", label: "state", type: "text" },
      { key: "zip_code", label: "zipCode", type: "text" },
      { key: "apn", label: "apn", type: "text" },
    ],
    sample: { addressLine1: "1234 Apple Ct", city: "Merced", state: "CA" },
  },
  {
    id: "business-search",
    label: "Business V2 Search",
    method: "POST",
    path: "/business-search",
    help: "Defaults galaxy-search-type to BusinessV2Search.",
    schema: [
      { key: "business_name", label: "businessName", type: "text" },
      { key: "address_line_1", label: "addressLine1", type: "text" },
      { key: "city", label: "city", type: "text" },
      { key: "state", label: "state", type: "text" },
    ],
    sample: { businessName: "Acme" },
  },
  {
    id: "domain-search",
    label: "Domain Search",
    method: "POST",
    path: "/domain-search",
    help: "Defaults galaxy-search-type to DomainSearch.",
    schema: [{ key: "domain", label: "domain", type: "text", placeholder: "example.com" }],
    sample: { domain: "example.com" },
  },
  {
    id: "workplace-search",
    label: "Workplace Search",
    method: "POST",
    path: "/workplace-search",
    help: "Defaults galaxy-search-type to WorkplaceSearch.",
    schema: [
      { key: "business_name", label: "businessName", type: "text" },
      { key: "first_name", label: "firstName", type: "text" },
      { key: "last_name", label: "lastName", type: "text" },
      { key: "city", label: "city", type: "text" },
      { key: "state", label: "state", type: "text" },
    ],
    sample: { businessName: "Acme", state: "CA" },
  },
  {
    id: "id-verification",
    label: "ID Verification",
    method: "POST",
    path: "/id-verification",
    help: "Requires at least two criteria. Defaults galaxy-search-type to DevAPIIDVerification.",
    schema: [
      { key: "first_name", label: "FirstName", type: "text" },
      { key: "last_name", label: "LastName", type: "text" },
      { key: "dob", label: "Dob", type: "text", placeholder: "MM/DD/YYYY" },
      { key: "ssn", label: "Ssn", type: "text" },
      { key: "phones.0", label: "Phones[0]", type: "text" },
      { key: "emails.0", label: "Emails[0]", type: "text" },
      { key: "address_line_1", label: "AddressLine1", type: "text" },
      { key: "address_line_2", label: "AddressLine2", type: "text" },
    ],
    sample: { FirstName: "John", LastName: "Doe", Phones: ["(123) 456-7890"] },
  },
  {
    id: "generic-criminal-search-v2",
    label: "Criminal Search V2 (generic)",
    method: "POST",
    path: "/criminal-search-v2",
    help: "Generic JSON body; use docs fields for best results.",
    schema: [],
    sample: {},
  },
  {
    id: "data-alerts-add-subscription",
    label: "Data Alerts: Add Subscription (generic)",
    method: "POST",
    path: "/data-alerts/add-subscription",
    help: "Generic JSON body; see docs for request schema.",
    schema: [],
    sample: {},
  },
];

const el = (id) => document.getElementById(id);

function setStatus(text, type = "info") {
  const node = el("status");
  node.textContent = text;
  node.className = "text-xs " + (type === "error" ? "text-rose-300" : type === "ok" ? "text-emerald-300" : "text-slate-400");
}

function pretty(v) {
  return JSON.stringify(v, null, 2);
}

function safeJsonParse(str) {
  try {
    return { ok: true, value: JSON.parse(str) };
  } catch (e) {
    return { ok: false, error: e };
  }
}

function setDeep(obj, path, value) {
  const parts = path.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    const isLast = i === parts.length - 1;

    // array index support
    const m = /^(.+)\[(\d+)\]$/.exec(p);
    if (m) {
      const k = m[1];
      const idx = Number(m[2]);
      cur[k] = cur[k] ?? [];
      while (cur[k].length <= idx) cur[k].push({});
      if (isLast) {
        cur[k][idx] = value;
      } else {
        cur = cur[k][idx] ?? (cur[k][idx] = {});
      }
      continue;
    }

    // dot numeric index support: foo.0.bar
    if (/^\d+$/.test(p)) {
      const idx = Number(p);
      if (!Array.isArray(cur)) {
        // convert object to array only if safe-ish
      }
      if (isLast) {
        cur[idx] = value;
      } else {
        cur[idx] = cur[idx] ?? {};
        cur = cur[idx];
      }
      continue;
    }

    if (isLast) {
      cur[p] = value;
    } else {
      cur[p] = cur[p] ?? {};
      cur = cur[p];
    }
  }
}

function buildBodyFromForm(endpoint) {
  const out = {};
  for (const f of endpoint.schema) {
    const input = el(`field_${endpoint.id}_${f.key}`);
    if (!input) continue;
    const raw = input.value;
    if (raw === "" || raw == null) continue;

    let v = raw;
    if (f.type === "number") {
      const n = Number(raw);
      if (!Number.isNaN(n)) v = n;
    }

    // translate snake_case-ish to wrapper model keys; wrapper handles aliases.
    setDeep(out, f.key, v);
  }
  return out;
}

function headersFromUI(endpoint) {
  const headers = {
    "content-type": "application/json",
  };

  const apName = el("apName").value.trim();
  const apPassword = el("apPassword").value;
  const searchType = el("searchType").value.trim();
  const clientSessionId = el("clientSessionId").value.trim();
  const clientType = el("clientType").value.trim();

  if (apName) headers["galaxy-ap-name"] = apName;
  if (apPassword) headers["galaxy-ap-password"] = apPassword;
  if (searchType) headers["galaxy-search-type"] = searchType;
  if (clientSessionId) headers["galaxy-client-session-id"] = clientSessionId;
  if (clientType) headers["galaxy-client-type"] = clientType;

  return headers;
}

function endpointById(id) {
  return ENDPOINTS.find((e) => e.id === id) ?? ENDPOINTS[0];
}

function setMode(mode) {
  const isForm = mode === "form";
  el("formContainer").classList.toggle("hidden", !isForm);
  el("jsonContainer").classList.toggle("hidden", isForm);

  el("modeForm").classList.toggle("bg-white/5", isForm);
  el("modeJson").classList.toggle("bg-white/5", !isForm);

  // keep json in sync when switching
  const endpoint = endpointById(el("endpointSelect").value);
  if (!isForm) {
    const body = buildBodyFromForm(endpoint);
    el("jsonBody").value = pretty(body);
  } else {
    // no-op: form remains source of truth
  }
}

function renderForm(endpoint) {
  const c = el("formContainer");
  c.innerHTML = "";

  if (!endpoint.schema.length) {
    const div = document.createElement("div");
    div.className = "rounded-xl border border-white/10 bg-slate-950/40 p-3 text-xs text-slate-300";
    div.textContent = "This endpoint uses a generic JSON body. Switch to JSON mode and paste the request body from the docs.";
    c.appendChild(div);
    return;
  }

  for (const f of endpoint.schema) {
    const wrap = document.createElement("div");
    wrap.className = "";

    const label = document.createElement("label");
    label.className = "text-xs font-medium text-slate-300";
    label.textContent = f.label;

    const input = document.createElement("input");
    input.id = `field_${endpoint.id}_${f.key}`;
    input.type = f.type === "number" ? "number" : "text";
    input.placeholder = f.placeholder ?? "";
    input.className =
      "mt-2 w-full rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none ring-cyan-400/20 focus:ring-4";

    wrap.appendChild(label);
    wrap.appendChild(input);
    c.appendChild(wrap);
  }
}

function setEndpoint(endpoint) {
  el("endpointHelp").textContent = `${endpoint.method} ${endpoint.path} — ${endpoint.help}`;
  renderForm(endpoint);
  el("jsonBody").value = pretty(endpoint.sample ?? {});
  setStatus("Ready.");
}

function buildCurl(endpoint, body, headers) {
  const parts = ["curl", "-sS", "-X", endpoint.method, JSON.stringify(location.origin + endpoint.path)];
  for (const [k, v] of Object.entries(headers)) {
    if (!v) continue;
    parts.push("-H", JSON.stringify(`${k}: ${v}`));
  }
  parts.push("--data", JSON.stringify(JSON.stringify(body)));
  return parts.join(" ");
}

async function send(endpoint) {
  el("sendBtn").disabled = true;
  setStatus("Sending…");

  const headers = headersFromUI(endpoint);

  let body;
  if (!el("jsonContainer").classList.contains("hidden")) {
    const parsed = safeJsonParse(el("jsonBody").value || "{}");
    if (!parsed.ok) {
      setStatus(`Invalid JSON: ${parsed.error.message}`, "error");
      el("sendBtn").disabled = false;
      return;
    }
    body = parsed.value;
  } else {
    body = buildBodyFromForm(endpoint);
  }

  // sync remembered creds
  syncCredStorage();

  try {
    const res = await fetch(endpoint.path, {
      method: endpoint.method,
      headers,
      body: JSON.stringify(body),
    });

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }

    const payload = {
      ok: res.ok,
      status: res.status,
      statusText: res.statusText,
      data,
    };

    el("responseBox").textContent = pretty(payload);
    setStatus(res.ok ? `Success (${res.status})` : `Error (${res.status})`, res.ok ? "ok" : "error");
  } catch (e) {
    el("responseBox").textContent = pretty({ ok: false, error: String(e) });
    setStatus(`Network error: ${String(e)}`, "error");
  } finally {
    el("sendBtn").disabled = false;
  }
}

function syncCredStorage() {
  const remember = el("rememberCreds").checked;
  const key = "enformiongo_ui_creds_v1";

  if (!remember) {
    localStorage.removeItem(key);
    return;
  }

  const data = {
    apName: el("apName").value,
    apPassword: el("apPassword").value,
  };
  localStorage.setItem(key, JSON.stringify(data));
}

function loadCredStorage() {
  const key = "enformiongo_ui_creds_v1";
  const raw = localStorage.getItem(key);
  if (!raw) return;
  const parsed = safeJsonParse(raw);
  if (!parsed.ok) return;
  el("rememberCreds").checked = true;
  el("apName").value = parsed.value.apName ?? "";
  el("apPassword").value = parsed.value.apPassword ?? "";
}

function copyToClipboard(text) {
  return navigator.clipboard.writeText(text);
}

function init() {
  // populate endpoint selector
  const select = el("endpointSelect");
  for (const ep of ENDPOINTS) {
    const opt = document.createElement("option");
    opt.value = ep.id;
    opt.textContent = ep.label;
    select.appendChild(opt);
  }

  loadCredStorage();

  // default endpoint
  setEndpoint(ENDPOINTS[0]);

  select.addEventListener("change", () => {
    setEndpoint(endpointById(select.value));
  });

  el("modeForm").addEventListener("click", () => setMode("form"));
  el("modeJson").addEventListener("click", () => setMode("json"));
  setMode("form");

  el("formatJsonBtn").addEventListener("click", () => {
    const parsed = safeJsonParse(el("jsonBody").value || "{}");
    if (!parsed.ok) {
      setStatus(`Invalid JSON: ${parsed.error.message}`, "error");
      return;
    }
    el("jsonBody").value = pretty(parsed.value);
    setStatus("Formatted.", "ok");
  });

  el("resetBtn").addEventListener("click", () => {
    const ep = endpointById(select.value);
    setEndpoint(ep);
    setMode("form");
  });

  el("sendBtn").addEventListener("click", () => send(endpointById(select.value)));

  el("copyCurlBtn").addEventListener("click", async () => {
    const ep = endpointById(select.value);
    const headers = headersFromUI(ep);
    const body = !el("jsonContainer").classList.contains("hidden")
      ? (safeJsonParse(el("jsonBody").value || "{}").value ?? {})
      : buildBodyFromForm(ep);

    const curl = buildCurl(ep, body, headers);
    try {
      await copyToClipboard(curl);
      setStatus("Copied cURL.", "ok");
    } catch (e) {
      setStatus(`Could not copy: ${String(e)}`, "error");
    }
  });

  el("copyResponseBtn").addEventListener("click", async () => {
    try {
      await copyToClipboard(el("responseBox").textContent || "");
      setStatus("Copied response.", "ok");
    } catch (e) {
      setStatus(`Could not copy: ${String(e)}`, "error");
    }
  });

  el("rememberCreds").addEventListener("change", syncCredStorage);
  el("apName").addEventListener("input", () => el("rememberCreds").checked && syncCredStorage());
  el("apPassword").addEventListener("input", () => el("rememberCreds").checked && syncCredStorage());

  el("togglePassword").addEventListener("click", () => {
    const i = el("apPassword");
    const show = i.type === "password";
    i.type = show ? "text" : "password";
    el("togglePassword").textContent = show ? "Hide" : "Show";
  });
}

init();
