import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Account.css'

function Account() {
  const [user, setUser] = useState(null)
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  useEffect(() => {
    async function fetchAccountData() {
      const token = localStorage.getItem('access_token')

      if (!token) {
        navigate('/login')
        return
      }

      const headers = {
        'Authorization': `Bearer ${token}`
      }

      try {
        // Fetch customer details
        const userResponse = await fetch(
          'http://127.0.0.1:8000/auth/me',
          { headers }
        )

        const userData = await userResponse.json()

        if (!userResponse.ok) {
          throw new Error(userData.detail || 'Unable to fetch account')
        }

        setUser(userData.user)

        // Fetch customer orders
        const orderResponse = await fetch(
          'http://127.0.0.1:8000/orders/my',
          { headers }
        )

        const orderData = await orderResponse.json()

        if (!orderResponse.ok) {
          throw new Error(orderData.detail || 'Unable to fetch orders')
        }

        setOrders(orderData.orders)

      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    fetchAccountData()
  }, [navigate])

  function handleLogout() {
  localStorage.removeItem('access_token')

  // Generate a fresh guest session
  const guestSessionId = crypto.randomUUID()

  localStorage.setItem('session_id', guestSessionId)

  navigate('/login')
}

  if (loading) {
    return <div className="account-page">Loading your account...</div>
  }

  return (
    <div className="account-page">

      <div className="account-header">
        <p className="account-tagline">WELCOME BACK</p>
        <h1>My Account</h1>
        <p>Manage your account and discover your orders.</p>
      </div>

      {error && <p className="account-error">{error}</p>}

      {user && (
        <section className="account-card">
          <h2>Personal Information</h2>

          <p><strong>Name:</strong> {user.full_name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Phone:</strong> {user.phone}</p>
        </section>
      )}

      <section className="orders-section">

        <div className="orders-heading">
          <p className="account-tagline">YOUR PURCHASES</p>
          <h2>My Orders</h2>
        </div>

        {orders.length === 0 ? (

          <div className="empty-orders">
            <h3>No orders yet</h3>
            <p>Your orders will appear here after your purchase.</p>
          </div>

        ) : (

          <div className="orders-list">

            {orders.map((order) => (

              <div className="order-card" key={order.id}>

                <div className="order-top">
                  <h3>Order #{order.id}</h3>

                  <span className="order-status">
                    {order.order_status}
                  </span>
                </div>

                <p>
                  <strong>Order Date:</strong>{' '}
                  {new Date(order.created_at).toLocaleDateString('en-IN')}
                </p>

                <div className="order-products">
  <h4>Products Purchased</h4>

  {order.products.map((product) => (
    <div className="order-product" key={product.product_id}>
      <span>
        {product.product_name} × {product.quantity}
      </span>

      <span>
        ₹{(product.price * product.quantity).toFixed(2)}
      </span>
    </div>
  ))}
</div>

<div className="order-total">
  <strong>Total Amount</strong>
  <strong>₹{Number(order.total_amount).toFixed(2)}</strong>
</div>

              </div>

            ))}

          </div>

        )}

      </section>

      <button className="logout-button" onClick={handleLogout}>
        Logout
      </button>

    </div>
  )
}

export default Account