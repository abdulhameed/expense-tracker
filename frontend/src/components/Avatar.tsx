import { ImgHTMLAttributes } from 'react';

type AvatarSize = 'small' | 'medium' | 'large';

interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src'> {
  src?: string;
  initials?: string;
  size?: AvatarSize;
  alt: string;
}

const sizeStyles: Record<AvatarSize, string> = {
  small: 'w-8 h-8 text-xs',
  medium: 'w-10 h-10 text-sm',
  large: 'w-12 h-12 text-base',
};

function getInitialsBgColor(initials: string): string {
  const colors = [
    'bg-primary-500',
    'bg-success-500',
    'bg-warning-500',
    'bg-error-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-cyan-500',
  ];

  // Generate a consistent color based on initials
  const charCode = initials.charCodeAt(0);
  return colors[charCode % colors.length];
}

export function Avatar({ src, initials = '?', size = 'medium', alt, className, ...props }: AvatarProps) {
  const sizeClass = sizeStyles[size];

  // If no image, show initials
  if (!src || !alt) {
    const bgColor = getInitialsBgColor(initials);
    return (
      <div
        className={`${sizeClass} ${bgColor} rounded-full flex items-center justify-center text-white font-bold border-2 border-neutral-200 ${className || ''}`}
        {...(props as any)}
      >
        {initials.slice(0, 2).toUpperCase()}
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={`${sizeClass} rounded-full object-cover border-2 border-neutral-200 ${className || ''}`}
      {...props}
    />
  );
}
