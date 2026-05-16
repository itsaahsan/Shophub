import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import AIAssistant from '../ai/AIAssistant';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <AIAssistant />
      <Footer />
    </div>
  );
};

export default Layout;
