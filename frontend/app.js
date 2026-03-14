/**
 * Omnibot — fake LLM chat logic
 *
 * Behaviour (matching wireframe flow):
 *  1. Bot shows initial greeting: "Hi! I'm Omnibot"
 *  2. User types a message and presses Enter or clicks send.
 *  3. The screen transitions: user message disappears,
 *     bot message area fades to the next response.
 *  4. Only the current bot message is visible at a time.
 */

// point to Flask development server
const API_BASE = "http://localhost:5000/api"

const botMessageEl = document.getElementById("bot-message");
const messageArea  = document.querySelector(".message-area");
const textarea     = document.getElementById("user-input");
const sendBtn      = document.getElementById("send-btn");

// conversation session_id
let sessionId = "default"

// ── Send handler ────────────────────────────────────────

async function handleSend() {
  const text = textarea.value.trim();
  if (!text) return;

  const replyFn = responses[Math.min(turn, responses.length - 1)];
  const reply = replyFn(text);
  turn++;

  // Clear input immediately
  textarea.value = "";

  // Fade out current message
  messageArea.classList.remove("fade-in");
  messageArea.classList.add("fade-out");

  setTimeout(() => {
    botMessageEl.textContent = reply;
    messageArea.classList.remove("fade-out");
    messageArea.classList.add("fade-in");
    textarea.focus();
  }, 280);
}

// Click or Enter to send
sendBtn.addEventListener("click", handleSend);
textarea.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

// Focus input on load
textarea.focus();