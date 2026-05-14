const form = document.getElementById("search-form");
const submitBtn = document.getElementById("submit-btn");
const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const chosenBox = document.getElementById("chosen");
const citationBox = document.getElementById("citation");
const bibtexBox = document.getElementById("bibtex");
const matchesBox = document.getElementById("matches");
const copyBibBtn = document.getElementById("copy-bib");

let latestBibtex = "";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultBox.classList.add("hidden");
  setStatus("正在检索，请稍候...");
  submitBtn.disabled = true;

  const payload = {
    description: document.getElementById("description").value.trim(),
    style: document.getElementById("style").value,
    top_k: Number(document.getElementById("top-k").value || 5),
    remote: document.getElementById("remote").checked,
    ai_rewrite: document.getElementById("ai-rewrite").checked,
    ai_provider: document.getElementById("use-minimax").checked ? "minimax" : null,
  };

  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "检索失败");
    }

    renderResult(data);
    setStatus(data.query.rewritten_text ? `AI 改写：${data.query.rewritten_text}` : "已完成检索。");
    resultBox.classList.remove("hidden");
  } catch (error) {
    setStatus(error.message || "请求失败");
  } finally {
    submitBtn.disabled = false;
  }
});

copyBibBtn.addEventListener("click", async () => {
  if (!latestBibtex) return;
  await navigator.clipboard.writeText(latestBibtex);
  setStatus("BibTeX 已复制到剪贴板。");
});

function renderResult(data) {
  latestBibtex = data.bibtex || "";

  if (data.chosen) {
    chosenBox.innerHTML = `
      <div class="chosen-title">${escapeHtml(data.chosen.title)}</div>
      <div class="meta">
        ${escapeHtml((data.chosen.authors || []).join(", "))}<br />
        ${escapeHtml(data.chosen.venue || "Unknown venue")} · ${escapeHtml(String(data.chosen.year || "n.d."))}<br />
        来源：${escapeHtml(data.chosen.source)} · 分数：${escapeHtml(String(data.chosen.score))}
      </div>
    `;
  } else {
    chosenBox.innerHTML = `<div class="meta">没有找到匹配论文。</div>`;
  }

  citationBox.textContent = data.citation || "暂无引用文本";
  bibtexBox.textContent = data.bibtex || "暂无 BibTeX";

  matchesBox.innerHTML = "";
  for (const match of data.matches || []) {
    const item = document.createElement("article");
    item.className = "match";
    item.innerHTML = `
      <h3>${escapeHtml(match.title)}</h3>
      <div class="meta">
        ${(match.authors || []).map(escapeHtml).join(", ")}<br />
        ${escapeHtml(match.venue || "Unknown venue")} · ${escapeHtml(String(match.year || "n.d."))}<br />
        来源：${escapeHtml(match.source)} · 分数：${escapeHtml(String(match.score))}
      </div>
      <div class="reason-list">${(match.reasons || []).map(escapeHtml).join(" | ")}</div>
    `;
    matchesBox.appendChild(item);
  }
}

function setStatus(text) {
  statusBox.textContent = text;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;")
    .replaceAll("'", "&#39;");
}
