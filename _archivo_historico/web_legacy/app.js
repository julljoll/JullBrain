/**
 * JullBrain Enterprise Legal Platform — Client-side Web Logic
 * Manejo interactivo de pestañas, acciones del pipeline, carga con SHA-256 y consultas RAG.
 */

let selectedFile = null;
let logPollingInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupDropzone();
  startLogPolling();
  loadDocumentsList();
});

// ── Manejo de Pestañas ────────────────────────────────────────────────────────
function setupTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      goToTab(targetId);
    });
  });
}

function goToTab(tabId) {
  document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  const targetTab = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
  const targetPane = document.getElementById(tabId);

  if (targetTab && targetPane) {
    targetTab.classList.add("active");
    targetPane.classList.add("active");
  }

  if (tabId === "tab-docs") {
    loadDocumentsList();
  }
}

// ── Disparador de Acciones del Pipeline (.bat Equivalente) ─────────────────────
async function triggerAction(actionName) {
  const terminal = document.getElementById("terminal-body");
  appendLog(`[DISPATCH] Solicitando acción: '${actionName}'...`, "log-warn");

  try {
    const res = await fetch("/api/v1/pipeline/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: actionName })
    });

    const data = await res.json();
    if (res.ok) {
      showToast(`Acción '${actionName}' iniciada correctamente`, "success");
      appendLog(`[OK] ${data.message || 'Proceso en ejecución en segundo plano.'}`, "log-ok");
    } else {
      showToast(`Error: ${data.detail || 'Falla al iniciar acción'}`, "error");
      appendLog(`[ERROR] ${data.detail || 'Error en el servidor'}`, "log-err");
    }
  } catch (err) {
    showToast(`Error de red al conectar con el backend: ${err.message}`, "error");
    appendLog(`[FATAL] Error de conexión: ${err.message}`, "log-err");
  }
}

// ── Streaming / Polling de Registros del Terminal ─────────────────────────────
function startLogPolling() {
  if (logPollingInterval) clearInterval(logPollingInterval);
  refreshLogs();
  logPollingInterval = setInterval(refreshLogs, 2500);
}

async function refreshLogs() {
  try {
    const res = await fetch("/api/v1/pipeline/logs");
    if (!res.ok) return;
    const data = await res.json();
    const terminal = document.getElementById("terminal-body");

    if (data.logs && data.logs.length > 0) {
      terminal.innerHTML = "";
      data.logs.forEach(line => {
        let cls = "log-dim";
        if (line.includes("[OK]") || line.includes("ÉXITO")) cls = "log-ok";
        else if (line.includes("[WARNING]") || line.includes("[WARN]")) cls = "log-warn";
        else if (line.includes("[ERROR]") || line.includes("[FATAL]")) cls = "log-err";
        
        const div = document.createElement("div");
        div.className = cls;
        div.textContent = line;
        terminal.appendChild(div);
      });
      terminal.scrollTop = terminal.scrollHeight;
    }
  } catch (e) {
    // Silencio en caso de caída temporal
  }
}

function appendLog(message, className = "log-dim") {
  const terminal = document.getElementById("terminal-body");
  const div = document.createElement("div");
  div.className = className;
  div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  terminal.appendChild(div);
  terminal.scrollTop = terminal.scrollHeight;
}

function clearTerminal() {
  const terminal = document.getElementById("terminal-body");
  terminal.innerHTML = `[INIT] Consola reiniciada.\n`;
}

// ── Drag & Drop y Cálculo SHA-256 en Cliente ─────────────────────────────────
function setupDropzone() {
  const dropzone = document.getElementById("dropzone");
  if (!dropzone) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("drag-over");
    }, false);
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("drag-over");
    }, false);
  });

  dropzone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFileSelect(files);
  });
}

async function handleFileSelect(files) {
  if (!files || files.length === 0) return;
  const file = files[0];

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Solo se admiten documentos en formato PDF.", "error");
    return;
  }

  selectedFile = file;
  document.getElementById("preview-name").textContent = file.name;
  document.getElementById("preview-size").textContent = formatBytes(file.size);
  document.getElementById("preview-hash").textContent = "Calculando SHA-256 criptográfico...";
  document.getElementById("file-preview").style.display = "block";

  // Cálculo en cliente con Web Crypto API
  try {
    const arrayBuffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
    document.getElementById("preview-hash").textContent = hashHex;
  } catch (err) {
    document.getElementById("preview-hash").textContent = "Error al calcular hash en cliente";
  }
}

async function uploadCurrentFile() {
  if (!selectedFile) {
    showToast("Por favor selecciona un archivo PDF primero.", "error");
    return;
  }

  const category = document.getElementById("category-select").value;
  const btn = document.getElementById("btn-upload");
  btn.disabled = true;
  btn.innerHTML = `<span>Subiendo documento...</span>`;

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("category", category);
  formData.append("client_sha256", document.getElementById("preview-hash").textContent);

  try {
    const res = await fetch("/api/v1/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (res.ok) {
      showToast(`¡Documento cargado en ${category}! SHA: ${data.sha256.substring(0, 12)}...`, "success");
      appendLog(`[UPLOAD] Guardado exitoso: RAG/datos_brutos/${category}/${selectedFile.name}`, "log-ok");
      appendLog(`[HASH SHA-256] ${data.sha256}`, "log-warn");
      selectedFile = null;
      document.getElementById("file-preview").style.display = "none";
      document.getElementById("file-input").value = "";
    } else {
      showToast(`Error al subir: ${data.detail || 'Falla del servidor'}`, "error");
    }
  } catch (err) {
    showToast(`Error de red al subir: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Subir a RAG/datos_brutos</span>`;
  }
}

// ── Inventario de Documentos ──────────────────────────────────────────────────
async function loadDocumentsList() {
  const tbody = document.getElementById("docs-table-body");
  if (!tbody) return;

  try {
    const res = await fetch("/api/v1/documents");
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--accent-danger);">No se pudo cargar el inventario.</td></tr>`;
      return;
    }

    const data = await res.json();
    const docs = data.documents || [];

    if (docs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-dim);">No hay documentos registrados en RAG/datos_brutos.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    docs.forEach(doc => {
      const tr = document.createElement("tr");
      const statusBadge = doc.is_converted
        ? `<span style="color: var(--accent-green); font-weight: 600;">✅ Estructurado</span>`
        : `<span style="color: var(--accent-gold); font-weight: 600;">⏳ Pendiente</span>`;

      tr.innerHTML = `
        <td><span class="badge" style="background: rgba(56, 189, 248, 0.1); color: var(--accent-blue);">${doc.category}</span></td>
        <td style="font-weight: 500;">${doc.filename}</td>
        <td style="color: var(--text-muted); font-size: 0.8rem;">${formatBytes(doc.size_bytes)}</td>
        <td>${statusBadge}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-dim);">Error de conexión al cargar lista.</td></tr>`;
  }
}

// ── Consultas RAG ─────────────────────────────────────────────────────────────
async function submitQuery() {
  const input = document.getElementById("query-input");
  const query = input.value.trim();
  if (!query) {
    showToast("Por favor ingresa una pregunta o consulta legal.", "error");
    return;
  }

  const responseBox = document.getElementById("response-box");
  const responseText = document.getElementById("response-text");
  const citationList = document.getElementById("citation-list");
  const guardianBadge = document.getElementById("guardian-badge");

  responseBox.style.display = "block";
  responseText.textContent = "Analizando corpus normativo y verificando citas probatorias con IBM Granite...";
  citationList.innerHTML = "";

  try {
    const res = await fetch("/api/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        notebook_id: "default_notebook",
        user_message: query,
        top_k: 10
      })
    });

    const data = await res.json();
    if (res.ok) {
      responseText.textContent = data.response;

      // Actualizar semáforo Guardian
      if (data.guardian_safe === false) {
        guardianBadge.className = "guardian-badge";
        guardianBadge.style.background = "rgba(239, 68, 68, 0.15)";
        guardianBadge.style.color = "#f87171";
        guardianBadge.style.border = "1px solid #ef4444";
        guardianBadge.textContent = "🛡️ GUARDIAN: RESTRINGIDO / ALUCINACIÓN";
      } else {
        guardianBadge.className = "guardian-badge guardian-safe";
        guardianBadge.textContent = "🛡️ GUARDIAN: EVIDENCIA VERIFICADA";
      }

      // Citas
      if (data.citations && data.citations.length > 0) {
        citationList.innerHTML = `<h5 style="margin-top: 1rem; margin-bottom: 0.5rem; color: var(--accent-gold);">📜 Citas y Trazabilidad Forense:</h5>`;
        data.citations.forEach(c => {
          const div = document.createElement("div");
          div.className = "citation-item";
          div.innerHTML = `
            <strong>${c.documento}</strong> — Pág. ${c.pagina} | ${c.articulo} | Confianza: <code>${c.nivel_confianza_pct}%</code>
            <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">"${c.fragmento_literal}"</div>
          `;
          citationList.appendChild(div);
        });
      }
    } else {
      responseText.textContent = `Error: ${data.detail || 'Falla en la inferencia RAG.'}`;
    }
  } catch (err) {
    responseText.textContent = `Error de red al consultar: ${err.message}`;
  }
}

// ── Utilidades ────────────────────────────────────────────────────────────────
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function formatBytes(bytes, decimals = 2) {
  if (!+bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}
