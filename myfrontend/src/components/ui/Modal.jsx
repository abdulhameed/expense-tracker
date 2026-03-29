import React, { useEffect } from 'react';
import { cn } from '../../utils/cn';
import { XMarkIcon as XIcon } from '@heroicons/react/24/outline'; // Updated import path

export const Modal = ({ isOpen, onClose, title, children, footer, className }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className={cn(
        "relative bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col",
        className
      )}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-neutral-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-neutral-900">
            {title}
          </h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-neutral-500 hover:bg-neutral-100 transition-colors"
          >
            <XIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Body */}
        <div className="px-6 py-4 overflow-y-auto flex-1">
          {children}
        </div>
        
        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-neutral-200 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
