import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md">
        <h1 className="mb-6 text-center text-2xl font-bold">Sign In</h1>
        <LoginForm />
      </div>
    </div>
  );
}
