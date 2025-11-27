import React, { useState, useRef, useEffect } from 'react'
import Header from './components/Header'
import ChatArea from './components/ChatArea'
import QuickActionChips from './components/QuickActionChips'
import InputField from './components/InputField'
import { apiService } from './services/api'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const chatEndRef = useRef(null)
  const companySymbol = 'ETERNAL' // Hardcoded for now

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleQuickAction = async (action) => {
    setIsLoading(true)
    
    try {
      let response
      switch (action) {
        case 'summarise':
          response = await apiService.getSummary(companySymbol)
          addMessage('assistant', response.summary || response.full_response || 'Summary not available')
          break
        case 'red_flags':
          response = await apiService.getRedFlags(companySymbol)
          const redFlagsText = response.red_flags?.map(flag => 
            `• ${flag.description || flag}`
          ).join('\n') || response.full_response || 'No red flags data available'
          addMessage('assistant', redFlagsText)
          break
        case 'bull_bear':
          response = await apiService.getBullBear(companySymbol)
          const bullBearText = response.full_response || 
            `**Bull Case:**\n${response.bull_case?.join('\n') || 'N/A'}\n\n**Bear Case:**\n${response.bear_case?.join('\n') || 'N/A'}`
          addMessage('assistant', bullBearText)
          break
        default:
          break
      }
    } catch (error) {
      console.error('Error fetching quick action:', error)
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return

    addMessage('user', text)
    setIsLoading(true)

    try {
      const response = await apiService.answerQuery(companySymbol, text)
      addMessage('assistant', response.answer || 'Sorry, I could not process your request.')
    } catch (error) {
      console.error('Error sending message:', error)
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const addMessage = (role, content) => {
    setMessages(prev => [...prev, { role, content, timestamp: new Date() }])
  }

  return (
    <div className="flex flex-col h-screen max-w-[400px] mx-auto bg-groww-black">
      <Header />
      <ChatArea 
        messages={messages} 
        isLoading={isLoading}
        chatEndRef={chatEndRef}
      />
      <div className="flex-shrink-0 pb-4 px-4">
        <QuickActionChips 
          onActionClick={handleQuickAction}
          disabled={isLoading}
        />
        <InputField 
          onSend={handleSendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  )
}

export default App


