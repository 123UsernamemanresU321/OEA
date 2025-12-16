(() => {
  const typeset = (el) => {
    if (!el || !window.MathJax) return;
    const ready = window.MathJax.startup && window.MathJax.startup.promise
      ? window.MathJax.startup.promise
      : Promise.resolve();
    ready.then(() => window.MathJax.typesetPromise([el]).catch(() => {}));
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
      previewWrapper.textContent = textarea.value || "Start typing LaTeX to preview…";
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
