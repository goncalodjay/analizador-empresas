'use client';
import { useRouter } from 'next/navigation';
import { StrategyForm } from '@/components/strategy/StrategyForm';

export default function NewStrategyPage() {
  const router = useRouter();

  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">New Strategy</h1>
      <div className="max-w-2xl">
        <StrategyForm mode="create" onSuccess={() => router.push('/strategy')} />
      </div>
    </div>
  );
}
