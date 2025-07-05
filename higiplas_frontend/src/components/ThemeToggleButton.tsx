// /app/components/ThemeToggleButton.tsx

"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'; 

// Se não tiver os ícones, instale-os:
// npm install @heroicons/react

export function ThemeToggleButton() {
  const { setTheme, theme } = useTheme();

  return (
    <button
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      aria-label="Toggle theme"
    >
      {theme === "light" ? (
        <MoonIcon className="h-6 w-6 text-gray-800"/>
      ) : (
        <SunIcon className="h-6 w-6 text-yellow-400"/>
      )}
    </button>
  );
}