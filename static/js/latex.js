(() => {
  const typeset = (el) => {
    if (!el || !window.MathJax) return;
    const ready = window.MathJax.startup && window.MathJax.startup.promise
      ? window.MathJax.startup.promise
      : Promise.resolve();
    ready.then(() => window.MathJax.typesetPromise([el]).catch(() => {}));
  };

  const escapeHtml = (str) =>
    (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");

  const convertLatexLists = (text) => {
    let safe = escapeHtml(text || "");
    const convert = (env, tag) => {
      const re = new RegExp(`\\\\\\s*begin\\{${env}\\}([\\s\\S]*?)\\\\\\s*end\\{${env}\\}`, "g");
      safe = safe.replace(re, (_, body) => {
        const items = (body || "")
          .split(/\\item/g)
          .map((i) => i.trim())
          .filter(Boolean);
        if (!items.length) return "";
        const lis = items.map((i) => `<li>${i}</li>`).join("");
        return `<${tag}>${lis}</${tag}>`;
      });
    };
    convert("itemize", "ul");
    convert("enumerate", "ol");
    return safe.replace(/\r?\n/g, "<br>");
  };

  const attachPreview = (textarea) => {
    if (!textarea.classList.contains("latex-input")) return;
    // create preview container if missing
    let previewWrapper = textarea.parentElement.querySelector(".latex-preview");
    if (!previewWrapper) {
      const wrapper = document.createElement("div");
      wrapper.className = "latex-preview-container mt-2";
      const label = document.createElement("div");
      label.className = "small text-muted mb-1";
      label.textContent = "Preview";
      previewWrapper = document.createElement("div");
      previewWrapper.className = "latex-preview border rounded p-3 bg-light";
      wrapper.appendChild(label);
      wrapper.appendChild(previewWrapper);
      textarea.insertAdjacentElement("afterend", wrapper);
    }

    const render = () => {
      const content = textarea.value || "";
      const html = convertLatexLists(content) || "Start typing LaTeX to preview…";
      previewWrapper.innerHTML = html;
      typeset(previewWrapper);
    };
    textarea.addEventListener("input", render);
    render();
  };

  window.insertLatexSnippet = (targetId, snippet) => {
    const el = document.getElementById(targetId);
    if (!el) return;
    const start = el.selectionStart || 0;
    const end = el.selectionEnd || 0;
    const val = el.value || "";
    el.value = val.slice(0, start) + snippet + val.slice(end);
    el.focus();
    const cursor = start + snippet.length;
    el.setSelectionRange(cursor, cursor);
    el.dispatchEvent(new Event("input"));
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("textarea.latex-input").forEach(attachPreview);
  });
})();
