import React from 'react'

const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-groww-mint text-groww-black rounded-br-sm'
            : 'bg-groww-surface text-groww-white border border-groww-border rounded-bl-sm'
        }`}
      >
        {isUser ? (
          <p className="text-sm font-medium whitespace-pre-wrap break-words">{content}</p>
        ) : (
          <div 
            className="text-sm leading-relaxed whitespace-pre-wrap break-words"
            dangerouslySetInnerHTML={{ 
              __html: content
                .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
                .replace(/^•\s/gm, '• ')
                .replace(/\n/g, '<br />')
            }}
          />
        )}
      </div>
    </div>
  )
}

export default MessageBubble

