
import { useEffect, useState } from 'react'
import '../App.css'
import Navbar from '../components/Navbar'
import { Link } from 'react-router-dom'
import './Home.css'

function getSessionId() {
  let sessionId = localStorage.getItem('session_id')

  if (!sessionId) {
    sessionId = crypto.randomUUID()
    localStorage.setItem('session_id', sessionId)
  }

  return sessionId
}


function App() {
  const [products, setProducts] = useState([])
  const [category, setCategory] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [messages, setMessages] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    console.log("Step 2: About to call fetch")
    fetch('http://127.0.0.1:8000/products')
    
      .then(response => response.json())
      .then(data => setProducts(data))
  }, [])

  function searchProducts() {
    let url = 'http://127.0.0.1:8000/products/search?category='
    url += encodeURIComponent(category)
    url += '&max_price=' + (maxPrice || 100000)
    
    fetch(url)
      .then(response => response.json())
      .then(data => setProducts(data))
  }
async function sendMessage() {
  if (!message.trim()) return

  console.log("1. Send button clicked:", message)

  const userMessage = message
  setMessages(prev => [...prev, { role: 'user', text: userMessage }])
  setMessage('')
  setLoading(true)

  try {
    console.log("2. Entered try block")
    console.log("3. Sending request to:", 'http://127.0.0.1:8000/chat')

    const token = localStorage.getItem('access_token')

    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify({
        message: userMessage,
        session_id: getSessionId()
      })
    })

    console.log("4. Response received:", response.status)

    const data = await response.json()
    console.log("5. Backend data:", data)

    if (!response.ok) throw new Error(data.detail || "Backend error")

    setMessages(prev => [...prev, { role: 'assistant', text: data.reply }])

  } catch (error) {
    console.log("ERROR:", error)

    setMessages(prev => [...prev, {
      role: 'assistant',
      text: 'Something went wrong. Please try again.'
    }])

  } finally {
    setLoading(false)
    console.log("6. Request completed")
  }
}
  return (
    <div>
        <Navbar />
      <section className="hero">
  <div className="hero-content">
    <p className="hero-tagline">THE ART OF ELEGANCE</p>

    <h1>
      Jewellery That
      <br />
      Tells Your Story.
    </h1>

    <p className="hero-description">
      Discover timeless pieces designed to make
      every moment a little more beautiful.
    </p>

    <Link to="/shop" className="hero-button">
      Explore Collection
    </Link>
  </div>

  <div className="hero-decoration">
    <span className="hero-flower">✿</span>
    <p>CÉLESTE ROSÉ</p>
    <span>Elegance in Every Detail</span>
  </div>
</section>
    <div className="chatbot">
  <h2>Chat with Celeste AI ✨</h2>

  <div className="chat-messages">
    {messages.map((msg, index) => (
      <p key={index} className={msg.role}>
        {msg.text}
      </p>
    ))}
    {loading && <p>AI is typing...</p>}
  </div>

  <div className="chat-input">
    <input
      value={message}
      onChange={e => setMessage(e.target.value)}
      onKeyDown={e => e.key === 'Enter' && sendMessage()}
      placeholder="Ask me about our jewellery..."
    />

    <button onClick={sendMessage}>Send</button>
  </div>
</div>
      <main>
        <div className="collection-heading">
  <p className="collection-tagline">CURATED WITH LOVE</p>
  <h2>Discover Our Collection</h2>
  <p>Beautiful details. Timeless elegance. Pieces made for you.</p>
</div>

        <div className="search-box">
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
          >
            <option value="">Select Category</option>
            <option value="Pendant">Pendant</option>
            <option value="Bracelet">Bracelet</option>
            <option value="Watch">Watch</option>
            <option value="Rings">Rings</option>
          </select>

          <input
            type="number"
            placeholder="Maximum Price ₹"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
          />

          <button onClick={searchProducts}>Search</button>

          <button onClick={() => window.location.reload()}>
            Show All
          </button>
        </div>

        <div className="products">
          {products.map(product => (
            <div className="product" key={product.id}>
              <h3>{product.name}</h3>
              <p>Category: {product.category}</p>
              <p>Price: ₹{product.price}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}

export default App

