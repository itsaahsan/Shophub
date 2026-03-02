import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { useAuthStore } from '../stores/authStore';
import toast from 'react-hot-toast';
import { ArrowRight, Lock, Mail } from 'lucide-react';

const Login: React.FC = () => {
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
      const { data } = await api.post('/auth/login', { email, password });
      setUser(data);
      toast.success('Welcome back!');
      navigate(redirectParam || '/', { replace: true });
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      let message = 'Login failed';
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
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-[400px]">
        {/* Logo/Icon */}
        <div className="flex flex-col items-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tighter text-primary">Shophub</h1>
          <p className="text-muted text-sm mt-2 font-medium">Welcome back to your account</p>
        </div>

        <div className="space-y-6">
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
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-accent transition-colors" />
              <input
                type="password"
                required
                placeholder="Password"
                className="input-field pl-10 bg-white"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            
            <div className="flex items-center justify-between px-1">
              <label className="flex items-center space-x-2 cursor-pointer group">
                <input type="checkbox" className="w-4 h-4 rounded border-border text-accent focus:ring-accent transition-all" />
                <span className="text-xs text-muted group-hover:text-primary transition-colors">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-xs font-semibold text-accent hover:underline">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full h-11 text-sm shadow-xl shadow-primary/10"
            >
              {loading ? 'Signing in...' : 'Sign In'}
              {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
            </button>
          </form>
        </div>

        <p className="mt-10 text-center text-sm text-muted">
          Don't have an account? <Link to="/signup" className="text-primary font-bold hover:underline">Create an account</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
