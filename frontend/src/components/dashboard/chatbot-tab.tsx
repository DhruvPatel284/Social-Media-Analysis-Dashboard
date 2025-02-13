'use client';

import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export function ChatbotTab() {
  const [message, setMessage] = useState('');

  const handleSendMessage = () => {
    if (!message.trim()) return;
    // Handle sending message to chatbot
    setMessage('');
  };

  return (
    <Card className="p-6">
      <div className="flex flex-col h-[600px]">
        <div className="flex-1 overflow-y-auto mb-4">
          {/* Chat messages will go here */}
        </div>
        <div className="flex gap-2">
          <Input
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <Button onClick={handleSendMessage}>Send</Button>
        </div>
      </div>
    </Card>
  );
}