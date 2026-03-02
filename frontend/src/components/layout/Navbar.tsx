import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User, Heart, LogOut, LayoutDashboard, Menu, X } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useCartStore } from '../../stores/cartStore';

const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const cartItems = useCartStore((state) => state.items);
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <nav className="bg-white border-b border-border sticky top-0 z-50">
      <div className="container mx-auto px-4 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center flex-shrink-0 group">
            <span className="text-2xl font-extrabold tracking-tighter text-primary group-hover:text-accent transition-colors duration-300">Shophub</span>
          </Link>

          {/* Search Bar - Center */}
          <div className="hidden md:flex flex-1 max-w-xl mx-8">
            <form onSubmit={handleSearch} className="w-full relative group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted group-focus-within:text-accent w-4 h-4 transition-colors" />
              <input
                type="text"
                placeholder="Search for anything..."
                className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-full text-sm focus:bg-white focus:ring-2 focus:ring-accent/20 focus:border-accent transition-all outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-2 sm:space-x-5">
            <Link to="/wishlist" className="p-2 text-muted hover:text-primary transition-colors">
              <Heart className="w-5 h-5" />
            </Link>
            
            <Link to="/cart" className="p-2 text-muted hover:text-primary relative transition-colors">
              <ShoppingCart className="w-5 h-5" />
              {cartItems.length > 0 && (
                <span className="absolute top-0 right-0 bg-accent text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                  {cartItems.reduce((acc, item) => acc + item.quantity, 0)}
                </span>
              )}
            </Link>

            {user ? (
              <div className="relative group flex items-center">
                <button className="flex items-center space-x-2 p-1 pl-2 hover:bg-card rounded-lg transition-colors border border-transparent hover:border-border">
                  <span className="hidden sm:block text-xs font-semibold text-primary">{user.name}</span>
                  <div className="w-8 h-8 bg-accent/10 rounded-full flex items-center justify-center text-accent">
                    <User className="w-4 h-4" />
                  </div>
                </button>
                <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-border rounded-xl shadow-hover py-2 hidden group-hover:block animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="px-4 py-2 border-b border-border mb-1">
                    <p className="text-xs text-muted">Signed in as</p>
                    <p className="text-sm font-bold truncate">{user.email}</p>
                  </div>
                  <Link to="/account-section" className="block px-4 py-2 text-sm text-primary hover:bg-card transition-colors font-semibold">My Account</Link>
                  <Link to="/account" className="block px-4 py-2 text-sm text-primary hover:bg-card transition-colors">Full Account</Link>
                  <Link to="/profile" className="block px-4 py-2 text-sm text-primary hover:bg-card transition-colors">Profile</Link>
                  <Link to="/orders" className="block px-4 py-2 text-sm text-primary hover:bg-card transition-colors">Orders History</Link>
                  {user.role === 'admin' && (
                    <Link to="/admin" className="block px-4 py-2 text-sm text-accent font-semibold hover:bg-card transition-colors flex items-center">
                      <LayoutDashboard className="w-4 h-4 mr-2" /> Admin Panel
                    </Link>
                  )}
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors flex items-center mt-1 border-t border-border pt-3"
                  >
                    <LogOut className="w-4 h-4 mr-2" /> Logout
                  </button>
                </div>
              </div>
            ) : (
              <Link to="/login" className="btn-primary text-sm px-5 h-9">
                Sign In
              </Link>
            )}
            
            <button className="md:hidden p-2 text-muted" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Search - Only on small screens */}
      <div className="md:hidden px-4 pb-3">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted w-4 h-4" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg text-sm outline-none"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </div>
    </nav>
  );
};

export default Navbar;
