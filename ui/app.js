// Worlds viewer: pick a run, then read its days, agents, records, generation, code and prompt.
// Everything from a run is rendered as text nodes, never as HTML.

const state = {
  worlds: [],
  runId: null,
  run: null,
  tab: null,
  agent: null,
  hideQuiet: false,
  recordFilter: "",
  file: null,
  timer: null,
};

const PALETTE = 8;
const LIVE_POLL_MS = 4000;
const $ = (selector) => document.querySelector(selector);

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value == null || value === false) continue;
    if (key === "class") el.className = value;
    else if (key === "style") el.style.cssText = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid instanceof Node ? kid : String(kid));
  }
  return el;
}

// ---------- formatting ----------

function statusInfo(status) {
  if (!status) return { label: "no summary", kind: "" };
  if (status === "finished") return { label: "finished", kind: "ok" };
  if (status === "running") return { label: "running", kind: "live" };
  if (status.includes("dry run")) return { label: "dry run failed", kind: "bad" };
  if (status.includes("crashed")) return { label: "world crashed", kind: "bad" };
  return { label: "stopped", kind: "warn" };
}

function parseDate(iso) {
  const d = new Date(`${String(iso).slice(0, 10)}T00:00:00`);
  return Number.isNaN(d.getTime()) ? null : d;
}

function dayLabel(iso) {
  const d = parseDate(iso);
  if (!d) return String(iso);
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}

function rangeLabel(first, last) {
  const a = parseDate(first);
  const b = parseDate(last);
  if (!a) return "—";
  const short = { month: "short", day: "numeric" };
  if (!b || first === last) return a.toLocaleDateString("en-US", { ...short, year: "numeric" });
  return `${a.toLocaleDateString("en-US", short)} → ${b.toLocaleDateString("en-US", { ...short, year: "numeric" })}`;
}

function whenLabel(seconds) {
  const d = new Date(seconds * 1000);
  return d.toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function money(value) {
  return value == null ? "—" : `$${Number(value).toFixed(2)}`;
}

function sizeLabel(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function lastLine(text) {
  const lines = String(text || "").trim().split("\n").filter((line) => line.trim());
  return lines.length ? lines[lines.length - 1].trim() : "";
}

function agentColor(agent) {
  const index = state.run?.agentIds.indexOf(agent) ?? -1;
  return index < 0 ? "var(--faint)" : `var(--a${index % PALETTE})`;
}

function pill(status) {
  const info = statusInfo(status);
  return h("span", { class: `pill ${info.kind}` }, info.label);
}

// ---------- hash ----------

function readHash() {
  const params = new URLSearchParams(location.hash.slice(1));
  return { run: params.get("run"), tab: params.get("tab"), agent: params.get("agent") };
}

function writeHash() {
  const params = new URLSearchParams();
  if (state.runId) params.set("run", state.runId);
  if (state.tab) params.set("tab", state.tab);
  if (state.agent) params.set("agent", state.agent);
  history.replaceState(null, "", `#${params}`);
}

// ---------- data ----------

async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

function prepare(data) {
  const events = data.events.filter((event) => typeof event.type === "string");
  data.generates = events.filter((event) => event.type === "generate");
  const days = [];
  const byDate = new Map();
  const tail = [];
  for (const event of events) {
    if (event.type === "day") {
      const day = { date: event.date, agents: event.agents || [], unknown: event.unknown || [], turns: new Map(), crashes: [] };
      days.push(day);
      byDate.set(event.date, day);
      continue;
    }
    if (!["call", "turn", "turn_failed", "crash"].includes(event.type)) continue;
    const day = event.date != null ? byDate.get(event.date) : null;
    if (!day) {
      if (event.type === "crash") tail.push(event);
      continue;
    }
    if (!event.agent) {
      day.crashes.push(event);
      continue;
    }
    if (!day.turns.has(event.agent)) {
      day.turns.set(event.agent, { agent: event.agent, calls: [], end: null, failed: null, crashes: [] });
    }
    const turn = day.turns.get(event.agent);
    if (event.type === "call") turn.calls.push(event);
    else if (event.type === "turn") turn.end = event;
    else if (event.type === "turn_failed") turn.failed = event;
    else turn.crashes.push(event);
  }
  data.days = days;
  data.tail = tail;
  data.agents = data.prompts?.agents && typeof data.prompts.agents === "object" ? data.prompts.agents : {};
  const ids = Object.keys(data.agents);
  for (const day of days) {
    for (const agent of [...day.agents, ...day.turns.keys()]) if (!ids.includes(agent)) ids.push(agent);
  }
  data.agentIds = ids;
  data.legacy = data.files.some((file) => file.name === "tree.json" || file.name === "story.md");
  return data;
}

function tableCount(records) {
  let rows = 0;
  for (const entity of Object.values(records || {})) {
    if (!entity || typeof entity !== "object") continue;
    for (const value of Object.values(entity)) rows += Array.isArray(value) ? value.length : 1;
  }
  return rows;
}

const TABS = [
  { id: "days", label: "Days", count: (d) => d.days.length, show: (d) => d.days.length || d.tail.length },
  { id: "agents", label: "Agents", count: (d) => d.agentIds.length, show: (d) => d.agentIds.length },
  { id: "records", label: "Records", count: (d) => tableCount(d.records), show: (d) => d.records && typeof d.records === "object" },
  { id: "generation", label: "Generation", count: (d) => d.generates.length, show: (d) => d.generates.length || d.stderr },
  { id: "code", label: "world.py", count: (d) => d.world_py.split("\n").length, show: (d) => d.world_py != null },
  { id: "prompt", label: "Prompt", count: () => null, show: (d) => d.prompt_text != null },
  { id: "files", label: "Files", count: (d) => d.files.length, show: () => true },
];

function visibleTabs() {
  return state.run ? TABS.filter((tab) => tab.show(state.run)) : [];
}

// ---------- loading ----------

async function loadWorlds() {
  state.worlds = await getJson("/api/worlds");
  const select = $("#run-select");
  select.replaceChildren();
  for (const world of state.worlds) {
    const group = h("optgroup", { label: world.world });
    for (const run of world.runs) {
      const bits = [run.name, statusInfo(run.status).label];
      if (run.cost_usd != null) bits.push(money(run.cost_usd));
      bits.push(whenLabel(run.modified));
      group.append(h("option", { value: run.id }, bits.join("  ·  ")));
    }
    select.append(group);
  }
  if (state.runId) select.value = state.runId;
}

function newestRunId() {
  let best = null;
  for (const world of state.worlds) {
    for (const run of world.runs) if (!best || run.modified > best.modified) best = run;
  }
  return best?.id ?? null;
}

async function selectRun(id, { keepView = false } = {}) {
  clearTimeout(state.timer);
  if (!keepView) {
    state.agent = null;
    state.file = null;
    state.recordFilter = "";
  }
  state.runId = id;
  $("#run-select").value = id;
  try {
    state.run = prepare(await getJson(`/api/run?id=${encodeURIComponent(id)}`));
  } catch (error) {
    state.run = null;
    $("#summary").replaceChildren(h("div", { class: "placeholder" }, `Could not load ${id}: ${error.message}`));
    $("#tabs").replaceChildren();
    $("#view").replaceChildren();
    return;
  }
  const ids = visibleTabs().map((tab) => tab.id);
  if (!ids.includes(state.tab)) {
    state.tab = state.run.legacy ? "files" : ["days", "generation"].find((id) => ids.includes(id)) ?? ids[0];
  }
  if (state.agent && !state.run.agentIds.includes(state.agent)) state.agent = null;
  const y = window.scrollY;
  render();
  if (keepView) window.scrollTo(0, y);
  $("#live").hidden = !state.run.live;
  if (state.run.live) {
    state.timer = setTimeout(async () => {
      await loadWorlds().catch(() => {});
      selectRun(state.runId, { keepView: true });
    }, LIVE_POLL_MS);
  }
}

// ---------- render ----------

function render() {
  writeHash();
  renderSummary();
  renderTabs();
  const view = $("#view");
  const renderers = { days: viewDays, agents: viewAgents, records: viewRecords, generation: viewGeneration, code: viewCode, prompt: viewPrompt, files: viewFiles };
  view.replaceChildren(renderers[state.tab]());
}

function fact(label, value, small = false) {
  return h("div", null, h("dt", null, label), h("dd", { class: small ? "small" : null }, value ?? "—"));
}

function renderSummary() {
  const d = state.run;
  const [world, ...rest] = d.id.split("/");
  const run = d.run || {};
  const status = run.status || (d.live ? "running" : null);
  const calls = run.calls ?? d.events.filter((e) => e.type === "call").length;
  const generated = d.generates.length
    ? d.generates[d.generates.length - 1].problem == null
      ? `passed on try ${d.generates.length}`
      : `failed ${d.generates.length} ${d.generates.length === 1 ? "try" : "tries"}`
    : null;
  const first = run.first_date ?? d.days[0]?.date;
  const last = run.last_date ?? d.days[d.days.length - 1]?.date;
  const facts = [];
  if (first) facts.push(fact("Simulated", `${rangeLabel(first, last)}  (${d.days.length} ${d.days.length === 1 ? "day" : "days"})`));
  if (generated) facts.push(fact("Dry run", generated));
  if (d.days.length || run.calls != null) {
    facts.push(fact("Agent calls", calls));
    facts.push(fact("Turns", run.turns ?? d.events.filter((e) => e.type === "turn").length));
    facts.push(fact("Crashes", run.crashes ?? d.events.filter((e) => e.type === "crash" || e.crash).length));
  }
  if (run.failed_turns) facts.push(fact("Failed turns", run.failed_turns));
  if (run.cost_usd != null) facts.push(fact("Cost", money(run.cost_usd)));
  if (run.world_model) facts.push(fact("World model", run.world_model, true));
  if (run.agent_model) facts.push(fact("Agent model", run.agent_model, true));
  if (run.prompt) facts.push(fact("Prompt", run.prompt, true));
  if (!facts.length) facts.push(fact("Files", d.files.length));

  $("#summary").replaceChildren(
    h("div", { class: "summary" },
      h("div", { class: "title-row" },
        h("h1", null, h("span", { class: "world" }, `${world} / `), rest.join("/") || "(top)"),
        d.legacy ? h("span", { class: "pill" }, "narrator run") : pill(status),
      ),
      status && !["finished", "running"].includes(status) ? h("p", { class: "status-text" }, status) : null,
      d.legacy ? h("p", { class: "status-text" }, "An older narrator run: its files are shown as they are.") : null,
      !d.run && !d.live && !d.legacy ? h("p", { class: "status-text" }, "No run.json: this run stopped before writing its summary.") : null,
      h("dl", { class: "facts" }, facts),
    ),
  );
}

function renderTabs() {
  $("#tabs").replaceChildren(
    ...visibleTabs().map((tab) => {
      const count = tab.count(state.run);
      return h("button", {
        type: "button",
        role: "tab",
        "aria-selected": String(tab.id === state.tab),
        onclick: () => {
          state.tab = tab.id;
          render();
        },
      }, tab.label, count != null ? h("span", { class: "count" }, count) : null);
    }),
  );
}

// ----- Days -----

function argsView(args) {
  if (args == null) return h("span", { class: "faint" }, "(bad arguments)");
  const entries = Object.entries(args);
  if (!entries.length) return h("span", { class: "faint" }, "()");
  return h("span", { class: "args mono" },
    entries.map(([key, value]) =>
      h("span", { class: "arg" }, h("span", { class: "k" }, key), typeof value === "string" ? value : JSON.stringify(value)),
    ),
  );
}

function crashBox(title, error) {
  return h("details", { class: "crash" },
    h("summary", null, `${title}: ${lastLine(error) || "no message"}`),
    h("pre", null, String(error || "")),
  );
}

function isErrorResult(text) {
  return /^(error|rejected|failed|skipped)\b/i.test(String(text || "").trim());
}

function turnView(day, turn) {
  const entity = state.run.agents[turn.agent]?.entity;
  const c = agentColor(turn.agent);
  let previousWhy = null;
  const calls = turn.calls.map((call) => {
    const why = (call.why || "").trim();
    const showWhy = why && why !== previousWhy;
    previousWhy = why;
    return h("li", { class: "call" },
      showWhy ? h("div", { class: "call-why" }, why) : null,
      h("div", { class: "call-line" },
        h("code", { class: "tool" }, call.tool),
        argsView(call.args),
        call.entity ? h("span", { class: "tag" }, call.entity) : null,
      ),
      h("div", { class: `call-result${isErrorResult(call.result) ? " err" : ""}` }, call.result ?? ""),
      call.crash ? crashBox("World code crashed", call.crash) : null,
    );
  });
  const callCount = turn.end?.calls ?? turn.calls.length;
  return h("div", { class: "turn", style: `--c: ${c}` },
    h("div", { class: "turn-head" },
      h("span", { class: "agent-name" }, turn.agent),
      entity ? h("span", { class: "tag" }, entity) : null,
      h("span", { class: "faint" }, callCount === 0 ? "no calls" : `${callCount} ${callCount === 1 ? "call" : "calls"}`),
    ),
    calls.length ? h("ol", { class: "calls" }, calls) : null,
    turn.crashes.map((crash) => crashBox("World code crashed", crash.error)),
    turn.failed ? crashBox("Turn failed", turn.failed.error) : null,
    turn.end ? h("div", { class: "notepad" }, h("span", { class: "label" }, "Notepad for tomorrow"), turn.end.notepad || "(empty)") : null,
  );
}

function viewDays() {
  const d = state.run;
  const agentsWithTurns = d.agentIds.filter((agent) => d.days.some((day) => day.turns.has(agent)));
  const toolbar = h("div", { class: "toolbar" },
    h("button", {
      type: "button", class: "chip", "aria-pressed": String(!state.agent),
      onclick: () => { state.agent = null; render(); },
    }, "All agents"),
    agentsWithTurns.map((agent) =>
      h("button", {
        type: "button", class: "chip", "aria-pressed": String(state.agent === agent), style: `--c: ${agentColor(agent)}`,
        onclick: () => { state.agent = state.agent === agent ? null : agent; render(); },
      }, h("span", { class: "dot" }), agent),
    ),
    h("label", { class: "toggle" },
      h("input", {
        type: "checkbox", checked: state.hideQuiet,
        onchange: (event) => { state.hideQuiet = event.target.checked; render(); },
      }),
      "Hide quiet days",
    ),
  );

  const list = h("div", { class: "days" });
  for (const day of d.days) {
    const order = [...day.agents, ...[...day.turns.keys()].filter((a) => !day.agents.includes(a))];
    const turns = order.map((agent) => day.turns.get(agent)).filter((turn) => turn && (!state.agent || turn.agent === state.agent));
    const quiet = !turns.length && !day.crashes.length;
    if (quiet && state.hideQuiet) continue;
    if (quiet) {
      const acting = d.live && day === d.days[d.days.length - 1];
      const who = state.agent
        ? `${state.agent} does not act`
        : day.agents.length
          ? `${day.agents.join(", ")} ${acting ? "acting now…" : "woken, no turns logged"}`
          : "nobody acts";
      list.append(h("div", { class: "quiet" }, h("span", { class: "date" }, dayLabel(day.date)), h("span", null, who)));
      continue;
    }
    list.append(
      h("article", { class: "day" },
        h("div", { class: "day-head" },
          h("span", { class: "date" }, dayLabel(day.date)),
          day.agents.map((agent) => h("span", { class: "chip", style: `--c: ${agentColor(agent)}` }, h("span", { class: "dot" }), agent)),
        ),
        day.unknown.length ? h("div", { class: "note" }, `agents_today named agents with no prompt: ${day.unknown.join(", ")}`) : null,
        day.crashes.map((crash) => h("div", { style: "padding: 0 14px 10px" }, crashBox("World code crashed", crash.error))),
        turns.map((turn) => turnView(day, turn)),
      ),
    );
  }
  if (d.tail.length) {
    list.append(
      h("article", { class: "day" },
        h("div", { class: "day-head" }, h("span", { class: "date" }, "The world stopped")),
        h("div", { style: "padding: 10px 14px" }, d.tail.map((crash) => crashBox("World code crashed", crash.error))),
      ),
    );
  }
  if (!list.children.length) list.append(h("div", { class: "placeholder" }, "No days to show."));
  return h("div", null, toolbar, list);
}

// ----- Agents -----

function viewAgents() {
  const d = state.run;
  const cards = d.agentIds.map((agent) => {
    const info = d.agents[agent] || {};
    const calls = d.events.filter((e) => e.type === "call" && e.agent === agent);
    const turns = d.events.filter((e) => e.type === "turn" && e.agent === agent).length;
    const tools = new Map();
    for (const call of calls) tools.set(call.tool, (tools.get(call.tool) || 0) + 1);
    const finalNotepad = d.notepads?.[agent];
    return h("article", { class: "card", style: `--c: ${agentColor(agent)}` },
      h("div", { class: "card-head" },
        h("span", { class: "dot" }),
        h("h2", null, agent),
        info.entity ? h("span", { class: "tag" }, info.entity) : null,
        h("span", { class: "faint" }, `${turns} ${turns === 1 ? "turn" : "turns"}, ${calls.length} ${calls.length === 1 ? "call" : "calls"}`),
        turns ? h("button", {
          type: "button", class: "linkish", style: "margin-left: auto",
          onclick: () => { state.agent = agent; state.tab = "days"; render(); window.scrollTo(0, 0); },
        }, "Show days →") : null,
      ),
      tools.size ? h("div", null,
        h("span", { class: "block-label" }, "Tools used"),
        h("div", { class: "tool-list" }, [...tools].map(([tool, n]) => h("span", { class: "tag mono" }, `${tool} ×${n}`))),
      ) : null,
      info.prompt ? h("div", null, h("span", { class: "block-label" }, "Prompt"), h("p", { class: "text" }, info.prompt)) : null,
      info.notepad != null ? h("div", null, h("span", { class: "block-label" }, "Starting notepad"), h("p", { class: "text boxed" }, info.notepad || "(empty)")) : null,
      finalNotepad != null ? h("div", null, h("span", { class: "block-label" }, "Last notepad"), h("p", { class: "text boxed" }, finalNotepad || "(empty)")) : null,
    );
  });
  return h("div", { class: "agents" }, cards);
}

// ----- Records -----

const NUMBER = /^-?\d+(\.\d+)?$/;

function cell(value) {
  if (value == null) return h("td", { class: "nil" }, "—");
  if (typeof value === "number" || (typeof value === "string" && NUMBER.test(value.trim()))) {
    return h("td", { class: `num${Number(value) < 0 ? " neg" : ""}` }, String(value));
  }
  if (typeof value === "object") return h("td", null, h("span", { class: "mono" }, JSON.stringify(value)));
  const text = String(value);
  return h("td", { class: text.length > 60 ? "long" : null }, text);
}

function tableView(rows) {
  const columns = [];
  for (const row of rows) for (const key of Object.keys(row)) if (!columns.includes(key)) columns.push(key);
  return h("div", { class: "table-wrap" },
    h("table", null,
      h("thead", null, h("tr", null, columns.map((column) => h("th", null, column)))),
      h("tbody", null, rows.map((row) => h("tr", null, columns.map((column) => cell(row[column]))))),
    ),
  );
}

function valueView(value, filter) {
  if (Array.isArray(value)) {
    const rows = filter ? value.filter((row) => JSON.stringify(row).toLowerCase().includes(filter)) : value;
    if (!rows.length) return h("div", { class: "table-wrap" }, h("div", { class: "empty" }, value.length ? "No rows match." : "Empty."));
    if (rows.every((row) => row && typeof row === "object" && !Array.isArray(row))) return tableView(rows);
    return tableView(rows.map((row) => ({ value: row })));
  }
  if (value && typeof value === "object") {
    return tableView(Object.entries(value).map(([key, item]) => ({ key, value: item })));
  }
  return h("div", { class: "table-wrap" }, h("div", { class: "empty mono" }, JSON.stringify(value)));
}

function slug(...parts) {
  return `r-${parts.join("-").replace(/[^a-zA-Z0-9]+/g, "-")}`;
}

function recordsBody() {
  const filter = state.recordFilter.trim().toLowerCase();
  const records = state.run.records;
  const body = h("div", null);
  for (const [entity, tables] of Object.entries(records)) {
    const section = h("section", { class: "entity", id: slug(entity) }, h("h2", null, entity));
    if (tables && typeof tables === "object" && !Array.isArray(tables)) {
      for (const [name, value] of Object.entries(tables)) {
        const count = Array.isArray(value) ? value.length : null;
        section.append(
          h("div", { class: "table-block", id: slug(entity, name) },
            h("h3", null, name, count != null ? h("span", { class: "faint" }, `${count} ${count === 1 ? "row" : "rows"}`) : null),
            valueView(value, filter),
          ),
        );
      }
    } else {
      section.append(valueView(tables, filter));
    }
    body.append(section);
  }
  return body;
}

function viewRecords() {
  const records = state.run.records;
  const nav = h("nav", { class: "records-nav", "aria-label": "Record tables" });
  for (const [entity, tables] of Object.entries(records)) {
    nav.append(h("a", { class: "entity-link", href: `#${slug(entity)}`, onclick: jump(slug(entity)) }, entity));
    if (tables && typeof tables === "object" && !Array.isArray(tables)) {
      for (const [name, value] of Object.entries(tables)) {
        nav.append(h("a", { href: `#${slug(entity, name)}`, onclick: jump(slug(entity, name)) },
          h("span", { class: "mono" }, name), Array.isArray(value) ? h("span", { class: "faint" }, value.length) : null));
      }
    }
  }
  const holder = h("div", null, recordsBody());
  const search = h("input", {
    type: "search", class: "search", placeholder: "Filter rows…", value: state.recordFilter, "aria-label": "Filter rows",
    oninput: (event) => { state.recordFilter = event.target.value; holder.replaceChildren(recordsBody()); },
  });
  const note = state.run.run?.last_date ? h("span", { class: "faint" }, `as of the end of ${dayLabel(state.run.run.last_date)}`) : null;
  return h("div", null,
    h("div", { class: "toolbar" }, search, note),
    h("div", { class: "records-layout" }, nav, holder),
  );
}

function jump(id) {
  return (event) => {
    event.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
}

// ----- Generation -----

function viewGeneration() {
  const d = state.run;
  const attempts = d.generates.map((g) => {
    const ok = g.problem == null;
    return h("article", { class: "card attempt" },
      h("div", { class: "attempt-head" },
        h("h2", { style: "font-size: 15px" }, `Try ${g.attempt}`),
        h("span", { class: `pill ${ok ? "ok" : "bad"}` }, ok ? "dry run passed" : "dry run crashed"),
      ),
      ok ? null : h("div", { class: "headline" }, lastLine(g.problem)),
      ok ? null : h("details", { class: "trace" }, h("summary", null, "Full error sent back to the world model"), h("pre", null, g.problem)),
    );
  });
  return h("div", { class: "attempts" },
    attempts,
    d.stderr ? h("article", { class: "card" }, h("span", { class: "block-label" }, "world_stderr.log"), h("pre", null, d.stderr)) : null,
  );
}

// ----- Code -----

function viewCode() {
  const lines = state.run.world_py.replace(/\n$/, "").split("\n");
  return h("div", { class: "code" }, h("pre", null, lines.map((line) => h("span", { class: "ln" }, line || " "))));
}

// ----- Prompt -----

function inline(text) {
  const parts = [];
  const pattern = /(`[^`]+`|\*\*[^*]+\*\*|(?<![\w*])\*[^*\s][^*]*\*(?![\w*])|(?<!\w)_[^_\s][^_]*_(?!\w))/g;
  let last = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    const token = match[0];
    if (token.startsWith("`")) parts.push(h("code", null, token.slice(1, -1)));
    else if (token.startsWith("**")) parts.push(h("strong", null, token.slice(2, -2)));
    else parts.push(h("em", null, token.slice(1, -1)));
    last = match.index + token.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function markdown(text) {
  return markdownInto(h("div", { class: "prose" }), text);
}

function markdownInto(root, text) {
  const lines = String(text).replace(/\r/g, "").split("\n");
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    if (line.startsWith("```")) {
      const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) code.push(lines[i++]);
      i++;
      root.append(h("pre", null, h("code", null, code.join("\n"))));
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      root.append(h(`h${heading[1].length}`, null, inline(heading[2])));
      i++;
      continue;
    }
    if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
      const ordered = /^\s*\d+[.)]/.test(line);
      const list = h(ordered ? "ol" : "ul");
      while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\s*([-*+]|\d+[.)])\s+/, "");
        i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) item += ` ${lines[i++].trim()}`;
        list.append(h("li", null, inline(item)));
      }
      root.append(list);
      continue;
    }
    if (line.startsWith(">")) {
      const quote = [];
      while (i < lines.length && lines[i].startsWith(">")) quote.push(lines[i++].replace(/^>\s?/, ""));
      root.append(markdownInto(h("blockquote"), quote.join("\n")));
      continue;
    }
    const para = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|>|\s*([-*+]|\d+[.)])\s)/.test(lines[i])) para.push(lines[i++].trim());
    root.append(h("p", null, inline(para.join(" "))));
  }
  return root;
}

function viewPrompt() {
  return h("div", null,
    h("div", { class: "source-path faint mono" }, state.run.run.prompt),
    markdown(state.run.prompt_text),
  );
}

// ----- Files -----

function viewFiles() {
  const d = state.run;
  const viewer = h("div", { class: "file-view" });
  const show = async (name) => {
    state.file = name;
    for (const button of list.querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.name === name));
    viewer.replaceChildren(h("div", { class: "faint" }, "Loading…"));
    try {
      const response = await fetch(`/api/file?id=${encodeURIComponent(d.id)}&name=${encodeURIComponent(name)}`, { cache: "no-store" });
      const text = await response.text();
      if (!response.ok) throw new Error(text);
      viewer.replaceChildren(fileBody(name, text));
    } catch (error) {
      viewer.replaceChildren(h("div", { class: "crash" }, `Could not read ${name}: ${error.message}`));
    }
  };
  const list = h("div", { class: "file-list" },
    d.files.map((file) =>
      h("button", { type: "button", "data-name": file.name, "aria-pressed": "false", onclick: () => show(file.name) },
        h("span", null, file.name), h("span", { class: "faint" }, sizeLabel(file.size))),
    ),
  );
  const pick = d.files.find((f) => f.name === state.file) || d.files.find((f) => f.name.endsWith(".md")) || d.files[0];
  if (pick) queueMicrotask(() => show(pick.name));
  return h("div", { class: "files" }, list, viewer);
}

function fileBody(name, text) {
  if (name.endsWith(".md")) return markdown(text);
  if (name.endsWith(".json")) {
    try { return h("pre", { class: "raw" }, JSON.stringify(JSON.parse(text), null, 2)); } catch { /* show raw */ }
  }
  if (name.endsWith(".jsonl")) {
    const pretty = text.split("\n").filter((line) => line.trim()).map((line) => {
      try { return JSON.stringify(JSON.parse(line), null, 2); } catch { return line; }
    });
    return h("pre", { class: "raw" }, pretty.join("\n\n"));
  }
  return h("pre", { class: "raw" }, text || "(empty file)");
}

// ---------- start ----------

async function start() {
  $("#run-select").addEventListener("change", (event) => selectRun(event.target.value));
  $("#refresh").addEventListener("click", async () => {
    await loadWorlds();
    if (state.runId) selectRun(state.runId, { keepView: true });
  });
  try {
    await loadWorlds();
  } catch (error) {
    $("#summary").replaceChildren(h("div", { class: "placeholder" }, `Could not reach the viewer server: ${error.message}`));
    return;
  }
  if (!state.worlds.length) {
    $("#summary").replaceChildren(h("div", { class: "placeholder" }, "No runs in worlds/ yet. Start one with: uv run --env-file .env worldgen PROMPT_FILE"));
    return;
  }
  const wanted = readHash();
  const known = state.worlds.some((world) => world.runs.some((run) => run.id === wanted.run));
  state.tab = wanted.tab;
  state.agent = wanted.agent;
  await selectRun(known ? wanted.run : newestRunId(), { keepView: true });
  window.addEventListener("hashchange", () => {
    const next = readHash();
    if (!next.run) return;
    state.tab = next.tab;
    state.agent = next.agent;
    selectRun(next.run, { keepView: next.run === state.runId });
  });
}

start();
