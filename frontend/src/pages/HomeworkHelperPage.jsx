import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MathJaxPreview from "react-mathjax-preview";
import "./HomeworkHelperPage.css";

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
        text: "مرحباً! 👋 أنا مساعدك الذكي للواجبات المنزلية.\n\n🎯 يمكنك:\n• كتابة سؤالك مباشرة\n• سحب وإفلات صورة من كتابك\n• لصق صورة من الحافظة (Ctrl+V)\n• تسجيل سؤالك صوتياً\n\nما الموضوع الذي تعمل عليه اليوم؟",
      },
    ]);

    // إضافة مستمع للصق الصور
    document.addEventListener("paste", handlePaste);

    return () => {
      document.removeEventListener("paste", handlePaste);
    };
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // معالجة لصق الصور
  const handlePaste = (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const blob = items[i].getAsFile();
        if (blob) {
          submitImageSearch(blob);
        }
        e.preventDefault();
        break;
      }
    }
  };

  // معالجة السحب والإفلات
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
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
        alert("يرجى إفلات صورة فقط (JPG, PNG, etc.)");
      }
    }
  };

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
          "عذراً، حدث خطأ أثناء محاولة الوصول إلى المساعد الذكي.";
        setMessages((prev) => [...prev, { sender: "ai", text: errorMessage }]);
      });
  };

  // معالجة رفع الصور
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
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
          const responseText = `📄 **تم العثور عليها في:** ${result.source}\n📖 **الصفحة:** ${result.page_number}\n\n${result.context_text}`;
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

  // التسجيل الصوتي المباشر
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

      // عداد الوقت
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("لا يمكن الوصول إلى الميكروفون. يرجى التحقق من الأذونات.");
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
            text: `🎤 **سؤالك:** "${transcribedText}"\n\n${answer}`,
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 min-h-screen flex flex-col">
      {/* Drag & Drop Overlay */}
      {isDragging && (
        <div className="fixed inset-0 bg-indigo-600 bg-opacity-90 z-50 flex items-center justify-center">
          <div className="text-center text-white">
            <i className="fas fa-cloud-upload-alt text-8xl mb-4 animate-bounce"></i>
            <p className="text-3xl font-bold">أفلت الصورة هنا</p>
            <p className="text-xl mt-2">سأبحث عنها في المحتوى التعليمي</p>
          </div>
        </div>
      )}

      <header className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bot-avatar bg-white text-indigo-600 rounded-full w-14 h-14 flex items-center justify-center text-3xl shadow-lg animate-pulse">
              <i className="fas fa-robot"></i>
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI Homework Helper</h1>
              <p className="text-indigo-100 text-sm flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                مساعدك الدراسي الذكي
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate("/student/dashboard")}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 backdrop-blur-sm px-4 py-2 rounded-lg flex items-center transition-all duration-300 hover:scale-105"
            >
              <i className="fas fa-arrow-left mr-2"></i> العودة
            </button>
          </div>
        </div>
      </header>

      <main
        className="flex-grow container mx-auto px-4 py-6 flex flex-col"
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="bg-white rounded-2xl shadow-2xl flex-grow flex flex-col overflow-hidden border border-indigo-100">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 px-6 py-4 border-b border-indigo-100 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
                <i className="fas fa-graduation-cap"></i>
              </div>
              <div>
                <h2 className="font-bold text-indigo-900 text-lg">
                  جلسة دراسية نشطة
                </h2>
                <p className="text-xs text-indigo-500 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
                  متصل الآن
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-indigo-600">
              <i className="fas fa-image"></i>
              <span>اسحب صورة أو الصق (Ctrl+V)</span>
            </div>
          </div>

          <div
            ref={chatContainerRef}
            className="flex-grow p-6 overflow-y-auto space-y-4 bg-gradient-to-b from-white to-indigo-50"
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
                    <div className="bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-800 rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 mr-3 shadow-md">
                      <i className="fas fa-robot text-xl"></i>
                    </div>
                  )}
                  <div
                    className={`${
                      msg.sender === "user"
                        ? "bg-gradient-to-br from-indigo-600 to-purple-600 text-white"
                        : "bg-white border-2 border-indigo-100 text-indigo-900"
                    } rounded-2xl p-4 px-5 max-w-3xl shadow-lg hover:shadow-xl transition-shadow duration-300`}
                  >
                    {msg.image && (
                      <div className="relative group mb-3">
                        <img
                          src={msg.image}
                          alt="Uploaded"
                          className="max-w-xs rounded-xl shadow-md cursor-pointer hover:scale-105 transition-transform duration-300"
                          onClick={() => window.open(msg.image, "_blank")}
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-xl transition-all duration-300 flex items-center justify-center">
                          <i className="fas fa-search-plus text-white text-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></i>
                        </div>
                      </div>
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
                      <div className="mt-4 flex flex-wrap gap-2">
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الرياضيات")
                          }
                          className="bg-gradient-to-r from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300 text-blue-700 px-4 py-2 rounded-xl text-sm flex items-center shadow-md hover:shadow-lg transition-all duration-300"
                        >
                          <i className="fas fa-square-root-alt mr-2"></i>{" "}
                          رياضيات
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("هل يمكنك مساعدتي في العلوم؟")
                          }
                          className="bg-gradient-to-r from-green-100 to-green-200 hover:from-green-200 hover:to-green-300 text-green-700 px-4 py-2 rounded-xl text-sm flex items-center shadow-md hover:shadow-lg transition-all duration-300"
                        >
                          <i className="fas fa-flask mr-2"></i> علوم
                        </button>
                        <button
                          onClick={() => handleQuickAction("أدرس التاريخ")}
                          className="bg-gradient-to-r from-yellow-100 to-yellow-200 hover:from-yellow-200 hover:to-yellow-300 text-yellow-700 px-4 py-2 rounded-xl text-sm flex items-center shadow-md hover:shadow-lg transition-all duration-300"
                        >
                          <i className="fas fa-landmark mr-2"></i> تاريخ
                        </button>
                        <button
                          onClick={() =>
                            handleQuickAction("أحتاج مساعدة في الأدب")
                          }
                          className="bg-gradient-to-r from-purple-100 to-purple-200 hover:from-purple-200 hover:to-purple-300 text-purple-700 px-4 py-2 rounded-xl text-sm flex items-center shadow-md hover:shadow-lg transition-all duration-300"
                        >
                          <i className="fas fa-book-open mr-2"></i> أدب
                        </button>
                      </div>
                    )}
                  </div>
                  {msg.sender === "user" && (
                    <div className="bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 order-last ml-3 shadow-md">
                      <i className="fas fa-user-graduate text-xl"></i>
                    </div>
                  )}
                </div>
              );
            })}

            {isTyping && (
              <div className="flex items-center space-x-3 animate-fade-in">
                <div className="bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-800 rounded-full w-12 h-12 flex items-center justify-center shadow-md">
                  <i className="fas fa-robot text-xl"></i>
                </div>
                <div className="bg-white border-2 border-indigo-100 rounded-2xl p-4 shadow-lg">
                  <div className="flex items-center space-x-2 text-indigo-600">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span className="text-sm">المساعد الذكي يفكر...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="border-t-2 border-indigo-100 p-4 bg-gradient-to-r from-white to-indigo-50">
            <form
              className="flex items-center space-x-3"
              onSubmit={handleSubmit}
            >
              <div className="flex-grow relative">
                <input
                  type="text"
                  placeholder="اكتب سؤالك هنا... أو الصق صورة (Ctrl+V)"
                  className="w-full px-5 py-4 pr-32 border-2 border-indigo-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-md hover:shadow-lg transition-all duration-300"
                  autoComplete="off"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                />
                <div className="absolute left-3 top-1/2 transform -translate-y-1/2 flex space-x-2">
                  <button
                    type="button"
                    onClick={handleImageButtonClick}
                    className="text-indigo-500 hover:text-indigo-700 p-2 rounded-lg hover:bg-indigo-50 transition-all duration-300"
                    title="رفع صورة"
                  >
                    <i className="fas fa-image text-xl"></i>
                  </button>
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`${
                      isRecording
                        ? "text-red-500 hover:text-red-700 animate-pulse"
                        : "text-indigo-500 hover:text-indigo-700"
                    } p-2 rounded-lg hover:bg-indigo-50 transition-all duration-300`}
                    title={isRecording ? "إيقاف التسجيل" : "تسجيل صوتي"}
                  >
                    <i
                      className={`fas ${
                        isRecording ? "fa-stop-circle" : "fa-microphone"
                      } text-xl`}
                    ></i>
                  </button>
                  {isRecording && (
                    <span className="text-red-500 text-sm font-mono flex items-center">
                      <span className="w-2 h-2 bg-red-500 rounded-full mr-1 animate-pulse"></span>
                      {formatTime(recordingTime)}
                    </span>
                  )}
                </div>
              </div>
              <button
                type="submit"
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-2xl p-4 flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105"
                aria-label="إرسال الرسالة"
              >
                <i className="fas fa-paper-plane text-xl"></i>
              </button>
            </form>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />

            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <p className="flex items-center">
                <i className="fas fa-info-circle mr-1"></i>
                المساعد الذكي قد ينتج معلومات غير دقيقة. تحقق دائماً من الإجابات
                المهمة.
              </p>
              <div className="flex items-center space-x-3 text-indigo-600">
                <span className="flex items-center">
                  <i className="fas fa-keyboard mr-1"></i>
                  اكتب
                </span>
                <span className="flex items-center">
                  <i className="fas fa-paste mr-1"></i>
                  الصق
                </span>
                <span className="flex items-center">
                  <i className="fas fa-hand-pointer mr-1"></i>
                  اسحب
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
