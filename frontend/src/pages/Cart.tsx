import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, ArrowRight, ShoppingCart as CartIcon } from 'lucide-react';
import { useCartStore } from '../stores/cartStore';

const Cart: React.FC = () => {
  const { items, addItem, removeItem, loading } = useCartStore();
  const navigate = useNavigate();

  const total = items.reduce((acc, item) => acc + item.price * item.quantity, 0);

  if (items.length === 0 && !loading) {
    return (
      <div className="text-center py-24 bg-card rounded-[3rem] border border-border border-dashed max-w-2xl mx-auto mt-10">
        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-subtle border border-border">
          <CartIcon className="w-10 h-10 text-gray-200" />
        </div>
        <h2 className="text-2xl font-bold text-primary mb-2">Your cart is empty</h2>
        <p className="text-muted mb-10 max-w-xs mx-auto">Looks like you haven't added anything to your cart yet.</p>
        <Link to="/" className="btn-primary inline-flex items-center px-8">
          Start Shopping <ArrowRight className="w-4 h-4 ml-2" />
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-extrabold text-primary tracking-tight">Shopping Cart</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-4">
          {items.map((item) => (
            <div key={item.product_id} className="bg-white p-6 rounded-2xl border border-border flex items-center space-x-4 shadow-subtle">
              <img
                src={item.image || 'https://placehold.co/100x100/f3f4f6/9ca3af?text=No+img'}
                alt={item.name}
                className="w-24 h-24 object-contain rounded-xl border border-border p-1"
              />
              <div className="flex-1 min-w-0">
                <Link to={`/product/${item.product_id}`} className="font-bold text-primary hover:text-accent transition-colors truncate block">{item.name}</Link>
                <p className="text-muted text-sm">${item.price.toFixed(2)}</p>
                <div className="flex items-center space-x-4 mt-3">
                  <div className="flex bg-card border border-border rounded-xl overflow-hidden">
                    <button onClick={() => addItem(item.product_id, Math.max(1, item.quantity - 1))} className="px-3 py-1.5 hover:bg-white transition-colors font-bold text-sm">-</button>
                    <span className="px-4 py-1.5 border-x border-border text-sm font-extrabold flex items-center">{item.quantity}</span>
                    <button onClick={() => addItem(item.product_id, item.quantity + 1)} className="px-3 py-1.5 hover:bg-white transition-colors font-bold text-sm">+</button>
                  </div>
                  <button onClick={() => removeItem(item.product_id)} className="text-red-500 hover:text-red-700 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-extrabold text-primary">${(item.price * item.quantity).toFixed(2)}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-white p-8 rounded-3xl border border-border space-y-6 sticky top-24 shadow-subtle">
            <h3 className="text-xl font-bold text-primary">Order Summary</h3>
            <div className="space-y-4 border-b border-border pb-6">
              <div className="flex justify-between text-muted text-sm">
                <span>Subtotal</span>
                <span className="font-bold text-primary">${total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-muted text-sm">
                <span>Shipping</span>
                <span className="text-success font-bold">Free</span>
              </div>
              <div className="flex justify-between text-muted text-sm">
                <span>Tax</span>
                <span className="font-bold text-primary">$0.00</span>
              </div>
            </div>
            <div className="flex justify-between text-2xl font-extrabold text-primary">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <button
              onClick={() => navigate('/checkout')}
              className="btn-primary w-full h-14 text-base shadow-xl shadow-primary/20"
            >
              Proceed to Checkout <ArrowRight className="w-5 h-5 ml-2" />
            </button>
            <p className="text-xs text-center text-muted">Secure payment powered by Stripe</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
