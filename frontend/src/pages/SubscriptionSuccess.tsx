import React, { useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import confetti from 'canvas-confetti';

const SubscriptionSuccess: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Fire confetti!
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#6366f1', '#a855f7', '#ec4899']
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-[2.5rem] shadow-2xl border border-border text-center">
        <div>
          <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-success/10 mb-8 animate-bounce">
            <CheckCircle className="h-12 w-12 text-success" />
          </div>
          <h2 className="text-3xl font-extrabold text-primary mb-2">Welcome to the Club!</h2>
          <p className="text-muted font-medium">
            Your subscription was successful. You now have access to all premium features.
          </p>
        </div>

        <div className="bg-gray-50 rounded-2xl p-6 text-left space-y-4">
          <div className="flex items-center space-x-3 text-sm text-primary font-bold">
            <Zap className="w-4 h-4 text-accent" />
            <span>Faster Shipping Activated</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-primary font-bold">
            <ShieldCheck className="w-4 h-4 text-accent" />
            <span>Priority Support Enabled</span>
          </div>
        </div>

        <div className="pt-4 space-y-4">
          <Link
            to="/account"
            className="w-full flex items-center justify-center px-8 py-4 border border-transparent text-sm font-bold rounded-2xl text-white bg-primary hover:bg-accent transition-all shadow-lg"
          >
            Manage Subscription
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
          <Link
            to="/"
            className="w-full flex items-center justify-center px-8 py-4 border border-border text-sm font-bold rounded-2xl text-primary bg-white hover:bg-gray-50 transition-all"
          >
            Continue Shopping
          </Link>
        </div>

        {sessionId && (
          <p className="text-[10px] text-muted uppercase tracking-widest font-bold">
            Order Ref: {sessionId.substring(0, 15)}...
          </p>
        )}
      </div>
    </div>
  );
};

export default SubscriptionSuccess;
