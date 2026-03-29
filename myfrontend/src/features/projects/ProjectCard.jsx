import React from 'react';

export const ProjectCard = ({ 
  icon: Icon, 
  title, 
  description, 
  budgetUsed, 
  amountSpent, 
  totalBudget, 
  collaborators,
  colorVariant = 'primary'
}) => {
  const getColors = () => {
    switch (colorVariant) {
      case 'primary': return { bg: 'bg-primary-50', text: 'text-primary-600', fill: 'bg-primary-600' };
      case 'success': return { bg: 'bg-success-50', text: 'text-success-600', fill: 'bg-success-600' };
      case 'warning': return { bg: 'bg-warning-50', text: 'text-warning-600', fill: 'bg-warning-500' };
      case 'error': return { bg: 'bg-error-50', text: 'text-error-600', fill: 'bg-error-600' };
      case 'purple': return { bg: 'bg-purple-50', text: 'text-purple-600', fill: 'bg-purple-600' };
      case 'rose': return { bg: 'bg-rose-50', text: 'text-rose-600', fill: 'bg-rose-600' };
      default: return { bg: 'bg-neutral-100', text: 'text-neutral-600', fill: 'bg-neutral-500' };
    }
  };
  const colors = getColors();

  return (
    <div className="group bg-white border border-neutral-200 p-6 rounded-2xl transition-all hover:shadow-md cursor-pointer flex flex-col h-full hover:border-primary-200">
      <div className="flex justify-between items-start mb-6">
        <div className={`p-3 rounded-xl ${colors.bg} ${colors.text}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex -space-x-2">
          {collaborators.map((img, idx) => (
            <img 
              key={idx}
              className="h-8 w-8 rounded-full border-2 border-white bg-neutral-100 object-cover" 
              src={img} 
              alt="Collaborator" 
            />
          ))}
        </div>
      </div>
      
      <h3 className="text-xl font-bold text-neutral-900 mb-1">{title}</h3>
      <p className="text-sm text-neutral-500 mb-6 flex-1">{description}</p>
      
      <div className="space-y-2 mt-auto">
        <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-neutral-500">
          <span>Budget Utilization</span>
          <span className="font-mono">{budgetUsed}%</span>
        </div>
        <div className="h-1.5 w-full bg-neutral-100 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all duration-500 ${colors.fill}`} style={{ width: `${budgetUsed}%` }}></div>
        </div>
        <div className="flex justify-between items-center pt-2">
          <span className="text-sm font-medium text-neutral-500">Spent</span>
          <span className="text-lg font-bold font-mono text-neutral-900">
            ${amountSpent.toLocaleString()} <span className="text-xs font-normal text-neutral-400">/ ${totalBudget.toLocaleString()}</span>
          </span>
        </div>
      </div>
    </div>
  );
};
