'use client';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useRef, useEffect } from 'react';

export function Header() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    }

    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showMenu]);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-neutral-200 bg-neutral-0 px-6 shadow-sm">
      <h1 className="text-lg font-semibold text-neutral-900">Stock Analyzer</h1>
      <div className="flex items-center gap-4">
        {user && <span className="text-sm text-neutral-600">{user.email}</span>}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-sm font-semibold text-neutral-0 hover:bg-primary-700 transition-colors"
            title={user?.email || 'User menu'}
            aria-label="User menu"
          >
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </button>
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-md border border-neutral-200 bg-neutral-0 shadow-lg">
              <div className="border-b border-neutral-200 px-4 py-3">
                <p className="text-sm font-semibold text-neutral-900">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="block w-full rounded-b-md px-4 py-2.5 text-left text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
