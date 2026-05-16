import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { User as UserIcon, Mail, Shield, Calendar, LogOut, Award, Check, Clock, AlertCircle, CreditCard, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { subscriptionApi } from '../services/api';
import { Subscription } from '../types';
import toast from 'react-hot-toast';

const Account: React.FC = () => {
  const { user, logout, updateProfile } = useAuthStore();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'account' | 'security' | 'certificates' | 'subscriptions'>('overview');
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState(user?.name || '');

  const { data: subscriptionsData } = useQuery({
    queryKey: ['my-subscriptions'],
    queryFn: () => subscriptionApi.getMe().then(res => res.data),
    enabled: !!user,
  });

  const activeSubscription = subscriptionsData?.subscriptions?.find((s: Subscription) => s.status === 'active');

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-primary mb-4">Please login to view your account</h2>
          <button onClick={() => navigate('/login')} className="btn-primary">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleStartEditName = () => {
    setNameInput(user.name);
    setEditingName(true);
  };

  const handleSaveName = async () => {
    const trimmed = nameInput.trim();
    if (!trimmed || trimmed === user.name) {
      setEditingName(false);
      return;
    }
    try {
      await updateProfile({ name: trimmed });
      toast.success('Name updated');
      setEditingName(false);
    } catch {
      toast.error('Failed to update name');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-[2.5rem] p-8 md:p-12 mb-8 shadow-subtle border border-border">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-start space-x-6">
              <div className="w-24 h-24 bg-gradient-to-br from-accent to-indigo-500 rounded-[1.5rem] flex items-center justify-center text-white shadow-lg">
                <UserIcon className="w-12 h-12" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-extrabold text-primary mb-2">{user.name}</h1>
                <p className="text-sm text-muted font-semibold uppercase tracking-widest mb-3">{user.role} Account</p>
                <div className="flex items-center space-x-2 text-sm text-success bg-success/10 px-3 py-1 rounded-full w-fit">
                  <Check className="w-4 h-4" />
                  <span>Account Verified</span>
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="btn-secondary h-11 text-red-500 border-red-200 hover:bg-red-50 flex items-center"
            >
              <LogOut className="w-4 h-4 mr-2" /> Logout
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 md:gap-4 mb-8 pb-4 border-b border-border">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'account', label: 'Account Info' },
            { id: 'subscriptions', label: 'Subscriptions' },
            { id: 'security', label: 'Security' },
            { id: 'certificates', label: 'Certificates' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-primary text-white'
                  : 'text-muted hover:text-primary border border-border hover:border-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Quick Stats */}
            <div className="bg-white p-6 rounded-2xl border border-border shadow-subtle">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-primary">Total Orders</h3>
                <div className="p-2 bg-accent/10 rounded-lg text-accent">
                  <Award className="w-5 h-5" />
                </div>
              </div>
              <p className="text-3xl font-extrabold text-primary">12</p>
              <p className="text-xs text-muted mt-2">Lifetime purchases</p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-border shadow-subtle">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-primary">Membership</h3>
                <div className={`p-2 rounded-lg ${activeSubscription ? 'bg-accent/10 text-accent' : 'bg-gray-100 text-gray-400'}`}>
                  <CreditCard className="w-5 h-5" />
                </div>
              </div>
              <p className="text-3xl font-extrabold text-primary">{activeSubscription ? activeSubscription.plan.name : 'Free'}</p>
              <p className="text-xs text-muted mt-2">{activeSubscription ? 'Premium Member' : 'Standard Member'}</p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-border shadow-subtle">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-primary">Member Since</h3>
                <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                  <Calendar className="w-5 h-5" />
                </div>
              </div>
              <p className="text-3xl font-extrabold text-primary">8mo</p>
              <p className="text-xs text-muted mt-2">Since March 2025</p>
            </div>
          </div>
        )}

        {/* Account Info Tab */}
        {activeTab === 'account' && (
          <div className="bg-white p-8 rounded-[2.5rem] border border-border shadow-subtle">
            <div className="space-y-8">
              <div className="flex items-center justify-between pb-6 border-b border-border">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <UserIcon className="w-5 h-5" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Full Name</p>
                    {editingName ? (
                      <input
                        autoFocus
                        className="input-field h-9 text-sm max-w-xs"
                        value={nameInput}
                        onChange={(e) => setNameInput(e.target.value)}
                      />
                    ) : (
                      <p className="font-bold text-primary text-lg">{user.name}</p>
                    )}
                  </div>
                </div>
                {editingName ? (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleSaveName}
                      className="btn-primary h-8 px-3 text-[11px]"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingName(false)}
                      className="btn-secondary h-8 px-3 text-[11px]"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={handleStartEditName}
                    className="text-xs font-bold text-accent hover:underline hover:text-primary transition-colors"
                  >
                    Edit
                  </button>
                )}
              </div>

              <div className="flex items-center justify-between pb-6 border-b border-border">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <Mail className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Email Address</p>
                    <p className="font-bold text-primary text-lg">{user.email}</p>
                  </div>
                </div>
                <button className="text-xs font-bold text-accent hover:underline hover:text-primary transition-colors">Change</button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Account Type</p>
                    <p className="font-bold text-primary text-lg capitalize">{user.role}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Subscriptions Tab */}
        {activeTab === 'subscriptions' && (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-extrabold text-primary">Your Subscriptions</h2>
              {!activeSubscription && (
                <button onClick={() => navigate('/plans')} className="btn-primary text-xs h-9 px-4">
                  Browse Plans
                </button>
              )}
            </div>

            {activeSubscription ? (
              <div className="bg-white border-2 border-accent rounded-[2.5rem] p-8 shadow-lg shadow-accent/5 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4">
                   <span className="bg-success text-white text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full">
                    Active
                  </span>
                </div>
                <div className="flex flex-col md:flex-row gap-8 items-start md:items-center">
                  <div className="w-20 h-20 bg-accent/10 rounded-3xl flex items-center justify-center text-accent">
                    <Crown className="w-10 h-10" />
                  </div>
                  <div className="flex-grow">
                    <h3 className="text-2xl font-bold text-primary mb-1">{activeSubscription.plan.name} Membership</h3>
                    <p className="text-muted text-sm mb-4">{activeSubscription.plan.description}</p>
                    <div className="flex flex-wrap gap-4">
                      <div className="bg-gray-50 px-4 py-2 rounded-xl border border-border">
                        <p className="text-[10px] text-muted uppercase font-bold">Billing Cycle</p>
                        <p className="text-sm font-bold text-primary capitalize">{activeSubscription.plan.billing_cycle}</p>
                      </div>
                      <div className="bg-gray-50 px-4 py-2 rounded-xl border border-border">
                        <p className="text-[10px] text-muted uppercase font-bold">Next Billing</p>
                        <p className="text-sm font-bold text-primary">
                          {activeSubscription.end_date ? new Date(activeSubscription.end_date).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                      <div className="bg-gray-50 px-4 py-2 rounded-xl border border-border">
                        <p className="text-[10px] text-muted uppercase font-bold">Price</p>
                        <p className="text-sm font-bold text-primary">${activeSubscription.plan.price}</p>
                      </div>
                    </div>
                  </div>
                  <div className="w-full md:w-auto flex flex-col gap-3">
                    <button className="btn-primary h-11 px-8 text-sm">
                      Manage via Stripe <ExternalLink className="w-4 h-4 ml-2" />
                    </button>
                    <button className="text-xs font-bold text-red-500 hover:underline">Cancel Subscription</button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white border border-border border-dashed rounded-[2.5rem] p-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 mx-auto mb-4">
                  <CreditCard className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-primary mb-2">No Active Subscription</h3>
                <p className="text-muted mb-6 max-w-sm mx-auto">
                  Subscribe to a premium plan to unlock exclusive features, faster shipping, and special discounts.
                </p>
                <button onClick={() => navigate('/plans')} className="btn-primary h-11 px-10">
                  View Pricing Plans
                </button>
              </div>
            )}

            {subscriptionsData?.subscriptions?.length > 1 && (
              <div className="mt-12">
                <h3 className="text-lg font-bold text-primary mb-6">Subscription History</h3>
                <div className="space-y-4">
                  {subscriptionsData.subscriptions.map((sub: Subscription) => (
                    <div key={sub.id} className="bg-white p-4 rounded-2xl border border-border flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center text-gray-500">
                          <Zap className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="font-bold text-primary">{sub.plan.name}</p>
                          <p className="text-xs text-muted">{new Date(sub.start_date).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-md ${
                        sub.status === 'active' ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-400'
                      }`}>
                        {sub.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="bg-white p-8 rounded-[2.5rem] border border-border shadow-subtle">
            <div className="space-y-8">
              <div className="flex items-center justify-between pb-6 border-b border-border">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <Shield className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Password</p>
                    <p className="font-bold text-primary">Last changed 2 months ago</p>
                  </div>
                </div>
                <button className="btn-secondary text-xs h-9 px-4">Change Password</button>
              </div>

              <div className="flex items-center justify-between pb-6 border-b border-border">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Two-Factor Authentication</p>
                    <p className="font-bold text-primary">Not enabled</p>
                  </div>
                </div>
                <button className="btn-secondary text-xs h-9 px-4">Enable 2FA</button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-card rounded-2xl text-muted">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-extrabold uppercase tracking-widest text-muted">Login History</p>
                    <p className="font-bold text-primary">Last login: Today at 2:30 PM</p>
                  </div>
                </div>
                <button className="text-xs font-bold text-accent hover:underline">View All</button>
              </div>
            </div>
          </div>
        )}

        {/* Certificates Tab */}
        {activeTab === 'certificates' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-extrabold text-primary mb-6">Account Certificates</h2>

            {/* Certificate Card - Verified Member */}
            <div className="bg-gradient-to-br from-success/10 to-success/5 p-6 rounded-[1.5rem] border border-success/30 shadow-lg overflow-hidden relative group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-success/10 rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform duration-300"></div>
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-success/20 rounded-xl text-success">
                      <Check className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-primary text-lg">Verified Member</h3>
                      <p className="text-xs text-muted">Issued on March 15, 2025</p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold uppercase px-3 py-1 bg-success/20 text-success rounded-full">Active</span>
                </div>
                <p className="text-sm text-muted mb-4">Your email and account have been verified. You're all set to shop with full benefits.</p>
                <div className="flex items-center justify-between text-xs text-muted">
                  <span>Certificate ID: SHOP-VER-2025-001</span>
                  <button className="text-success font-bold hover:underline">Download</button>
                </div>
              </div>
            </div>

            {/* Certificate Card - Regular Shopper */}
            <div className="bg-gradient-to-br from-accent/10 to-accent/5 p-6 rounded-[1.5rem] border border-accent/30 shadow-lg overflow-hidden relative group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-accent/10 rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform duration-300"></div>
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-accent/20 rounded-xl text-accent">
                      <Award className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-primary text-lg">Regular Shopper</h3>
                      <p className="text-xs text-muted">Earned on May 1, 2025</p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold uppercase px-3 py-1 bg-accent/20 text-accent rounded-full">Active</span>
                </div>
                <p className="text-sm text-muted mb-4">You've made 5+ purchases. Enjoy exclusive discounts and early access to sales.</p>
                <div className="flex items-center justify-between text-xs text-muted">
                  <span>Certificate ID: SHOP-REG-2025-001</span>
                  <button className="text-accent font-bold hover:underline">Download</button>
                </div>
              </div>
            </div>

            {/* Certificate Card - Coming Soon */}
            <div className="bg-gradient-to-br from-gray-100 to-gray-50 p-6 rounded-[1.5rem] border border-gray-300 border-dashed shadow-lg overflow-hidden relative group opacity-50">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gray-200 rounded-full -mr-16 -mt-16"></div>
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-gray-200 rounded-xl text-gray-400">
                      <Clock className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-600 text-lg">Premium Member</h3>
                      <p className="text-xs text-gray-500">Available when spending $5,000+</p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold uppercase px-3 py-1 bg-gray-300 text-gray-600 rounded-full">Locked</span>
                </div>
                <p className="text-sm text-gray-600 mb-4">Unlock premium member status by reaching $5,000 in total purchases.</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Current progress: $2,450 / $5,000 (49%)</span>
                </div>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 p-6 rounded-2xl">
              <p className="text-sm text-blue-900">
                <span className="font-bold">Certificates are earned automatically</span> based on your account verification and purchase history. They provide exclusive benefits, discounts, and special offers.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Account;
