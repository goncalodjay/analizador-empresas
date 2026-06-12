'use client';
import { useAuth } from '@/lib/auth-context';

export default function DashboardPage() {
  const { user } = useAuth();
  return (
    <div>
      <h1 className="text-2xl font-bold text-neutral-900">Dashboard</h1>
      {user && <p className="mt-2 text-neutral-600">Welcome, {user.email}</p>}
    </div>
  );
}
