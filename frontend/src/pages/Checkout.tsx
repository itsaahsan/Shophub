import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { orderApi } from '../services/api';
import { ShippingAddress } from '../types';
import toast from 'react-hot-toast';
import { Lock, CreditCard, ShieldCheck } from 'lucide-react';

const Checkout: React.FC = () => {
  const [address, setAddress] = useState<ShippingAddress>({
    full_name: '',
    address_line: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'US',
  });

  const checkoutMutation = useMutation({
    mutationFn: (data: any) => orderApi.checkout(data),
    onSuccess: (res) => {
      window.location.href = res.data.url;
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Checkout failed');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    checkoutMutation.mutate({ shipping_address: address });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAddress({ ...address, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-[#fafafa] pt-12 pb-24">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="space-y-10">
          <div>
            <h1 className="text-3xl font-extrabold text-primary tracking-tight mb-2">Checkout</h1>
            <p className="text-muted">Fill in your shipping details to complete the order.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            <section className="bg-white p-8 rounded-3xl border border-border shadow-subtle">
              <h3 className="text-lg font-bold mb-6 flex items-center">
                <div className="w-8 h-8 bg-card rounded-lg flex items-center justify-center mr-3 text-primary border border-border">1</div>
                Shipping Information
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">Full Name</label>
                  <input
                    type="text"
                    name="full_name"
                    required
                    placeholder="John Doe"
                    className="input-field"
                    value={address.full_name}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">Address Line</label>
                  <input
                    type="text"
                    name="address_line"
                    required
                    placeholder="123 Modern Lane"
                    className="input-field"
                    value={address.address_line}
                    onChange={handleChange}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">City</label>
                    <input
                      type="text"
                      name="city"
                      required
                      placeholder="San Francisco"
                      className="input-field"
                      value={address.city}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">State</label>
                    <input
                      type="text"
                      name="state"
                      required
                      placeholder="CA"
                      className="input-field"
                      value={address.state}
                      onChange={handleChange}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">Zip Code</label>
                    <input
                      type="text"
                      name="zip_code"
                      required
                      placeholder="94103"
                      className="input-field"
                      value={address.zip_code}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-extrabold uppercase tracking-widest text-muted mb-2">Country</label>
                    <input
                      type="text"
                      name="country"
                      required
                      className="input-field"
                      value={address.country}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>
            </section>

            <section className="bg-white p-8 rounded-3xl border border-border shadow-subtle">
              <h3 className="text-lg font-bold mb-6 flex items-center">
                <div className="w-8 h-8 bg-card rounded-lg flex items-center justify-center mr-3 text-primary border border-border">2</div>
                Payment Method
              </h3>
              <div className="p-6 rounded-2xl border-2 border-accent bg-accent/5 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-accent rounded-lg text-white mr-4">
                    <CreditCard className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-bold text-primary">Stripe Secure Payment</p>
                    <p className="text-xs text-muted">All major cards supported.</p>
                  </div>
                </div>
                <ShieldCheck className="w-6 h-6 text-accent" />
              </div>
            </section>

            <button
              type="submit"
              disabled={checkoutMutation.isPending}
              className="btn-primary w-full h-14 text-base shadow-xl shadow-primary/20"
            >
              {checkoutMutation.isPending ? 'Connecting to Stripe...' : 'Complete Purchase'}
              {!checkoutMutation.isPending && <Lock className="w-4 h-4 ml-3" />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
