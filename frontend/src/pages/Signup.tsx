import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { useAuthStore } from '../stores/authStore';
import toast from 'react-hot-toast';
import { ArrowRight, Lock, Mail, User } from 'lucide-react';

const Signup: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const setUser = useAuthStore((state) => state.setUser);
  const redirectParam = new URLSearchParams(location.search).get('redirect');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/auth/signup', { name, email, password });
      setUser(data);
      toast.success('Account created! Welcome to shophub.');
      navigate(redirectParam || '/', { replace: true });
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      let message = 'Signup failed';
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail.map((e: any) => e.msg).join(', ');
      }
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-[450px]">
        {/* Logo/Icon */}
        <div className="flex flex-col items-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tighter text-primary">shophub</h1>
          <p className="text-muted text-sm mt-2 text-center max-w-[300px]">Create an account to unlock AI-powered recommendations.</p>
        </div>

        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="text"
                required
                placeholder="Full Name"
                className="input-field pl-10"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="relative group">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="email"
                required
                placeholder="Email address"
                className="input-field pl-10"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="password"
                required
                minLength={6}
                maxLength={72}
                placeholder="Password (6–72 characters)"
                className="input-field pl-10"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            
            <div className="flex items-start space-x-2 py-2 px-1">
              <input type="checkbox" required className="mt-1 w-4 h-4 rounded border-border text-accent focus:ring-accent transition-all" />
              <span className="text-[11px] text-muted leading-relaxed">
                I agree to the{' '}
                <Link to="/terms" className="font-bold text-primary hover:underline">Terms of Service</Link>{' '}
                and{' '}
                <Link to="/privacy" className="font-bold text-primary hover:underline">Privacy Policy</Link>.
              </span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full h-12 text-sm shadow-xl shadow-primary/10"
            >
              {loading ? 'Creating account...' : 'Create Account'}
              {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
            </button>
          </form>
        </div>

        <p className="mt-10 text-center text-sm text-muted">
          Already a member? <Link to="/login" className="text-primary font-bold hover:underline">Sign In instead</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
