// /src/app/dashboard/layout.tsx
import { Sidebar } from '@/components/dashboard/Sidebar';
import ClientLayout from '@/components/ClientLayout';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClientLayout>
      <div className="flex h-screen bg-gray-100 dark:bg-gray-900 overflow-hidden">
        <Sidebar />
        
        {/* Área principal do conteúdo */}
        <div className="flex-1 flex flex-col md:ml-64"> {/* O ml-64 (margin-left) compensa o tamanho do sidebar */}
          <div className="flex-1 flex flex-col overflow-y-auto">
            {children}
          </div>
        </div>
      </div>
    </ClientLayout>
  );
}