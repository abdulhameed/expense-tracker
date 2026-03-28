import { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hoverable?: boolean;
}

export function Card({ children, hoverable = false, className, ...props }: CardProps) {
  const hoverClass = hoverable ? 'hover:shadow-lg' : '';
  const baseStyles = 'bg-white rounded-lg border border-neutral-200 shadow-sm p-6';

  return (
    <div
      className={`${baseStyles} transition-shadow ${hoverClass} ${className || ''}`}
      {...props}
    >
      {children}
    </div>
  );
}
