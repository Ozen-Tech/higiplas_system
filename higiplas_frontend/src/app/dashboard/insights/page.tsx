"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/dashboard/Header";
import ClientLayout from "@/components/ClientLayout";
import { Card, CardContent } from "@/components/ui/card";

export default function InsightsPage() {
  const router = useRouter();

  useEffect(() => {
    const t = setTimeout(() => router.replace("/dashboard"), 2000);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <ClientLayout>
      <Header />
      <main className="p-6 max-w-2xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <p className="text-gray-600 dark:text-gray-400">
              O recurso de insights com IA foi removido do sistema. Redirecionando para o dashboard...
            </p>
          </CardContent>
        </Card>
      </main>
    </ClientLayout>
  );
}
