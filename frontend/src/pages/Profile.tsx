import React from 'react';
import { useAuthStore } from '../stores/authStore';
import { User as UserIcon, Mail, Shield, Calendar, LogOut } from 'lucide-react';

const Profile: React.FC = () => {
  const { user, logout } = useAuthStore();

  if (!user) return null;

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
        <div className="md:col-span-1 flex flex-col items-center">
          <div className="w-32 h-32 bg-accent/10 rounded-[2.5rem] border border-accent/20 flex items-center justify-center text-accent mb-6 shadow-xl shadow-accent/10">
            <UserIcon className="w-16 h-16" />
          </div>
          <h2 className="text-xl font-bold text-primary mb-1">{user.name}</h2>
          <p className="text-muted text-sm uppercase tracking-widest font-extrabold">{user.role}</p>
          
          <button 
            onClick={logout}
            className="btn-secondary w-full mt-10 h-11 text-red-500 border-red-100 hover:bg-red-50"
          >
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </button>
        </div>

        <div className="md:col-span-2 space-y-6">
          <div className="bg-white p-8 rounded-[2.5rem] border border-border shadow-subtle space-y-8">
            <div className="flex items-center justify-between border-b border-border pb-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-card rounded-2xl text-muted">
                  <Mail className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-[10px] font-extrabold uppercase tracking-widest text-muted">Email Address</p>
                  <p className="font-bold text-primary">{user.email}</p>
                </div>
              </div>
              <button className="text-xs font-bold text-accent hover:underline">Change</button>
            </div>

            <div className="flex items-center justify-between border-b border-border pb-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-card rounded-2xl text-muted">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-[10px] font-extrabold uppercase tracking-widest text-muted">Security</p>
                  <p className="font-bold text-primary">Password last changed 3 months ago</p>
                </div>
              </div>
              <button className="text-xs font-bold text-accent hover:underline">Reset</button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-card rounded-2xl text-muted">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-[10px] font-extrabold uppercase tracking-widest text-muted">Member Since</p>
                  <p className="font-bold text-primary">March 2024</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
