import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  Users, 
  ShoppingBag, 
  Settings, 
  ArrowLeft,
  ChevronRight,
  TrendingUp,
  BarChart3
} from 'lucide-react';

const AdminLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();

  const menuItems = [
    { name: 'Overview', path: '/admin', icon: LayoutDashboard },
    { name: 'Products', path: '/admin/products', icon: Package },
    { name: 'Orders', path: '/admin/orders', icon: ShoppingBag },
    { name: 'Customers', path: '/admin/users', icon: Users },
    { name: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
    { name: 'Settings', path: '/admin/settings', icon: Settings },
  ];

  return (
    <div className="fixed inset-0 flex bg-background z-[100]">
      {/* Dark Sidebar - Shopify Style */}
      <aside className="w-64 bg-[#111111] text-white flex flex-col h-full border-r border-white/5">
        <div className="p-6">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-xl font-extrabold tracking-tighter text-white">Shophub</span>
            <span className="text-[10px] font-bold bg-accent/20 text-accent px-1.5 py-0.5 rounded uppercase">Admin</span>
          </Link>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                  isActive 
                    ? 'bg-white/10 text-white shadow-sm ring-1 ring-white/10' 
                    : 'text-white/60 hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center">
                  <item.icon className={`w-4 h-4 mr-3 ${isActive ? 'text-accent' : 'text-inherit'}`} />
                  {item.name}
                </div>
                {isActive && <div className="w-1.5 h-1.5 bg-accent rounded-full"></div>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 mt-auto">
          <div className="bg-white/5 p-4 rounded-2xl border border-white/10">
            <div className="flex items-center space-x-2 text-accent mb-2">
              <TrendingUp className="w-4 h-4" />
              <span className="text-[10px] font-extrabold uppercase tracking-widest">Growth Plan</span>
            </div>
            <p className="text-xs text-white/60 mb-3">Your sales are up 12% this month.</p>
            <button className="w-full bg-white text-primary text-[11px] font-bold py-2 rounded-lg hover:bg-gray-100 transition-colors">
              View Analytics
            </button>
          </div>
          
          <Link to="/" className="flex items-center text-white/60 hover:text-white text-xs mt-6 px-3 py-2 group">
            <ArrowLeft className="w-3 h-3 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to Shop
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-[#fafafa]">
        {/* Header */}
        <header className="h-16 bg-white border-b border-border px-8 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-2 text-xs text-muted">
            <span>Admin</span>
            <ChevronRight className="w-3 h-3" />
            <span className="font-bold text-primary">
              {menuItems.find(i => i.path === location.pathname)?.name || 'Dashboard'}
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-muted hover:text-primary transition-colors relative">
              <div className="w-2 h-2 bg-red-500 rounded-full absolute top-2 right-2 ring-2 ring-white"></div>
              <LayoutDashboard className="w-5 h-5" />
            </button>
            <div className="w-8 h-8 rounded-full bg-card border border-border flex items-center justify-center overflow-hidden">
              <img src="https://ui-avatars.com/api/?name=Admin&background=6366f1&color=fff" alt="Admin" />
            </div>
          </div>
        </header>

        {/* Content Container */}
        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
