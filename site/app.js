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
  const labels = { markets: "全球指数", cross_assets: "跨资产", vix: "VIX", us10y: "美债 10Y", news: "新闻" };
  const list = $("#health-list");
  list.replaceChildren();
  Object.entries(globalData.health || {}).forEach(([key, item]) => {
    const chip = document.createElement("span");
    chip.className = `health-chip ${item.status || "missing"}`;
    chip.textContent = `${labels[key] || key} · ${(item.status || "missing").toUpperCase()}`;
    list.append(chip);
  });
}

function renderCrossAssets(globalData) {
  const grid = $("#cross-asset-grid");
  grid.replaceChildren();
  (globalData.cross_assets || []).forEach((asset) => {
    const card = document.createElement("article");
    const role = asset.role === "context" ? "背景观察" : "进入评分";
    card.className = `cross-asset-card ${asset.role === "context" ? "context" : "scored"}${asset.stale ? " stale" : ""}`;

    const top = document.createElement("header");
    const code = document.createElement("b"); code.textContent = asset.code;
    const badge = document.createElement("span"); badge.textContent = role;
    top.append(code, badge);

    const close = document.createElement("strong");
    close.textContent = number(asset.close, asset.code === "USDCNH" ? 4 : 2);
    const change = document.createElement("div");
    const pct = document.createElement("b"); pct.textContent = signed(asset.pct); pct.className = pctClass(asset.pct);
    const state = document.createElement("small"); state.textContent = asset.stale ? "STALE / 最近有效值" : "LATEST";
    change.append(pct, state);
    const name = document.createElement("p"); name.textContent = asset.name || asset.region || asset.code;
    card.append(top, close, change, name);
    grid.append(card);
  });

  if (!grid.children.length) {
    const empty = document.createElement("p");
    empty.className = "cross-asset-empty";
    empty.textContent = "等待首轮跨资产行情。";
    grid.append(empty);
  }
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

function renderEventChains(analysis) {
  const list = $("#event-chain-list");
  list.replaceChildren();
  const events = (analysis.events || []).slice(0, 6);

  events.forEach((event) => {
    const card = document.createElement("article");
    card.className = `event-chain-card event-${event.key || "other"}`;

    const header = document.createElement("header");
    const identity = document.createElement("div");
    const label = document.createElement("h4"); label.textContent = event.label || "未分类事件";
    const meta = document.createElement("span"); meta.textContent = `${Number(event.headline_count) || 0} 条去重线索`;
    identity.append(label, meta);
    const status = document.createElement("b"); status.textContent = "待市场确认";
    header.append(identity, status);

    const flow = document.createElement("div");
    flow.className = "event-flow";
    const stages = [
      ["01 / EVENT CLUSTER", "标题线索", null],
      ["02 / MACRO PATH", "宏观传导", event.macro_path],
      ["03 / A-SHARE LENS", "A 股映射", event.a_share_lens],
      ["04 / INVALIDATION", "失效条件", event.invalidation],
    ];
    stages.forEach(([kicker, titleText, body], index) => {
      const stage = document.createElement("section");
      stage.className = `event-stage stage-${index + 1}`;
      const small = document.createElement("small"); small.textContent = kicker;
      const title = document.createElement("h5"); title.textContent = titleText;
      stage.append(small, title);
      if (index === 0) {
        const headlines = document.createElement("ul");
        (event.headlines || []).slice(0, 2).forEach((item) => {
          const row = document.createElement("li");
          const link = document.createElement("a"); link.textContent = item.title || "未命名标题";
          if (String(item.link || "").startsWith("https://news.google.com/")) {
            link.href = item.link; link.target = "_blank"; link.rel = "noreferrer";
          }
          row.append(link); headlines.append(row);
        });
        stage.append(headlines);
      } else {
        const copy = document.createElement("p"); copy.textContent = body || "等待规则补充";
        stage.append(copy);
      }
      flow.append(stage);
    });

    const watch = document.createElement("div");
    watch.className = "event-watch";
    const watchLabel = document.createElement("span"); watchLabel.textContent = "CONFIRM / 观察指标";
    watch.append(watchLabel);
    (event.watch || []).forEach((item) => {
      const chip = document.createElement("span");
      const state = ["fresh", "stale", "missing"].includes(item.state) ? item.state : "missing";
      chip.className = `watch-chip ${state}`;
      chip.textContent = `${item.label || item.code || "指标"} ${item.value || "--"} · ${state.toUpperCase()}`;
      watch.append(chip);
    });

    card.append(header, flow, watch);
    list.append(card);
  });

  if (!events.length) {
    const empty = document.createElement("p");
    empty.className = "event-chain-empty";
    empty.textContent = "本轮去重标题未命中预设事件簇，保留原始标题等待后续验证。";
    list.append(empty);
  }
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

async function copyUrl(url) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(url);
    return;
  }
  const input = document.createElement("textarea");
  input.value = url;
  input.setAttribute("readonly", "");
  input.style.position = "fixed";
  input.style.opacity = "0";
  document.body.append(input);
  input.select();
  document.execCommand("copy");
  input.remove();
}

function setupShare(analysis) {
  const buttons = [$("#hero-share"), $("#share-button")].filter(Boolean);
  const feedback = $("#share-feedback");
  const url = `${window.location.origin}${window.location.pathname}`;
  const score = Number(analysis.score) || 0;
  const payload = {
    title: "A-Share Pulse · 市场天气台",
    text: `今日跨市场风险温度 ${score >= 0 ? "+" : ""}${score} · ${analysis.stance || "等待数据"}。查看可追溯证据：`,
    url,
  };

  buttons.forEach((button) => button.addEventListener("click", async () => {
    try {
      if (navigator.share) {
        await navigator.share(payload);
        if (feedback) feedback.textContent = "已打开系统分享。";
      } else {
        await copyUrl(url);
        if (feedback) feedback.textContent = "大屏链接已复制。";
      }
    } catch (error) {
      if (error?.name !== "AbortError" && feedback) {
        feedback.textContent = "暂时无法分享，可下载简报或复制浏览器地址。";
      }
    }
  }));
}

async function init() {
  try {
    const [analysis, globalData, latest, scorecard] = await Promise.all(Object.values(DATA).map(loadJson));
    renderScore(analysis); renderHealth(globalData); renderMarkets(globalData); renderCrossAssets(globalData);
    renderSignals(analysis); renderScorecard(scorecard); renderEventChains(analysis); renderNews(analysis);
    setupShare(analysis);
    const sh = latest.latest_daily?.indices?.sh000001;
    text("#sh-close", number(sh?.close));
    const pct = $("#sh-pct"); pct.textContent = signed(sh?.pct); pct.className = pctClass(sh?.pct);
  } catch (error) {
    console.error(error);
    text("#summary", "数据载入失败，请前往 GitHub 查看任务状态。");
  }
}

init();
