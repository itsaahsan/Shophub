import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '../services/api';
import { ShoppingBag, Calendar, User, DollarSign, ExternalLink, Filter } from 'lucide-react';
import { Order } from '../types';

const AdminOrders: React.FC = () => {
  const { data: orders, isLoading } = useQuery({
    queryKey: ['admin-orders'],
    queryFn: () => adminApi.getOrders().then(res => res.data),
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-success/10 text-success border-success/20';
      case 'pending': return 'bg-warning/10 text-warning border-warning/20';
      case 'shipped': return 'bg-blue-100 text-blue-600 border-blue-200';
      case 'delivered': return 'bg-indigo-100 text-indigo-600 border-indigo-200';
      case 'cancelled': return 'bg-red-50 text-red-500 border-red-100';
      default: return 'bg-gray-100 text-gray-500 border-gray-200';
    }
  };

  if (isLoading) return <div className="p-8">Loading orders...</div>;

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-primary mb-2">Orders</h1>
          <p className="text-muted">Track and manage all system transactions.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-border rounded-xl text-sm font-bold text-muted hover:text-primary transition-colors">
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
          <button className="btn-primary py-2 px-6 text-sm rounded-xl font-bold">New Order</button>
        </div>
      </div>

      <div className="bg-white rounded-[2rem] border border-border shadow-subtle overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-[#fafafa] border-b border-border">
            <tr>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Order ID</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Customer</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Date</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Total</th>
              <th className="px-6 py-4 text-xs font-extrabold uppercase tracking-widest text-muted">Status</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {orders?.map((order: Order) => (
              <tr key={order.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-5">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-card border border-border flex items-center justify-center text-muted">
                      <ShoppingBag className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="font-bold text-primary block">#{order.id.substring(0, 8).toUpperCase()}</span>
                      <span className="text-[10px] text-muted font-bold uppercase tracking-tight">Manual Order</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5 text-sm">
                  <div className="flex items-center text-primary font-medium">
                    <User className="w-3 h-3 mr-2 text-muted" />
                    User ID: {order.user_id.substring(0, 8)}...
                  </div>
                </td>
                <td className="px-6 py-5 text-sm text-muted">
                  <div className="flex items-center">
                    <Calendar className="w-3 h-3 mr-2" />
                    {new Date(order.created_at).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="flex items-center font-bold text-primary">
                    <DollarSign className="w-3 h-3 text-success" />
                    {order.total.toFixed(2)}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${getStatusColor(order.status)}`}>
                    {order.status}
                  </span>
                </td>
                <td className="px-6 py-5 text-right">
                  <button className="p-2 text-muted hover:text-accent transition-colors">
                    <ExternalLink className="w-5 h-5" />
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

export default AdminOrders;
