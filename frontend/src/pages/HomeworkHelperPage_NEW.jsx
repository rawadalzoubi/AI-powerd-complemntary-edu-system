import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MathJaxPreview from "react-mathjax-preview";
import "./HomeworkHelperPage.css";

const HomeworkHelperPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedAudio, setSelectedAudio] = useState(null);
  const navigate = useNavigate();
  const chatContainerRef = useRef(null);
  const fileInputRef = useRef(null);
  const audioInputRef = useRef(null);

  // تحديث API URL للنظام الجديد
  const API_BASE_URL = "http://127.0.0.1:8080";

  useEffect(() => {
    setMessages([
      {
        sender: "ai",
        text: "مرحباً! 👋 أنا مساعدك الذكي للواجبات المنزلية. يمكنني مساعدتك في الرياضيات، العلوم، التاريخ، الأدب، وأكثر. يمكنك:\n\n📝 كتابة سؤالك\n🖼️ رفع صورة من كتابك\n🎤 تسجيل سؤالك صوتياً\n\nما الموضوع الذي تعمل عليه اليوم؟",
      },
    ]);
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleQuickAction = (message) => {
    setInputValue(message);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const message = inputValue.trim();
    if (message) {
      submitMessage(message);
    }
  };

  // إرسال سؤال نصي
  const submitMessage = (message) => {
    setMessages((prev) => [...prev, { sender: "user", text: message }]);
    setInputValue("");
    setIsTyping(true);

    fetch(`${API_BASE_URL}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message }),
    })
      .then((response) => {
        if (!response.ok) {
          return response
            .json()
            .catch(() => {
              throw new Error(`HTTP error! status: ${response.status}`);
            })
            .then((errorData) => {
              throw new Error(
                errorData.detail || `HTTP error! status: ${response.status}`
              );
            });
        }
        return response.json();
      })
      .then((data) => {
        setIsTyping(false);
        const aiResponse =
          data.answer || "عذراً، لم أتمكن من فهم الإجابة من النظام.";
        setMessages((prev) => [...prev, { sender: "ai", text: aiResponse }]);
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error fetching AI response:", error);
        const errorMessage =
          error.message ||
          "عذراً، حدث خطأ أثناء محاولة الوصول إلى المساعد الذكي. يرجى المحاولة مرة أخرى.";
        setMessages((prev) => [...prev, { sender: "ai", text: errorMessage }]);
      });
  };

  // معالجة رفع الصور
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      submitImageSearch(file);
    }
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
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setIsTyping(false);
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          const responseText = `📄 تم العثور عليها في: ${result.source}\n📖 الصفحة: ${result.page_number}\n\n${result.context_text}`;
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
              text: "عذراً، لم أتمكن من العثور على محتوى مطابق لهذه الصورة.",
            },
          ]);
        }
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error with image search:", error);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "عذراً، حدث خطأ أثناء معالجة الصورة. يرجى المحاولة مرة أخرى.",
          },
        ]);
      });
  };

  // معالجة رفع الصوت
  const handleAudioUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedAudio(file);
      submitAudioSearch(file);
    }
  };

  const submitAudioSearch = (audioFile) => {
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: "🎤 جاري معالجة الصوت...",
      },
    ]);
    setIsTyping(true);

    const formData = new FormData();
    formData.append("file", audioFile);

    fetch(`${API_BASE_URL}/search-voice`, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setIsTyping(false);
        const transcribedText = data.transcribed_text || "";
        const answer = data.answer || "";

        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: `🎤 سؤالك: "${transcribedText}"\n\n${answer}`,
            transcription: transcribedText,
          },
        ]);
      })
      .catch((error) => {
        setIsTyping(false);
        console.error("Error with audio search:", error);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: "عذراً، حدث خطأ أثناء معالجة الصوت. يرجى المحاولة مرة أخرى.",
          },
        ]);
      });
  };

  const handleImageButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleAudioButtonClick = () => {
    audioInputRef.current?.click();
  };

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col">
      <header className="bg-indigo-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bot-avatar bg-white text-indigo-600 rounded-full w-12 h-12 flex items-center justify-center text-2xl">
              <i className="fas fa-robot"></i>
            </div>
            <div>
              <h1 className="text-2xl font-bold">AI Homework Helper</h1>
              <p className="text-indigo-200 text-sm">
                مساعدك الدراسي على مدار الساعة
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate("/student/dashboard")}
              className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center"
            >
              <i className="fas fa-arrow-left mr-2"></i> العودة للوحة التحكم
            </button>
            <button className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center">
              <i className="fas fa-book mr-2"></i> المواد
            </button>
            <button className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center">
              <i className="fas fa-history mr-2"></i> السجل
            </button>
          </div>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-6 flex flex-col">
        <div className="bg-white rounded-xl shadow-lg flex-grow flex flex-col overflow-hidden">
          <div className="bg-indigo-50 px-6 py-4 border-b border-indigo-100 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-600 text-white rounded-full w-10 h-10 flex items-center justify-center">
                <i className="fas fa-graduation-cap"></i>
              </div>
              <div>
                <h2 className="font-semibold text-indigo-900">جلسة دراسية</h2>
                <p className="text-xs text-indigo-500">نشط الآن</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button className="text-indigo-600 hover:text-indigo-800 p-2 rounded-full hover:bg-indigo-100">
                <i className="fas fa-ellipsis-v"></i>
              </button>
            </div>
          </div>

          <div
            ref={chatContainerRef}
            id="chat-container"
            className="flex-grow p-6 overflow-y-auto space-y-4"
          >
            {messages.map((msg, index) => {
              const isArabic = /[\u0600-\u06FF]/.test(msg.text);
              const style = {
                whiteSpace: "pre-wrap",
                direction: isArabic ? "rtl" : "ltr",
                textAlign: isArabic ? "right" : "left",
              };

              return (
                <div
                  key={index}
                  className={`message-enter flex items-start space-x-3 py-2 ${
                    msg.sender === "user" ? "justify-end" : ""
                  }`}
                >
                  {msg.sender === "ai" && (
                    <div className="bg-indigo-100 text-indigo-800 rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 mr-3">
                      <i className="fas fa-robot"></i>
                    </div>
                  )}
                  <div
                    className={`${
                      msg.sender === "user"
                        ? "bg-indigo-600 text-white"
                        : "bg-indigo-50 text-indigo-900"
                    } rounded-lg p-3 px-4 max-w-3xl shadow`}
                  >
                    {msg.image && (
                      <img
                        src={msg.image}
                        alt="Uploaded"
                        className="max-w-xs rounded-lg mb-2"
                      />
                    )}
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
                        style={style}
                      />
                    ) : (
                      <div style={style}>{msg.text}</div>
                    )}
                    {msg.sender === "ai" && index === 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الرياضيات")
                          }
                          className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center"
                        >
                          <i className="fas fa-square-root-alt mr-2"></i>{" "}
                          رياضيات
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("هل يمكنك مساعدتي في العلوم؟")
                          }
                          className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center"
                        >
                          <i className="fas fa-flask mr-2"></i> علوم
                        </button>
                        <button
                          onClick={() => handleQuickAction("أدرس التاريخ")}
                          className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center"
                        >
                          <i className="fas fa-landmark mr-2"></i> تاريخ
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الأدب الإنجليزي")
                          }
                          className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center"
                        >
                          <i className="fas fa-book-open mr-2"></i> أدب
                        </button>
                      </div>
                    )}
                  </div>
                  {msg.sender === "user" && (
                    <div className="bg-indigo-600 text-white rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 order-last ml-3">
                      <i className="fas fa-user-graduate"></i>
                    </div>
                  )}
                </div>
              );
            })}

            {isTyping && (
              <div id="typing-indicator">
                <div className="flex items-center space-x-2 text-indigo-600">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span>المساعد الذكي يكتب...</span>
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-indigo-100 p-4 bg-white">
            <form
              id="chat-form"
              className="flex items-center space-x-3"
              onSubmit={handleSubmit}
            >
              <div className="flex-grow relative">
                <input
                  id="message-input"
                  type="text"
                  placeholder="اكتب سؤالك هنا..."
                  className="w-full px-4 py-3 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  autoComplete="off"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex space-x-2">
                  <button
                    type="button"
                    onClick={handleImageButtonClick}
                    className="text-indigo-400 hover:text-indigo-600 p-2"
                    title="رفع صورة"
                  >
                    <i className="fas fa-image"></i>
                  </button>
                  <button
                    type="button"
                    onClick={handleAudioButtonClick}
                    className="text-indigo-400 hover:text-indigo-600 p-2"
                    title="تسجيل صوتي"
                  >
                    <i className="fas fa-microphone"></i>
                  </button>
                </div>
              </div>
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg p-3 flex items-center justify-center transition-colors"
                aria-label="إرسال الرسالة"
              >
                <i className="fas fa-paper-plane"></i>
              </button>
            </form>

            {/* Hidden file inputs */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />
            <input
              ref={audioInputRef}
              type="file"
              accept="audio/*"
              onChange={handleAudioUpload}
              style={{ display: "none" }}
            />

            <p className="text-xs text-gray-500 mt-2 text-center">
              المساعد الذكي قد ينتج معلومات غير دقيقة. تحقق دائماً من الإجابات
              المهمة.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomeworkHelperPage;
