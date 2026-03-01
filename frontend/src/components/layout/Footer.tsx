import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-border py-8 mt-8">
      <div className="container mx-auto px-4 flex flex-col items-center space-y-3 text-center">
        <p className="text-xs text-muted font-medium tracking-wide">
          &copy; {new Date().getFullYear()} <span className="font-bold text-primary">shophub</span>. All rights reserved.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-[11px] font-semibold uppercase tracking-widest">
          <Link to="/privacy" className="text-muted hover:text-primary transition-colors">
            Privacy Policy
          </Link>
          <span className="text-border">•</span>
          <Link to="/terms" className="text-muted hover:text-primary transition-colors">
            Terms of Service
          </Link>
          <span className="text-border">•</span>
          <Link to="/contact" className="text-muted hover:text-primary transition-colors">
            Contact Us
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
