'use client';

import React, { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  fullWidth?: boolean;
}

export default function Button({
  children,
  variant = 'primary',
  fullWidth = false,
  className = '',
  ...props
}: ButtonProps) {
  const baseClasses =
    'px-4 py-2 rounded-md font-semibold transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary:
      'bg-higiplas-blue text-white hover:bg-blue-800 focus:ring-higiplas-blue',
    secondary:
      'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400',
    danger:
      'bg-red-600 text-white hover:bg-red-700 focus:ring-red-600',
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${
        fullWidth ? 'w-full' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}