import { useEffect, useState } from 'react'
import './ChatAssistant.css'

function getSessionId() {
  let sessionId = localStorage.getItem('session_id')

  if (!sessionId) {
    sessionId = crypto.randomUUID()
    localStorage.setItem('session_id', sessionId)
  }

  return sessionId
}

function ChatAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  async function sendMessage(customMessage) {
    const userMessage = (customMessage ?? message).trim()

    if (!userMessage || loading) return

    setMessages(prev => [
      ...prev,
      { role: 'user', text: userMessage }
    ])

    setMessage('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')

      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && {
            'Authorization': `Bearer ${token}`
          })
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: getSessionId()
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Backend error')
      }

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: data.reply,
          comparison: data.comparison
        }
      ])

    } catch (error) {
      console.log('Chat error:', error)

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: 'Something went wrong. Please try again. 💗'
        }
      ])

    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    function handleAddToCart(event) {
      const productMessage = event.detail?.message

      if (productMessage) {
        setIsOpen(true)
        sendMessage(productMessage)
      }
    }

    window.addEventListener('celeste:add-to-cart', handleAddToCart)

    return () => {
      window.removeEventListener('celeste:add-to-cart', handleAddToCart)
    }
  }, [loading])

  const suggestedReplies = [
    {
      label: 'Show me bracelets 🎀',
      message: 'Show me some bracelets'
    },
    {
      label: 'Under ₹200 ✨',
      message: 'Show me jewellery under ₹200'
    },
    {
      label: 'Help me choose 💗',
      message: 'Help me choose jewellery'
    }
  ]

  return (
    <div className="chat-assistant">

      <button
        className="chat-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? 'Close Chat ✕' : 'Chat with Celeste AI 🎀'}
      </button>

      {isOpen && (
        <div className="chat-window">

          <div className="chat-header">
            <h3>Celeste AI 🎀</h3>
            <p>Your Personal Jewellery Bestie ✨</p>
          </div>

          <div className="chat-messages">

            {messages.length === 0 && (
              <div className="chat-welcome">
                <h3>Hey, gorgeous! 🎀</h3>
                <p>
                  Welcome to CELESTE ROSE ✨
                  <br />
                  Let's find something you'll absolutely love! 💗
                </p>
              </div>
            )}

            {messages.map((msg, index) => (
              <div key={index} className={`message-container ${msg.role}`}>

                <div className={`message-bubble ${msg.role}`}>
                  {msg.text}
                </div>

                {msg.comparison?.products?.length > 0 && (

                  <div className="comparison-section">

                    <h3>🎀 Your Jewellery Match-Up ✨</h3>

                    <div className="comparison-products">

                      {msg.comparison.products.map((product, productIndex) => (

                        <div
                          className="comparison-card"
                          key={`${product.id}-${productIndex}`}
                        >

                          <div className="comparison-image">
                            <span>CELESTE ROSE ✨</span>
                          </div>

                          <div className="comparison-info">

                            <h4>{product.name}</h4>

                            <p className="comparison-colour">
                              {product.color}
                            </p>

                            <h3 className="comparison-price">
                              ₹{Number(product.price).toFixed(2)}
                            </h3>

                            <div className="comparison-details">

                              <p>
                                <span>Style</span>
                                <strong>
                                  {product.style_type || 'Not specified'}
                                </strong>
                              </p>

                              <p>
                                <span>Availability</span>
                                <strong>
                                  {product.stock > 0
                                    ? `${product.stock} available`
                                    : 'Out of stock'}
                                </strong>
                              </p>

                              {product.occasion && (
                                <p>
                                  <span>Occasion</span>
                                  <strong>{product.occasion}</strong>
                                </p>
                              )}

                            </div>

                            <button
                              className="comparison-add-button"
                              disabled={loading || product.stock <= 0}
                              onClick={() =>
                                sendMessage(
                                  `I want to add ${product.name} in ${product.color} to my cart.`
                                )
                              }
                            >
                              {product.stock > 0
                                ? 'Add to Cart 🎀'
                                : 'Out of Stock'}
                            </button>

                          </div>

                        </div>

                      ))}

                    </div>

                  </div>

                )}

              </div>
            ))}

            {loading && <p className="typing-indicator">Celeste AI is thinking... 🎀✨</p>}

            {!loading && (
              <div className="suggested-replies">

                <p>Little suggestions for you 💗</p>

                <div className="suggested-reply-buttons">

                  {suggestedReplies.map((reply, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(reply.message)}
                    >
                      {reply.label}
                    </button>
                  ))}

                </div>

              </div>
            )}

          </div>

          <div className="chat-input">

            <input
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') sendMessage()
              }}
              placeholder="Ask about our jewellery..."
            />

            <button
              onClick={() => sendMessage()}
              disabled={loading}
            >
              Send ✨
            </button>

          </div>

        </div>
      )}

    </div>
  )
}

export default ChatAssistant