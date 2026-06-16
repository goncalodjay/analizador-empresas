'use client';
import { useState } from 'react';
import { apiFetch } from '@/lib/api';

interface IOLSetupFormProps {
  onSuccess: () => void;
}

export function IOLSetupForm({ onSuccess }: IOLSetupFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiFetch('/iol/setup', {
        method: 'POST',
        body: JSON.stringify({
          iol_username: username,
          iol_password: password,
        }),
      });
      setUsername('');
      setPassword('');
      onSuccess();
    } catch (err) {
      setError(
        err instanceof Error && err.message.includes('401')
          ? 'Invalid IOL credentials. Please check your username and password.'
          : 'Failed to connect IOL account. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-md border border-neutral-200 bg-neutral-50 p-6">
      <h2 className="mb-4 text-lg font-semibold text-neutral-900">Connect IOL Account</h2>
      <p className="mb-4 text-sm text-neutral-600">
        Your IOL credentials are encrypted and stored securely. Your password is never stored in plain text.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="iol-username" className="block text-sm font-medium text-neutral-700 mb-1">
            IOL Username
          </label>
          <input
            id="iol-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading}
            className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-600 focus:ring-1 focus:ring-primary-600 disabled:bg-neutral-100"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label htmlFor="iol-password" className="block text-sm font-medium text-neutral-700 mb-1">
            IOL Password
          </label>
          <input
            id="iol-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
            className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-600 focus:ring-1 focus:ring-primary-600 disabled:bg-neutral-100"
          />
        </div>

        {error && <p className="text-sm text-error">{error}</p>}

        <button
          type="submit"
          disabled={loading || !username || !password}
          className="w-full rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-neutral-0 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Connecting...' : 'Connect IOL Account'}
        </button>
      </form>
    </div>
  );
}
