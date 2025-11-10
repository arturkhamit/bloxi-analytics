import { fetchData } from "./fetch-data.js";
import { renderStatistics } from "./fill-statisticts.js";

(function () {
  const STORAGE_KEY = "bloxi_chat_history";

  const openBtn = document.querySelector(".chatbot-trigger");
  const modal = document.getElementById("chatbotModal");
  if (!modal) return;

  const backdrop = modal.querySelector(".chatbot-modal__backdrop");
  const closeBtn = document.getElementById("chatbotCloseBtn");
  const clearBtn = document.getElementById("chatbotClearBtn");
  const form = document.getElementById("chatbotForm");
  const input = document.getElementById("chatbotInput");
  const messagesBox = document.getElementById("chatbotMessages");

  let messages = []; // [{role:'user'|'assistant', text:'...'}]

  function saveHistory() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.error(e);
    }
  }

  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  function scrollToBottom() {
    if (!messagesBox) return;
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function createMessageElement(text, role) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chatbot-message");
    wrapper.classList.add(
      role === "user" ? "chatbot-message--user" : "chatbot-message--assistant"
    );

    if (role === "user") {
      const avatar = document.createElement("div");
      avatar.className = "chatbot-message-avatar";
      avatar.innerHTML = '<i class="bx bx-user"></i>';
      wrapper.appendChild(avatar);
    }

    const bubble = document.createElement("div");
    bubble.classList.add("chatbot-bubble");
    bubble.classList.add(
      role === "user" ? "chatbot-bubble--user" : "chatbot-bubble--assistant"
    );
    bubble.textContent = text;

    wrapper.appendChild(bubble);

    return wrapper;
  }

  function renderAll() {
    if (!messagesBox) return;
    messagesBox.innerHTML = "";
    messages.forEach((m) => {
      messagesBox.appendChild(createMessageElement(m.text, m.role));
    });
    scrollToBottom();
  }

  function addMessage(role, text, { render = true } = {}) {
    messages.push({ role, text });
    if (render && messagesBox) {
      messagesBox.appendChild(createMessageElement(text, role));
      scrollToBottom();
    }
    saveHistory();
  }
  function clearChat() {
    messages = [];

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.error(e);
    }

    saveHistory();

    renderAll();
  }

  function showTyping() {
    if (!messagesBox) return;
    removeTyping();

    const wrapper = document.createElement("div");
    wrapper.className = "chatbot-message chatbot-message--assistant";
    wrapper.dataset.typing = "true";

    const bubble = document.createElement("div");
    bubble.className =
      "chatbot-bubble chatbot-bubble--assistant chatbot-typing";
    bubble.innerHTML = `
      <span class="chatbot-typing-dot"></span>
      <span class="chatbot-typing-dot"></span>
      <span class="chatbot-typing-dot"></span>
    `;

    wrapper.appendChild(bubble);
    messagesBox.appendChild(wrapper);
    scrollToBottom();
  }

  function removeTyping() {
    if (!messagesBox) return;
    const el = messagesBox.querySelector('[data-typing="true"]');
    if (el) el.remove();
  }

  /* ===== modal open/close ===== */

  function openModal() {
    modal.classList.add("open");
    document.body.classList.add("chatbot-open");
    if (input) setTimeout(() => input.focus(), 80);
  }

  function closeModal() {
    modal.classList.remove("open");
    document.body.classList.remove("chatbot-open");
  }

  /* ===== init history ===== */

  const stored = loadHistory();
  if (stored && Array.isArray(stored) && stored.length) {
    messages = stored;
    renderAll();
  } else {
    clearChat();
  }

  /* ===== events ===== */

  openBtn && openBtn.addEventListener("click", openModal);
  backdrop && backdrop.addEventListener("click", closeModal);
  closeBtn && closeBtn.addEventListener("click", closeModal);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  form &&
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;

      addMessage("user", text);
      const data = await fetchData({ query: text });
      console.log(typeof data);
      
      
      // const stats = data[data.length-1];
      // renderStatistics(stats, data);

      input.value = "";

      showTyping();

      // TODO: тут буде справжній запит до AI
      setTimeout(() => {
        removeTyping();
        const reply = "Demo answer for: " + text;
        addMessage("assistant", data);
      }, 1500);
    });

  clearBtn &&
    clearBtn.addEventListener("click", () => {
      clearChat();
    });
})();
