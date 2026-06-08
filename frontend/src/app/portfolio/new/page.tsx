import { PositionForm } from '@/components/portfolio/PositionForm';

export default function NewPositionPage() {
  return (
    <div className="p-6">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Add Position</h1>
      <div className="max-w-lg">
        <PositionForm />
      </div>
    </div>
  );
}
