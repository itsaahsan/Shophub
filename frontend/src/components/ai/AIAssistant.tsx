import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Bot, User, ShoppingBag, Sparkles } from 'lucide-react';
import { aiApi } from '../../services/api';
import { Product } from '../../types';
import { Link } from 'react-router-dom';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  products?: Product[];
}

const AIAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m your Shophub AI assistant. How can I help you find the perfect product today?' }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMsg = message.trim();
    setMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await aiApi.chat(userMsg);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: res.data.reply, 
        products: res.data.products 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again later.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[60]">
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 bg-primary text-white rounded-full shadow-2xl flex items-center justify-center hover:bg-accent hover:scale-110 transition-all duration-300 group relative"
        >
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-accent rounded-full border-2 border-white animate-pulse"></div>
          <Sparkles className="w-6 h-6 group-hover:rotate-12 transition-transform" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white w-[380px] h-[550px] rounded-[2rem] shadow-2xl border border-border flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-300">
          {/* Header */}
          <div className="bg-primary p-6 text-white flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                <Bot className="w-6 h-6 text-accent" />
              </div>
              <div>
                <h3 className="font-bold text-sm">Shophub AI</h3>
                <div className="flex items-center text-[10px] text-accent font-bold uppercase tracking-widest">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full mr-1.5 animate-pulse"></div>
                  Online
                </div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start max-w-[85%] space-x-3 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-accent/10 text-accent' : 'bg-primary text-white'}`}>
                    {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className="space-y-3">
                    <div className={`p-4 rounded-2xl text-sm shadow-sm ${
                      msg.role === 'user' 
                        ? 'bg-accent text-white rounded-tr-none' 
                        : 'bg-white border border-border text-primary rounded-tl-none'
                    }`}>
                      {msg.content}
                    </div>

                    {/* Product Recommendations */}
                    {msg.products && msg.products.length > 0 && (
                      <div className="grid grid-cols-1 gap-2 mt-2">
                        {msg.products.map(product => (
                          <Link 
                            key={product.id} 
                            to={`/product/${product.id}`}
                            className="flex items-center space-x-3 p-2 bg-white border border-border rounded-xl hover:border-accent transition-colors group"
                            onClick={() => setIsOpen(false)}
                          >
                            <div className="w-12 h-12 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                              <img src={product.images[0]} alt={product.name} className="w-full h-full object-cover" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-bold text-primary truncate group-hover:text-accent">{product.name}</p>
                              <p className="text-[10px] font-bold text-muted">${product.price}</p>
                            </div>
                            <ShoppingBag className="w-4 h-4 text-muted group-hover:text-accent" />
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-border p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-6 bg-white border-t border-border">
            <form onSubmit={handleSend} className="relative">
              <input
                type="text"
                placeholder="Ask me anything..."
                className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-border rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-accent/20 outline-none transition-all"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!message.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary text-white rounded-lg hover:bg-accent disabled:opacity-50 disabled:hover:bg-primary transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <p className="text-[9px] text-center text-muted mt-3 font-medium">
              AI can make mistakes. Check important info.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
