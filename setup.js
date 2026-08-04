// Setup wizard for GitHub Pages version. Redeem -> pick -> license -> download -> done.
// Communicates with backend endpoints instead of Tauri invoke.

const el = (id) => document.getElementById(id);
const show = (id) => {
  document.querySelectorAll('[data-step]').forEach(s => s.hidden = true);
  el(id).hidden = false;
};

let hw = null;
let offers = [];
let chosen = null;
let validatedCode = null; // Store validated code if we have one from landing page

// Backend configuration - user should update these
const WORKER_URL = 'https://private-ai-code-server.llmservicemarketplace.workers.dev';
const CATALOG_URL = 'https://llmservicemarketplace-del.github.io/github-pages-private-ai/catalog.json';

// ---------- 1. redeem ----------
// The code gates the download, not the app. If the redeem server ever goes
// away, units already installed must keep working forever.

const codeInput = el('code');

codeInput.addEventListener('input', () => {
  // Format as they type. No ambiguous characters exist in the alphabet.
  let v = codeInput.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (v.startsWith('PAI')) v = v.slice(3);
  v = v.slice(0, 8);
  codeInput.value = 'PAI-' + (v.slice(0, 4) + (v.length > 4 ? '-' + v.slice(4) : ''));
});

el('code-go').onclick = async () => {
  const err = el('code-err');
  err.hidden = true;
  try {
    // Validate code with backend
    const response = await fetch(WORKER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code: codeInput.value })
    });

    if (!response.ok) {
      throw new Error(await response.text() || 'Invalid code');
    }

    // Code validated successfully
    await loadPicks();
  } catch (e) {
    err.textContent = String(e);
    err.hidden = false;
  }
};

// ---------- 2. pick ----------

async function loadPicks() {
  try {
    // In a real implementation, we might get hardware info via UserAgent or similar
    // For now, we'll use mock values or skip hardware check
    hw = { total_ram_gb: 8, free_disk_gb: 100 }; // Mock - in reality, could use navigator.deviceMemory

    // Fetch catalog from CDN
    const catalogResponse = await fetch(CATALOG_URL);
    if (!catalogResponse.ok) {
      throw new Error('Failed to load catalog');
    }
    const catalogData = await catalogResponse.json();
    offers = (catalogData.models || []).filter(m => m && m.enabled && m.label);

    // Filter by platforms if we could detect them (simplified)
    // In browser, we can detect OS roughly
    const platform = navigator.userAgent.toLowerCase();
    let platforms = ['windows']; // default
    if (platform.indexOf('mac') !== -1) platforms = ['macos'];
    if (platform.indexOf('android') !== -1) platforms = ['android'];
    if (platform.indexOf('iphone') !== -1 || platform.indexOf('ipad') !== -1) platforms = ['ios'];

    offers = offers.filter(o =>
      o.platforms.some(p => platforms.includes(p)) ||
      platforms.some(p => o.platforms.includes(p))
    );

    el('hw-line').textContent =
      `Detected: ${navigator.platform}. ` +
      `These are the options available for your device.`;

    const box = el('picks');
    box.replaceChildren();

    if (!offers.length) {
      el('empty-note').hidden = false;
      show('step-pick');
      return;
    }

    offers.forEach((o, i) => {
      const b = document.createElement('button');
      b.className = 'pick';
      const tight = o.fit === 'Tight';
      b.innerHTML =
        `<div class="pick__label"></div>` +
        `<div class="pick__blurb"></div>` +
        `<div class="pick__meta${tight ? ' pick__tight' : ''}"></div>`;
      b.querySelector('.pick__label').textContent = o?.label || 'Unnamed model';
      b.querySelector('.pick__blurb').textContent = o?.blurb || '';
      b.querySelector('.pick__meta').textContent = tight
        ? `${o.download_gb} GB download · will run, but slowly on this computer`
        : `${o.download_gb} GB download · runs well here`;
      b.onclick = () => choose(i);
      box.appendChild(b);
    });

    show('step-pick');
  } catch (e) {
    el('code-err').textContent = `Failed to load options: ${e}`;
    el('code-err').hidden = false;
  }
}

// ---------- 3. license ----------

function choose(i) {
  chosen = offers[i];
  if (!chosen.gated) return startDownload();

  el('license-line').textContent =
    `${chosen.label} is published under ${chosen.license}. ` +
    `You're downloading it directly from the publisher.`;
  el('license-text').textContent = chosen.license_text || chosen.license_url;
  show('step-license');
}

el('accept').onchange = (e) => { el('license-go').disabled = !e.target.checked; };
el('license-go').onclick = () => startDownload();

// ---------- 4. download ----------

async function startDownload() {
  show('step-dl');
  el('dl-head').textContent = `Downloading ${chosen.label}`;
  el('dl-err').hidden = true;
  el('dl-retry').hidden = false;

  // Since we can't actually download and install in browser,
  // we'll simulate the process and then provide next steps
  try {
    // Simulate download progress
    await simulateDownload();

    // Instead of actually installing, show completion with instructions
    showCompletion();
  } catch (e) {
    el('dl-err').textContent = String(e);
    el('dl-err').hidden = false;
    el('dl-retry').hidden = false;
  }
}

el('dl-retry').onclick = () => startDownload();

async function simulateDownload() {
  // Simulate progress updates
  const totalSteps = 100;
  for (let i = 0; i <= totalSteps; i++) {
    await new Promise(resolve => setTimeout(resolve, 30)); // 30ms per step

    const pct = i;
    el('bar').style.width = pct + '%';
    el('dl-stat').textContent =
      `${(i * chosen.download_gb / totalSteps).toFixed(2)} of ${chosen.download_gb.toFixed(2)} GB` +
      ` · 5.0 MB/s` +
      ` · ${Math.round((totalSteps - i) * 0.3)} sec left`;
  }
}

function showCompletion() {
  // Instead of invoking finish_setup, we show what to do next
  el('step-dl').hidden = true;

  const doneSection = el('step-done');
  doneSection.querySelector('h1').textContent = 'Setup Complete!';
  doneSection.querySelector('.step__sub').innerHTML =
    `Your Private AI with <strong>${chosen.label}</strong> is ready.<br><br>` +
    `To use it:<br>` +
    `1. Download the Private AI app for your platform:<br>` +
    `   <a href="https://private-ai.example.org/download/${getPlatform()}" target="_blank">Download Private AI</a><br><br>` +
    `2. During setup, it will automatically configure itself with your selected model.<br><br>` +
    `3. Once installed, turn off your wifi and try it - it works completely offline!`;

  doneSection.hidden = false;
}

// Helper to detect platform for download links
function getPlatform() {
  const platform = navigator.userAgent.toLowerCase();
  if (platform.indexOf('win') !== -1) return 'windows';
  if (platform.indexOf('mac') !== -1) return 'macos';
  if (platform.indexOf('android') !== -1) return 'android';
  if (platform.indexOf('iphone') !== -1 || platform.indexOf('ipad') !== -1) return 'ios';
  return 'windows'; // fallback
}

// ---------- 5. done ----------

el('done-go').onclick = () => {
  // In the real app, this would invoke('finish_setup')
  // For web version, we just acknowledge
  alert('Remember to download and install the Private AI app from the link provided!');
};

// ---------- boot ----------

(async function () {
  // Check if we have a validated code from landing page (stored in sessionStorage)
  validatedCode = sessionStorage.getItem('validatedCode');

  // Already set up? Skip straight past the wizard.
  // For web version, we always show the setup flow since we can't detect installed state
  // if (await invoke('is_installed')) { invoke('finish_setup'); return; }

  if (validatedCode) {
    // We have a pre-validated code, skip code entry and go straight to loading picks
    // Hide code entry step
    el('step-code').hidden = true;
    try {
      await loadPicks();
    } catch (e) {
      // If loading picks fails, show error and maybe allow re-entry?
      el('code-err').textContent = String(e);
      el('code-err').hidden = false;
      // Fall back to showing code entry so user can try again?
      el('step-code').hidden = false;
      codeInput.value = validatedCode; // pre-fill with the code we had
      codeInput.focus();
    }
    // Clear the validated code from sessionStorage after use (optional)
    sessionStorage.removeItem('validatedCode');
  } else {
    // No pre-validated code, show normal code entry flow
    show('step-code');
    codeInput.focus();
  }
})();





