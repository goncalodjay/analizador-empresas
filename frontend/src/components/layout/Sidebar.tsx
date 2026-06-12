'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/portfolio', label: 'Portfolio', icon: '💼' },
  { href: '/analysis', label: 'Analysis', icon: '📈' },
  { href: '/watchlists', label: 'Watchlist', icon: '👁️' },
  { href: '/strategy', label: 'Strategies', icon: '🎯' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) => {
    // Strip route group from pathname for comparison
    const cleanPathname = pathname.replace(/^\/(auth|dashboard)/, '');
    return cleanPathname.startsWith(href);
  };

  return (
    <>
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="fixed left-4 top-4 z-50 rounded-md bg-neutral-800 p-2 text-neutral-0 lg:hidden"
        aria-label="Toggle sidebar"
      >
        {collapsed ? '☰' : '✕'}
      </button>
      <aside
        className={`fixed left-0 top-0 z-40 h-screen w-64 transform bg-neutral-900 text-neutral-0 transition-transform duration-300 ${
          collapsed ? '-translate-x-full' : 'translate-x-0'
        } lg:translate-x-0`}
      >
        <div className="flex h-16 items-center gap-3 border-b border-neutral-700 px-6">
          <span className="text-2xl">📈</span>
          <span className="text-lg font-bold">Analyzer</span>
        </div>
        <nav className="flex flex-col gap-1 p-4">
          {navItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-4 py-2.5 text-sm font-medium transition-colors ${
                  active
                    ? 'bg-primary-600 text-neutral-0'
                    : 'text-neutral-300 hover:bg-neutral-800 hover:text-neutral-0'
                }`}
                title={item.label}
              >
                <span className="text-base">{item.icon}</span>
                <span className="hidden lg:inline">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
