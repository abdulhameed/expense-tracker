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
    <nav className="text-sm" aria-label="Breadcrumb">
      <ol className="flex items-center gap-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            {item.href ? (
              <Link
                to={item.href}
                className="text-primary-600 hover:text-primary-700 hover:underline font-medium transition-colors
                  focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
              >
                {item.label}
              </Link>
            ) : (
              <span
                aria-current="page"
                className="text-neutral-700 font-medium"
              >
                {item.label}
              </span>
            )}
            {index < items.length - 1 && (
              <span className="text-neutral-400" aria-hidden="true">{separator}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
