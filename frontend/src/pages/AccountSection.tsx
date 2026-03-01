import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Award, LogOut, ArrowRight, Lock, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';

const AccountSection: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'profile' | 'certificates'>('profile');

  if (!user) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-[400px] text-center">
          <h1 className="text-4xl font-extrabold tracking-tighter text-primary mb-2">shophub</h1>
          <p className="text-muted text-sm mb-10">Sign in to access your account</p>
          <button
            onClick={() => navigate('/login')}
            className="btn-primary w-full h-11"
          >
            Go to Sign In
          </button>
        </div>
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/');
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-[420px]">
        {/* Header */}
        <div className="flex flex-col items-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-br from-accent to-indigo-500 rounded-[1rem] flex items-center justify-center text-white mb-4 shadow-lg">
            <User className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-extrabold text-primary mb-1">{user.name}</h1>
          <p className="text-muted text-sm font-semibold uppercase tracking-widest">{user.role}</p>
          <div className="flex items-center space-x-1.5 text-success text-sm mt-3 bg-success/10 px-3 py-1.5 rounded-full">
            <CheckCircle2 className="w-4 h-4" />
            <span className="font-semibold">Verified</span>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex-1 py-2 px-4 rounded-lg font-bold text-sm transition-all ${
              activeTab === 'profile'
                ? 'bg-primary text-white'
                : 'bg-card border border-border text-muted hover:border-primary'
            }`}
          >
            Profile
          </button>
          <button
            onClick={() => setActiveTab('certificates')}
            className={`flex-1 py-2 px-4 rounded-lg font-bold text-sm transition-all ${
              activeTab === 'certificates'
                ? 'bg-primary text-white'
                : 'bg-card border border-border text-muted hover:border-primary'
            }`}
          >
            Certificates
          </button>
        </div>

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-4">
            {/* Email */}
            <div className="relative group">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="email"
                disabled
                placeholder="Email"
                value={user.email}
                className="input-field pl-10 bg-card text-muted cursor-not-allowed"
              />
            </div>

            {/* Account Type */}
            <div className="relative group">
              <Award className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="text"
                disabled
                placeholder="Account Type"
                value={user.role === 'admin' ? 'Admin Account' : 'Customer Account'}
                className="input-field pl-10 bg-card text-muted cursor-not-allowed capitalize"
              />
            </div>

            {/* Member Since */}
            <div className="relative group">
              <Award className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="text"
                disabled
                placeholder="Member Since"
                value="March 2025 • 8 months"
                className="input-field pl-10 bg-card text-muted cursor-not-allowed"
              />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3 mt-6">
              <div className="bg-card border border-border rounded-lg p-3 text-center">
                <p className="text-2xl font-extrabold text-primary">12</p>
                <p className="text-xs text-muted font-semibold mt-1">Orders</p>
              </div>
              <div className="bg-card border border-border rounded-lg p-3 text-center">
                <p className="text-2xl font-extrabold text-success">$2,450</p>
                <p className="text-xs text-muted font-semibold mt-1">Spent</p>
              </div>
            </div>

            {/* Edit Profile Button */}
            <button
              className="btn-secondary w-full h-11 text-sm mt-6"
              onClick={() => navigate('/account')}
            >
              Edit Profile
            </button>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="w-full h-11 btn-secondary border-red-200 text-red-500 hover:bg-red-50 text-sm font-bold flex items-center justify-center"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          </div>
        )}

        {/* Certificates Tab */}
        {activeTab === 'certificates' && (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            {/* Elite Shopper Certificate */}
            <div className="bg-gradient-to-r from-purple-200/40 to-purple-100/30 border border-purple-300/40 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-purple-200/40 rounded-lg text-purple-600 flex-shrink-0 mt-0.5">
                    <Award className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-primary text-sm">Elite Shopper</h3>
                    <p className="text-xs text-muted">Earned Feb 20, 2025</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-purple-200/40 text-purple-700 px-2.5 py-1 rounded-full flex-shrink-0">Active</span>
              </div>
              <p className="text-xs text-muted mt-2 leading-relaxed">Premium status with exclusive perks</p>
            </div>

            {/* VIP Member Certificate */}
            <div className="bg-gradient-to-r from-amber-200/40 to-amber-100/30 border border-amber-300/40 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-amber-200/40 rounded-lg text-amber-600 flex-shrink-0 mt-0.5">
                    <Award className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-primary text-sm">VIP Member</h3>
                    <p className="text-xs text-muted">Earned Jan 10, 2025</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-amber-200/40 text-amber-700 px-2.5 py-1 rounded-full flex-shrink-0">Active</span>
              </div>
              <p className="text-xs text-muted mt-2 leading-relaxed">VIP access to special sales & events</p>
            </div>

            {/* Loyalty Star Certificate */}
            <div className="bg-gradient-to-r from-cyan-200/40 to-cyan-100/30 border border-cyan-300/40 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-cyan-200/40 rounded-lg text-cyan-600 flex-shrink-0 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-primary text-sm">Loyalty Star</h3>
                    <p className="text-xs text-muted">Earned Dec 5, 2024</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-cyan-200/40 text-cyan-700 px-2.5 py-1 rounded-full flex-shrink-0">Active</span>
              </div>
              <p className="text-xs text-muted mt-2 leading-relaxed">Loyalty rewards & bonus points</p>
            </div>

            {/* Verified Member Certificate */}
            <div className="bg-gradient-to-r from-success/20 to-success/10 border border-success/30 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-success/20 rounded-lg text-success flex-shrink-0 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-primary text-sm">Verified Member</h3>
                    <p className="text-xs text-muted">Issued Mar 15, 2025</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-success/20 text-success px-2.5 py-1 rounded-full flex-shrink-0">Active</span>
              </div>
              <p className="text-xs text-muted mt-2 leading-relaxed">Email verified & account activated</p>
            </div>

            {/* Regular Shopper Certificate */}
            <div className="bg-gradient-to-r from-accent/20 to-accent/10 border border-accent/30 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-accent/20 rounded-lg text-accent flex-shrink-0 mt-0.5">
                    <Award className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-primary text-sm">Regular Shopper</h3>
                    <p className="text-xs text-muted">Earned May 1, 2025</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-accent/20 text-accent px-2.5 py-1 rounded-full flex-shrink-0">Active</span>
              </div>
              <p className="text-xs text-muted mt-2 leading-relaxed">5+ purchases completed</p>
            </div>

            {/* Premium Member Certificate (Locked) */}
            <div className="bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-300 border-dashed rounded-xl p-4 opacity-60">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-gray-200 rounded-lg text-gray-400 flex-shrink-0 mt-0.5">
                    <Lock className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-gray-600 text-sm">Premium Member</h3>
                    <p className="text-xs text-gray-500">Unlock at $5,000 spent</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-gray-300 text-gray-600 px-2.5 py-1 rounded-full flex-shrink-0">49%</span>
              </div>
              <p className="text-xs text-gray-600 mt-2 leading-relaxed">$2,450 / $5,000 to unlock premium benefits</p>
            </div>

            {/* Diamond Member Certificate (Locked) */}
            <div className="bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-300 border-dashed rounded-xl p-4 opacity-60">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-gray-200 rounded-lg text-gray-400 flex-shrink-0 mt-0.5">
                    <Lock className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-gray-600 text-sm">Diamond Member</h3>
                    <p className="text-xs text-gray-500">Unlock at $10,000 spent</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-gray-300 text-gray-600 px-2.5 py-1 rounded-full flex-shrink-0">24%</span>
              </div>
              <p className="text-xs text-gray-600 mt-2 leading-relaxed">$2,450 / $10,000 to unlock diamond status</p>
            </div>

            {/* Platinum Member Certificate (Locked) */}
            <div className="bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-300 border-dashed rounded-xl p-4 opacity-60">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-2 bg-gray-200 rounded-lg text-gray-400 flex-shrink-0 mt-0.5">
                    <Lock className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-gray-600 text-sm">Platinum Member</h3>
                    <p className="text-xs text-gray-500">Unlock at $25,000 spent</p>
                  </div>
                </div>
                <span className="text-xs font-bold bg-gray-300 text-gray-600 px-2.5 py-1 rounded-full flex-shrink-0">9%</span>
              </div>
              <p className="text-xs text-gray-600 mt-2 leading-relaxed">$2,450 / $25,000 to unlock platinum benefits</p>
            </div>

            {/* View All Button */}
            <button
              onClick={() => navigate('/account')}
              className="w-full h-11 btn-secondary text-sm font-bold flex items-center justify-center mt-4 sticky bottom-0"
            >
              View Full Account <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        )}

        {/* Bottom Links */}
        <div className="mt-8 pt-6 border-t border-border text-center">
          <p className="text-xs text-muted">
            Need help? <a href="#" className="text-accent font-bold hover:underline">Contact Support</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AccountSection;
