import React from 'react';
import { ProjectCard } from '../features/projects/ProjectCard';
import { Button } from '../components/ui/Button';
import { 
  FolderPlusIcon, 
  HomeModernIcon, 
  ComputerDesktopIcon, 
  PaperAirplaneIcon,
  RocketLaunchIcon,
  HeartIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

const dummyProjects = [
  {
    icon: HomeModernIcon, title: 'Home Renovation', desc: 'Interior design & structural updates',
    budgetUsed: 85, amountSpent: 72400, totalBudget: 85000, colorVariant: 'primary',
    collaborators: ['https://ui-avatars.com/api/?name=Jane+Doe&background=random', 'https://ui-avatars.com/api/?name=John+Smith&background=random']
  },
  {
    icon: ComputerDesktopIcon, title: 'Tech Upgrade', desc: 'DevOps hardware & cloud subscriptions',
    budgetUsed: 42, amountSpent: 5250, totalBudget: 12500, colorVariant: 'success',
    collaborators: ['https://ui-avatars.com/api/?name=Alice+Lin&background=random']
  },
  {
    icon: PaperAirplaneIcon, title: 'European Summer Trip', desc: 'Flights, stay & culinary experiences',
    budgetUsed: 12, amountSpent: 1800, totalBudget: 15000, colorVariant: 'warning',
    collaborators: ['https://ui-avatars.com/api/?name=Mark+Z&background=random']
  },
  {
    icon: RocketLaunchIcon, title: 'Brand Identity Launch', desc: 'Marketing, ads & creative assets',
    budgetUsed: 68, amountSpent: 34000, totalBudget: 50000, colorVariant: 'purple',
    collaborators: ['https://ui-avatars.com/api/?name=Emma+W&background=random']
  },
  {
    icon: HeartIcon, title: 'Wellness Retreat', desc: 'Yoga training & nutritional planning',
    budgetUsed: 94, amountSpent: 4700, totalBudget: 5000, colorVariant: 'rose',
    collaborators: ['https://ui-avatars.com/api/?name=Sara+K&background=random']
  }
];

export default function Projects() {
  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 mb-2">Projects</h1>
          <p className="text-neutral-500 max-w-md">Track, manage, and optimize your financial ventures with precision.</p>
        </div>
        <Button className="flex items-center justify-center gap-2">
          <FolderPlusIcon className="w-5 h-5" />
          New Project
        </Button>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-neutral-200 p-8 rounded-2xl flex flex-col justify-between min-h-[160px] shadow-sm">
          <span className="text-xs font-semibold text-neutral-500 tracking-widest uppercase">Active Projects</span>
          <div className="text-5xl font-extrabold tracking-tighter text-primary-600 mt-4">12</div>
          <div className="flex items-center gap-1 text-success-600 text-sm mt-2 font-medium">
            <ArrowTrendingUpIcon className="w-4 h-4" />
            <span>2 added this month</span>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-primary-600 to-primary-800 p-8 rounded-2xl flex flex-col justify-between min-h-[160px] text-white shadow-md relative overflow-hidden">
          <div className="absolute -right-4 -bottom-4 opacity-10">
            <RocketLaunchIcon className="w-32 h-32" />
          </div>
          <span className="text-xs font-semibold opacity-80 tracking-widest uppercase relative z-10">Total Budget</span>
          <div className="text-5xl font-extrabold tracking-tighter font-mono mt-4 relative z-10">$245,000</div>
          <div className="text-sm opacity-90 mt-2 relative z-10">Allocated across all verticals</div>
        </div>
        
        <div className="bg-white border border-neutral-200 p-8 rounded-2xl flex flex-col justify-between min-h-[160px] shadow-sm">
          <span className="text-xs font-semibold text-neutral-500 tracking-widest uppercase">Overall Spending</span>
          <div className="text-5xl font-extrabold tracking-tighter text-neutral-900 mt-4 font-mono">$182,430</div>
          <div className="w-full bg-neutral-100 h-2 rounded-full mt-6 overflow-hidden">
            <div className="bg-success-500 h-full rounded-full" style={{ width: '74%' }}></div>
          </div>
          <div className="flex justify-between text-xs mt-2 font-medium text-neutral-500">
            <span>74% Exhausted</span>
            <span>$62,570 Remaining</span>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {dummyProjects.map((p, idx) => <ProjectCard key={idx} {...p} />)}
        
        <div className="group border-2 border-dashed border-neutral-300 p-6 rounded-2xl flex flex-col items-center justify-center text-neutral-400 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50 transition-all cursor-pointer min-h-[250px]">
          <FolderPlusIcon className="w-10 h-10 mb-4" />
          <p className="font-bold text-neutral-700 group-hover:text-primary-600">Add New Project</p>
          <p className="text-xs text-center mt-2 opacity-60">Start a new financial journey</p>
        </div>
      </section>

      <section className="bg-white border border-neutral-200 p-8 rounded-3xl relative overflow-hidden shadow-sm">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="max-w-md">
            <h2 className="text-2xl font-bold text-neutral-900 mb-2">Spending Horizon</h2>
            <p className="text-neutral-500 text-sm">Visualize project trajectories against quarterly benchmarks with overlapping time horizons.</p>
          </div>
          <div className="flex gap-4">
            <button className="bg-neutral-100 px-4 py-2 rounded-lg text-sm font-semibold text-neutral-700 hover:bg-neutral-200 transition-colors">Weekly</button>
            <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md hover:bg-primary-700 transition-colors">Monthly</button>
          </div>
        </div>
        
        <div className="h-64 mt-8 w-full relative">
          <div className="absolute inset-0 flex items-end justify-between gap-1 sm:gap-2">
            {[40, 60, 50, 80, 45, 30, 70, 90, 55].map((height, i) => (
              <div 
                key={i} 
                className={`w-full rounded-t-lg transition-all duration-1000 ${i % 2 === 0 ? 'bg-primary-200' : 'bg-primary-100'}`} 
                style={{ height: `${height}%` }}
              ></div>
            ))}
          </div>
          <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px] border border-white/50 rounded-xl flex items-center justify-center pointer-events-none">
            <span className="text-sm font-black uppercase tracking-[0.2em] text-neutral-700 bg-white/80 px-4 py-2 rounded-lg shadow-sm">Projection Landscape</span>
          </div>
        </div>
      </section>
    </div>
  );
}
