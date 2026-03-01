import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowRight, Lock } from 'lucide-react';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In this demo, we don't wire a real email backend.
    setSubmitted(true);
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-[400px]">
        <div className="flex flex-col items-center mb-10">
          <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center mb-4">
            <Lock className="w-6 h-6 text-accent" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-primary mb-2">
            Forgot Password
          </h1>
          <p className="text-muted text-sm text-center">
            Enter your email address and we'll show a confirmation message. In this demo, emails are not actually sent.
          </p>
        </div>

        {submitted ? (
          <div className="bg-success/5 border border-success/20 rounded-2xl p-4 text-sm text-success mb-6">
            If an account exists for <span className="font-semibold">{email}</span>, you’ll receive a password reset link shortly.
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative group">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
            <input
              type="email"
              required
              placeholder="Email address"
              className="input-field pl-10 bg-white"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary w-full h-11 text-sm shadow-xl shadow-primary/10"
          >
            Send reset link
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-muted">
          Remember your password?{' '}
          <Link to="/login" className="text-primary font-bold hover:underline">
            Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};

export default ForgotPassword;

