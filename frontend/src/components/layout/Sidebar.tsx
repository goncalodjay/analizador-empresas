'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/strategy', label: 'Strategy' },
  { href: '/analysis', label: 'Analysis' },
  { href: '/settings', label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <>
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="fixed left-4 top-4 z-50 rounded-md bg-gray-800 p-2 text-white lg:hidden"
      >
        {collapsed ? '☰' : '✕'}
      </button>
      <aside
        className={`fixed left-0 top-0 z-40 h-full w-64 transform bg-gray-800 text-white transition-transform ${
          collapsed ? '-translate-x-full' : 'translate-x-0'
        } lg:translate-x-0`}
      >
        <div className="flex h-16 items-center justify-center border-b border-gray-700">
          <span className="text-xl font-bold">📈 Analyzer</span>
        </div>
        <nav className="mt-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-6 py-3 text-sm transition-colors hover:bg-gray-700 ${
                pathname === item.href ? 'bg-gray-700 font-medium' : ''
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
