import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Spinner } from '../Spinner';

describe('Spinner Component', () => {
  it('renders spinner SVG', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('renders small size', () => {
    const { container } = render(<Spinner size="small" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('w-4');
    expect(svg).toHaveClass('h-4');
  });

  it('renders medium size by default', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('w-8');
    expect(svg).toHaveClass('h-8');
  });

  it('renders large size', () => {
    const { container } = render(<Spinner size="large" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('w-12');
    expect(svg).toHaveClass('h-12');
  });

  it('applies animation class', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('animate-spin');
  });

  it('applies primary color by default', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('text-primary-600');
  });

  it('applies custom color', () => {
    const { container } = render(<Spinner color="text-error-600" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('text-error-600');
  });

  it('renders with proper SVG structure', () => {
    const { container } = render(<Spinner />);
    const circles = container.querySelectorAll('circle');
    expect(circles.length).toBeGreaterThan(0);
  });

  it('renders accessible spinner', () => {
    const { container } = render(<Spinner />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('viewBox', '0 0 24 24');
    expect(svg).toHaveAttribute('xmlns', 'http://www.w3.org/2000/svg');
  });
});
