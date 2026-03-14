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

const botMessageEl = document.getElementById("bot-message");
const messageArea  = document.querySelector(".message-area");
const textarea     = document.getElementById("user-input");
const sendBtn      = document.getElementById("send-btn");

// ── Fake response bank ──────────────────────────────────
// Each entry is a function that receives the user's text
// and returns the bot's reply. They fire in order; the last
// one loops for any extra messages.

const responses = [
  (userText) => {
    // Try to extract a name from "my name is ___" or just greet
    const nameMatch = userText.match(/(?:my name is|i'm|i am)\s+(\w+)/i);
    const name = nameMatch ? nameMatch[1] : "there";
    return `Hi ${name}! What kind of books have you enjoyed recently?`;
  },
  (_) =>
    "Nice! And what draws you in — is it the writing style, the world‑building, the characters, or something else?",
  (_) =>
    "Got it. Do you lean more toward fiction or non‑fiction these days?",
  (_) =>
    "Interesting. Are you in the mood for something comforting and familiar, or do you want to be challenged?",
  (_) =>
    "One last question — do you prefer a quick read or a book you can really sink into over a week or two?",
  (_) =>
    "Thanks! Based on everything you've told me, I think you'd love \"Piranesi\" by Susanna Clarke. It's a beautifully strange, immersive novel about a man living in a mysterious house full of endless halls and statues. Want another recommendation, or does that sound good?",
];

let turn = 0;

// ── Send handler ────────────────────────────────────────

function handleSend() {
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