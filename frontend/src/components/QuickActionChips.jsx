import React from 'react'
import { FileText, AlertTriangle, TrendingUp } from 'lucide-react'

const QuickActionChips = ({ onActionClick, disabled }) => {
  const actions = [
    {
      id: 'summarise',
      label: 'Summarise',
      icon: FileText,
      color: 'text-groww-white',
    },
    {
      id: 'red_flags',
      label: 'Red Flags',
      icon: AlertTriangle,
      color: 'text-groww-coral',
    },
    {
      id: 'bull_bear',
      label: 'Bull/Bear',
      icon: TrendingUp,
      color: 'text-groww-white',
    },
  ]

  return (
    <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
      {actions.map((action) => {
        const Icon = action.icon
        return (
          <button
            key={action.id}
            onClick={() => !disabled && onActionClick(action.id)}
            disabled={disabled}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-full
              bg-groww-chip border border-groww-chip-border
              ${action.color} text-sm font-medium
              transition-all duration-200
              ${disabled 
                ? 'opacity-50 cursor-not-allowed' 
                : 'hover:bg-groww-surface hover:border-groww-border active:scale-95'
              }
              whitespace-nowrap
            `}
          >
            <Icon size={16} />
            <span>{action.label}</span>
          </button>
        )
      })}
    </div>
  )
}

export default QuickActionChips


