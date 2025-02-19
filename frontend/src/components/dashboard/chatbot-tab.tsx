import { useState, useRef, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Loader2, Send, Bot, User } from 'lucide-react'
import axios from "axios"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

interface Message {
  id: string
  sender: "user" | "bot"
  content: string
  timestamp: Date
}

interface ChatbotTabProps {
  category: string
}

export function ChatbotTab({ category }: ChatbotTabProps) {
  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("script_creation")
  const [scriptContent, setScriptContent] = useState("")
  const [targetScriptType, setTargetScriptType] = useState("")
  const [isScriptUpdating, setIsScriptUpdating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim() && activeTab !== "script_enhance") return
    if (activeTab === "script_enhance" && (!scriptContent.trim() || !targetScriptType.trim())) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      content: activeTab === "script_enhance" 
        ? `Enhance script to ${targetScriptType} style:\n${scriptContent}`
        : message,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setMessage("")
    setIsLoading(true)

    try {
      const payload = {
        category,
        question: activeTab === "script_enhance" ? `Convert script to ${targetScriptType} style` : message,
        mode: activeTab,
        script_content: activeTab === "script_enhance" ? scriptContent : undefined,
        target_type: activeTab === "script_enhance" ? targetScriptType : undefined,
      }

      const response = await axios.post("http://localhost:5000/api/chat", payload)
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        content: response.data.response,
        timestamp: new Date(response.data.metadata.timestamp),
      }
      setMessages((prev) => [...prev, botMessage])

      // Update script content with animation if in enhance mode
      if (activeTab === "script_enhance") {
        setIsScriptUpdating(true)
        setScriptContent(response.data.response)
        setTimeout(() => setIsScriptUpdating(false), 1000) // Animation duration
      }

    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        content: "Sorry, there was an error processing your request. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="p-6 bg-zinc-900/50 backdrop-blur-lg border-indigo-500/20 shadow-lg transition-all duration-300 ease-in-out hover:shadow-indigo-500/10">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="script_creation">Script Creation</TabsTrigger>
          <TabsTrigger value="script_enhance">Script Enhancer</TabsTrigger>
        </TabsList>
        <TabsContent value="script_creation">
          <div className="flex flex-col h-[600px]">
            <div className="flex-1 overflow-y-auto mb-4 space-y-6 pr-4 scrollbar-thin scrollbar-thumb-indigo-600 scrollbar-track-transparent">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex items-end gap-2 ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  } animate-in slide-in-from-${msg.sender === "user" ? "right" : "left"}`}
                >
                  {msg.sender === "bot" && <Bot className="h-6 w-6 text-indigo-400 mb-3" />}
                  <div
                    className={`group max-w-[80%] transform transition-all duration-300 ease-in-out ${
                      msg.sender === "user"
                        ? "bg-gradient-to-br from-indigo-600 to-indigo-700 text-white"
                        : "bg-zinc-800/80 text-zinc-100"
                    } p-4 rounded-2xl ${
                      msg.sender === "user" ? "rounded-br-sm" : "rounded-bl-sm"
                    } shadow-lg hover:shadow-xl hover:scale-[1.02]`}
                  >
                    <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                  </div>
                  {msg.sender === "user" && <User className="h-6 w-6 text-indigo-400 mb-3" />}
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start items-end gap-2">
                  <Bot className="h-6 w-6 text-indigo-400 mb-3" />
                  <div className="bg-zinc-800/80 p-4 rounded-2xl rounded-bl-sm shadow-lg animate-pulse">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" />
                        <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-150" />
                        <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce delay-300" />
                      </div>
                      <span className="text-indigo-400 text-sm">Thinking</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="flex gap-3 pt-2 border-t border-indigo-500/20">
              <Input
                placeholder="Type your message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
                disabled={isLoading}
                className="bg-zinc-800/50 border-zinc-700 focus:border-indigo-500 focus:ring-indigo-500/50 placeholder:text-zinc-500 text-zinc-100 rounded-xl transition-all duration-300"
              />
              <Button
                onClick={handleSendMessage}
                disabled={isLoading}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 rounded-xl transform transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-indigo-500/20 disabled:opacity-50 disabled:hover:scale-100"
              >
                {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </TabsContent>
        <TabsContent value="script_enhance">
          <div className="flex flex-col h-[600px] space-y-4">
            <div className="space-y-2">
              <Label className="text-zinc-100">Target Script Type</Label>
              <Input
                placeholder="Enter desired script type (e.g., Technical, Conversational, Professional)..."
                value={targetScriptType}
                onChange={(e) => setTargetScriptType(e.target.value)}
                className="bg-zinc-800/50 border-zinc-700 focus:border-indigo-500 focus:ring-indigo-500/50 placeholder:text-zinc-500 text-zinc-100 rounded-xl transition-all duration-300"
              />
            </div>
            <div className="space-y-2 flex-1">
              <Label className="text-zinc-100">Your Script</Label>
              <Textarea
                placeholder="Paste your script here..."
                value={scriptContent}
                onChange={(e) => setScriptContent(e.target.value)}
                className={`h-[400px] bg-zinc-800/50 border-zinc-700 focus:border-indigo-500 focus:ring-indigo-500/50 placeholder:text-zinc-500 text-zinc-100 rounded-xl transition-all duration-300 ${
                  isScriptUpdating ? 'animate-pulse border-indigo-500 shadow-lg shadow-indigo-500/20' : ''
                }`}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !scriptContent.trim() || !targetScriptType.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-6 rounded-xl transform transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-indigo-500/20 disabled:opacity-50 disabled:hover:scale-100"
            >
              {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Enhance Script"}
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  )
}

export default ChatbotTab