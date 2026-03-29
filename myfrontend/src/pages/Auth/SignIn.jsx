import React from 'react';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Link } from 'react-router-dom';

export default function SignIn() {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center text-white font-bold text-xl mb-4 shadow-sm">
            $
          </div>
          <h1 className="text-2xl font-bold text-neutral-900">Welcome back</h1>
          <p className="text-neutral-500 mt-2">Enter your details to sign in to your account</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4 pt-4">
            <Input label="Email address" type="email" placeholder="name@yourcompany.com" />
            <Input label="Password" type="password" placeholder="••••••••" />
            
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500" />
                <span className="text-sm text-neutral-600">Remember me</span>
              </label>
              <a href="#" className="text-sm font-medium text-primary-600 hover:text-primary-700">Forgot password?</a>
            </div>
            
            <Button className="w-full" type="button">Sign In</Button>
            
            <div className="text-center mt-4 text-sm text-neutral-600">
              Don't have an account?{' '}
              <Link to="/signup" className="font-medium text-primary-600 hover:text-primary-700 transition-colors">
                Sign up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
