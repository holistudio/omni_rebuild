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