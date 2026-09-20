const DATA = {
  analysis: "data/analysis.json",
  global: "data/global.json",
  latest: "data/latest.json",
  scorecard: "data/scorecard.json",
};

const $ = (selector) => document.querySelector(selector);
const text = (selector, value) => { const node = $(selector); if (node) node.textContent = value ?? "--"; };
const number = (value, digits = 2) => Number.isFinite(Number(value)) ? Number(value).toLocaleString("zh-CN", { minimumFractionDigits: digits, maximumFractionDigits: digits }) : "--";
const signed = (value) => Number.isFinite(Number(value)) ? `${Number(value) >= 0 ? "+" : ""}${Number(value).toFixed(2)}%` : "--";

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.json();
}

function pctClass(value) {
  return Number(value) > 0 ? "up" : Number(value) < 0 ? "down" : "";
}

function renderScore(analysis) {
  const score = Math.max(-100, Math.min(100, Number(analysis.score) || 0));
  text("#score", `${score >= 0 ? "+" : ""}${score}`);
  text("#stance", analysis.stance);
  text("#confidence", `CONFIDENCE / ${analysis.confidence || "低"}`);
  text("#summary", analysis.summary);
  text("#updated-at", analysis.generated_at);
  text("#methodology", analysis.methodology);
  document.documentElement.style.setProperty("--score-pos", `${(score + 100) / 2}%`);
  $("#score").style.color = score >= 5 ? "var(--red)" : score <= -5 ? "var(--green)" : "var(--amber)";
}

function renderHealth(globalData) {
  const labels = { markets: "全球指数", vix: "VIX", us10y: "美债 10Y", news: "新闻" };
  const list = $("#health-list");
  list.replaceChildren();
  Object.entries(globalData.health || {}).forEach(([key, item]) => {
    const chip = document.createElement("span");
    chip.className = `health-chip ${item.status || "missing"}`;
    chip.textContent = `${labels[key] || key} · ${(item.status || "missing").toUpperCase()}`;
    list.append(chip);
  });
}

function renderMarkets(globalData) {
  const grid = $("#market-grid");
  grid.replaceChildren();
  (globalData.markets || []).forEach((market) => {
    const card = document.createElement("article");
    card.className = "market-card";
    const header = document.createElement("header");
    const name = document.createElement("span"); name.textContent = market.name;
    const code = document.createElement("small"); code.textContent = market.code;
    header.append(name, code);
    const close = document.createElement("strong"); close.textContent = number(market.close);
    const footer = document.createElement("footer");
    const region = document.createElement("span"); region.textContent = market.region;
    const pct = document.createElement("b"); pct.textContent = signed(market.pct); pct.className = pctClass(market.pct);
    footer.append(region, pct);
    card.append(header, close, footer);
    if (market.stale) card.title = "本轮未刷新，显示最近有效值";
    grid.append(card);
  });
  const macro = globalData.macro || {};
  text("#vix", number(macro.vix?.value));
  text("#vix-date", `${macro.vix?.date || "--"}${macro.vix?.stale ? " · STALE" : ""}`);
  text("#us10y", Number.isFinite(Number(macro.us10y?.value)) ? `${number(macro.us10y.value)}%` : "--");
  text("#us10y-date", `${macro.us10y?.date || "--"}${macro.us10y?.stale ? " · STALE" : ""}`);
}

function renderSignals(analysis) {
  const list = $("#signal-list");
  list.replaceChildren();
  const signals = analysis.signals || [];
  const max = Math.max(1, ...signals.map((item) => Math.abs(Number(item.contribution) || 0)));
  signals.forEach((signal) => {
    const row = document.createElement("article"); row.className = "signal-row";
    const label = document.createElement("div");
    const title = document.createElement("h3"); title.textContent = signal.label;
    const note = document.createElement("p"); note.textContent = `${signal.value} · ${signal.note}`;
    label.append(title, note);
    const bar = document.createElement("div"); bar.className = "signal-bar";
    const fill = document.createElement("i");
    const contribution = Number(signal.contribution) || 0;
    fill.style.width = `${Math.abs(contribution) / max * 100}%`;
    if (contribution < 0) fill.className = "negative";
    bar.append(fill);
    const value = document.createElement("div"); value.className = `signal-value ${pctClass(contribution)}`;
    value.textContent = `${contribution >= 0 ? "+" : ""}${contribution.toFixed(1)}`;
    row.append(label, bar, value); list.append(row);
  });
}

function renderScorecard(scorecard) {
  const directional = Number(scorecard.directional_1d) || 0;
  const minimum = Number(scorecard.minimum_samples) || 20;
  text("#sample-progress", `${directional} / ${minimum}`);
  text("#hit-rate", scorecard.hit_rate_1d == null ? "待验证" : `${Number(scorecard.hit_rate_1d).toFixed(1)}%`);
  text("#proof-status", String(scorecard.status || "collecting").toUpperCase());
  $("#sample-fill").style.width = `${Math.min(100, directional / minimum * 100)}%`;
}

function renderNews(analysis) {
  const list = $("#news-list"); list.replaceChildren();
  (analysis.news || []).slice(0, 8).forEach((item) => {
    const row = document.createElement("li");
    const link = document.createElement("a");
    link.textContent = item.title;
    if (String(item.link || "").startsWith("https://news.google.com/")) {
      link.href = item.link; link.target = "_blank"; link.rel = "noreferrer";
    }
    const source = document.createElement("span"); source.className = "news-source"; source.textContent = item.source || "未知来源";
    row.append(link, source); list.append(row);
  });
}

async function init() {
  try {
    const [analysis, globalData, latest, scorecard] = await Promise.all(Object.values(DATA).map(loadJson));
    renderScore(analysis); renderHealth(globalData); renderMarkets(globalData);
    renderSignals(analysis); renderScorecard(scorecard); renderNews(analysis);
    const sh = latest.latest_daily?.indices?.sh000001;
    text("#sh-close", number(sh?.close));
    const pct = $("#sh-pct"); pct.textContent = signed(sh?.pct); pct.className = pctClass(sh?.pct);
  } catch (error) {
    console.error(error);
    text("#summary", "数据载入失败，请前往 GitHub 查看任务状态。");
  }
}

init();
