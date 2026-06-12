import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  return (
    <div>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-neutral-900">Create Account</h1>
        <p className="mt-2 text-sm text-neutral-600">Join to start managing your portfolio</p>
      </div>
      <RegisterForm />
      <p className="mt-6 text-center text-sm text-neutral-600">
        Already have an account?{' '}
        <a href="/login" className="font-semibold text-primary-600 hover:text-primary-700 transition-colors">
          Sign in
        </a>
      </p>
    </div>
  );
}
