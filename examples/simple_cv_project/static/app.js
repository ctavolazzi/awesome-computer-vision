const OUTPUTS = [
  {
    name: "Synthetic scene",
    file: "output/synthetic_scene.ppm",
  },
  {
    name: "Grayscale",
    file: "output/grayscale.pgm",
  },
  {
    name: "Gaussian blur",
    file: "output/blurred.pgm",
  },
  {
    name: "Sobel edges",
    file: "output/edges.pgm",
  },
  {
    name: "Harris corners",
    file: "output/corners.ppm",
  },
];

const MIN_SIZE = 128;
const MAX_SIZE = 512;

const gallery = document.getElementById("gallery");
const statsRoot = document.getElementById("stats");
const cardTemplate = document.getElementById("image-card");
const statTemplate = document.getElementById("stat-row");
const regenerateForm = document.getElementById("regenerate-form");
const sizeInput = document.getElementById("image-size");
const regenerateButton = document.getElementById("regenerate-button");
const statusMessage = document.getElementById("status-message");
const lastRun = document.getElementById("last-run");
const galleryPanel = document.getElementById("pipeline");
const statsPanel = document.querySelector(".panel.stats");

function cacheBusted(url) {
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}t=${Date.now()}`;
}

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

function tokenizeAnymap(text) {
  const tokens = [];
  for (const line of text.split(/\n|\r/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    tokens.push(...trimmed.split(/\s+/));
  }
  return tokens;
}

function parseAnymap(text) {
  const tokens = tokenizeAnymap(text);
  const magic = tokens.shift();
  if (!magic || (magic !== "P2" && magic !== "P3")) {
    throw new Error("Unsupported Netpbm format: " + magic);
  }

  const width = Number(tokens.shift());
  const height = Number(tokens.shift());
  const maxValue = Number(tokens.shift());
  if (!width || !height || !maxValue) {
    throw new Error("Invalid Netpbm header");
  }

  const pixelCount = width * height;
  const buffer = new Uint8ClampedArray(pixelCount * 4);

  if (magic === "P3") {
    for (let i = 0; i < pixelCount; i += 1) {
      const r = Number(tokens[i * 3 + 0]);
      const g = Number(tokens[i * 3 + 1]);
      const b = Number(tokens[i * 3 + 2]);
      const offset = i * 4;
      buffer[offset + 0] = (r / maxValue) * 255;
      buffer[offset + 1] = (g / maxValue) * 255;
      buffer[offset + 2] = (b / maxValue) * 255;
      buffer[offset + 3] = 255;
    }
  } else if (magic === "P2") {
    for (let i = 0; i < pixelCount; i += 1) {
      const value = Number(tokens[i]);
      const scaled = (value / maxValue) * 255;
      const offset = i * 4;
      buffer[offset + 0] = scaled;
      buffer[offset + 1] = scaled;
      buffer[offset + 2] = scaled;
      buffer[offset + 3] = 255;
    }
  }

  return { width, height, buffer };
}

function drawToCanvas(canvas, image) {
  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas 2D context not available");
  }
  if (canvas.width !== image.width || canvas.height !== image.height) {
    canvas.width = image.width;
    canvas.height = image.height;
  }
  const imageData = new ImageData(image.buffer, image.width, image.height);
  context.putImageData(imageData, 0, 0);
}

async function loadGallery() {
  gallery?.setAttribute("aria-busy", "true");
  galleryPanel?.setAttribute("aria-busy", "true");
  gallery.innerHTML = "";
  for (const output of OUTPUTS) {
    try {
      const text = await fetchText(cacheBusted(output.file));
      const parsed = parseAnymap(text);
      const node = cardTemplate.content.cloneNode(true);
      const canvas = node.querySelector(".card__canvas");
      const title = node.querySelector(".card__title");
      const link = node.querySelector(".card__download");

      title.textContent = output.name;
      canvas.setAttribute("aria-label", `${output.name} visualization`);
      link.href = output.file;

      drawToCanvas(canvas, parsed);
      gallery.appendChild(node);
    } catch (error) {
      console.error(error);
      const message = document.createElement("p");
      const detail = error instanceof Error ? error.message : String(error);
      message.className = "error";
      message.textContent = `Unable to load ${output.name}: ${detail}`;
      gallery.appendChild(message);
    }
  }
  gallery?.setAttribute("aria-busy", "false");
  galleryPanel?.setAttribute("aria-busy", "false");
}

function updateSizeFromMeta(meta) {
  if (!meta || !sizeInput) {
    return;
  }
  const { size, width } = meta;
  const next = typeof size === "number" ? size : width;
  if (typeof next === "number" && next >= MIN_SIZE && next <= MAX_SIZE) {
    sizeInput.value = String(next);
  }
}

function updateLastRun(meta, generatedAt) {
  if (!lastRun) {
    return;
  }

  if (!generatedAt) {
    lastRun.removeAttribute("dateTime");
    lastRun.textContent = "Not available";
    return;
  }

  const stamp = new Date(generatedAt);
  if (Number.isNaN(stamp.getTime())) {
    lastRun.removeAttribute("dateTime");
    lastRun.textContent = generatedAt;
    return;
  }

  const formatter = new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  });
  const size = meta?.size ?? meta?.width;
  lastRun.dateTime = stamp.toISOString();
  const sizeSuffix = typeof size === "number" ? ` (at ${size}px)` : "";
  lastRun.textContent = `${formatter.format(stamp)}${sizeSuffix}`;
}

async function loadStats() {
  statsPanel?.setAttribute("aria-busy", "true");
  statsRoot.innerHTML = "";
  try {
    const payload = await fetchJson(cacheBusted("output/summary.json"));
    const stats = payload.images || {};

    updateSizeFromMeta(payload.meta);
    updateLastRun(payload.meta, payload.generated_at);

    for (const [name, info] of Object.entries(stats)) {
      const node = statTemplate.content.cloneNode(true);
      node.querySelector(".stat__name").textContent = name;
      node
        .querySelector(".stat__value")
        .textContent = `min ${info.min} • max ${info.max} • mean ${info.mean}`;
      statsRoot.appendChild(node);
    }
  } catch (error) {
    console.error(error);
    const warning = document.createElement("p");
    const detail = error instanceof Error ? error.message : String(error);
    warning.className = "error";
    warning.textContent = `Unable to load statistics: ${detail}`;
    statsRoot.appendChild(warning);
    updateLastRun(null, null);
  }
  statsPanel?.setAttribute("aria-busy", "false");
}

async function requestRegeneration(size) {
  const response = await fetch("/api/regenerate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ size }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

function setStatus(message, isError = false) {
  if (!statusMessage) {
    return;
  }
  statusMessage.textContent = message;
  statusMessage.classList.toggle("status--error", isError);
}

if (regenerateForm && sizeInput && regenerateButton) {
  regenerateForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const parsed = Number(sizeInput.value);

    if (!Number.isFinite(parsed)) {
      setStatus("Enter a valid integer size.", true);
      return;
    }
    if (parsed < MIN_SIZE || parsed > MAX_SIZE) {
      setStatus(
        `Size must be between ${MIN_SIZE} and ${MAX_SIZE} pixels.`,
        true
      );
      return;
    }

    regenerateButton.disabled = true;
    setStatus(`Generating ${parsed}px outputs...`);

    try {
      const payload = await requestRegeneration(parsed);
      updateSizeFromMeta(payload.summary?.meta);
      updateLastRun(payload.summary?.meta, payload.summary?.generated_at);
      await Promise.all([loadGallery(), loadStats()]);
      setStatus(`Generated ${parsed}px outputs.`);
    } catch (error) {
      console.error(error);
      const detail = error instanceof Error ? error.message : String(error);
      setStatus(`Unable to regenerate: ${detail}`, true);
    } finally {
      regenerateButton.disabled = false;
    }
  });
}

Promise.all([loadGallery(), loadStats()]).catch((error) => {
  console.error(error);
  const detail = error instanceof Error ? error.message : String(error);
  setStatus(`Initial load failed: ${detail}`, true);
});
