'use client';

import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface QuickActionsProps {
  onNovoOrcamento?: () => void;
}

export function QuickActions({ onNovoOrcamento }: QuickActionsProps) {
  const router = useRouter();

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="flex flex-col gap-3">
        <Button
          size="lg"
          className="rounded-full shadow-lg h-14 w-14 p-0"
          onClick={() => onNovoOrcamento ? onNovoOrcamento() : router.push('/vendedor/app')}
        >
          <Plus size={24} />
        </Button>
      </div>
    </div>
  );
}

