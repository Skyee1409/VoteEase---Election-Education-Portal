/* ═══════════════════════════════════════════════════════════
   VoteEase — app.js
   All UI interactions + Flask API calls
═══════════════════════════════════════════════════════════ */

'use strict';

/* ── Section Navigation ──────────────────────────────────── */
function showSection(id) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(id);
  if (target) {
    target.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  document.querySelectorAll('.nav-links').forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === '#' + id);
  });
  // Load timeline data when that section is shown
  if (id === 'timeline') loadElections();
  if (id === 'home') loadNews();
}

/* ── Mobile Hamburger ────────────────────────────────────── */
function toggleMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

/* ── Live News ───────────────────────────────────────────── */
async function loadNews() {
  const container = document.getElementById('newsContainer');
  if (!container) return;

  try {
    const res  = await fetch('/api/news');
    const data = await res.json();
    const news = data.news || [];

    if (!news.length) {
      container.innerHTML = '<div class="loading-msg">No news updates at the moment.</div>';
      return;
    }

    container.innerHTML = news.map(item => `
      <div class="news-card">
        <span class="news-tag ${item.type}">${item.tag}</span>
        <h3>${item.title}</h3>
        <p>${item.content}</p>
        <span class="news-date">🗓️ ${formatDate(item.date)}</span>
      </div>
    `).join('');
  } catch {
    container.innerHTML = '<div class="loading-msg">⚠️ Failed to load news updates.</div>';
  }
}


/* ── Election Timeline ───────────────────────────────────── */
let allElections = [];

async function loadElections() {
  const list = document.getElementById('timelineList');
  list.innerHTML = '<div class="loading-msg"><span class="spinner"></span> Loading elections...</div>';
  try {
    const res  = await fetch('/api/elections');
    const data = await res.json();
    allElections = data.elections || [];
    renderElections(allElections);
  } catch {
    list.innerHTML = '<div class="loading-msg">⚠️ Could not load elections. Please try again.</div>';
  }
}

function renderElections(elections) {
  const list = document.getElementById('timelineList');
  if (!elections.length) {
    list.innerHTML = '<div class="loading-msg">No elections found.</div>';
    return;
  }
  const icons = { National: '🇮🇳', State: '🏛️', Local: '🏘️' };
  list.innerHTML = elections.map(e => `
    <div class="timeline-item">
      <div class="tl-icon">${icons[e.type] || '🗳️'}</div>
      <div class="tl-info">
        <div class="tl-title">${e.title}</div>
        <div class="tl-desc">${e.description}</div>
      </div>
      <div class="tl-meta">
        <span class="badge badge-${e.status}">${e.status.toUpperCase()}</span>
        <div class="tl-date">📅 ${formatDate(e.date)}</div>
        <div class="tl-phases">${e.phases} phase${e.phases > 1 ? 's' : ''}</div>
      </div>
    </div>
  `).join('');
}

function filterElections(filter, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const filtered = filter === 'all'
    ? allElections
    : allElections.filter(e => e.status === filter);
  renderElections(filtered);
}

/* ── Polling Booth Locator ───────────────────────────────── */
async function findBooths() {
  const city    = document.getElementById('booth_city').value.trim();
  const pincode = document.getElementById('booth_pin').value.trim();
  const results = document.getElementById('boothResults');

  if (!city && !pincode)
    return alert('❌ Please enter a city or pin code.');

  results.innerHTML = '<div class="loading-msg"><span class="spinner"></span> Searching booths...</div>';

  try {
    const res  = await fetch('/api/find-booth', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ city, pincode }),
    });
    const data = await res.json();

    if (data.booths && data.booths.length) {
      results.innerHTML = `
        <p style="color:var(--text-muted);font-size:0.88rem;margin-bottom:1rem;">
          Found <strong style="color:#818cf8">${data.total}</strong> polling booth(s) near you:
        </p>
        ${data.booths.map(b => `
          <div class="booth-card">
            <div class="booth-num">${b.booth_number}</div>
            <div class="booth-info">
              <h4>${b.name}</h4>
              <p>📍 ${b.address}</p>
              <p>⏰ ${b.timing}</p>
              <div class="booth-tags">
                ${b.facilities.map(f => `<span class="booth-tag">${f}</span>`).join('')}
              </div>
            </div>
            <div class="booth-distance">${b.distance}</div>
          </div>
        `).join('')}
      `;
    } else {
      results.innerHTML = '<div class="loading-msg">No booths found for the given location.</div>';
    }
  } catch {
    results.innerHTML = '<div class="loading-msg">⚠️ Network error. Please try again.</div>';
  }
}


/* ── Notification Modal ──────────────────────────────────── */
function showNotifModal() {
  document.getElementById('notifModal').classList.add('open');
}

function closeNotifModal(e) {
  if (!e || e.target === document.getElementById('notifModal')) {
    document.getElementById('notifModal').classList.remove('open');
  }
}

async function subscribeNotifications() {
  const email = document.getElementById('notif_email').value.trim();
  const phone = document.getElementById('notif_phone').value.trim();
  const msg   = document.getElementById('notifMsg');

  if (!email && !phone)
    return (msg.innerHTML = '<span style="color:#fca5a5">❌ Please enter email or phone.</span>');

  try {
    const res  = await fetch('/api/subscribe-notifications', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ email, phone }),
    });
    const data = await res.json();
    msg.innerHTML = data.success
      ? `<span style="color:#6ee7b7">✅ ${data.message}</span>`
      : `<span style="color:#fca5a5">❌ ${data.error}</span>`;
  } catch {
    msg.innerHTML = '<span style="color:#fca5a5">⚠️ Network error. Try again.</span>';
  }
}

/* ── Chatbot ─────────────────────────────────────────────── */
function openChat() {
  document.getElementById('chatWindow').classList.add('open');
  // Remove notification badge
  const badge = document.querySelector('.chat-badge');
  if (badge) badge.style.display = 'none';
  document.getElementById('chatInput').focus();
}

function closeChat() {
  document.getElementById('chatWindow').classList.remove('open');
}

async function sendMessage() {
  const input   = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  appendMessage('user', message);
  input.value = '';

  // Typing indicator
  const typingId = appendMessage('bot', '⏳ Typing...');

  try {
    const res  = await fetch('/api/chatbot', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ message }),
    });
    const data = await res.json();
    updateMessage(typingId, data.response, data.timestamp);
  } catch {
    updateMessage(typingId, '⚠️ Could not connect. Please try again.', '');
  }
}

function sendQuick(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

function appendMessage(role, text) {
  const msgs = document.getElementById('chatMessages');
  const id   = 'msg-' + Date.now();
  const now  = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  msgs.insertAdjacentHTML('beforeend', `
    <div class="chat-msg ${role}" id="${id}">
      <div class="msg-bubble">${escapeHtml(text)}</div>
      <div class="msg-time">${now}</div>
    </div>
  `);
  msgs.scrollTop = msgs.scrollHeight;
  return id;
}

function updateMessage(id, text, time) {
  const el = document.getElementById(id);
  if (el) {
    el.querySelector('.msg-bubble').textContent = text;
    if (time) el.querySelector('.msg-time').textContent = time;
  }
}

/* ── Language Toggle (EN ↔ HI) ──────────────────────────── */
let isHindi = false;

const translations = {
  heroTitle : ['Your Vote,<br/><span class="gradient-text">Your Future</span>',
               'आपका वोट,<br/><span class="gradient-text">आपका भविष्य</span>'],
  heroSub   : ['Register to vote, find your polling booth, track elections, and get instant help — all in one place.',
               'वोट करने के लिए पंजीकरण करें, मतदान केंद्र खोजें, चुनाव ट्रैक करें — सब एक ही जगह।'],
  featTitle : ['Our Services', 'हमारी सेवाएं'],
};

function toggleLang() {
  isHindi = !isHindi;
  const btn = document.getElementById('langBtn');
  btn.textContent = isHindi ? '🌐 English' : '🌐 हिंदी';

  const idx = isHindi ? 1 : 0;
  for (const [elId, texts] of Object.entries(translations)) {
    const el = document.getElementById(elId);
    if (el) el.innerHTML = texts[idx];
  }
}

/* ── Voice Assistance ────────────────────────────────────── */
let voiceActive = false;
let synth = window.speechSynthesis;

function speak(text) {
  if (!synth) return alert('Voice not supported in this browser.');
  synth.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang  = isHindi ? 'hi-IN' : 'en-IN';
  utt.rate  = 0.9;
  synth.speak(utt);
}

function toggleVoice() {
  voiceActive = !voiceActive;
  const bar  = document.getElementById('voiceBar');
  const btn  = document.getElementById('voiceBtn');

  if (voiceActive) {
    bar.style.display = 'flex';
    btn.style.background = 'rgba(79,70,229,0.5)';
    speak('Voice assistance activated. Welcome to VoteEase. How can I help you today?');
    document.getElementById('voiceText').textContent = 'Voice assistance active';
  } else {
    stopVoice();
  }
}

function stopVoice() {
  voiceActive = false;
  synth && synth.cancel();
  document.getElementById('voiceBar').style.display = 'none';
  document.getElementById('voiceBtn').style.background = '';
}

/* ── Utilities ───────────────────────────────────────────── */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return isNaN(d) ? dateStr : d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function showError(el, msg) {
  el.style.display = 'block';
  el.innerHTML = `❌ ${msg}`;
  el.className = 'error-banner';
}

function showRegionalParties(stateId, btn) {
  // Update buttons
  document.querySelectorAll('.state-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  // Update content
  document.querySelectorAll('.state-parties-group').forEach(g => g.classList.remove('active'));
  const target = document.getElementById('parties-' + stateId);
  if (target) target.classList.add('active');
}

/* ── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Show home section on load
  showSection('home');
  loadNews();

  // Enter key on booth input
  document.getElementById('booth_pin').addEventListener('keydown', e => {
    if (e.key === 'Enter') findBooths();
  });

  // Close mobile menu on link click
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      document.getElementById('navLinks').classList.remove('open');
    });
  });

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    nav.style.boxShadow = window.scrollY > 10
      ? '0 4px 24px rgba(0,0,0,0.5)'
      : 'none';
  });
});
