import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MathJaxPreview from 'react-mathjax-preview';
import './HomeworkHelperPage.css';

const HomeworkHelperPage = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const navigate = useNavigate();
    const chatContainerRef = useRef(null);

    const API_URL = 'http://127.0.0.1:8080/ask_question';

    useEffect(() => {
        setMessages([
            {
                sender: 'ai',
                text: "Hello! 👋 I'm your AI Homework Helper. I can help you with math, science, history, literature, and more. What subject are you working on today?"
            }
        ]);
    }, []);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
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

    const submitMessage = (message) => {
        setMessages(prev => [...prev, { sender: 'user', text: message }]);
        setInputValue('');
        setIsTyping(true);

        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: message, top_k: 5 }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().catch(() => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }).then(errorData => {
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            setIsTyping(false);
            const aiResponse = data.answer || "Sorry, I couldn't understand the response from the AI.";
            setMessages(prev => [...prev, { sender: 'ai', text: aiResponse }]);
        })
        .catch(error => {
            setIsTyping(false);
            console.error('Error fetching AI response:', error);
            const errorMessage = error.message || 'Sorry, I encountered an error trying to reach the AI helper. Please try again later.';
            setMessages(prev => [...prev, { sender: 'ai', text: errorMessage }]);
        });
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
                            <p className="text-indigo-200 text-sm">Your 24/7 study assistant</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <button onClick={() => navigate('/student/dashboard')} className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center">
                            <i className="fas fa-arrow-left mr-2"></i> Back to Dashboard
                        </button>
                        <button className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center">
                            <i className="fas fa-book mr-2"></i> Subjects
                        </button>
                        <button className="bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg flex items-center">
                            <i className="fas fa-history mr-2"></i> History
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
                                <h2 className="font-semibold text-indigo-900">Study Session</h2>
                                <p className="text-xs text-indigo-500">Active now</p>
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <button className="text-indigo-600 hover:text-indigo-800 p-2 rounded-full hover:bg-indigo-100">
                                <i className="fas fa-ellipsis-v"></i>
                            </button>
                        </div>
                    </div>

                    <div ref={chatContainerRef} id="chat-container" className="flex-grow p-6 overflow-y-auto space-y-4">
                        {messages.map((msg, index) => {
                            // Detect if the message contains Arabic characters to apply RTL styling.
                            const isArabic = /[\u0600-\u06FF]/.test(msg.text);
                            const style = {
                                whiteSpace: 'pre-wrap',
                                direction: isArabic ? 'rtl' : 'ltr',
                                textAlign: isArabic ? 'right' : 'left',
                            };

                            return (
                                <div key={index} className={`message-enter flex items-start space-x-3 py-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                                    {msg.sender === 'ai' && (
                                        <div className="bg-indigo-100 text-indigo-800 rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 mr-3">
                                            <i className="fas fa-robot"></i>
                                        </div>
                                    )}
                                    <div className={`${msg.sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-indigo-50 text-indigo-900'} rounded-lg p-3 px-4 max-w-3xl shadow`}>
                                        {msg.sender === 'ai' ? (
                                            <MathJaxPreview 
                                                math={msg.text} 
                                                config={{
                                                    tex: { 
                                                        inlineMath: [['$', '$'], ['\(', '\)']],
                                                        displayMath: [['$$', '$$'], ['\[', '\]']],
                                                    }
                                                }}
                                                style={style}
                                            />
                                        ) : (
                                            <div style={style}>{msg.text}</div>
                                        )}
                                        {msg.sender === 'ai' && index === 0 && (
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                <button onClick={() => handleQuickAction('I need help with math homework')} className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center">
                                                    <i className="fas fa-square-root-alt mr-2"></i> Math
                                                </button>
                                                <button onClick={() => handleQuickAction('Can you help me with science?')} className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center">
                                                    <i className="fas fa-flask mr-2"></i> Science
                                                </button>
                                                <button onClick={() => handleQuickAction("I'm studying history")} className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center">
                                                    <i className="fas fa-landmark mr-2"></i> History
                                                </button>
                                                <button onClick={() => handleQuickAction('I need help with English literature')} className="quick-action-btn bg-indigo-100 hover:bg-indigo-200 text-indigo-700 px-3 py-2 rounded-lg text-sm flex items-center">
                                                    <i className="fas fa-book-open mr-2"></i> Literature
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                    {msg.sender === 'user' && (
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
                                    <span>AI Homework Helper is typing...</span>
                                </div>
                            </div>
                        )}
                    </div>
                    
                    <div className="border-t border-indigo-100 p-4 bg-white">
                        <form id="chat-form" className="flex items-center space-x-3" onSubmit={handleSubmit}>
                            <div className="flex-grow relative">
                                <input
                                    id="message-input"
                                    type="text"
                                    placeholder="Ask your homework question..."
                                    className="w-full px-4 py-3 border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    autoComplete="off"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                />
                                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex space-x-2">
                                    <button type="button" className="text-indigo-400 hover:text-indigo-600 p-2">
                                        <i className="fas fa-paperclip"></i>
                                    </button>
                                    <button type="button" className="text-indigo-400 hover:text-indigo-600 p-2">
                                        <i className="fas fa-microphone"></i>
                                    </button>
                                </div>
                            </div>
                            <button
                                type="submit"
                                className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg p-3 flex items-center justify-center transition-colors"
                                aria-label="Send message"
                            >
                                <i className="fas fa-paper-plane"></i>
                            </button>
                        </form>
                        <p className="text-xs text-gray-500 mt-2">AI Homework Helper may produce inaccurate information. Always verify critical answers.</p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default HomeworkHelperPage; 