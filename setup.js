// Private AI web setup wizard.
// Verifies purchase code, loads model catalog, and downloads the selected files.

const WORKER_URL =
  "https://private-ai-code-server.llmservicemarketplace.workers.dev";

const CATALOG_URL =
  "https://llmservicemarketplace-del.github.io/github-pages-private-ai/catalog.json";

const INSTALLER_URL =
  "https://github.com/llmservicemarketplace-del/github-pages-private-ai/releases/download/v1.0.0/LFM_Console.exe";

const el = (id) => document.getElementById(id);

const show = (id) => {
  document.querySelectorAll("[data-step]").forEach((section) => {
    section.hidden = true;
  });

  const target = el(id);

  if (target) {
    target.hidden = false;
  }
};

let offers = [];
let chosen = null;

const codeInput = el("code");

// Format codes as PAI-XXXX-XXXX.
codeInput.addEventListener("input", () => {
  let value = codeInput.value
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");

  if (value.startsWith("PAI")) {
    value = value.slice(3);
  }

  value = value.slice(0, 8);

  codeInput.value =
    "PAI-" +
    value.slice(0, 4) +
    (value.length > 4 ? "-" + value.slice(4) : "");
});

el("code-go").onclick = async () => {
  const errorLine = el("code-err");
  errorLine.hidden = true;

  try {
    const code = codeInput.value.trim().toUpperCase();

    if (!/^PAI-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(code)) {
      throw new Error("Please enter a valid code in the format PAI-XXXX-XXXX.");
    }

    const response = await fetch(WORKER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ code })
    });

    const result = await response.json();

    if (!response.ok || !result.valid) {
      throw new Error(result.error || "Invalid purchase code.");
    }

    sessionStorage.setItem("validatedCode", code);
    await loadModels();
  } catch (error) {
    errorLine.textContent =
      error instanceof Error ? error.message : String(error);

    errorLine.hidden = false;
  }
};

async function loadModels() {
  const response = await fetch(CATALOG_URL, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("The model catalog could not be loaded.");
  }

  const catalog = await response.json();

  offers = (catalog.models || []).filter((model) => {
    return model && model.enabled && model.label && model.url;
  });

  const userAgent = navigator.userAgent.toLowerCase();
  let platform = "windows";

  if (userAgent.includes("android")) {
    platform = "android";
  } else if (
    userAgent.includes("iphone") ||
    userAgent.includes("ipad")
  ) {
    platform = "ios";
  } else if (userAgent.includes("mac")) {
    platform = "macos";
  }

  offers = offers.filter((model) => {
    return (
      Array.isArray(model.platforms) &&
      model.platforms.includes(platform)
    );
  });

  el("hw-line").textContent =
    `Detected: ${navigator.platform}. ` +
    "Choose the AI model you want installed.";

  const box = el("picks");
  box.replaceChildren();

  if (!offers.length) {
    el("empty-note").hidden = false;
    show("step-pick");
    return;
  }

  el("empty-note").hidden = true;

  offers.forEach((model, index) => {
    const button = document.createElement("button");
    button.className = "pick";

    button.innerHTML =
      '<div class="pick__label"></div>' +
      '<div class="pick__blurb"></div>' +
      '<div class="pick__meta"></div>';

    button.querySelector(".pick__label").textContent =
      model.label;

    button.querySelector(".pick__blurb").textContent =
      model.blurb || "";

    button.querySelector(".pick__meta").textContent =
      `${Number(model.download_gb || 0).toFixed(1)} GB download · ` +
      `${Number(model.ram_gb || 0).toFixed(1)} GB RAM recommended`;

    button.onclick = () => chooseModel(index);
    box.appendChild(button);
  });

  show("step-pick");
}

function chooseModel(index) {
  chosen = offers[index];

  if (!chosen) {
    alert("That model option could not be loaded.");
    return;
  }

  localStorage.setItem(
    "privateAiSelectedModel",
    JSON.stringify({
      id: chosen.id,
      label: chosen.label,
      url: chosen.url,
      sha256: chosen.sha256 || "",
      license: chosen.license || ""
    })
  );

  if (!chosen.gated) {
    beginDownloads();
    return;
  }

  el("license-line").textContent =
    `${chosen.label} is published under ${chosen.license}. ` +
    "The model is downloaded directly from its publisher.";

  el("license-text").textContent =
    chosen.license_text ||
    chosen.license_url ||
    "Review the publisher's license before continuing.";

  el("accept").checked = false;
  el("license-go").disabled = true;
  show("step-license");
}

el("accept").onchange = (event) => {
  el("license-go").disabled = !event.target.checked;
};

el("license-go").onclick = beginDownloads;

function beginDownloads() {
  if (!chosen) {
    alert("Choose a model first.");
    return;
  }

  show("step-dl");

  el("dl-head").textContent =
    `Preparing ${chosen.label}`;

  el("dl-err").hidden = true;
  el("dl-retry").hidden = true;
  el("bar").style.width = "100%";

  try {
    if (
      !chosen.url ||
      chosen.url.includes("/ORG/REPO/") ||
      chosen.url.includes("FILL_ME")
    ) {
      throw new Error(
        "This model still has a placeholder Hugging Face download URL."
      );
    }

    el("dl-stat").textContent =
      "Opening the model and application downloads...";

    // Start the selected Hugging Face model download.
    const modelWindow = window.open(
      chosen.url,
      "_blank",
      "noopener"
    );

    if (!modelWindow) {
      throw new Error(
        "Your browser blocked the model download. Allow pop-ups and try again."
      );
    }

    showCompletion();
  } catch (error) {
    el("dl-err").textContent =
      error instanceof Error ? error.message : String(error);

    el("dl-err").hidden = false;
    el("dl-retry").hidden = false;
  }
}

el("dl-retry").onclick = beginDownloads;

function showCompletion() {
  const doneSection = el("step-done");

  doneSection.querySelector("h1").textContent =
    "Downloads Started";

  doneSection.querySelector(".step__sub").innerHTML =
    `Your selected model is <strong>${escapeHtml(chosen.label)}</strong>.<br><br>` +
    `1. The selected AI model download has opened in a new tab.<br><br>` +
    `2. Download the Private AI Windows application:<br>` +
    `<a href="${INSTALLER_URL}" target="_blank" rel="noopener">` +
    `Download Private AI</a><br><br>` +
    `3. Internet is needed only for these initial downloads.<br><br>` +
    `4. After the model is placed in the application's model folder and configured, ` +
    `the AI can run locally without an internet connection.`;

  show("step-done");
}

el("done-go").onclick = () => {
  window.open(INSTALLER_URL, "_blank", "noopener");
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

show("step-code");
codeInput.focus();
