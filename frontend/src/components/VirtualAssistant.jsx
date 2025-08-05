"use client"

import { useState } from "react"
import { MessageCircle, X, Send, Bot, User } from "lucide-react"
import { getUserGroup } from "../utils/auth"

export default function VirtualAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      message: "Hello! I'm your DALScooter virtual assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const userGroups = getUserGroup()
  const isAdmin = userGroups.includes("BikeFranchise")

  // Lambda function endpoint (you'll need to update this with your actual endpoint)
  const LEX_API_URL = import.meta.env.VITE_LEX_API_URL || 'https://your-lex-api-gateway-url.amazonaws.com/prod/lex'

  const callLambdaFunction = async (userInput) => {
    try {
      console.log('Calling Lambda function with URL:', LEX_API_URL)
      console.log('Request payload:', { message: userInput, userId: localStorage.getItem('userEmail') || 'guest', sessionId: `session_${Date.now()}` })
      
      const response = await fetch(LEX_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userInput,
          userId: localStorage.getItem('userEmail') || 'guest',
          sessionId: `session_${Date.now()}`
        })
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Response data:', data)
      return data.message || "I'm sorry, I couldn't process your request. Please try again."
    } catch (error) {
      console.error('Error calling Lambda function:', error)
      // Return error message instead of fallback
      return "I'm sorry, I'm having trouble connecting to my services right now. Please try again later."
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: messages.length + 1,
      type: "user",
      message: inputMessage,
      timestamp: new Date(),
    }

    setMessages([...messages, userMessage])
    setIsLoading(true)

    try {
      // Call Lambda function
      const botResponse = await callLambdaFunction(inputMessage)
      
      const botMessage = {
        id: messages.length + 2,
        type: "bot",
        message: botResponse,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error('Error getting bot response:', error)
      // Error response
      const errorMessage = {
        id: messages.length + 2,
        type: "bot",
        message: "I'm sorry, I'm having trouble connecting to my services right now. Please try again later.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setInputMessage("")
    }
  }

  const quickQuestions = [
    "How do I register?",
    "What vehicle types are available?",
    "How do I book a ride?",
  ]

  const handleQuickQuestion = async (question) => {
    const userMessage = {
      id: messages.length + 1,
      type: "user",
      message: question,
      timestamp: new Date(),
    }

    setMessages([...messages, userMessage])
    setIsLoading(true)

    try {
      const botResponse = await callLambdaFunction(question)
      
      const botMessage = {
        id: messages.length + 2,
        type: "bot",
        message: botResponse,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error('Error getting bot response:', error)
      const errorMessage = {
        id: messages.length + 2,
        type: "bot",
        message: "I'm sorry, I'm having trouble connecting to my services right now. Please try again later.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 p-4 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-110 z-50 ${
          isAdmin
            ? "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
            : "bg-gradient-to-r from-indigo-500 to-blue-400 hover:from-indigo-600 hover:to-blue-500"
        } text-white`}
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-[33.6rem] h-[28.8rem] bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 flex flex-col z-40">
          {/* Header */}
          <div
            className={`p-4 rounded-t-2xl text-white ${
              isAdmin ? "bg-gradient-to-r from-red-500 to-red-600" : "bg-gradient-to-r from-indigo-500 to-blue-400"
            }`}
          >
            <div className="flex items-center space-x-3">
              <Bot className="h-6 w-6" />
              <div>
                <h3 className="font-semibold">{isAdmin ? "Admin Assistant" : "DALScooter Assistant"}</h3>
                <p className="text-xs opacity-90">
                  {isAdmin ? "Franchise Support • Ready to help" : "Online • Ready to help"}
                </p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-2 ${
                  msg.type === "user" ? "flex-row-reverse space-x-reverse" : ""
                }`}
              >
                <div
                  className={`p-2 rounded-full ${
                    msg.type === "user" ? (isAdmin ? "bg-red-500" : "bg-indigo-500") : "bg-slate-200"
                  }`}
                >
                  {msg.type === "user" ? (
                    <User className="h-4 w-4 text-white" />
                  ) : (
                    <Bot className="h-4 w-4 text-slate-600" />
                  )}
                </div>
                <div
                  className={`max-w-xs p-3 rounded-2xl ${
                    msg.type === "user"
                      ? isAdmin
                        ? "bg-red-500 text-white"
                        : "bg-indigo-500 text-white"
                      : "bg-slate-100 text-slate-800"
                  }`}
                >
                  <p className="text-sm">{msg.message}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start space-x-2">
                <div className="p-2 rounded-full bg-slate-200">
                  <Bot className="h-4 w-4 text-slate-600" />
                </div>
                <div className="max-w-xs p-3 rounded-2xl bg-slate-100 text-slate-800">
                  <p className="text-sm">Thinking...</p>
                </div>
              </div>
            )}
          </div>

          {/* Quick Questions */}
          <div className="px-4 pb-2">
            <div className="flex flex-wrap gap-1">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  disabled={isLoading}
                  className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded-full transition-colors duration-200 disabled:opacity-50"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200/50">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                disabled={isLoading}
                placeholder={isAdmin ? "Ask about franchise operations..." : "Type your message..."}
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg bg-white/80 focus:border-indigo-500 focus:outline-none text-sm disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className={`p-2 rounded-lg transition-colors duration-200 text-white disabled:opacity-50 ${
                  isAdmin ? "bg-red-500 hover:bg-red-600" : "bg-indigo-500 hover:bg-indigo-600"
                }`}
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}