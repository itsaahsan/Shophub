import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { orderApi } from '../services/api';
import { Order } from '../types';
import { Package, MapPin, CreditCard, ChevronLeft, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const OrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  
  const { data: order, isLoading } = useQuery<Order>({
    queryKey: ['order', id],
    queryFn: () => orderApi.get(id!).then(res => res.data),
    enabled: !!id,
  });

  const cancelMutation = useMutation({
    mutationFn: () => orderApi.cancel(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['order', id] });
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Order cancelled successfully');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to cancel order');
    },
  });

  if (isLoading) return <div className="text-center py-20">Loading order details...</div>;
  if (!order) return <div className="text-center py-20">Order not found.</div>;

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-500/10 text-yellow-600',
    paid: 'bg-success/10 text-success',
    shipped: 'bg-blue-500/10 text-blue-600',
    delivered: 'bg-green-600/10 text-green-700',
    cancelled: 'bg-red-500/10 text-red-500',
  };

  return (
    <div className="max-w-4xl mx-auto py-10">
      <Link to="/orders" className="inline-flex items-center text-xs font-bold uppercase tracking-widest text-muted hover:text-primary mb-8 transition-colors group">
        <ChevronLeft className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" />
        Back to Orders
      </Link>

      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-primary tracking-tight">Order Details</h1>
          <p className="text-muted mt-1">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
        </div>
        <div className="text-left md:text-right space-y-3">
          <div>
            <p className="text-xs font-bold text-muted uppercase tracking-widest mb-1">Status</p>
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-extrabold uppercase tracking-widest ${statusColors[order.status] || 'bg-accent/10 text-accent'}`}>
              {order.status}
            </span>
          </div>
          {order.status === 'pending' && (
            <button
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
              className="inline-flex items-center px-4 py-2 bg-red-50 text-red-600 rounded-xl text-xs font-bold hover:bg-red-100 transition-colors disabled:opacity-50"
            >
              <XCircle className="w-3.5 h-3.5 mr-1.5" />
              {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Order'}
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-3xl border border-border p-8 shadow-subtle">
            <h3 className="font-bold mb-6 flex items-center">
              <Package className="w-5 h-5 mr-2 text-accent" />
              Items Summary
            </h3>
            <div className="space-y-6">
              {order.items.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-card rounded-xl border border-border p-2">
                      <img src={item.image || 'https://placehold.co/64x64/f3f4f6/9ca3af?text=No+img'} alt="" className="w-full h-full object-contain" />
                    </div>
                    <div>
                      <p className="font-bold text-primary text-sm">{item.name}</p>
                      <p className="text-xs text-muted">Qty: {item.quantity} × ${item.price.toFixed(2)}</p>
                    </div>
                  </div>
                  <p className="font-bold text-primary">${(item.quantity * item.price).toFixed(2)}</p>
                </div>
              ))}
            </div>
            <div className="mt-10 pt-6 border-t border-border space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted">Subtotal</span>
                <span className="font-bold">${order.total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted">Shipping</span>
                <span className="text-success font-bold">Free</span>
              </div>
              <div className="flex justify-between text-xl font-extrabold pt-3 border-t border-border">
                <span>Total</span>
                <span>${order.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-border p-8 shadow-subtle">
            <h3 className="font-bold mb-6 flex items-center">
              <MapPin className="w-5 h-5 mr-2 text-accent" />
              Shipping
            </h3>
            <div className="text-sm space-y-1 font-medium text-muted leading-relaxed">
              <p className="text-primary font-bold">{order.shipping_address.full_name}</p>
              <p>{order.shipping_address.address_line}</p>
              <p>{order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip_code}</p>
              <p>{order.shipping_address.country}</p>
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-border p-8 shadow-subtle">
            <h3 className="font-bold mb-6 flex items-center">
              <CreditCard className="w-5 h-5 mr-2 text-accent" />
              Payment
            </h3>
            <div className="text-sm font-medium text-muted">
              <p>Stripe Transaction</p>
              <p className="text-[10px] font-mono mt-2 break-all bg-card p-2 rounded-lg border border-border">
                {order.stripe_session_id || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
