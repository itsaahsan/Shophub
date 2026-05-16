import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { subscriptionApi } from '../services/api';
import { Check, Zap, Shield, Crown } from 'lucide-react';
import { SubscriptionPlan } from '../types';
import toast from 'react-hot-toast';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';

const Plans: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const { data: plans, isLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: () => subscriptionApi.listPlans().then(res => res.data),
  });

  const checkoutMutation = useMutation({
    mutationFn: (planId: string) => subscriptionApi.createCheckout(planId),
    onSuccess: (res) => {
      window.location.href = res.data.url;
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to start checkout');
    }
  });

  const handleSubscribe = (planId: string) => {
    if (!user) {
      toast.error('Please login to subscribe');
      navigate('/login?redirect=/plans');
      return;
    }
    checkoutMutation.mutate(planId);
  };

  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Loading plans...</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-20 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold text-primary mb-4 tracking-tight">
            Choose the Perfect <span className="text-accent">Plan</span>
          </h1>
          <p className="text-lg text-muted max-w-2xl mx-auto">
            Unlock exclusive benefits, faster shipping, and premium support with our Shophub membership plans.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans?.map((plan: SubscriptionPlan) => (
            <div 
              key={plan.id} 
              className={`bg-white rounded-[2.5rem] p-10 border-2 transition-all duration-300 hover:shadow-2xl relative overflow-hidden flex flex-col ${
                plan.name.toLowerCase().includes('pro') ? 'border-accent ring-4 ring-accent/10 scale-105 z-10' : 'border-border'
              }`}
            >
              {plan.name.toLowerCase().includes('pro') && (
                <div className="absolute top-5 right-5">
                  <span className="bg-accent text-white text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-8">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${
                  plan.name.toLowerCase().includes('pro') ? 'bg-accent/10 text-accent' : 'bg-gray-100 text-gray-500'
                }`}>
                  {plan.name.toLowerCase().includes('pro') ? <Crown className="w-8 h-8" /> : <Zap className="w-8 h-8" />}
                </div>
                <h3 className="text-2xl font-bold text-primary mb-2">{plan.name}</h3>
                <p className="text-muted text-sm leading-relaxed">{plan.description}</p>
              </div>

              <div className="mb-8">
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-extrabold text-primary">${plan.price}</span>
                  <span className="text-muted font-semibold">/{plan.billing_cycle}</span>
                </div>
              </div>

              <div className="space-y-4 mb-10 flex-grow">
                {plan.features.map((feature, idx) => (
                  <div key={idx} className="flex items-start space-x-3">
                    <div className="mt-1 flex-shrink-0 w-5 h-5 rounded-full bg-success/10 text-success flex items-center justify-center">
                      <Check className="w-3 h-3" />
                    </div>
                    <span className="text-sm text-primary font-medium">{feature}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={checkoutMutation.isPending}
                className={`w-full py-4 rounded-2xl font-bold text-sm transition-all duration-300 ${
                  plan.name.toLowerCase().includes('pro')
                    ? 'bg-accent text-white hover:bg-primary shadow-lg shadow-accent/20'
                    : 'bg-primary text-white hover:bg-accent'
                } disabled:opacity-50`}
              >
                {checkoutMutation.isPending ? 'Processing...' : `Get ${plan.name}`}
              </button>
            </div>
          ))}

          {/* Fallback for guest if no plans or just to show a free tier if not in DB */}
          {plans?.length === 0 && (
             <div className="col-span-full text-center py-20 bg-white rounded-[2.5rem] border-2 border-dashed border-border">
                <Shield className="w-16 h-16 text-muted mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-primary">No plans available right now.</h2>
                <p className="text-muted">Check back later for our premium offerings.</p>
             </div>
          )}
        </div>

        <div className="mt-20 bg-primary rounded-[3rem] p-12 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent/20 rounded-full -mr-32 -mt-32 blur-3xl"></div>
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="max-w-lg">
              <h2 className="text-3xl font-extrabold mb-4">Enterprise Solutions?</h2>
              <p className="text-indigo-100 leading-relaxed">
                Looking for a custom plan for your large-scale business? We offer tailored solutions with dedicated account managers and API access.
              </p>
            </div>
            <button className="bg-white text-primary px-10 py-4 rounded-2xl font-bold hover:bg-accent hover:text-white transition-all whitespace-nowrap">
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Plans;
