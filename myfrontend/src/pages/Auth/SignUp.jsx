import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRightIcon, EyeIcon } from '@heroicons/react/24/outline';

export default function SignUp() {
  const navigate = useNavigate();

  const handleSignUp = (e) => {
    e.preventDefault();
    navigate('/app');
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-neutral-950 text-white font-sans selection:bg-primary-500/30">
      
      {/* Left Side: Editorial Brand Message */}
      <section className="hidden md:flex md:w-1/2 lg:w-3/5 bg-neutral-950 relative overflow-hidden flex-col justify-between p-16 border-r border-white/5">
        <div className="absolute inset-0 z-0">
          <div className="absolute top-0 right-0 w-full h-[80%] bg-gradient-to-dl from-primary-600/20 via-primary-900/10 to-transparent blur-3xl opacity-60"></div>
          <div className="absolute bottom-0 left-0 w-full h-[60%] bg-gradient-to-tr from-emerald-600/10 to-transparent blur-3xl opacity-40"></div>
          
          {/* Abstract Grid Graphic Overlay */}
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03]"></div>
          
          <div className="absolute top-[20%] right-[10%] w-[30vw] h-[30vw] min-w-[300px] border border-white/5 rounded-full blur-sm opacity-20"></div>
          <div className="absolute top-[30%] right-[20%] w-[15vw] h-[15vw] min-w-[150px] border border-primary-500/20 rounded-full blur-sm opacity-30"></div>
        </div>

        <div className="relative z-10">
          <Link to="/" className="flex items-center gap-3 mb-16 group w-max">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)] group-hover:shadow-[0_0_30px_rgba(37,99,235,0.6)] transition-all">
              <span className="text-white font-bold text-lg">$</span>
            </div>
            <span className="text-2xl font-bold tracking-tight text-white group-hover:text-primary-400 transition-colors">Lumen Ledger</span>
          </Link>
          
          <h1 className="text-5xl lg:text-7xl font-extrabold text-white tracking-tighter leading-[1.1] mb-8">
            The Financial <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-200">Architect.</span>
          </h1>
          <p className="text-xl text-neutral-400 max-w-lg leading-relaxed font-light">
            Move beyond the simple ledger. Create a breathable landscape of your fiscal health with editorial precision and structural clarity.
          </p>
        </div>

        <div className="relative z-10 flex flex-col gap-8">
          <div className="flex gap-12 items-end">
            <div>
              <div className="text-emerald-400 text-4xl font-bold font-mono tracking-tighter">99.9%</div>
              <div className="text-neutral-500 text-xs uppercase tracking-widest mt-1">Data Accuracy</div>
            </div>
            <div>
              <div className="text-emerald-400 text-4xl font-bold font-mono tracking-tighter">$4.2B+</div>
              <div className="text-neutral-500 text-xs uppercase tracking-widest mt-1">Assets Managed</div>
            </div>
          </div>
          <div className="pt-8 border-t border-white/10">
            <p className="text-sm text-neutral-500 italic">"Precision is the foundation of trust."</p>
          </div>
        </div>
      </section>

      {/* Right Side: Sign-up Form */}
      <section className="flex-grow md:w-1/2 lg:w-2/5 flex flex-col justify-center px-8 py-16 lg:px-24 relative overflow-y-auto">
        <div className="max-w-md mx-auto w-full relative z-10">
          
          {/* Mobile Logo */}
          <Link to="/" className="md:hidden flex items-center gap-2 mb-12">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold">$</div>
            <span className="text-xl font-bold tracking-tight text-white">Lumen Ledger</span>
          </Link>

          <div className="mb-10">
            <h2 className="text-3xl font-bold text-white tracking-tight mb-2">Start Your Architecture</h2>
            <p className="text-neutral-400">Begin your journey towards total financial clarity.</p>
          </div>

          <form onSubmit={handleSignUp} className="space-y-5">
            <div className="space-y-1.5">
              <label className="block text-xs font-bold uppercase tracking-widest text-neutral-500" htmlFor="full_name">Full Name</label>
              <input 
                id="full_name" 
                type="text" 
                placeholder="Alexander Hamilton" 
                className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-primary-500 text-white placeholder:text-neutral-600 transition-all duration-200" 
                required
              />
            </div>

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
              <label className="block text-xs font-bold uppercase tracking-widest text-neutral-500" htmlFor="company">Company Name</label>
              <input 
                id="company" 
                type="text" 
                placeholder="The Treasury Inc." 
                className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-primary-500 text-white placeholder:text-neutral-600 transition-all duration-200" 
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold uppercase tracking-widest text-neutral-500" htmlFor="password">Password</label>
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
                  id="terms" 
                  type="checkbox" 
                  className="h-5 w-5 rounded border border-white/20 bg-white/5 text-primary-500 focus:ring-primary-500 focus:ring-offset-neutral-950" 
                  required
                />
              </div>
              <label htmlFor="terms" className="text-sm text-neutral-400 leading-snug">
                I agree to the <a href="#" className="text-primary-400 font-bold hover:underline">Terms of Service</a> and <a href="#" className="text-primary-400 font-bold hover:underline">Privacy Policy</a>.
              </label>
            </div>

            <div className="pt-2">
              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-primary-600 to-indigo-600 text-white py-4 rounded-xl font-bold shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] transition-all duration-200 flex items-center justify-center gap-2 hover:-translate-y-0.5"
              >
                Create Account
                <ArrowRightIcon className="w-5 h-5" />
              </button>
            </div>
          </form>

          <div className="mt-10 text-center">
            <p className="text-neutral-500 text-sm">
              Already have an architecture? 
              <Link to="/signin" className="text-primary-400 font-bold hover:underline ml-1">Sign in instead</Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
