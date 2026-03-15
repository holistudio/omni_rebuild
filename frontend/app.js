/**
 * Omnibot — real LLM chat via Flask backend
 *
 * Behaviour:
 *  1. On page load, fetches an LLM-generated intro message from /api/intro.
 *  2. User types a message and presses Enter or clicks send.
 *  3. The message is sent to the Flask backend at /api/chat.
 *  4. The bot's response fades in, replacing the previous message.
 *  5. Only the current bot message is visible at a time.
 */

// point to Flask development server
const API_BASE = "http://localhost:5000/api"

const botMessageEl = document.getElementById("bot-message");
const messageArea  = document.querySelector(".message-area");
const textarea     = document.getElementById("user-input");
const sendBtn      = document.getElementById("send-btn");

// conversation session_id
let sessionId = "default"

// ── Fetch LLM intro on page load ───────────────────────

async function fetchIntro() {
  // Temporary loading state
  botMessageEl.textContent = "...just a sec!";

  try {
    // Send POST request to intro end-point
    const res = await fetch(`${API_BASE}/intro`, {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body: JSON.stringify({ session_id: sessionId }),
    })

    // Intro greeting from LLM
    const data = await res.json();
    sessionId = data.session_id;

    // Display LLM intro
    setTimeout(() => {
      botMessageEl.textContent = data.response;
      messageArea.classList.remove("fade-out");
      messageArea.classList.add("fade-in");
      textarea.focus();
    }, 280);
  } catch (err) {
    console.error("Intro fetch error:", err);
    botMessageEl.textContent = "Hi! I'm Omnibot. What kind of books do you enjoy?";
  }
}
// ── Send handler ────────────────────────────────────────

async function handleSend() {
  const text = textarea.value.trim();
  if (!text) return;

  // Clear input immediately
  textarea.value = "";

  // Disable send button
  sendBtn.disabled = true;

  // Fade out current message
  messageArea.classList.remove("fade-in");
  messageArea.classList.add("fade-out");

  
  try {
    // Send POST request to chatbot/LLM
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body: JSON.stringify({ session_id: sessionId, message: text}),
    })

    // Response from LLM
    const data = await res.json();
    sessionId = data.session_id;

    // Display LLM response
    setTimeout(() => {
      botMessageEl.textContent = data.response;
      messageArea.classList.remove("fade-out");
      messageArea.classList.add("fade-in");
      textarea.focus();
    }, 280);

  } catch (err) {
    console.error("Error: ", err);

    // Display error message
    setTimeout(() => {
      botMessageEl.textContent = "Sorry, something went wrong.";
      messageArea.classList.remove("fade-out");
      messageArea.classList.add("fade-in");
    }, 280);
  }

  // Re-enable send button and focus input
  sendBtn.disabled = false;
  textarea.focus();
}

// Message display functions
function showBotMessage(text) {
  setTimeout(() => {
    botMessageEl.textContent = text;
    messageArea.classList.remove("fade-out");
    messageArea.classList.add("fade-in");
  }, 280);
}

function showBotHtml(html) {
  setTimeout(() => {
    botMessageEl.innerHTML = html;
    messageArea.classList.remove("fade-out");
    messageArea.classList.add("fade-in");
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

// On page load fetch the LLM intro
fetchIntro();

// Focus input on load
textarea.focus();