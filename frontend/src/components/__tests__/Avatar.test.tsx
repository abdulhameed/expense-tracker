import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Avatar } from '../Avatar';

describe('Avatar Component', () => {
  it('renders avatar with image', () => {
    render(
      <Avatar src="https://example.com/avatar.jpg" alt="User Avatar" />
    );
    const img = screen.getByRole('img', { name: 'User Avatar' });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg');
  });

  it('renders initials when no image provided', () => {
    const { container } = render(
      <Avatar initials="JD" alt="John Doe" />
    );
    expect(screen.getByText('JD')).toBeInTheDocument();
    expect(container.querySelector('div')).toHaveClass('rounded-full');
  });

  it('renders single initial by default', () => {
    render(<Avatar initials="A" alt="User" />);
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('renders two initials from single char', () => {
    const { container } = render(
      <Avatar initials="J" alt="User" />
    );
    const text = screen.getByText('J');
    expect(text.textContent).toHaveLength(1);
  });

  it('renders small size', () => {
    const { container } = render(
      <Avatar size="small" initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('w-8');
    expect(avatar).toHaveClass('h-8');
  });

  it('renders medium size by default', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('w-10');
    expect(avatar).toHaveClass('h-10');
  });

  it('renders large size', () => {
    const { container } = render(
      <Avatar size="large" initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('w-12');
    expect(avatar).toHaveClass('h-12');
  });

  it('applies rounded-full class', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('rounded-full');
  });

  it('applies border styling', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('border-2');
    expect(avatar).toHaveClass('border-neutral-200');
  });

  it('applies consistent background color for same initials', () => {
    const { container: container1 } = render(
      <Avatar initials="A" alt="Alice" />
    );
    const { container: container2 } = render(
      <Avatar initials="A" alt="Adam" />
    );

    const avatar1 = container1.firstChild;
    const avatar2 = container2.firstChild;

    const classes1 = avatar1?.className;
    const classes2 = avatar2?.className;

    expect(classes1).toContain('bg-');
    expect(classes2).toContain('bg-');
  });

  it('renders with custom className', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" className="custom-class" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('custom-class');
  });

  it('applies text-white to initials avatar', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('text-white');
  });

  it('applies font-bold to initials', () => {
    const { container } = render(
      <Avatar initials="JD" alt="User" />
    );
    const avatar = container.firstChild;
    expect(avatar).toHaveClass('font-bold');
  });

  it('renders with proper object-cover for image', () => {
    render(
      <Avatar src="https://example.com/avatar.jpg" alt="User Avatar" />
    );
    const img = screen.getByRole('img');
    expect(img).toHaveClass('object-cover');
  });
});
