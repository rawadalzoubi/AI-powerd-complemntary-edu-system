import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MathJaxPreview from "react-mathjax-preview";
import "./HomeworkHelperPage_FINAL.css";

const HomeworkHelperPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const navigate = useNavigate();
  const chatContainerRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);

  const API_BASE_URL = "http://127.0.0.1:8080";

  useEffect(() => {
    setMessages([
      {
        sender: "ai",
        text: "مرحباً! 👋 أنا مساعدك الذكي للواجبات المنزلية.\n\n🎯 يمكنك:\n• كتابة سؤالك مباشرة\n• سحب وإفلات صورة من كتابك\n• لصق صورة (Ctrl+V)\n• تسجيل سؤالك صوتياً 🎤\n\nكيف يمكنني مساعدتك اليوم؟",
      },
    ]);

    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handlePaste = (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const blob = items[i].getAsFile();
        if (blob) {
          submitImageSearch(blob);
          e.preventDefault();
        }
        break;
      }
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.target === e.currentTarget) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        submitImageSearch(file);
      } else {
        alert("يرجى إفلات صورة فقط (JPG, PNG)");
      }
    }
  };

  const handleQuickAction = (message) => {
    setInputValue(message);
    setTimeout(() => {
      document.getElementById("message-input")?.focus();
    }, 100);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const message = inputValue.trim();
    if (message) {
      submitMessage(message);
    }
  };

  const submitMessage = (message) => {
    setMessages((prev) => [...prev, { sender: "user", text: message }]);
    setInputValue("");
    setIsTyping(true);

    fetch(`${API_BASE_URL}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message }),
    })
      .then((response) =>
        response.ok ? response.json() : Promise.reject(response)
      )
      .then((data) => {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: data.answer || "عذراً، لم أتمكن من فهم الإجابة.",
          },
        ]);
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error:", error);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
          },
        ]);
      });
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) submitImageSearch(file);
  };

  const submitImageSearch = (imageFile) => {
    const imageUrl = URL.createObjectURL(imageFile);
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: "🖼️ جاري البحث بالصورة...",
        image: imageUrl,
      },
    ]);
    setIsTyping(true);

    const formData = new FormData();
    formData.append("file", imageFile);

    fetch(`${API_BASE_URL}/search-image`, {
      method: "POST",
      body: formData,
    })
      .then((response) =>
        response.ok ? response.json() : Promise.reject(response)
      )
      .then((data) => {
        setIsTyping(false);
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          const responseText = `📄 **المصدر:** ${result.source}\n📖 **الصفحة:** ${result.page_number}\n\n${result.context_text}`;
          setMessages((prev) => [
            ...prev,
            {
              sender: "ai",
              text: responseText,
              imageResults: data.results,
            },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              sender: "ai",
              text: "لم أجد محتوى مطابق لهذه الصورة.",
            },
          ]);
        }
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error:", error);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "خطأ في معالجة الصورة.",
          },
        ]);
      });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        submitAudioSearch(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Microphone error:", error);
      alert("لا يمكن الوصول للميكروفون");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const submitAudioSearch = (audioBlob) => {
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: "🎤 جاري معالجة الصوت...",
      },
    ]);
    setIsTyping(true);

    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");

    fetch(`${API_BASE_URL}/search-voice`, {
      method: "POST",
      body: formData,
    })
      .then((response) =>
        response.ok ? response.json() : Promise.reject(response)
      )
      .then((data) => {
        setIsTyping(false);
        const transcribedText = data.transcribed_text || "";
        const answer = data.answer || "";

        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: `🎤 **سؤالك:** "${transcribedText}"\n\n${answer}`,
            transcription: transcribedText,
          },
        ]);
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error:", error);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "خطأ في معالجة الصوت.",
          },
        ]);
      });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="homework-helper-container">
      {isDragging && (
        <div className="drag-overlay">
          <div className="drag-content">
            <i className="fas fa-cloud-upload-alt drag-icon"></i>
            <p className="drag-title">أفلت الصورة هنا</p>
            <p className="drag-subtitle">سأبحث عنها في المحتوى التعليمي</p>
          </div>
        </div>
      )}

      <header className="header-gradient">
        <div className="header-content">
          <div className="header-left">
            <div className="bot-avatar-header">
              <i className="fas fa-robot"></i>
            </div>
            <div className="header-text">
              <h1 className="header-title">AI Homework Helper</h1>
              <p className="header-subtitle">
                <span className="status-dot"></span>
                مساعدك الدراسي الذكي
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate("/student/dashboard")}
            className="back-button"
          >
            <i className="fas fa-arrow-right"></i>
            <span>العودة</span>
          </button>
        </div>
      </header>

      <main
        className="main-content"
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="chat-container">
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-icon">
                <i className="fas fa-graduation-cap"></i>
              </div>
              <div>
                <h2 className="chat-title">جلسة دراسية نشطة</h2>
                <p className="chat-status">
                  <span className="status-indicator"></span>
                  متصل الآن
                </p>
              </div>
            </div>
            <div className="chat-header-right">
              <i className="fas fa-image"></i>
              <span>اسحب صورة أو الصق (Ctrl+V)</span>
            </div>
          </div>

          <div ref={chatContainerRef} className="messages-area">
            {messages.map((msg, index) => {
              const isArabic = /[\u0600-\u06FF]/.test(msg.text);

              return (
                <div
                  key={index}
                  className={`message-wrapper ${
                    msg.sender === "user" ? "user-message" : "ai-message"
                  }`}
                >
                  {msg.sender === "ai" && (
                    <div className="avatar ai-avatar">
                      <i className="fas fa-robot"></i>
                    </div>
                  )}

                  <div
                    className={`message-bubble ${
                      msg.sender === "user" ? "user-bubble" : "ai-bubble"
                    }`}
                  >
                    {msg.image && (
                      <div className="message-image-container">
                        <img
                          src={msg.image}
                          alt="Uploaded"
                          className="message-image"
                          onClick={() => window.open(msg.image, "_blank")}
                        />
                      </div>
                    )}

                    <div
                      className="message-text"
                      dir={isArabic ? "rtl" : "ltr"}
                    >
                      {msg.sender === "ai" ? (
                        <MathJaxPreview
                          math={msg.text}
                          config={{
                            tex: {
                              inlineMath: [
                                ["$", "$"],
                                ["\\(", "\\)"],
                              ],
                              displayMath: [
                                ["$$", "$$"],
                                ["\\[", "\\]"],
                              ],
                            },
                          }}
                        />
                      ) : (
                        msg.text
                      )}
                    </div>

                    {msg.sender === "ai" && index === 0 && (
                      <div className="quick-actions">
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الرياضيات")
                          }
                          className="quick-btn math-btn"
                        >
                          <i className="fas fa-square-root-alt"></i>
                          <span>رياضيات</span>
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("هل يمكنك مساعدتي في العلوم؟")
                          }
                          className="quick-btn science-btn"
                        >
                          <i className="fas fa-flask"></i>
                          <span>علوم</span>
                        </button>
                        <button
                          onClick={() => handleQuickAction("أدرس التاريخ")}
                          className="quick-btn history-btn"
                        >
                          <i className="fas fa-landmark"></i>
                          <span>تاريخ</span>
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الأدب")
                          }
                          className="quick-btn literature-btn"
                        >
                          <i className="fas fa-book-open"></i>
                          <span>أدب</span>
                        </button>
                      </div>
                    )}
                  </div>

                  {msg.sender === "user" && (
                    <div className="avatar user-avatar">
                      <i className="fas fa-user-graduate"></i>
                    </div>
                  )}
                </div>
              );
            })}

            {isTyping && (
              <div className="message-wrapper ai-message">
                <div className="avatar ai-avatar">
                  <i className="fas fa-robot"></i>
                </div>
                <div className="message-bubble ai-bubble typing-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">المساعد الذكي يفكر...</span>
                </div>
              </div>
            )}
          </div>

          <div className="input-area">
            <form className="input-form" onSubmit={handleSubmit}>
              <div className="input-wrapper">
                <input
                  id="message-input"
                  type="text"
                  placeholder="اكتب سؤالك هنا... أو الصق صورة (Ctrl+V)"
                  className="message-input"
                  autoComplete="off"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  dir="auto"
                />
                <div className="input-actions">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="action-btn"
                    title="رفع صورة"
                  >
                    <i className="fas fa-image"></i>
                  </button>
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`action-btn ${isRecording ? "recording" : ""}`}
                    title={isRecording ? "إيقاف التسجيل" : "تسجيل صوتي"}
                  >
                    <i
                      className={`fas ${
                        isRecording ? "fa-stop-circle" : "fa-microphone"
                      }`}
                    ></i>
                  </button>
                  {isRecording && (
                    <span className="recording-time">
                      <span className="recording-dot"></span>
                      {formatTime(recordingTime)}
                    </span>
                  )}
                </div>
              </div>
              <button type="submit" className="send-button">
                <i className="fas fa-paper-plane"></i>
              </button>
            </form>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />

            <div className="input-footer">
              <p className="disclaimer">
                <i className="fas fa-info-circle"></i>
                المساعد الذكي قد ينتج معلومات غير دقيقة. تحقق دائماً من الإجابات
                المهمة.
              </p>
              <div className="input-hints">
                <span>
                  <i className="fas fa-keyboard"></i> اكتب
                </span>
                <span>
                  <i className="fas fa-paste"></i> الصق
                </span>
                <span>
                  <i className="fas fa-hand-pointer"></i> اسحب
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomeworkHelperPage;
