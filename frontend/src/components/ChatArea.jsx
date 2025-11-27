import React from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import MessageBubble from './MessageBubble'

const ChatArea = ({ messages, isLoading, chatEndRef }) => {
  const hasMessages = messages.length > 0

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      {!hasMessages ? (
        // Welcome State
        <div className="flex flex-col items-center justify-center h-full -mt-20">
          <div className="relative mb-6">
            <Sparkles 
              size={80} 
              className="text-groww-mint drop-shadow-[0_0_20px_rgba(0,208,156,0.6)] animate-pulse" 
            />
          </div>
          <p className="text-center text-groww-gray text-sm max-w-[280px] leading-relaxed">
            Hi, I'm <span className="text-groww-mint font-medium">Tensor</span>. Your AI-assistant to help answer your questions about the fundamentals of{' '}
            <span className="text-groww-mint font-medium">Eternal</span>.
          </p>
        </div>
      ) : (
        // Messages
        <div className="space-y-4 pb-4">
          {messages.map((message, index) => (
            <MessageBubble 
              key={index}
              role={message.role}
              content={message.content}
            />
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-groww-gray">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-sm">Tensor is thinking...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      )}
    </div>
  )
}

export default ChatArea


