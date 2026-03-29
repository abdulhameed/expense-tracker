import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../../utils/cn';
import { 
  HomeIcon, 
  BanknotesIcon, 
  FolderIcon, 
  ChartPieIcon,
  WalletIcon,
  UserGroupIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/app', icon: HomeIcon },
  { name: 'Transactions', href: '/app/transactions', icon: BanknotesIcon },
  { name: 'Projects', href: '/app/projects', icon: FolderIcon },
  { name: 'Reports', href: '/app/reports', icon: ChartPieIcon },
  { name: 'Budgets', href: '/app/budgets', icon: WalletIcon },
  { name: 'Team', href: '/app/team', icon: UserGroupIcon },
];

export const Sidebar = ({ isOpen, onClose }) => {
  return (
    <>
      <div 
        className={cn(
          "fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={onClose}
      />
      <aside className={cn(
        "w-64 bg-white border-r border-neutral-200 h-screen fixed left-0 top-0 p-6 z-50 transition-transform duration-300",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold">
              $
            </div>
            <span className="text-xl font-bold text-neutral-900">
              ExpenseTracker
            </span>
          </div>
          <button onClick={onClose} className="lg:hidden p-1 text-neutral-500 hover:bg-neutral-100 rounded">
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
        
        <nav className="space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) => cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors",
                isActive 
                  ? "bg-primary-50 text-primary-700" 
                  : "text-neutral-700 hover:bg-neutral-50"
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};
