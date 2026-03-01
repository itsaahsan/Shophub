import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, DollarSign, ShoppingBag, Package, TrendingUp } from 'lucide-react';
import { AdminStats } from '../types';

const AdminDashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery<AdminStats>({
    queryKey: ['admin-stats'],
    queryFn: () => adminApi.getStats().then(res => res.data),
  });

  if (isLoading) return <div className="text-center py-20">Loading dashboard...</div>;
  if (!stats) return <div className="text-center py-20">Failed to load stats.</div>;

  const cards = [
    { title: 'Total Revenue', value: `$${stats.total_revenue.toFixed(2)}`, icon: DollarSign, color: 'bg-green-500' },
    { title: 'Total Sales', value: stats.total_sales, icon: ShoppingBag, color: 'bg-blue-500' },
    { title: 'Total Users', value: stats.total_users, icon: Users, color: 'bg-purple-500' },
    { title: 'Total Products', value: stats.total_products, icon: Package, color: 'bg-orange-500' },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Admin Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 flex items-center space-x-4 shadow-sm">
            <div className={`${card.color} p-3 rounded-xl text-white`}>
              <card.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-gray-500">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Revenue Chart */}
        <div className="lg:col-span-2 bg-white p-8 rounded-2xl border border-gray-100">
          <h3 className="text-xl font-bold mb-8">Revenue Overview</h3>
          <div className="h-80">
            {stats.revenue_chart.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.revenue_chart}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="revenue" fill="#2563eb" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <TrendingUp className="w-12 h-12 mb-2 opacity-20" />
                <p>No revenue data yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Orders */}
        <div className="bg-white p-8 rounded-2xl border border-gray-100">
          <h3 className="text-xl font-bold mb-8">Recent Orders</h3>
          <div className="space-y-4">
            {stats.recent_orders.length === 0 ? (
              <p className="text-gray-500 text-center py-10 italic">No orders yet</p>
            ) : (
              stats.recent_orders.map((order) => (
                <div key={order.id} className="flex items-center justify-between border-b border-gray-50 pb-4">
                  <div>
                    <p className="font-bold text-sm">Order #{order.id.slice(-6)}</p>
                    <p className="text-xs text-gray-400">{new Date(order.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm text-blue-600">${order.total.toFixed(2)}</p>
                    <p className="text-[10px] uppercase font-bold text-green-500">{order.status}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
