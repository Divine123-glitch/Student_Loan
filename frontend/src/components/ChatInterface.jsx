import React, { useState, useRef, useEffect } from 'react';
import { Send, Moon, Sun, LogOut, Menu, X, Plus, Trash2, ExternalLink } from 'lucide-react';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const API_URL = 'http://localhost:8000/api';
  const token = localStorage.getItem('token');

  useEffect(() => {
    // Check if user is authenticated
    if (!token) {
      window.location.href = '/login';
      return;
    }
    
    // Load saved session from localStorage
    const savedSessionId = localStorage.getItem('nelfund_session_id');
    if (savedSessionId) {
      setCurrentSessionId(savedSessionId);
      loadChatHistory(savedSessionId);
    }
    
    // Load sessions from server
    loadSessions();
    
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  // Load chat history when session changes
  useEffect(() => {
    if (currentSessionId && messages.length === 0) {
      loadChatHistory(currentSessionId);
    }
  }, [currentSessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const response = await axios.get(`${API_URL}/chat/sessions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessions(response.data.sessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadChatHistory = async (sessionId) => {
    if (!sessionId) return;
    
    setLoadingHistory(true);
    try {
      const response = await axios.get(`${API_URL}/chat/history/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Convert stored chats to message format
      const formattedMessages = [];
      response.data.chats.forEach(chat => {
        formattedMessages.push({
          role: 'user',
          content: chat.user_message
        });
        formattedMessages.push({
          role: 'assistant',
          content: chat.bot_response,
          sources: chat.sources || []
        });
      });
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading chat history:', error);
      // If history can't be loaded, start fresh
      setMessages([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    const messageText = input; // Save before clearing
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/chat`,
        {
          message: messageText,
          session_id: currentSessionId
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      const newSessionId = response.data.session_id;
      setCurrentSessionId(newSessionId);
      localStorage.setItem('nelfund_session_id', newSessionId);
      
      // Reload sessions
      loadSessions();
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.';
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMessage,
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    localStorage.removeItem('nelfund_session_id');
    inputRef.current?.focus();
  };

  const selectSession = (sessionId) => {
    setCurrentSessionId(sessionId);
    localStorage.setItem('nelfund_session_id', sessionId);
    // History will load via useEffect
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();

    try {
      await axios.delete(`${API_URL}/chat/session/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (sessionId === currentSessionId) {
        startNewChat();
      }
      loadSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('nelfund_session_id');
    window.location.href = '/';
  };

  const bgColor = darkMode ? 'bg-[#1e1e1e]' : 'bg-white';
  const textColor = darkMode ? 'text-gray-100' : 'text-gray-900';
  const secondaryBg = darkMode ? 'bg-[#2d2d2d]' : 'bg-gray-50';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';
  const hoverBg = darkMode ? 'hover:bg-[#3d3d3d]' : 'hover:bg-gray-100';

  return (
    <div className={`flex h-screen ${bgColor} ${textColor} transition-colors duration-200`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} ${secondaryBg} border-r ${borderColor} transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="font-semibold">NELFUND Navigator</h2>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden">
            <X className="w-5 h-5" />
          </button>
        </div>

        <button
          onClick={startNewChat}
          className={`m-3 p-3 rounded-lg ${hoverBg} border ${borderColor} transition-colors flex items-center justify-center space-x-2`}
        >
          <Plus className="w-5 h-5" />
          <span>New Chat</span>
        </button>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {sessions.length > 0 ? (
            sessions.map((session) => (
              <div
                key={session.session_id}
                className={`p-3 rounded-lg ${hoverBg} cursor-pointer transition-colors group relative ${
                  session.session_id === currentSessionId ? 'bg-indigo-600 text-white' : ''
                }`}
                onClick={() => selectSession(session.session_id)}
              >
                <div className="text-sm truncate">{session.first_message}</div>
                <div className="text-xs opacity-60 mt-1">{session.message_count} messages</div>
                <button
                  onClick={(e) => deleteSession(session.session_id, e)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          ) : (
            <p className={`text-sm p-3 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
              No saved sessions yet. Start chatting!
            </p>
          )}
        </div>

        <div className="p-3 border-t border-gray-700 space-y-2">
          <a
            href="https://nelf.gov.ng"
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center space-x-2 p-3 rounded-lg ${hoverBg} transition-colors`}
          >
            <ExternalLink className="w-4 h-4" />
            <span className="text-sm">Official NELFUND</span>
          </a>
          {token && (
            <button
              onClick={handleLogout}
              className={`w-full flex items-center space-x-2 p-3 rounded-lg ${hoverBg} transition-colors`}
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Logout</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`${secondaryBg} border-b ${borderColor} p-4 flex justify-between items-center`}>
          <div className="flex items-center space-x-3">
            {!sidebarOpen && (
              <button onClick={() => setSidebarOpen(true)}>
                <Menu className="w-5 h-5" />
              </button>
            )}
            <h1 className="text-lg font-semibold">NELFUND AI Assistant</h1>
          </div>
          
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`p-2 rounded-lg ${hoverBg} transition-colors`}
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {loadingHistory ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
                <p>Loading chat history...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md px-4">
                <div className="text-4xl mb-4">👋</div>
                <h2 className="text-2xl font-semibold mb-2">Welcome to NELFUND Navigator</h2>
                <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-6`}>
                  Ask me anything about NELFUND student loans, eligibility, application process, or documentation requirements.
                </p>
                <div className="grid grid-cols-1 gap-3">
                  {[
                    "Am I eligible for NELFUND?",
                    "How do I apply for a student loan?",
                    "What documents do I need?",
                    "When do I start repaying?"
                  ].map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInput(suggestion)}
                      className={`p-3 rounded-lg ${secondaryBg} ${hoverBg} border ${borderColor} text-left transition-colors`}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto py-8 px-4">
              {messages.map((message, index) => (
                <div key={index} className={`mb-6 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-2xl rounded-tr-sm'
                      : `${secondaryBg} rounded-2xl rounded-tl-sm border ${borderColor}`
                  } p-4 shadow-sm`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-600 text-xs opacity-70">
                        <div className="font-semibold mb-1">Sources:</div>
                        {message.sources.map((source, idx) => (
                          <div key={idx}>• {source}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="mb-6 text-left">
                  <div className={`inline-block ${secondaryBg} rounded-2xl rounded-tl-sm border ${borderColor} p-4`}>
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className={`${secondaryBg} border-t ${borderColor} p-4`}>
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
            <div className={`flex items-center space-x-2 ${bgColor} border ${borderColor} rounded-2xl p-2 shadow-sm`}>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about NELFUND..."
                className={`flex-1 ${bgColor} ${textColor} px-4 py-2 focus:outline-none`}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
          <p className={`text-center text-xs mt-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            AI-powered answers backed by official NELFUND documents
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;