import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRightIcon, EyeIcon } from '@heroicons/react/24/outline';

export default function SignIn() {
  const navigate = useNavigate();

  const handleSignIn = (e) => {
    e.preventDefault();
    navigate('/app');
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-neutral-950 text-white font-sans selection:bg-primary-500/30">
      
      {/* Left Side: Editorial Brand Message */}
      <section className="hidden md:flex md:w-1/2 lg:w-3/5 bg-neutral-950 relative overflow-hidden flex-col justify-between p-16 border-r border-white/5">
        <div className="absolute inset-0 z-0">
          <div className="absolute top-0 left-0 w-full h-[80%] bg-gradient-to-br from-indigo-600/20 via-primary-900/10 to-transparent blur-3xl opacity-60"></div>
          <div className="absolute bottom-0 right-0 w-full h-[60%] bg-gradient-to-tl from-purple-600/10 to-transparent blur-3xl opacity-40"></div>
          
          {/* Abstract Grid Graphic Overlay */}
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03]"></div>
          
          {/* Abstract Architecture Orbs */}
          <div className="absolute top-[40%] left-[20%] w-[15vw] h-[15vw] min-w-[200px] border border-white/5 rounded-full blur-md opacity-30"></div>
        </div>

        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3 mb-16 group w-max">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-indigo-600 rounded-lg flex items-center justify-center shadow-[0_0_20px_rgba(79,70,229,0.4)] group-hover:shadow-[0_0_30px_rgba(79,70,229,0.6)] transition-all">
              <span className="text-white font-bold text-lg">$</span>
            </div>
            <span className="text-2xl font-bold tracking-tight text-white group-hover:text-primary-400 transition-colors">Lumen Ledger</span>
          </Link>
          
          <h1 className="text-5xl lg:text-7xl font-extrabold text-white tracking-tighter leading-[1.1] mb-8">
            Access Your <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-indigo-300">Architecture.</span>
          </h1>
          <p className="text-xl text-neutral-400 max-w-lg leading-relaxed font-light">
            Welcome back to the command center. Continue building and curating your financial landscape with precision.
          </p>
        </div>

        <div className="relative z-10 flex flex-col gap-8">
          <div className="flex gap-12 items-end">
            <div>
              <div className="text-indigo-400 text-4xl font-bold font-mono tracking-tighter">Zero</div>
              <div className="text-neutral-500 text-xs uppercase tracking-widest mt-1">Latency Reports</div>
            </div>
            <div>
              <div className="text-indigo-400 text-4xl font-bold font-mono tracking-tighter">100%</div>
              <div className="text-neutral-500 text-xs uppercase tracking-widest mt-1">Encrypted Secure</div>
            </div>
          </div>
          <div className="pt-8 border-t border-white/10">
            <p className="text-sm text-neutral-500 italic">"Clarity is the ultimate sophisticated currency."</p>
          </div>
        </div>
      </section>

      {/* Right Side: Sign-in Form */}
      <section className="flex-grow md:w-1/2 lg:w-2/5 flex flex-col justify-center px-8 py-16 lg:px-24 relative overflow-y-auto">
        <div className="max-w-md mx-auto w-full relative z-10">
          
          {/* Mobile Logo */}
          <Link to="/" className="md:hidden flex items-center gap-2 mb-12">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold">$</div>
            <span className="text-xl font-bold tracking-tight text-white">Lumen Ledger</span>
          </Link>

          <div className="mb-10">
            <h2 className="text-3xl font-bold text-white tracking-tight mb-2">Welcome Back</h2>
            <p className="text-neutral-400">Enter your credentials to regain control.</p>
          </div>

          <form onSubmit={handleSignIn} className="space-y-5">
            <div className="space-y-1.5">
              <label className="block text-xs font-bold uppercase tracking-widest text-neutral-500" htmlFor="email">Work Email</label>
              <input 
                id="email" 
                type="email" 
                placeholder="alexander@treasury.gov" 
                className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-primary-500 text-white placeholder:text-neutral-600 transition-all duration-200" 
                required
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="block text-xs font-bold uppercase tracking-widest text-neutral-500" htmlFor="password">Password</label>
                <a href="#" className="text-xs font-bold text-primary-400 hover:text-primary-300">Forgot?</a>
              </div>
              <div className="relative">
                <input 
                  id="password" 
                  type="password" 
                  placeholder="••••••••••••" 
                  className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-primary-500 text-white placeholder:text-neutral-600 transition-all duration-200" 
                  required
                />
                <button type="button" className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-white transition-colors">
                  <EyeIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex items-start gap-3 py-2">
              <div className="flex items-center h-5">
                <input 
                  id="remember" 
                  type="checkbox" 
                  className="h-5 w-5 rounded border border-white/20 bg-white/5 text-primary-500 focus:ring-primary-500 focus:ring-offset-neutral-950" 
                />
              </div>
              <label htmlFor="remember" className="text-sm text-neutral-400 leading-snug">
                Remember my terminal
              </label>
            </div>

            <div className="pt-4">
              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-primary-600 to-indigo-600 text-white py-4 rounded-xl font-bold shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] transition-all duration-200 flex items-center justify-center gap-2 hover:-translate-y-0.5"
              >
                Sign In to Dashboard
                <ArrowRightIcon className="w-5 h-5" />
              </button>
            </div>
          </form>

          <div className="mt-10 text-center">
            <p className="text-neutral-500 text-sm">
              New to the ecosystem? 
              <Link to="/signup" className="text-primary-400 font-bold hover:underline ml-1">Establish your architecture</Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
