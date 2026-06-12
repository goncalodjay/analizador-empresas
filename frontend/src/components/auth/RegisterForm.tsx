'use client';
import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

export function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      router.push('/login');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md bg-error/10 border border-error/20 p-3 text-sm text-error">
          {error}
        </div>
      )}
      <div>
        <label className="block text-sm font-semibold text-neutral-900 mb-1">Email address</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm bg-neutral-0 focus:outline-none focus:ring-1 focus:ring-primary-600 focus:border-primary-600 transition-colors"
          required
          aria-label="Email address"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-neutral-900 mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm bg-neutral-0 focus:outline-none focus:ring-1 focus:ring-primary-600 focus:border-primary-600 transition-colors"
          required
          aria-label="Password"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold text-neutral-900 mb-1">Confirm Password</label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm bg-neutral-0 focus:outline-none focus:ring-1 focus:ring-primary-600 focus:border-primary-600 transition-colors"
          required
          aria-label="Confirm password"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-neutral-0 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Creating account...' : 'Create Account'}
      </button>
    </form>
  );
}
