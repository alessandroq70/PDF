"use strict";

// In-memory list of the PDFs the user has chosen, in merge order.
let files = [];

const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const fileListEl = document.getElementById("file-list");
const mergeBtn = document.getElementById("merge-btn");
const clearBtn = document.getElementById("clear-btn");
const statusEl = document.getElementById("status");

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function setStatus(message, kind) {
  statusEl.textContent = message || "";
  statusEl.className = "status" + (kind ? " " + kind : "");
}

// Add freshly picked files, ignoring anything that isn't a PDF and any exact
// duplicate (same name + size) already in the list.
function addFiles(fileListLike) {
  const incoming = Array.from(fileListLike);
  let skipped = 0;
  for (const file of incoming) {
    const isPdf =
      file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
    if (!isPdf) {
      skipped++;
      continue;
    }
    const duplicate = files.some(
      (f) => f.name === file.name && f.size === file.size
    );
    if (!duplicate) files.push(file);
  }
  render();
  if (skipped > 0) {
    setStatus(`${skipped} file ignorato/i perché non è un PDF.`, "error");
  } else {
    setStatus("");
  }
}

function removeAt(index) {
  files.splice(index, 1);
  render();
}

function move(index, delta) {
  const target = index + delta;
  if (target < 0 || target >= files.length) return;
  [files[index], files[target]] = [files[target], files[index]];
  render();
}

function render() {
  fileListEl.innerHTML = "";
  files.forEach((file, i) => {
    const li = document.createElement("li");
    li.className = "file-item";
    li.innerHTML = `
      <span class="file-index">${i + 1}</span>
      <span class="file-name" title="${file.name}">${file.name}</span>
      <span class="file-size">${formatSize(file.size)}</span>
      <button class="icon-btn" data-act="up" ${i === 0 ? "disabled" : ""} title="Sposta su">▲</button>
      <button class="icon-btn" data-act="down" ${i === files.length - 1 ? "disabled" : ""} title="Sposta giù">▼</button>
      <button class="icon-btn" data-act="remove" title="Rimuovi">✕</button>
    `;
    li.querySelector('[data-act="up"]').addEventListener("click", () => move(i, -1));
    li.querySelector('[data-act="down"]').addEventListener("click", () => move(i, 1));
    li.querySelector('[data-act="remove"]').addEventListener("click", () => removeAt(i));
    fileListEl.appendChild(li);
  });

  const hasEnough = files.length >= 2;
  mergeBtn.disabled = !hasEnough;
  clearBtn.disabled = files.length === 0;
}

// --- File picking: click + drag & drop -----------------------------------

fileInput.addEventListener("change", (e) => {
  addFiles(e.target.files);
  fileInput.value = ""; // allow re-selecting the same file later
});

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files);
});

clearBtn.addEventListener("click", () => {
  files = [];
  render();
  setStatus("");
});

// --- Merge + save ----------------------------------------------------------

async function saveBlob(blob) {
  // Preferred path (Chrome / Edge on Windows): a real "Save As" dialog where
  // the user chooses the folder and file name.
  if (typeof window.showSaveFilePicker === "function") {
    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: "documenti-uniti.pdf",
        types: [
          {
            description: "PDF",
            accept: { "application/pdf": [".pdf"] },
          },
        ],
      });
      const writable = await handle.createWritable();
      await writable.write(blob);
      await writable.close();
      return "saved";
    } catch (err) {
      if (err && err.name === "AbortError") return "cancelled";
      // Fall through to classic download on any other failure.
    }
  }

  // Fallback: trigger a normal download (browser decides the folder).
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "documenti-uniti.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  return "downloaded";
}

mergeBtn.addEventListener("click", async () => {
  if (files.length < 2) {
    setStatus("Seleziona almeno 2 file PDF.", "error");
    return;
  }

  mergeBtn.disabled = true;
  clearBtn.disabled = true;
  setStatus("Unione in corso…", "busy");

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file, file.name));

  try {
    const res = await fetch("/merge", { method: "POST", body: formData });
    if (!res.ok) {
      let message = "Errore durante l'unione dei file.";
      try {
        const data = await res.json();
        if (data.error) message = data.error;
      } catch (_) {}
      setStatus(message, "error");
      return;
    }

    const blob = await res.blob();
    const result = await saveBlob(blob);

    if (result === "cancelled") {
      setStatus("Salvataggio annullato.", "");
    } else if (result === "saved") {
      setStatus("✓ File salvato nella posizione scelta.", "success");
    } else {
      setStatus("✓ File pronto: controlla la cartella Download.", "success");
    }
  } catch (err) {
    setStatus("Impossibile contattare il server. È ancora in esecuzione?", "error");
  } finally {
    render(); // re-enable buttons based on current state
  }
});

render();
