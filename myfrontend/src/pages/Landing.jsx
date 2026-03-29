import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  ChartBarIcon, 
  WalletIcon, 
  UserGroupIcon, 
  ChevronRightIcon,
  SparklesIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

const Landing = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-primary-500/30 overflow-hidden relative">
      
      {/* Background Ambient Glows */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] rounded-full bg-primary-600/20 blur-[120px]" />
        <div className="absolute top-[40%] -right-[10%] w-[50%] h-[50%] rounded-full bg-indigo-600/10 blur-[120px]" />
        <div className="absolute -bottom-[20%] left-[20%] w-[60%] h-[60%] rounded-full bg-emerald-600/10 blur-[120px]" />
      </div>

      {/* Glassmorphic Navbar */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-neutral-950/70 backdrop-blur-2xl border-b border-white/5 shadow-2xl py-4' : 'bg-transparent py-6'}`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-12 flex justify-between items-center">
          <div className="flex items-center gap-2 group cursor-pointer">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] group-hover:shadow-[0_0_30px_rgba(37,99,235,0.6)] transition-all">
              $
            </div>
            <span className="text-xl font-bold tracking-tight text-white group-hover:text-primary-400 transition-colors">
              Lumen Ledger
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#product" className="text-white/70 hover:text-white transition-colors">Product</a>
            <a href="#features" className="text-white/70 hover:text-white transition-colors">Features</a>
            <a href="#testimonials" className="text-white/70 hover:text-white transition-colors">Wall of Love</a>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/signin" className="hidden md:block px-5 py-2.5 text-sm font-medium text-white/80 hover:text-white transition-colors">Login</Link>
            <Link to="/signup" className="px-6 py-2.5 rounded-full text-sm font-bold bg-white text-neutral-950 hover:bg-neutral-200 transition-all hover:scale-105 active:scale-95 flex items-center gap-2">
              Get Started <ChevronRightIcon className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10">
        
        {/* Massive Hero Section */}
        <section className="pt-40 pb-20 md:pt-52 md:pb-32 px-6 flex flex-col items-center text-center max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary-500/30 bg-primary-500/10 text-primary-400 text-xs font-bold uppercase tracking-widest mb-10 shadow-[0_0_20px_rgba(37,99,235,0.15)] ring-1 ring-inset ring-primary-500/20 backdrop-blur-md">
            <SparklesIcon className="w-4 h-4" />
            <span>Lumen 2.0 is Here</span>
          </div>
          <h1 className="text-6xl md:text-8xl font-extrabold tracking-tighter mb-8 leading-[1.05]">
            Editorial Precision for <br className="hidden md:block"/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 via-indigo-400 to-emerald-400 animate-gradient-x">
              Financial Clarity.
            </span>
          </h1>
          <p className="max-w-2xl text-lg md:text-xl text-neutral-400 mb-12 font-light leading-relaxed">
            Treat your data like a beautifully structured landscape. Lumen Ledger transforms cluttered ledgers into a breathable, high-fidelity financial architecture.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link to="/signup" className="px-8 py-4 rounded-full font-bold text-lg bg-gradient-to-r from-primary-500 to-indigo-600 shadow-[0_0_40px_rgba(79,70,229,0.4)] hover:shadow-[0_0_60px_rgba(79,70,229,0.6)] transition-all hover:-translate-y-1">
              Start Your Architecture
            </Link>
            <Link to="/app" className="px-8 py-4 rounded-full font-bold text-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all hover:-translate-y-1 flex items-center justify-center gap-2 backdrop-blur-md">
              View Live Demo
            </Link>
          </div>
        </section>

        {/* Abstract Floating Mockup */}
        <section className="px-6 pb-32 md:pb-48 -mt-10 relative perspective-normal">
          <div className="max-w-6xl mx-auto relative group">
            <div className="absolute inset-0 bg-gradient-to-b from-primary-500/20 to-transparent blur-3xl opacity-50 group-hover:opacity-70 transition-opacity duration-1000"></div>
            <div className="relative rounded-[2rem] border border-white/10 bg-neutral-900/50 backdrop-blur-xl shadow-2xl overflow-hidden ring-1 ring-white/5 transition-transform duration-700 hover:rotate-2 hover:scale-[1.02]">
              
              {/* Fake Window Controls */}
              <div className="h-12 border-b border-white/5 flex items-center px-6 gap-2 bg-neutral-950/50">
                <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
              </div>
              
              {/* Fake Dashboard Content */}
              <div className="p-8 grid grid-cols-12 gap-6 h-[500px]">
                {/* Sidebar mock */}
                <div className="hidden lg:col-span-2 lg:flex flex-col gap-4 border-r border-white/5 pr-6">
                  <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 mb-8"></div>
                  <div className="h-4 w-24 bg-white/10 rounded-md"></div>
                  <div className="h-4 w-16 bg-white/10 rounded-md"></div>
                  <div className="h-4 w-32 bg-white/5 rounded-md"></div>
                  <div className="h-4 w-20 bg-white/5 rounded-md"></div>
                  <div className="h-4 w-28 bg-white/5 rounded-md mt-auto"></div>
                </div>
                
                {/* Main pane mock */}
                <div className="col-span-12 lg:col-span-10 flex flex-col gap-6">
                  <div className="flex justify-between items-end">
                    <div>
                      <div className="h-3 w-32 bg-primary-400/50 rounded-md mb-3"></div>
                      <div className="h-12 w-64 bg-white/90 rounded-xl"></div>
                    </div>
                    <div className="flex gap-2">
                      <div className="h-10 w-24 bg-white/10 rounded-lg"></div>
                      <div className="h-10 w-10 bg-white/10 rounded-lg"></div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-6 flex-1">
                    <div className="col-span-2 bg-white/5 rounded-2xl border border-white/5 p-6 flex flex-col justify-between relative overflow-hidden">
                      <div className="flex justify-between">
                        <div className="h-5 w-32 bg-white/20 rounded-md"></div>
                        <div className="h-4 w-16 bg-emerald-400/50 rounded-md"></div>
                      </div>
                      <div className="h-32 w-full mt-auto relative flex items-end gap-2">
                        {[40, 60, 45, 80, 55, 90, 75].map((h, i) => (
                           <div key={i} className="flex-1 bg-gradient-to-t from-primary-500/50 to-primary-400/10 rounded-t-sm" style={{ height: `${h}%` }}></div>
                        ))}
                      </div>
                    </div>
                    <div className="col-span-1 bg-white/5 border border-white/5 rounded-2xl p-6 flex flex-col gap-4">
                       <div className="h-5 w-24 bg-white/20 rounded-md mb-2"></div>
                       {[60, 80, 30].map((w, i) => (
                         <div key={i} className="space-y-2">
                           <div className="flex justify-between">
                             <div className="h-3 w-16 bg-white/10 rounded-md"></div>
                             <div className="h-3 w-8 bg-white/10 rounded-md"></div>
                           </div>
                           <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                             <div className={`h-full bg-${i === 0 ? 'primary' : i === 1 ? 'emerald' : 'amber'}-500/80 rounded-full`} style={{ width: `${w}%` }}></div>
                           </div>
                         </div>
                       ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Glass Element */}
            <div className="absolute -bottom-10 -right-10 md:w-80 bg-neutral-900/40 backdrop-blur-3xl p-6 rounded-3xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] z-20 animate-bounce" style={{ animationDuration: '4s' }}>
              <div className="flex flex-col gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                    <SparklesIcon className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold text-sm">Audit Complete</h4>
                    <span className="text-xs text-neutral-400">Zero anomalies detected.</span>
                  </div>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full w-full bg-emerald-400 rounded-full"></div>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Feature Bento Grid */}
        <section id="features" className="py-24 px-6 max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white mb-4">Precision-engineered for Wealth</h2>
            <p className="text-neutral-400 max-w-2xl mx-auto">It's not just a tracker; it's a financial engine designed for maximum clarity.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-2 group relative bg-neutral-900/50 backdrop-blur-lg border border-white/10 p-10 rounded-[2rem] overflow-hidden hover:bg-neutral-800/50 transition-colors">
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-3xl group-hover:bg-primary-500/20 transition-colors"></div>
              <div className="relative z-10 w-14 h-14 bg-primary-500/20 border border-primary-500/30 flex items-center justify-center rounded-2xl mb-6">
                <ChartBarIcon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Real-time Insights</h3>
              <p className="text-neutral-400 leading-relaxed max-w-md">Experience zero-latency financial reporting. Every transaction is mapped to your architectural horizon the moment it occurs.</p>
            </div>
            
            <div className="md:col-span-1 group relative bg-neutral-900/50 backdrop-blur-lg border border-white/10 p-10 rounded-[2rem] overflow-hidden hover:bg-neutral-800/50 transition-colors">
              <div className="relative z-10 w-14 h-14 bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center rounded-2xl mb-6">
                <WalletIcon className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Budget Control</h3>
              <p className="text-neutral-400 leading-relaxed">Granular limits that feel like an extension of your intent.</p>
            </div>

            <div className="md:col-span-1 group relative bg-neutral-900/50 backdrop-blur-lg border border-white/10 p-10 rounded-[2rem] overflow-hidden hover:bg-neutral-800/50 transition-colors">
              <div className="relative z-10 w-14 h-14 bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center rounded-2xl mb-6">
                <UserGroupIcon className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Collaboration</h3>
              <p className="text-neutral-400 leading-relaxed">Multi-user environments with permission-based access.</p>
            </div>

            <div className="md:col-span-2 group relative bg-gradient-to-br from-primary-900/40 to-indigo-900/20 backdrop-blur-lg border border-primary-500/20 p-10 rounded-[2rem] overflow-hidden hover:border-primary-500/40 transition-colors flex items-center justify-between">
              <div className="max-w-md">
                <div className="relative z-10 w-14 h-14 bg-white/10 border border-white/20 flex items-center justify-center rounded-2xl mb-6">
                  <GlobeAltIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Global Architecture</h3>
                <p className="text-neutral-300 leading-relaxed">Multi-currency, timezone agnostic tracking that scales with your ambition across the global plane.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-6 relative mt-16">
          <div className="max-w-6xl mx-auto rounded-[3rem] bg-gradient-to-r from-primary-600 via-indigo-600 to-purple-700 p-12 md:p-24 text-center text-white overflow-hidden relative shadow-[0_0_80px_rgba(79,70,229,0.3)]">
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
            <div className="relative z-10">
              <h2 className="text-4xl md:text-6xl font-extrabold mb-8 tracking-tighter">Ready to curate your wealth?</h2>
              <p className="text-xl text-white/80 mb-12 max-w-xl mx-auto font-light">Join the elite firm of financial architects using Lumen Ledger today.</p>
              <Link to="/signup" className="inline-block bg-white text-primary-600 px-10 py-5 rounded-full font-bold text-lg shadow-2xl hover:scale-105 transition-transform">
                Start Building Free
              </Link>
            </div>
            <div className="absolute -top-32 -right-32 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-black/20 rounded-full blur-3xl"></div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-neutral-950 mt-12 pb-12">
          <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex flex-col items-center md:items-start gap-2">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-primary-500 font-bold flex items-center justify-center text-xs text-white">$</div>
                <span className="text-lg font-bold text-white">Lumen Ledger</span>
              </div>
              <p className="text-neutral-500 text-sm">© 2026 Lumen Ledger. Precision for Clarity.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-8 text-sm text-neutral-400">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Security</a>
              <a href="#" className="hover:text-white transition-colors">Twitter</a>
            </div>
          </div>
        </footer>

      </main>
    </div>
  );
};

export default Landing;
