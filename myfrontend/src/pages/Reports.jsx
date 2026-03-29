import React from 'react';
import { Button } from '../components/ui/Button';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  ArrowDownTrayIcon,
  AdjustmentsHorizontalIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const monthlyData = [
  { name: 'JAN', income: 4000, expenses: 2400 },
  { name: 'FEB', income: 4200, expenses: 2100 },
  { name: 'MAR', income: 3800, expenses: 2800 },
  { name: 'APR', income: 4500, expenses: 2600 },
  { name: 'MAY', income: 4100, expenses: 3200 },
  { name: 'JUN', income: 4800, expenses: 2900 },
];

const breakdownData = [
  { name: 'Housing', value: 48, color: '#0ea5e9' }, // primary-500 equivalent if using tailwind colors, we'll use hex
  { name: 'Lifestyle', value: 32, color: '#10b981' }, // success-500
  { name: 'Groceries', value: 20, color: '#f59e0b' }, // warning-500
];

const budgetAdherence = [
  { name: 'International Travel', type: 'Annual Allocation', spent: 3200, total: 5000, utilized: 64, variant: 'primary' },
  { name: 'Dining & Entertainment', type: 'Monthly Allocation', spent: 920, total: 800, utilized: 115, variant: 'error' },
  { name: 'Home Utilities', type: 'Fixed Monthly', spent: 310, total: 450, utilized: 68, variant: 'success' },
  { name: 'Digital Subscriptions', type: 'Monthly SaaS', spent: 145, total: 150, utilized: 96, variant: 'warning' },
];

export default function Reports() {
  return (
    <div className="space-y-8">
      {/* Header / Filter Bar */}
      <section className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 mb-2">Financial Reports</h1>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex bg-neutral-100 rounded-lg p-1 border border-neutral-200">
            <button className="px-4 py-1.5 text-xs font-semibold rounded-md bg-white text-primary-600 shadow-sm border border-neutral-200">Last 6 Months</button>
            <button className="px-4 py-1.5 text-xs font-medium text-neutral-500 hover:text-neutral-900 transition-colors">Year to Date</button>
            <button className="px-4 py-1.5 text-xs font-medium text-neutral-500 hover:text-neutral-900 transition-colors">Custom</button>
          </div>
          <div className="h-6 w-px bg-neutral-300"></div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-neutral-200 rounded-lg text-xs font-medium text-neutral-600 hover:bg-neutral-50 transition-colors">
            <AdjustmentsHorizontalIcon className="w-4 h-4" />
            All Categories
          </button>
          <Button variant="secondary" size="sm" className="flex items-center gap-2 h-[34px]">
            <ArrowDownTrayIcon className="w-4 h-4" />
            Export PDF
          </Button>
        </div>
      </section>

      {/* Insights Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-white border border-neutral-200 rounded-xl p-6 flex items-center justify-between shadow-sm">
          <div>
            <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest mb-4">Spending Intelligence</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-neutral-900">
                <span className="w-2 h-2 rounded-full bg-primary-500"></span>
                <span>Top category: <span className="font-bold">Housing</span> ($2,450.00)</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-900">
                <span className="w-2 h-2 rounded-full bg-error-500"></span>
                <span>Spending up <span className="font-bold text-error-600">5.2%</span> from last month</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-900">
                <span className="w-2 h-2 rounded-full bg-success-500"></span>
                <span>Savings rate optimized at <span className="font-bold text-success-600">22%</span></span>
              </div>
            </div>
          </div>
          <div className="hidden lg:flex w-24 h-24 bg-primary-50 rounded-full items-center justify-center border border-primary-100">
            <SparklesIcon className="text-primary-600 w-10 h-10" />
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-xl p-6 text-white flex flex-col justify-between shadow-md">
          <span className="text-xs font-medium opacity-80 uppercase tracking-widest">Net Worth Growth</span>
          <div className="mt-4">
            <span className="text-4xl font-extrabold tracking-tight font-mono">+$12,450</span>
            <p className="text-[10px] opacity-70 mt-2 uppercase tracking-widest font-bold">Total Delta Q3-Q4</p>
          </div>
        </div>
      </section>

      {/* Main Visualizations Grid */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Monthly Trends */}
        <div className="lg:col-span-2 bg-white border border-neutral-200 rounded-xl p-6 md:p-8 shadow-sm">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-lg font-bold text-neutral-900">Monthly Trends</h3>
              <p className="text-xs text-neutral-500">Income vs Expenses Analysis</p>
            </div>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary-500"></span>
                <span className="text-xs font-medium text-neutral-600">Income</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-success-400"></span>
                <span className="text-xs font-medium text-neutral-600">Expenses</span>
              </div>
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
                <RechartsTooltip cursor={{ fill: '#f3f4f6' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Bar dataKey="income" fill="#0ea5e9" radius={[4, 4, 0, 0]} maxBarSize={40} />
                <Bar dataKey="expenses" fill="#4ade80" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Spending Breakdown */}
        <div className="lg:col-span-1 bg-white border border-neutral-200 rounded-xl p-6 md:p-8 shadow-sm flex flex-col">
          <h3 className="text-lg font-bold text-neutral-900 mb-1">Spending Breakdown</h3>
          <p className="text-xs text-neutral-500 mb-6">By Primary Category</p>
          
          <div className="relative w-full aspect-square flex-1 min-h-[200px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={breakdownData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={95}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                  startAngle={180}
                  endAngle={0}
                >
                  {breakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center mt-8">
              <span className="text-xs font-medium text-neutral-500 uppercase tracking-tighter">Total Spent</span>
              <span className="text-2xl font-bold font-mono text-neutral-900">$8.4k</span>
            </div>
          </div>
          
          <div className="space-y-4 mt-2">
            {breakdownData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-sm font-medium text-neutral-700">{item.name}</span>
                </div>
                <span className="text-sm font-bold font-mono text-neutral-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Budget Adherence */}
        <div className="lg:col-span-3 bg-white border border-neutral-200 rounded-xl p-6 md:p-8 shadow-sm">
          <div className="mb-8">
            <h3 className="text-lg font-bold text-neutral-900">Budget Adherence</h3>
            <p className="text-xs text-neutral-500">Current utilization of allocated funds</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
            {budgetAdherence.map((budget, idx) => {
              const overBudget = budget.utilized > 100;
              const fillAmt = Math.min(budget.utilized, 100);
              
              let barColor = 'bg-primary-500';
              let textColor = 'text-primary-600';
              
              if (budget.variant === 'error' || overBudget) { barColor = 'bg-error-500'; textColor = 'text-error-600'; }
              else if (budget.variant === 'success') { barColor = 'bg-success-500'; textColor = 'text-success-600'; }
              else if (budget.variant === 'warning') { barColor = 'bg-warning-500'; textColor = 'text-warning-600'; }
              
              return (
                <div key={idx} className="space-y-3">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-sm font-bold text-neutral-900">{budget.name}</p>
                      <p className="text-[10px] text-neutral-500 uppercase tracking-wider">{budget.type}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-mono font-bold ${overBudget ? 'text-error-600' : 'text-neutral-900'}`}>
                        ${budget.spent.toLocaleString()} / ${budget.total.toLocaleString()}
                      </p>
                      <p className={`text-[10px] font-bold uppercase tracking-tight ${textColor}`}>
                        {overBudget ? 'Over Budget' : `${budget.utilized}% Utilized`}
                      </p>
                    </div>
                  </div>
                  <div className="h-2 w-full bg-neutral-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full transition-all duration-1000 ${barColor}`} style={{ width: `${fillAmt}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </section>
    </div>
  );
}
