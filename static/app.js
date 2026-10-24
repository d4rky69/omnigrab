document.addEventListener("DOMContentLoaded", () => {
  const inspectForm = document.getElementById("inspectForm");
  const urlInput = document.getElementById("urlInput");
  const pasteBtn = document.getElementById("pasteBtn");
  const clearBtn = document.getElementById("clearBtn");
  const submitBtn = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");
  const statusMessage = document.getElementById("statusMessage");
  const statusText = document.getElementById("statusText");
  const errorBox = document.getElementById("errorBox");
  const errorTitle = document.getElementById("errorTitle");
  const errorDetail = document.getElementById("errorDetail");
  const cookiePromptBtnWrap = document.getElementById("cookiePromptBtnWrap");
  const openCookieFromErrorBtn = document.getElementById("openCookieFromErrorBtn");
  const resultCard = document.getElementById("resultCard");
  const mediaThumb = document.getElementById("mediaThumb");
  const mediaTitle = document.getElementById("mediaTitle");
  const mediaUploader = document.getElementById("mediaUploader");
  const platformBadge = document.getElementById("platformBadge");
  const durationBadge = document.getElementById("durationBadge");
  const originalLink = document.getElementById("originalLink");
  const optionsList = document.getElementById("optionsList");
  const formatTabs = document.getElementById("formatTabs");
  const downloadModal = document.getElementById("downloadModal");
  const dlStatusTitle = document.getElementById("dlStatusTitle");
  const dlStatusSub = document.getElementById("dlStatusSub");
  const historyList = document.getElementById("historyList");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");

  // Cookie modal elements
  const openCookieModalBtn = document.getElementById("openCookieModalBtn");
  const closeCookieModalBtn = document.getElementById("closeCookieModalBtn");
  const cancelCookieModalBtn = document.getElementById("cancelCookieModalBtn");
  const cookieModal = document.getElementById("cookieModal");
  const cookieInput = document.getElementById("cookieInput");
  const saveCookieBtn = document.getElementById("saveCookieBtn");
  const clearCookieBtn = document.getElementById("clearCookieBtn");
  const cookieDot = document.getElementById("cookieDot");
  const cookieLabel = document.getElementById("cookieLabel");

  // Share modal elements
  const openShareModalBtn = document.getElementById("openShareModalBtn");
  const closeShareModalBtn = document.getElementById("closeShareModalBtn");
  const shareModal = document.getElementById("shareModal");
  const shareUrlInput = document.getElementById("shareUrlInput");
  const copyShareUrlBtn = document.getElementById("copyShareUrlBtn");
  const copyBtnText = document.getElementById("copyBtnText");
  const shareQrCanvas = document.getElementById("shareQrCanvas");
  const shareQrImg = document.getElementById("shareQrImg");
  const shareWhatsapp = document.getElementById("shareWhatsapp");
  const shareTelegram = document.getElementById("shareTelegram");
  const shareTwitter = document.getElementById("shareTwitter");
  const nativeShareBtn = document.getElementById("nativeShareBtn");
  const shareMediaBtn = document.getElementById("shareMediaBtn");

  let currentMediaData = null;
  let activeFilter = "all";
  let activePublicUrl = null;

  // Discover active public tunnel URL if present
  async function checkTunnelStatus() {
    try {
      const res = await fetch("/api/tunnel/info");
      const data = await res.json();
      if (data.tunnel_active && data.public_url) {
        activePublicUrl = data.public_url;
      }
    } catch (e) {
      console.warn("Could not check tunnel info", e);
    }
  }
  checkTunnelStatus();

  function getEffectiveShareUrl() {
    if (activePublicUrl) return activePublicUrl;
    if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
      return window.location.origin;
    }
    return window.location.origin;
  }

  function renderQrCode(url) {
    if (typeof QRCode !== "undefined" && QRCode.toCanvas) {
      QRCode.toCanvas(shareQrCanvas, url, {
        width: 176,
        margin: 1,
        color: {
          dark: '#090a0f',
          light: '#ffffff'
        }
      }, function (error) {
        if (error) {
          fallbackQr(url);
        } else {
          shareQrCanvas.classList.remove("hidden");
          shareQrImg.classList.add("hidden");
        }
      });
    } else {
      fallbackQr(url);
    }
  }

  function fallbackQr(url) {
    shareQrCanvas.classList.add("hidden");
    shareQrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(url)}`;
    shareQrImg.classList.remove("hidden");
  }

  function openShareModal(customUrl = null, customTitle = null) {
    const targetUrl = customUrl || getEffectiveShareUrl();
    const title = customTitle || "OmniGrab — Download High-Definition Videos, Audio & Photos!";
    shareUrlInput.value = targetUrl;
    renderQrCode(targetUrl);

    // Update social share links
    shareWhatsapp.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(title + " " + targetUrl)}`;
    shareTelegram.href = `https://t.me/share/url?url=${encodeURIComponent(targetUrl)}&text=${encodeURIComponent(title)}`;
    shareTwitter.href = `https://twitter.com/intent/tweet?url=${encodeURIComponent(targetUrl)}&text=${encodeURIComponent(title)}`;

    shareModal.classList.remove("hidden");
  }

  function closeShareModal() {
    shareModal.classList.add("hidden");
  }

  if (openShareModalBtn) openShareModalBtn.addEventListener("click", () => openShareModal());
  if (closeShareModalBtn) closeShareModalBtn.addEventListener("click", closeShareModal);
  if (shareModal) {
    shareModal.addEventListener("click", (e) => {
      if (e.target === shareModal) closeShareModal();
    });
  }

  if (copyShareUrlBtn) {
    copyShareUrlBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(shareUrlInput.value);
        copyBtnText.textContent = "Copied!";
        copyShareUrlBtn.classList.add("from-emerald-600", "to-teal-600");
        setTimeout(() => {
          copyBtnText.textContent = "Copy";
          copyShareUrlBtn.classList.remove("from-emerald-600", "to-teal-600");
        }, 2000);
      } catch (err) {
        shareUrlInput.select();
        document.execCommand("copy");
        copyBtnText.textContent = "Copied!";
        setTimeout(() => {
          copyBtnText.textContent = "Copy";
        }, 2000);
      }
    });
  }

  if (nativeShareBtn) {
    nativeShareBtn.addEventListener("click", async () => {
      const url = shareUrlInput.value;
      if (navigator.share) {
        try {
          await navigator.share({
            title: "OmniGrab Media Downloader",
            text: "Download high-definition videos, audio, and photos easily with OmniGrab!",
            url: url
          });
        } catch (e) {
          /* user dismissed or closed */
        }
      } else {
        copyShareUrlBtn.click();
      }
    });
  }

  if (shareMediaBtn) {
    shareMediaBtn.addEventListener("click", () => {
      if (!currentMediaData) return;
      const shareUrl = `${getEffectiveShareUrl()}?url=${encodeURIComponent(currentMediaData.url)}`;
      openShareModal(shareUrl, `Check out this ${currentMediaData.platform || "media"}: "${currentMediaData.title}" on OmniGrab!`);
    });
  }

  // Check cookie status on load
  async function checkCookieStatus() {
    try {
      const res = await fetch("/api/cookies/status");
      const data = await res.json();
      if (data.active) {
        cookieDot.className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
        cookieLabel.textContent = "Cookies: Active";
      } else {
        cookieDot.className = "w-2 h-2 rounded-full bg-slate-500";
        cookieLabel.textContent = "Cookies: Inactive";
      }
    } catch (e) {
      console.warn("Could not check cookie status", e);
    }
  }
  checkCookieStatus();

  // Modal open/close
  function toggleCookieModal(show) {
    if (show) {
      cookieModal.classList.remove("hidden");
    } else {
      cookieModal.classList.add("hidden");
    }
  }

  openCookieModalBtn.addEventListener("click", () => toggleCookieModal(true));
  closeCookieModalBtn.addEventListener("click", () => toggleCookieModal(false));
  cancelCookieModalBtn.addEventListener("click", () => toggleCookieModal(false));
  if (openCookieFromErrorBtn) {
    openCookieFromErrorBtn.addEventListener("click", () => toggleCookieModal(true));
  }

  // Save cookies
  saveCookieBtn.addEventListener("click", async () => {
    const text = cookieInput.value.trim();
    if (!text) {
      alert("Please paste your cookies content first.");
      return;
    }
    try {
      saveCookieBtn.disabled = true;
      saveCookieBtn.textContent = "Saving...";
      const res = await fetch("/api/cookies/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cookies: text })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to save cookies");
      alert("Cookies saved successfully! YouTube bot check is now bypassed.");
      toggleCookieModal(false);
      checkCookieStatus();
      cookieInput.value = "";
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      saveCookieBtn.disabled = false;
      saveCookieBtn.textContent = "Save Cookies";
    }
  });

  // Clear cookies
  clearCookieBtn.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to remove saved cookies?")) return;
    try {
      await fetch("/api/cookies/clear", { method: "DELETE" });
      checkCookieStatus();
      alert("Cookies cleared.");
    } catch (err) {
      alert("Error clearing cookies: " + err.message);
    }
  });

  // Toggle clear button
  urlInput.addEventListener("input", () => {
    if (urlInput.value.trim().length > 0) {
      clearBtn.classList.remove("hidden");
    } else {
      clearBtn.classList.add("hidden");
    }
  });

  clearBtn.addEventListener("click", () => {
    urlInput.value = "";
    clearBtn.classList.add("hidden");
    urlInput.focus();
  });

  // Paste from clipboard
  pasteBtn.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        clearBtn.classList.remove("hidden");
        if (text.startsWith("http://") || text.startsWith("https://")) {
          inspectForm.dispatchEvent(new Event("submit"));
        }
      }
    } catch (err) {
      console.warn("Clipboard access denied or unsupported", err);
      urlInput.focus();
    }
  });

  // Sample links
  document.querySelectorAll(".sample-link").forEach(btn => {
    btn.addEventListener("click", () => {
      urlInput.value = btn.dataset.url;
      clearBtn.classList.remove("hidden");
      inspectForm.dispatchEvent(new Event("submit"));
    });
  });

  // Handle Form Submit
  inspectForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (!url) return;

    hideError();
    setLoading(true, "Connecting to media extractor...");

    try {
      const response = await fetch("/api/inspect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to inspect URL.");
      }

      currentMediaData = data;
      renderResultCard(data);
      saveToHistory(data);
      renderHistory();

    } catch (err) {
      showError("Analysis Failed", err.message || "Could not retrieve media details.");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading, message = "") {
    if (loading) {
      submitBtn.disabled = true;
      btnText.textContent = "Analyzing...";
      btnSpinner.classList.remove("hidden");
      statusMessage.classList.remove("hidden");
      statusText.textContent = message;
      resultCard.classList.add("hidden");
    } else {
      submitBtn.disabled = false;
      btnText.textContent = "Fetch Media";
      btnSpinner.classList.add("hidden");
      statusMessage.classList.add("hidden");
    }
  }

  function showError(title, message) {
    errorTitle.textContent = title;
    errorDetail.textContent = message;
    errorBox.classList.remove("hidden");
    resultCard.classList.add("hidden");

    if (message.includes("bot check") || message.includes("account authentication") || message.includes("Cookies")) {
      cookiePromptBtnWrap.classList.remove("hidden");
    } else {
      cookiePromptBtnWrap.classList.add("hidden");
    }

    errorBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function hideError() {
    errorBox.classList.add("hidden");
    cookiePromptBtnWrap.classList.add("hidden");
  }

  function renderResultCard(data) {
    mediaTitle.textContent = data.title;
    mediaTitle.title = data.title;
    mediaUploader.textContent = data.uploader || "Creator";
    platformBadge.textContent = data.platform || "Media";
    durationBadge.textContent = data.duration !== "N/A" ? data.duration : (data.platform === "Pinterest" ? "Pin" : "Media");
    originalLink.href = data.url;

    const p = (data.platform || "").toLowerCase();
    if (p.includes("youtube")) {
      platformBadge.className = "px-2 py-0.5 rounded bg-red-600 text-white backdrop-blur-sm";
    } else if (p.includes("instagram")) {
      platformBadge.className = "px-2 py-0.5 rounded bg-gradient-to-r from-pink-500 to-purple-600 text-white";
    } else if (p.includes("pinterest")) {
      platformBadge.className = "px-2 py-0.5 rounded bg-rose-600 text-white";
    } else if (p.includes("tiktok")) {
      platformBadge.className = "px-2 py-0.5 rounded bg-cyan-600 text-white";
    } else {
      platformBadge.className = "px-2 py-0.5 rounded bg-purple-600 text-white";
    }

    if (data.thumbnail) {
      mediaThumb.src = data.thumbnail;
      mediaThumb.classList.remove("hidden");
    } else {
      mediaThumb.src = "data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22300%22%20height%3D%22200%22%20viewBox%3D%220%200%20300%20200%22%3E%3Crect%20fill%3D%22%2312141d%22%20width%3D%22300%22%20height%3D%22200%22%2F%3E%3Ctext%20fill%3D%22%2364748b%22%20font-family%3D%22sans-serif%22%20font-size%3D%2214%22%20x%3D%2250%25%22%20y%3D%2250%25%22%20text-anchor%3D%22middle%22%3ENo%20Preview%3C%2Ftext%3E%3C%2Fsvg%3E";
    }

    renderOptions(data.options, activeFilter);
    resultCard.classList.remove("hidden");
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Filter Tabs
  formatTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab-btn");
    if (!btn || !currentMediaData) return;

    formatTabs.querySelectorAll(".tab-btn").forEach(b => {
      b.className = "tab-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 text-slate-400 hover:text-white";
    });
    btn.className = "tab-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-600 text-white";

    activeFilter = btn.dataset.tab;
    renderOptions(currentMediaData.options, activeFilter);
  });

  function renderOptions(options, filter) {
    optionsList.innerHTML = "";

    const filtered = options.filter(opt => {
      if (filter === "all") return true;
      return opt.type === filter;
    });

    if (filtered.length === 0) {
      optionsList.innerHTML = `
        <div class="text-center py-6 text-slate-500 text-xs bg-white/[0.01] rounded-xl border border-white/5">
          No ${filter} formats available for this media item.
        </div>
      `;
      return;
    }

    filtered.forEach(opt => {
      const row = document.createElement("div");
      row.className = "flex items-center justify-between p-3 rounded-xl bg-obsidian/60 hover:bg-obsidian/90 border border-white/5 hover:border-white/10 transition group";

      let typeBadge = "";
      if (opt.type === "video") {
        typeBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/10 border border-blue-500/20 text-blue-400">Video</span>`;
      } else if (opt.type === "audio") {
        typeBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/10 border border-amber-500/20 text-amber-400">Audio</span>`;
      } else {
        typeBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">Photo</span>`;
      }

      const sizeDisplay = opt.size ? `<span class="text-xs text-slate-400">${opt.size}</span>` : "";

      row.innerHTML = `
        <div class="flex items-center gap-3">
          ${typeBadge}
          <div>
            <div class="text-xs font-semibold text-white group-hover:text-purple-300 transition">${opt.label}</div>
            <div class="text-[11px] text-slate-400 flex items-center gap-2">
              <span>Format: .${opt.ext.toUpperCase()}</span>
              <span>•</span>
              <span>${opt.quality}</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          ${sizeDisplay}
          <button 
            class="download-btn px-4 py-2 bg-purple-600 hover:bg-purple-500 active:scale-[0.97] text-white font-semibold text-xs rounded-lg transition shadow-md shadow-purple-600/20 flex items-center gap-1.5"
            data-opt-id="${opt.id}"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            <span>Download</span>
          </button>
        </div>
      `;

      const dlBtn = row.querySelector(".download-btn");
      dlBtn.addEventListener("click", () => triggerDownload(opt, dlBtn));

      optionsList.appendChild(row);
    });
  }

  function triggerDownload(option, buttonEl) {
    if (!currentMediaData) return;

    showToast(`Downloading: ${option.label}`, "Processing media & streaming to your device...");

    const originalContent = buttonEl.innerHTML;
    buttonEl.disabled = true;
    buttonEl.innerHTML = `
      <svg class="animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Working...</span>
    `;

    const params = new URLSearchParams({
      url: currentMediaData.url,
      type: option.type,
      ext: option.ext,
      title: currentMediaData.title
    });

    if (option.format_spec) {
      params.append("format_spec", option.format_spec);
    }
    if (option.direct_url) {
      params.append("direct_url", option.direct_url);
    }

    const downloadUrl = `/api/download?${params.toString()}`;

    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = downloadUrl;
    document.body.appendChild(iframe);

    setTimeout(() => {
      buttonEl.disabled = false;
      buttonEl.innerHTML = originalContent;
      setTimeout(() => iframe.remove(), 10000);
    }, 4000);
  }

  function showToast(title, sub) {
    dlStatusTitle.textContent = title;
    dlStatusSub.textContent = sub;
    downloadModal.classList.remove("hidden");
    setTimeout(() => {
      downloadModal.classList.add("hidden");
    }, 6000);
  }

  function saveToHistory(item) {
    try {
      let history = JSON.parse(localStorage.getItem("omnigrab_history") || "[]");
      history = history.filter(h => h.url !== item.url);
      history.unshift({
        title: item.title,
        url: item.url,
        platform: item.platform,
        thumbnail: item.thumbnail,
        date: new Date().toLocaleDateString()
      });
      if (history.length > 6) history = history.slice(0, 6);
      localStorage.setItem("omnigrab_history", JSON.stringify(history));
    } catch (e) {
      console.warn("Storage error", e);
    }
  }

  function renderHistory() {
    try {
      const history = JSON.parse(localStorage.getItem("omnigrab_history") || "[]");
      if (history.length === 0) {
        historyList.innerHTML = `<p class="text-xs text-slate-600 text-center py-4 bg-white/[0.02] rounded-xl border border-white/5">No recent downloads yet. Paste a link above to get started!</p>`;
        return;
      }

      historyList.innerHTML = "";
      history.forEach(item => {
        const div = document.createElement("div");
        div.className = "flex items-center justify-between p-2.5 rounded-xl bg-obsidian/40 hover:bg-obsidian/70 border border-white/5 transition cursor-pointer group";
        div.innerHTML = `
          <div class="flex items-center gap-3 overflow-hidden">
            <div class="w-10 h-10 rounded-lg overflow-hidden bg-slate-800 flex-shrink-0 border border-white/5">
              ${item.thumbnail ? `<img src="${item.thumbnail}" class="w-full h-full object-cover">` : `<div class="w-full h-full flex items-center justify-center text-[10px] text-slate-500">N/A</div>`}
            </div>
            <div class="overflow-hidden">
              <p class="text-xs font-semibold text-slate-200 group-hover:text-purple-300 truncate">${item.title}</p>
              <p class="text-[10px] text-slate-500">${item.platform || "Web"} • ${item.date}</p>
            </div>
          </div>
          <button class="re-grab-btn px-2.5 py-1 text-[11px] font-medium text-slate-400 group-hover:text-white bg-white/5 group-hover:bg-purple-600 rounded-lg transition whitespace-nowrap">
            Load
          </button>
        `;

        div.addEventListener("click", () => {
          urlInput.value = item.url;
          clearBtn.classList.remove("hidden");
          inspectForm.dispatchEvent(new Event("submit"));
        });

        historyList.appendChild(div);
      });
    } catch (e) {
      console.warn("History render error", e);
    }
  }

  clearHistoryBtn.addEventListener("click", () => {
    localStorage.removeItem("omnigrab_history");
    renderHistory();
  });

  renderHistory();

  // Auto-fetch if a shared URL is in query string (?url=...)
  try {
    const params = new URLSearchParams(window.location.search);
    const sharedUrl = params.get("url");
    if (sharedUrl) {
      urlInput.value = sharedUrl;
      clearBtn.classList.remove("hidden");
      setTimeout(() => {
        inspectForm.dispatchEvent(new Event("submit"));
      }, 300);
    }
  } catch (e) {
    console.warn("Could not parse shared query parameter", e);
  }
});
