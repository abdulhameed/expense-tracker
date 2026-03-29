import React from 'react';
import { BellIcon, Bars3Icon } from '@heroicons/react/24/outline'; 

export const Navbar = ({ onMenuClick }) => {
  return (
    <nav className="bg-white border-b border-neutral-200 px-6 py-4 sticky top-0 z-30">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={onMenuClick} className="lg:hidden p-2 -ml-2 text-neutral-600 hover:bg-neutral-100 rounded-lg">
            <Bars3Icon className="w-6 h-6" />
          </button>
          <div className="lg:hidden text-xl font-bold text-neutral-900">
            ExpenseTracker
          </div>
        </div>
        <div className="flex items-center gap-4 ml-auto">
          <button className="p-2 rounded-lg text-neutral-600 hover:bg-neutral-100">
            <BellIcon className="w-5 h-5" />
          </button>
          <button className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold shadow-sm">
              U
            </div>
          </button>
        </div>
      </div>
    </nav>
  );
};
