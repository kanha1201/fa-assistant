import React, { useState } from 'react'
import { Send } from 'lucide-react'

const InputField = ({ onSend, disabled }) => {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center gap-2 bg-groww-surface rounded-2xl px-4 py-3 border border-groww-border">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about Eternal's financials..."
          disabled={disabled}
          className="flex-1 bg-transparent text-groww-white placeholder-groww-gray text-sm outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className={`
            p-2 rounded-full transition-all duration-200
            ${input.trim() && !disabled
              ? 'bg-groww-mint text-groww-black hover:bg-groww-mint/90 active:scale-95'
              : 'bg-groww-chip text-groww-gray cursor-not-allowed'
            }
          `}
        >
          <Send size={18} />
        </button>
      </div>
    </form>
  )
}

export default InputField


