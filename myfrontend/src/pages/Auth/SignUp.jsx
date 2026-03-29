import React from 'react';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Link } from 'react-router-dom';

export default function SignUp() {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center text-white font-bold text-xl mb-4 shadow-sm">
            $
          </div>
          <h1 className="text-2xl font-bold text-neutral-900">Create an account</h1>
          <p className="text-neutral-500 mt-2">Start tracking your expenses effectively</p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4 pt-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="First name" placeholder="John" />
              <Input label="Last name" placeholder="Doe" />
            </div>
            <Input label="Email address" type="email" placeholder="name@yourcompany.com" />
            <Input label="Password" type="password" placeholder="••••••••" />
            
            <Button className="w-full" type="button">Create Account</Button>
            
            <div className="text-center mt-4 text-sm text-neutral-600">
              Already have an account?{' '}
              <Link to="/signin" className="font-medium text-primary-600 hover:text-primary-700 transition-colors">
                Sign in
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
