import React from 'react'
import { ArrowLeft, MoreVertical, Sparkles } from 'lucide-react'

const Header = () => {
  return (
    <div className="sticky top-0 z-50 bg-groww-black/95 backdrop-blur-md border-b border-groww-border">
      <div className="flex items-center justify-between px-4 py-3 h-14">
        {/* Back Arrow */}
        <button 
          className="p-2 -ml-2 text-groww-white hover:bg-groww-surface rounded-lg transition-colors"
          onClick={() => window.history.back()}
        >
          <ArrowLeft size={20} />
        </button>

        {/* Tensor Logo and Name */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Sparkles 
              size={20} 
              className="text-groww-mint drop-shadow-[0_0_8px_rgba(0,208,156,0.5)]" 
            />
          </div>
          <span className="text-white font-semibold text-lg">Tensor</span>
        </div>

        {/* Menu */}
        <button 
          className="p-2 -mr-2 text-groww-white hover:bg-groww-surface rounded-lg transition-colors"
        >
          <MoreVertical size={20} />
        </button>
      </div>
    </div>
  )
}

export default Header


