import React, { useEffect, useState } from "react";
import socket from "./socket";
import "./App.css";

function App() {
  const [open, setOpen] = useState(false);

  // Chat state
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Onboarding state
  const [onboardingDone, setOnboardingDone] = useState(false);
  const [showConfirmSkip, setShowConfirmSkip] = useState(false);

  const [userInfo, setUserInfo] = useState({
    name: "",
    phone: "",
    email: "",
  });

  const [errors, setErrors] = useState({});

  // =========================
  // Socket listeners
  // =========================
  useEffect(() => {
    socket.on("status", (data) => {
      setMessages((prev) => [
        ...prev,
        { from: "system", text: data.message },
      ]);
    });

    socket.on("bot_reply", (data) => {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: data.text },
      ]);
    });

    return () => {
      socket.off("status");
      socket.off("bot_reply");
    };
  }, []);

  // =========================
  // Validation
  // =========================
  const validate = () => {
    const newErrors = {};

    if (!userInfo.name) {
      newErrors.name = "Please enter your name";
    }

    if (!userInfo.phone) {
      newErrors.phone = "Please enter your phone number";
    } else if (!/^\d{10}$/.test(userInfo.phone)) {
      newErrors.phone = "Phone number must be exactly 10 digits";
    }

    if (!userInfo.email) {
      newErrors.email = "Please enter your email address";
    } else if (!/^\S+@\S+\.\S+$/.test(userInfo.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    setErrors(newErrors);

    const hasMissing =
      !userInfo.name || !userInfo.phone || !userInfo.email;

    const hasInvalid = Object.keys(newErrors).length > 0;

    return {
      isValid: !hasInvalid,
      isComplete: !hasMissing,
    };
  };

  // =========================
  // Finish onboarding
  // =========================
  const finishOnboarding = () => {
    socket.emit("user_info", userInfo);

    setOnboardingDone(true);
    setShowConfirmSkip(false);

    setMessages([{ from: "bot", text: "👋 Hi! How can I help you?" }]);
  };

  // =========================
  // Continue logic
  // =========================
  const handleContinue = () => {
    const { isValid, isComplete } = validate();

    if (isValid && isComplete) {
      finishOnboarding();
    } else {
      setShowConfirmSkip(true);
    }
  };

  // =========================
  // Send chat message
  // =========================
  const sendMessage = () => {
    if (!input.trim()) return;

    const text = input.trim();
    setMessages((prev) => [...prev, { from: "user", text }]);
    socket.emit("message", { text });
    setInput("");
  };

  // =========================
  // UI
  // =========================
  return (
    <>
      {/* FLOATING CHAT LAUNCHER (HIDDEN WHEN OPEN) */}
      {!open && (
        <button
          className="chat-launcher"
          onClick={() => setOpen(true)}
        >
          💬
        </button>
      )}

      {/* CHAT WINDOW */}
      {open && (
        <div className="chat-widget">
          <div className="chat-header">
            Support Chatbot
            <button
              className="chat-close"
              onClick={() => setOpen(false)}
            >
              ✖
            </button>
          </div>

          {/* ONBOARDING */}
          {!onboardingDone ? (
            <div className="onboarding">
              <strong>Before we begin</strong>
              <p>You may share your details (optional)</p>

              <input
                placeholder="Name"
                value={userInfo.name}
                className={errors.name ? "input-error" : ""}
                onChange={(e) =>
                  setUserInfo({ ...userInfo, name: e.target.value })
                }
              />
              {errors.name && (
                <div className="error-text">{errors.name}</div>
              )}

              <input
                placeholder="Phone (10 digits)"
                value={userInfo.phone}
                className={errors.phone ? "input-error" : ""}
                onChange={(e) =>
                  setUserInfo({ ...userInfo, phone: e.target.value })
                }
              />
              {errors.phone && (
                <div className="error-text">{errors.phone}</div>
              )}

              <input
                placeholder="Email"
                value={userInfo.email}
                className={errors.email ? "input-error" : ""}
                onChange={(e) =>
                  setUserInfo({ ...userInfo, email: e.target.value })
                }
              />
              {errors.email && (
                <div className="error-text">{errors.email}</div>
              )}

              {/* PRIMARY BUTTONS */}
              {!showConfirmSkip && (
                <div className="onboarding-actions">
                  <button onClick={finishOnboarding}>Skip</button>
                  <button onClick={handleContinue}>Continue</button>
                </div>
              )}

              {/* CONFIRMATION */}
              {showConfirmSkip && (
                <div className="confirm-skip">
                  <p>
                    Some details are missing or invalid.
                    Do you want to continue without filling them?
                  </p>
                  <div className="onboarding-actions">
                    <button onClick={finishOnboarding}>
                      Continue anyway
                    </button>
                    <button onClick={() => setShowConfirmSkip(false)}>
                      Fix details
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* CHAT MESSAGES */}
              <div className="chat-messages">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={
                      m.from === "user"
                        ? "msg msg-user"
                        : m.from === "bot"
                        ? "msg msg-bot"
                        : "msg msg-system"
                    }
                  >
                    {m.text}
                  </div>
                ))}
              </div>

              {/* INPUT */}
              <div className="chat-input-row">
                <input
                  className="chat-input"
                  placeholder="Type your message…"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
                <button className="chat-send" onClick={sendMessage}>
                  Send
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}

export default App;
