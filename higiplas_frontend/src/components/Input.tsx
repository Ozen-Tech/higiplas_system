'use client';

import React, { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export default function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-medium text-neutral-gray-700">{label}</label>
      <input
        className={`border border-neutral-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-higiplas-blue focus:border-higiplas-blue ${className}`}
        {...props}
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}