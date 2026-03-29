import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export const Card = forwardRef(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "bg-white rounded-xl border border-neutral-200 shadow-sm hover:shadow-md transition-shadow duration-200",
      className
    )}
    {...props}
  >
    {children}
  </div>
));
Card.displayName = "Card";

export const CardHeader = forwardRef(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pb-0", className)} {...props}>
    {children}
  </div>
));
CardHeader.displayName = "CardHeader";

export const CardTitle = forwardRef(({ className, children, ...props }, ref) => (
  <h3 ref={ref} className={cn("text-lg font-semibold text-neutral-900 leading-none", className)} {...props}>
    {children}
  </h3>
));
CardTitle.displayName = "CardTitle";

export const CardContent = forwardRef(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-4", className)} {...props}>
    {children}
  </div>
));
CardContent.displayName = "CardContent";
