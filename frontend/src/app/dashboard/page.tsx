'use client';
import { useAuth } from '@/lib/auth-context';

export default function DashboardPage() {
  const { user } = useAuth();
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      {user && <p className="mt-2 text-gray-600">Welcome, {user.email}</p>}
    </div>
  );
}
