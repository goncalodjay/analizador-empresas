'use client';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export function TopBar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <h1 className="text-lg font-semibold text-gray-900">Stock Analyzer</h1>
      <div className="flex items-center gap-4">
        {user && <span className="text-sm text-gray-600">{user.email}</span>}
        <button
          onClick={handleLogout}
          className="rounded-md bg-red-500 px-3 py-1.5 text-sm text-white hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
