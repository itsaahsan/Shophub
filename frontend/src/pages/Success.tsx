import React, { useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, Package, ArrowRight } from 'lucide-react';
import { useCartStore } from '../stores/cartStore';

const Success: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const clearCart = useCartStore((state) => state.clearCart);

  useEffect(() => {
    clearCart();
  }, [clearCart]);

  return (
    <div className="max-w-md mx-auto text-center py-20">
      <div className="bg-success/10 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8">
        <CheckCircle className="w-12 h-12 text-success" />
      </div>
      <h1 className="text-4xl font-extrabold text-primary tracking-tight mb-4">Payment Successful!</h1>
      <p className="text-muted mb-12">Thank you for your purchase. Your order is being processed.</p>
      
      <div className="bg-white p-6 rounded-2xl border border-border mb-8 text-left shadow-subtle">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-accent/10 rounded-lg text-accent">
            <Package className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-muted font-bold uppercase tracking-widest">Stripe Session ID</p>
            <p className="text-xs font-mono truncate text-primary mt-1">{sessionId}</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <Link to="/orders" className="btn-primary w-full h-12 text-sm">
          View My Orders
        </Link>
        <Link to="/" className="btn-secondary w-full h-12 text-sm">
          Continue Shopping <ArrowRight className="w-4 h-4 ml-1" />
        </Link>
      </div>
    </div>
  );
};

export default Success;
