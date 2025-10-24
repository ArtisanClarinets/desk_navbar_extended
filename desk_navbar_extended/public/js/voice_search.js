(() => {
  frappe.provide("desk_navbar_extended.voice");
  window.desk_navbar_extended = window.desk_navbar_extended || {};
  window.desk_navbar_extended.voice = window.desk_navbar_extended.voice || {};

  const state = {
    button: null,
    status: null,
    recognition: null,
    listening: false,
    startTimestamp: 0,
    mediaRecorder: null,
    chunks: [],
    settings: null,
    cancelShortcutInstalled: false,
  };

  function resolveSearchInput() {
    const candidates = [
      "#navbar-search",
      ".navbar-search input",
      "input[data-element='awesome-bar']",
    ];
    for (const selector of candidates) {
      const node = document.querySelector(selector);
      if (node) return node;
    }
    if (frappe.search?.utils?.search_input) {
      return frappe.search.utils.search_input;
    }
    return null;
  }

  function ensureStatusElement() {
    if (state.status) return state.status;
    const status = document.createElement("span");
    status.className = "desk-navbar-extended-voice__status";
    status.setAttribute("role", "status");
    status.textContent = __("Tap to dictate");
    state.button?.parentElement?.appendChild(status);
    state.status = status;
    return status;
  }

  function updateStatus(message, confidence) {
    const status = ensureStatusElement();
    status.textContent = confidence
      ? `${message} (${Math.round(confidence * 100)}%)`
      : message;
  }

  function stopNativeRecognition() {
    if (!state.recognition) return;
    state.recognition.onresult = null;
    state.recognition.onend = null;
    state.recognition.onerror = null;
    state.recognition.stop();
    state.listening = false;
    state.button?.classList.remove("is-recording");
    updateStatus(__("Transcription complete"));
  }

  function injectButton() {
    if (state.button) return state.button;
    const input = resolveSearchInput();
    if (!input) return null;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "desk-navbar-extended-voice__button";
    button.setAttribute("aria-label", __("Start voice search"));
    button.innerHTML = "<span aria-hidden='true'>🎤</span>";
    button.addEventListener("click", () => {
      if (state.listening) {
        stopRecording();
      } else {
        startRecording();
      }
    });

    input.parentElement?.appendChild(button);
    state.button = button;
    ensureStatusElement();
    return button;
  }

  function buildRecognition() {
    if (state.recognition) return state.recognition;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const recognition = new SpeechRecognition();
    recognition.lang = frappe.boot?.user?.language || "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0];
      if (!transcript) return;
      const input = resolveSearchInput();
      if (!input) return;
      input.value = transcript.transcript;
      updateStatus(__("Understood"), transcript.confidence);
      triggerSearch(input);
    };

    recognition.onerror = (event) => {
      updateStatus(__("Voice search error"));
      frappe.msgprint({
        title: __("Voice Search"),
        message: event.error,
        indicator: "red",
      });
    };

    recognition.onend = () => {
      state.listening = false;
      state.button?.classList.remove("is-recording");
    };

    state.recognition = recognition;
    return recognition;
  }

  function triggerSearch(input) {
    if (frappe.search?.utils?.search) {
      frappe.search.utils.search(input.value);
    } else {
      input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter" }));
    }
  }

  function startNativeRecording() {
    const recognition = buildRecognition();
    if (!recognition) return false;
    recognition.start();
    state.listening = true;
    state.button?.classList.add("is-recording");
    state.startTimestamp = Date.now();
    updateStatus(__("Listening"));
    return true;
  }

  function stopRecording() {
    if (state.recognition && state.listening) {
      stopNativeRecognition();
    }
    if (state.mediaRecorder) {
      state.mediaRecorder.stop();
    }
  }

  function fallbackRecorderSupported() {
    return Boolean(
      navigator.mediaDevices?.getUserMedia && window.MediaRecorder,
    );
  }

  async function startFallbackRecorder() {
    if (!fallbackRecorderSupported()) {
      frappe.msgprint({
        title: __("Voice Search"),
        message: __("Browser does not support voice capture."),
        indicator: "orange",
      });
      updateStatus(__("Unsupported"));
      return;
    }

    state.chunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    state.mediaRecorder = recorder;
    state.listening = true;
    state.button?.classList.add("is-recording");
    updateStatus(__("Recording"));

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        state.chunks.push(event.data);
      }
    };

    recorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      state.listening = false;
      state.button?.classList.remove("is-recording");
      const blob = new Blob(state.chunks, { type: "audio/webm" });
      state.mediaRecorder = null;
      const base64 = await blob.arrayBuffer().then((buffer) => {
        const bytes = new Uint8Array(buffer);
        let binary = "";
        bytes.forEach((b) => (binary += String.fromCharCode(b)));
        return window.btoa(binary);
      });
      updateStatus(__("Uploading"));
      try {
        await frappe.call({
          method: "desk_navbar_extended.api.transcribe_audio",
          args: { audio: base64, filename: "voice-search.webm" },
        });
        updateStatus(__("Sent for transcription"));
      } catch (error) {
        updateStatus(__("Upload failed"));
        frappe.msgprint({
          title: __("Voice Search"),
          message: error.message,
          indicator: "red",
        });
      }
    };

    recorder.start();
  }

  function startRecording() {
    if (startNativeRecording()) return;
    startFallbackRecorder();
  }

  function installCancelShortcut() {
    if (state.cancelShortcutInstalled) return;
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && state.listening) {
        event.preventDefault();
        stopRecording();
        updateStatus(__("Cancelled"));
      }
    });
    state.cancelShortcutInstalled = true;
  }

  function installButton() {
    if (!injectButton()) return;
    installCancelShortcut();
  }

  window.desk_navbar_extended.voice.init = (settings) => {
    state.settings = settings;
    const onReady = (callback) => {
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", callback, { once: true });
      } else {
        callback();
      }
    };
    onReady(() => {
      installButton();
    });
  };
})();
