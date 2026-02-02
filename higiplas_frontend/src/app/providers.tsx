// /src/app/providers.tsx
"use client";

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';
// #region agent log
const _plog = (msg: string, data: object, h: string) => { try { fetch('http://127.0.0.1:7242/ingest/dd87b882-9f5c-4d4f-ba43-1e6325b293f7', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'providers.tsx', message: msg, data, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: h }) }).catch(() => {}); } catch {} };
// #endregion
import { ThemeProvider } from 'next-themes';
import dynamic from 'next/dynamic';

const Toaster = dynamic(
  () => import('react-hot-toast').then((mod) => ({ default: mod.Toaster })),
  { ssr: false }
);

export function Providers({ children }: { children: ReactNode }) {
  // #region agent log
  _plog('Providers render', { hasChildren: !!children }, 'H3');
  // #endregion
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AuthProvider>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}