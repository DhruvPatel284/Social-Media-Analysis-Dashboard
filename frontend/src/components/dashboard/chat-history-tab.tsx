'use client';

import { Card } from '@/components/ui/card';

export function ChatHistoryTab() {
  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-4">Chat History</h3>
      <div className="space-y-4">
        {/* Chat history list will go here */}
      </div>
    </Card>
  );
}