'use client';

import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  // While loading, render a blank container
  if (loading) {
    return <div className="min-h-screen bg-neutral-50" />;
  }

  // If not authenticated, redirect and render blank container
  if (!user) {
    router.push('/login');
    return <div className="min-h-screen bg-neutral-50" />;
  }

  return (
    <div className="flex min-h-screen bg-neutral-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex flex-1 flex-col lg:ml-64">
        {/* Header */}
        <Header />

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="px-6 py-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
