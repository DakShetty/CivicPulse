import React, { useState } from 'react';
import { api } from '../api/client';
import { User, UserRole } from '../types';
import {
  Activity,
  Shield,
  HardHat,
  User as UserIcon,
  Lock,
  Mail,
  UserCheck,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (user: User, token: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [selectedRole, setSelectedRole] = useState<'reporter' | 'field_worker'>('reporter');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);
    setLoading(true);

    try {
      const res = await api.login(email, password);
      localStorage.setItem('civicpulse_token', res.token);
      onLoginSuccess(res.user, res.token);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessNotice(null);
    setLoading(true);

    try {
      const res = await api.register(displayName, email, password, selectedRole);

      if (res.pending_approval) {
        setSuccessNotice(
          'Worker account registered successfully! Your account is pending administrator approval before you can log in.'
        );
        setMode('login');
        setPassword('');
      } else if (res.token && res.user) {
        localStorage.setItem('civicpulse_token', res.token);
        onLoginSuccess(res.user, res.token);
      } else {
        setSuccessNotice('Account created successfully! Please sign in.');
        setMode('login');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemoLogin = async (demoEmail: string, demoPass: string) => {
    setError(null);
    setSuccessNotice(null);
    setEmail(demoEmail);
    setPassword(demoPass);
    setLoading(true);

    try {
      const res = await api.login(demoEmail, demoPass);
      localStorage.setItem('civicpulse_token', res.token);
      onLoginSuccess(res.user, res.token);
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        {/* Brand Header */}
        <div className="text-center">
          <div className="inline-flex w-12 h-12 rounded-2xl bg-teal-500 items-center justify-center shadow-lg shadow-teal-500/30 mb-3">
            <Activity className="w-7 h-7 text-slate-950 stroke-[2.5]" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Civic<span className="text-teal-600">Pulse</span> Portal
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Role-Based Civic Infrastructure & Operations Management
          </p>
        </div>

        {/* Tab Selector */}
        <div className="bg-slate-200/80 p-1 rounded-xl flex">
          <button
            type="button"
            onClick={() => {
              setMode('login');
              setError(null);
              setSuccessNotice(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
              mode === 'login'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('register');
              setError(null);
              setSuccessNotice(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
              mode === 'register'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Register Account
          </button>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successNotice && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{successNotice}</span>
          </div>
        )}

        {/* Form Container */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-5">
          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@civicpulse.org"
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-teal-600 text-white font-bold text-sm shadow-md hover:bg-teal-700 disabled:opacity-50 transition"
              >
                {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Full Display Name
                </label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="e.g. Alex Rivera"
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@civicpulse.org"
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Password (min 6 characters)
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              {/* Role Selection */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                  Account Type *
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectedRole('reporter')}
                    className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                      selectedRole === 'reporter'
                        ? 'border-teal-500 bg-teal-50/70 ring-1 ring-teal-500'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
                      <UserIcon className="w-3.5 h-3.5 text-teal-600" />
                      Citizen User
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      Immediate access to report and track local issues.
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedRole('field_worker')}
                    className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                      selectedRole === 'field_worker'
                        ? 'border-amber-500 bg-amber-50/70 ring-1 ring-amber-500'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
                      <HardHat className="w-3.5 h-3.5 text-amber-600" />
                      Field Worker
                    </div>
                    <div className="text-[10px] text-amber-700 font-semibold mt-1">
                      Requires Admin approval before first sign-in.
                    </div>
                  </button>
                </div>
              </div>

              {/* Security Policy Alert */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-[11px] text-slate-600 flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Admin Security:</strong> Administrator accounts cannot be self-registered and must be provisioned securely by an existing Municipal Admin.
                </span>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-teal-600 text-white font-bold text-sm shadow-md hover:bg-teal-700 disabled:opacity-50 transition"
              >
                {loading ? 'Creating account...' : 'Create Account'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
