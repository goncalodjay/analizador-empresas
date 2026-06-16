import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-neutral-900">Sign In</h1>
        <p className="mt-2 text-sm text-neutral-600">Access your investment portfolio and analytics</p>
      </div>
      <LoginForm />
      <p className="mt-6 text-center text-sm text-neutral-600">
        Don't have an account?{' '}
        <a href="/register" className="font-semibold text-primary-600 hover:text-primary-700 transition-colors">
          Sign up
        </a>
      </p>
    </div>
  );
}
