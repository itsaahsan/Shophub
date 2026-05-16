import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '../services/api';
import { User, Shield, User as UserIcon, Mail, Calendar, MoreVertical, Search } from 'lucide-react';
import { User as UserType } from '../types';

const AdminUsers: React.FC = () => {
  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers().then(res => res.data),
  });

  if (isLoading) return <div className="p-8">Loading users...</div>;

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-primary mb-2">Customers</h1>
          <p className="text-muted">Manage your user base and permissions.</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted w-4 h-4" />
            <input 
              type="text" 
              placeholder="Search users..." 
              className="pl-10 pr-4 py-2 bg-white border border-border rounded-xl text-sm focus:ring-2 focus:ring-accent/20 outline-none w-64"
            />
          </div>
          <button className="btn-primary py-2 px-6 text-sm rounded-xl">Export</button>
        </div>
      </div>

      <div className="bg-white rounded-[2rem] border border-border shadow-subtle overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-[#fafafa] border-b border-border">
            <tr>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">User</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Role</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Email</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Joined</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Status</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {users?.map((user: UserType) => (
              <tr key={user.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-5">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent overflow-hidden">
                      {user.avatar ? (
                        <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
                      ) : (
                        <UserIcon className="w-5 h-5" />
                      )}
                    </div>
                    <span className="font-bold text-primary">{user.name}</span>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                    user.role === 'admin' ? 'bg-indigo-100 text-indigo-600' : 'bg-blue-100 text-blue-600'
                  }`}>
                    {user.role === 'admin' && <Shield className="w-3 h-3 mr-1" />}
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-5 text-sm text-muted">
                  <div className="flex items-center">
                    <Mail className="w-3 h-3 mr-2" />
                    {user.email}
                  </div>
                </td>
                <td className="px-6 py-5 text-sm text-muted">
                   <div className="flex items-center">
                    <Calendar className="w-3 h-3 mr-2" />
                    {(user as any).created_at ? new Date((user as any).created_at).toLocaleDateString() : 'N/A'}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <span className="inline-flex items-center text-success">
                    <div className="w-1.5 h-1.5 bg-success rounded-full mr-2"></div>
                    <span className="text-xs font-bold">Active</span>
                  </span>
                </td>
                <td className="px-6 py-5 text-right">
                  <button className="p-2 text-muted hover:text-primary transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminUsers;
