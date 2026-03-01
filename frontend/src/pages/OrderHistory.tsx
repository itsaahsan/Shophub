import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { orderApi } from '../services/api';
import { Order } from '../types';
import { Link } from 'react-router-dom';
import { Package, ChevronRight, Clock } from 'lucide-react';

const OrderHistory: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => orderApi.list().then(res => res.data),
  });

  if (isLoading) return <div className="text-center py-20">Loading orders...</div>;

  return (
    <div className="max-w-4xl mx-auto py-10">
      {data?.orders.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-[2.5rem] border border-border border-dashed">
          <Package className="w-12 h-12 text-muted mx-auto mb-4 opacity-20" />
          <p className="text-muted font-bold">You haven't placed any orders yet.</p>
          <Link to="/" className="btn-primary inline-flex mt-6">Start Shopping</Link>
        </div>
      ) : (
        <div className="space-y-6">
          {data?.orders.map((order: Order) => (
            <Link 
              key={order.id} 
              to={`/orders/${order.id}`}
              className="block bg-white p-6 rounded-3xl border border-border hover:border-accent transition-all duration-300 shadow-subtle group"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-card rounded-2xl flex items-center justify-center text-accent">
                    <Package className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="font-bold text-primary">Order #{order.id.slice(-8).toUpperCase()}</p>
                    <div className="flex items-center text-xs text-muted mt-1 space-x-3">
                      <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {new Date(order.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{order.items.length} items</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between md:justify-end md:space-x-10">
                  <div className="text-left md:text-right">
                    <p className="text-lg font-extrabold text-primary">${order.total.toFixed(2)}</p>
                    <span className={`inline-block px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-widest mt-1 ${
                      order.status === 'paid' ? 'bg-success/10 text-success' : 'bg-accent/10 text-accent'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-muted group-hover:text-accent group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrderHistory;
