/* ═══════════════════════════════════════════════════════════
   HYPERBOARD — app.js
   Logique complète : horloge, particules, données, IPC Python
   ═══════════════════════════════════════════════════════════ */

"use strict";

// ── IPC vers Python ──────────────────────────────────────
function sendToPython(obj) {
    try {
        window.webkit.messageHandlers.hyperboard.postMessage(JSON.stringify(obj));
    } catch(e) {
        console.warn("IPC indisponible (mode prévisualisation):", e);
    }
}

function closeBoard()    { sendToPython({ action: "close"  }); }
function launchAxiom()   { sendToPython({ action: "axiom"  }); }
function switchWorld(w)  { sendToPython({ action: "world", world: w }); }
function launchApp(cmd)  { sendToPython({ action: "launch", app: cmd }); }
function mediaCmd(cmd)   { sendToPython({ action: "launch", app: `playerctl ${cmd}` }); }

// ── Fermeture par Escape ─────────────────────────────────
document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeBoard();
});

// ── Horloge en temps réel ────────────────────────────────
function updateClock() {
    const now  = new Date();
    const hms  = now.toLocaleTimeString("fr-FR", { hour12: false });
    const date = now.toLocaleDateString("fr-FR", {
        weekday: "long", day: "numeric", month: "long", year: "numeric"
    });
    document.getElementById("clock-time").textContent = hms;
    document.getElementById("clock-date").textContent =
        date.charAt(0).toUpperCase() + date.slice(1);
}
setInterval(updateClock, 1000);
updateClock();

// ── Réception des données depuis Python ──────────────────
window.receiveData = function(data) {
    if (data.system)  updateStats(data.system);
    if (data.news)    updateNews(data.news);
    if (data.games)   updateGames(data.games);
    if (data.weather) updateWeather(data.weather);
    if (data.music)   updateMusic(data.music);
    if (data.world)   updateWorld(data.world);
};

// ── Ouverture du board ───────────────────────────────────
window.onBoardOpen = function() {
    const board = document.getElementById("board");
    board.classList.add("visible");
    initParticles();
    // Demander les données fraîches
    sendToPython({ action: "get_data" });
};

// ── Fermeture animée ─────────────────────────────────────
window.onBoardClose = function() {
    const board = document.getElementById("board");
    board.classList.remove("visible");
};

// ── Au chargement initial ─────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    // Animation d'entrée légère
    setTimeout(() => {
        const board = document.getElementById("board");
        board.classList.add("visible");
    }, 50);

    // Données de démo pendant le chargement
    loadDemoData();
    initParticles();
    loadAppsForWorld("prog");

    // Demander les vraies données
    sendToPython({ action: "get_data" });
});

// ── Stats système ────────────────────────────────────────
function updateStats(s) {
    // CPU
    setBar("cpu-bar",   s.cpu_pct,  "cpu-val",  `${s.cpu_pct}%`);
    // RAM
    setBar("ram-bar",   s.ram_pct,  "ram-val",  `${s.ram_used}G/${s.ram_total}G`);
    // GPU temp (max 110°)
    const gpuTempPct = Math.min((parseFloat(s.gpu_temp) / 100) * 100, 100);
    setBar("gpu-bar",   gpuTempPct, "gpu-temp", `${s.gpu_temp}°C`);
    // GPU utilisation
    setBar("gpu-use-bar", parseFloat(s.gpu_pct), "gpu-val", `${s.gpu_pct}%`);
    // Disque
    setBar("disk-bar",  s.disk_pct, "disk-val", `${s.disk_pct}%`);
    // VRAM
    document.getElementById("vram-text").textContent = s.gpu_mem || "—";
    // Batterie
    if (s.battery !== null && s.battery !== undefined) {
        const batCard = document.getElementById("battery-card");
        batCard.style.display = "flex";
        document.getElementById("bat-pct").textContent = `${Math.round(s.battery)}%`;
        document.getElementById("bat-icon").textContent = s.charging ? "🔌" : "🔋";
        setBar("bat-bar", s.battery, null, null);
    }
}

function setBar(barId, pct, valId, text) {
    const bar = document.getElementById(barId);
    if (bar) bar.style.width = `${Math.min(Math.max(pct, 0), 100)}%`;
    if (valId && text) {
        const val = document.getElementById(valId);
        if (val) val.textContent = text;
    }
}

// ── Actualités ───────────────────────────────────────────
function updateNews(news) {
    const list = document.getElementById("news-list");
    if (!news || news.length === 0) {
        list.innerHTML = "<div style='color:var(--text-dim);padding:12px'>Aucune actualité</div>";
        return;
    }
    list.innerHTML = news.map((item, i) => `
        <a class="news-item" href="${item.url}" onclick="openURL('${item.url}'); return false;">
            <div class="news-score">▲${item.score}</div>
            <div>
                <div class="news-title">${escapeHtml(item.title)}</div>
                <div class="news-author">par ${item.by}</div>
            </div>
        </a>
    `).join("");
}

function openURL(url) {
    sendToPython({ action: "launch", app: `firefox ${url}` });
    closeBoard();
}

// ── Jeux recommandés ─────────────────────────────────────
function updateGames(games) {
    const grid = document.getElementById("games-grid");
    grid.innerHTML = games.map(g => `
        <div class="game-item" onclick="searchGame('${g.name}')">
            <span class="game-emoji">${g.emoji}</span>
            <div>
                <div class="game-name">${escapeHtml(g.name)}</div>
                <div class="game-genre">${escapeHtml(g.genre)}</div>
            </div>
        </div>
    `).join("");
}

function searchGame(name) {
    const url = `https://store.steampowered.com/search/?term=${encodeURIComponent(name)}`;
    sendToPython({ action: "launch", app: `firefox ${url}` });
    closeBoard();
}

// ── Météo ────────────────────────────────────────────────
function updateWeather(w) {
    const icons = {
        "Sunny": "☀️", "Clear": "🌙", "Partly cloudy": "⛅",
        "Cloudy": "☁️", "Overcast": "🌫️", "Rain": "🌧️",
        "Light rain": "🌦️", "Heavy rain": "⛈️", "Snow": "❄️",
        "Thundery outbreaks": "⚡", "Fog": "🌁",
    };
    const desc  = w.desc || "—";
    const icon  = Object.entries(icons).find(([k]) => desc.includes(k))?.[1] || "🌤️";
    document.getElementById("weather-icon").textContent = icon;
    document.getElementById("weather-temp").textContent = `${w.temp_c}°C`;
    document.getElementById("weather-desc").textContent = desc;
    document.getElementById("weather-feels").textContent = `Ressenti : ${w.feels}°C`;
    document.getElementById("weather-humidity").textContent = `💧 ${w.humidity}%`;
}

// ── Musique ──────────────────────────────────────────────
function updateMusic(m) {
    const title  = m.title  || "—";
    const artist = m.artist || "—";
    const status = m.status || "Stopped";
    document.getElementById("music-title").textContent  = title;
    document.getElementById("music-artist").textContent = artist;
    document.getElementById("play-btn").textContent     = status === "Playing" ? "⏸" : "▶";

    // Animer l'icône si en cours
    const icon = document.querySelector(".music-icon");
    if (status === "Playing") {
        icon.style.animationPlayState = "running";
    } else {
        icon.style.animationPlayState = "paused";
    }
}

// ── Monde actif ──────────────────────────────────────────
function updateWorld(world) {
    document.body.setAttribute("data-world", world);
    const info = {
        gaming:  { emoji: "🎮", name: "CIRCUIT NOIR"   },
        cybersec:{ emoji: "🛡️", name: "GHOST PROTOCOL" },
        prog:    { emoji: "🔬", name: "DEEP SPACE IDE"  },
    }[world] || { emoji: "🔬", name: "DEEP SPACE IDE" };

    document.getElementById("world-emoji").textContent = info.emoji;
    document.getElementById("world-name").textContent  = info.name;

    // Activer le bouton du monde courant
    document.querySelectorAll(".world-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.world === world);
    });

    loadAppsForWorld(world);
}

// ── Apps rapides par monde ───────────────────────────────
const APPS = {
    gaming: [
        { name: "Steam",    emoji: "🎮", cmd: "steam" },
        { name: "Lutris",   emoji: "🏆", cmd: "lutris" },
        { name: "Bottles",  emoji: "🍾", cmd: "bottles" },
        { name: "Heroic",   emoji: "🦸", cmd: "heroic" },
        { name: "Discord",  emoji: "💬", cmd: "discord" },
        { name: "MangoHUD", emoji: "📊", cmd: "mangohud" },
    ],
    cybersec: [
        { name: "Wireshark",emoji: "🦈", cmd: "wireshark" },
        { name: "Ghidra",   emoji: "🔍", cmd: "ghidra" },
        { name: "MSF",      emoji: "💀", cmd: "kitty -e msfconsole" },
        { name: "Nmap",     emoji: "📡", cmd: "kitty -e nmap" },
        { name: "BurpSuite",emoji: "🕷️", cmd: "burpsuite" },
        { name: "Tor",      emoji: "🧅", cmd: "tor-browser" },
    ],
    prog: [
        { name: "VSCode",   emoji: "📝", cmd: "code" },
        { name: "Terminal", emoji: "⬛", cmd: "kitty" },
        { name: "Arduino",  emoji: "⚡", cmd: "arduino-ide" },
        { name: "Docker",   emoji: "🐳", cmd: "kitty -e lazydocker" },
        { name: "LazyGit",  emoji: "🌿", cmd: "kitty -e lazygit" },
        { name: "Jupyter",  emoji: "📓", cmd: "kitty -e jupyter lab" },
    ],
};

function loadAppsForWorld(world) {
    const apps = APPS[world] || APPS.prog;
    const grid = document.getElementById("app-grid");
    grid.innerHTML = apps.map(a => `
        <div class="app-item" onclick="launchApp('${a.cmd}')">
            <span class="app-icon">${a.emoji}</span>
            <span class="app-name">${a.name}</span>
        </div>
    `).join("");
}

// ── Données de démo (avant le vrai chargement) ───────────
function loadDemoData() {
    // Stats placeholder animés
    setTimeout(() => setBar("cpu-bar", 35, "cpu-val", "35%"), 200);
    setTimeout(() => setBar("ram-bar", 60, "ram-val", "9.6G/16G"), 400);
    setTimeout(() => setBar("gpu-bar", 55, "gpu-temp", "55°C"), 600);
    setTimeout(() => setBar("disk-bar",45, "disk-val", "45%"), 800);

    // News placeholder
    document.getElementById("news-list").innerHTML = `
        <div class="news-loading">
            <div class="spinner"></div>
            <span>Chargement des actualités...</span>
        </div>`;

    // Jeux par défaut
    updateGames(APPS.prog.map(a => ({ emoji: a.emoji, name: a.name, genre: "Application" })));

    // Météo placeholder
    document.getElementById("weather-temp").textContent = "—°C";
    document.getElementById("weather-desc").textContent = "Chargement...";
}

// ── Canvas Particules ────────────────────────────────────
function initParticles() {
    const canvas = document.getElementById("particles-canvas");
    const ctx    = canvas.getContext("2d");
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;

    const PARTICLE_COUNT = 80;
    const particles = [];

    // Couleur selon le monde
    const world = document.body.getAttribute("data-world") || "prog";
    const colors = {
        gaming:  ["#FF006E", "#00F5FF", "#7B2FFF"],
        cybersec:["#00FF41", "#003300", "#00AA44"],
        prog:    ["#A78BFA", "#2DD4BF", "#FF8C42"],
    }[world] || ["#A78BFA", "#2DD4BF", "#FF8C42"];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x:    Math.random() * canvas.width,
            y:    Math.random() * canvas.height,
            r:    Math.random() * 2 + 0.5,
            vx:   (Math.random() - 0.5) * 0.4,
            vy:   (Math.random() - 0.5) * 0.4,
            color: colors[Math.floor(Math.random() * colors.length)],
            alpha: Math.random() * 0.5 + 0.1,
        });
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;
            // Rebond sur les bords
            if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

            // Dessiner
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color + Math.floor(p.alpha * 255).toString(16).padStart(2, "0");
            ctx.fill();

            // Connexions entre particules proches
            for (const q of particles) {
                const d = Math.hypot(p.x - q.x, p.y - q.y);
                if (d < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(q.x, q.y);
                    ctx.strokeStyle = p.color + Math.floor((1 - d / 100) * 25).toString(16).padStart(2,"0");
                    ctx.lineWidth   = 0.5;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(drawParticles);
    }
    drawParticles();
}

// ── Utilitaires ──────────────────────────────────────────
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
