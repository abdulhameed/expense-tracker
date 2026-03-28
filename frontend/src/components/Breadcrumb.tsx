import { Link } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: string;
}

export function Breadcrumb({ items, separator = '/' }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
      <ol className="flex items-center gap-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            {item.href ? (
              <Link
                to={item.href}
                className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className="text-neutral-600 font-medium">{item.label}</span>
            )}
            {index < items.length - 1 && (
              <span className="text-neutral-400">{separator}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
