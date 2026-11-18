import { useEffect, useState } from 'react'
import './Admin.css'




function Admin() {
    const [stats, setStats] = useState({
  total_sales: 0,
  total_orders: 0,
  total_products: 0,
  total_customers: 0
})
const [products, setProducts] = useState([])
const [orders, setOrders] = useState([])
const [chatLogs, setChatLogs] = useState([])
const [salesAnalytics, setSalesAnalytics] = useState({
    monthly_sales: [],
    average_order_value: 0,
    order_status_breakdown: []
})
const [orderFilter, setOrderFilter] = useState('All')
const [topProducts, setTopProducts] = useState([])
const [newProduct, setNewProduct] = useState({
  name: '',
  category: '',
  price: ''
})
const [notification, setNotification] = useState('')
const [editProduct, setEditProduct] = useState(null)




useEffect(() => {
  async function fetchDashboard() {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/admin/dashboard',
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (!response.ok) throw new Error('Failed to fetch dashboard data')

      const data = await response.json()
      setStats(data)

    } catch (error) {
      console.error(error)
    }
  }

  fetchDashboard()
}, [])

useEffect(() => {
  async function fetchTopProducts() {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/admin/top-products',
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (!response.ok) throw new Error('Failed to fetch top products')

      const data = await response.json()
      setTopProducts(data)

    } catch (error) {
      console.error(error)
    }
  }

  fetchTopProducts()
}, [])
useEffect(() => {
  async function fetchProducts() {
    try {
      const response = await fetch('http://127.0.0.1:8000/products')

      if (!response.ok) {
        throw new Error('Failed to fetch products')
      }

      const data = await response.json()
      setProducts(data)

    } catch (error) {
      console.error(error)
    }
  }

  fetchProducts()
}, [])
useEffect(() => {
    async function fetchOrders() {
        try {
            const response = await fetch(
                'http://127.0.0.1:8000/admin/orders',
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                }
            )

            if (!response.ok) {
                throw new Error('Failed to fetch orders')
            }

            const data = await response.json()
            setOrders(data.orders)

        } catch (error) {
            console.error('Orders Error:', error)
        }
    }

    fetchOrders()
}, [])
useEffect(() => {
    async function fetchChatLogs() {
        try {
            const response = await fetch(
                'http://127.0.0.1:8000/admin/chat-logs',
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                }
            )

            if (!response.ok) {
                throw new Error('Failed to fetch chat logs')
            }

            const data = await response.json()
            setChatLogs(data)

        } catch (error) {
            console.error('Chat Logs Error:', error)
        }
    }

    fetchChatLogs()
}, [])
useEffect(() => {
    const fetchSalesAnalytics = async () => {
        try {
            const token = localStorage.getItem('access_token')

            const response = await fetch('http://127.0.0.1:8000/admin/sales-analytics', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })

            const data = await response.json()

            if (response.ok) {
                setSalesAnalytics(data)
            }
        } catch (error) {
            console.error('Sales Analytics Error:', error)
        }
    }

    fetchSalesAnalytics()
}, [])



async function handleUpdateOrderStatus(orderId, newStatus) {
    try {
        const params = new URLSearchParams({
            status: newStatus
        })

        const response = await fetch(
            `http://127.0.0.1:8000/admin/orders/${orderId}/status?${params}`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`
                }
            }
        )

        if (!response.ok) {
            throw new Error('Failed to update order status')
        }

        const data = await response.json()

        setNotification(data.message + ' ✨')
        setTimeout(() => setNotification(''), 3000)

        // Update order status locally
        setOrders(prevOrders =>
            prevOrders.map(order =>
                order.id === orderId
                    ? { ...order, order_status: newStatus }
                    : order
            )
        )

    } catch (error) {
        console.error(error)
        setNotification('Could not update order status.')
        setTimeout(() => setNotification(''), 3000)
    }
}

async function handleAddProduct(e) {
    e.preventDefault()

    try {
        const params = new URLSearchParams({
            name: newProduct.name,
            category: newProduct.category,
            price: newProduct.price
        })

        const response = await fetch(
            `http://127.0.0.1:8000/products?${params}`,
            {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`
                }
            }
        )

        if (!response.ok) {
            throw new Error('Failed to add product')
        }

        setNotification('Product added successfully! ✨')
setTimeout(() => setNotification(''), 3000)

        setNewProduct({
            name: '',
            category: '',
            price: ''
        })

        const updatedProducts = await fetch('http://127.0.0.1:8000/products')
        setProducts(await updatedProducts.json())
        const dashboardResponse = await fetch('http://127.0.0.1:8000/admin/dashboard', {
    headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
    }
})

setStats(await dashboardResponse.json())

    } catch (error) {
        console.error(error)
        setNotification('Could not add product. Please try again.')
setTimeout(() => setNotification(''), 3000)
    }
}
async function handleEditProduct(e) {
    e.preventDefault()

    try {
        const params = new URLSearchParams({
            price: editProduct.price
        })

        const response = await fetch(
            `http://127.0.0.1:8000/products/${editProduct.id}?${params}`,
            {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`
                }
            }
        )

        if (!response.ok) {
            throw new Error('Failed to update product')
        }

        setNotification('Product updated successfully! ✨')
        setTimeout(() => setNotification(''), 3000)

        setEditProduct(null)

        const updatedProducts = await fetch('http://127.0.0.1:8000/products')
        setProducts(await updatedProducts.json())

    } catch (error) {
        console.error(error)
        setNotification('Could not update product.')
        setTimeout(() => setNotification(''), 3000)
    }
}
async function handleDeleteProduct(productId) {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/products/${productId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )

    if (!response.ok) throw new Error('Delete failed')

    setNotification('Product deleted successfully! ✨')
    setTimeout(() => setNotification(''), 3000)

    const updatedProducts = await fetch('http://127.0.0.1:8000/products')
    setProducts(await updatedProducts.json())

    const updatedStats = await fetch('http://127.0.0.1:8000/admin/dashboard', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    setStats(await updatedStats.json())

  } catch (error) {
    console.error(error)
    setNotification('Could not delete product.')
    setTimeout(() => setNotification(''), 3000)
  }
}
    return (
        <div className='admin-layout'>
            <aside className='admin-sidebar'>
        <h2>CELESTE ROSE</h2>
        <p>ADMIN PANEL</p>

        <nav>
            <a href="#overview">Overview</a>
            <a href="#products">Products</a>
            <a href="#orders">Orders</a>
            <a href="#analytics">Analytics</a>    
            <a href="#chats">Chats</a>
            <a href="#ai-monitoring">AI - Monitoring</a>
        



        </nav>
</aside>

        <main className='admin-main'>

            {notification && (
    <div className="admin-notification">
        {notification}
    </div>
)}
        <header className='admin-header'>
        <div>

            <h1>Dashboard Overview</h1>
            <p>Welcome to your CELESTE ROSE admin panel.</p>
        </div>
        <span>Administrator</span>
        </header>

        <section className='admin-stats' id='overview'>
        <div className="admin-card">
            <h3>Total Sales</h3>
            <p>₹{stats.total_sales.toLocaleString('en-IN')}</p>
        </div>

        <div className="admin-card">
            <h3>Total Orders</h3>
            <p>{stats.total_orders}</p>
        </div>
        
        <div className="admin-card">
            <h3>Total Products</h3>
            <p>{stats.total_products}</p>
        </div>
        
        <div className="admin-card">
            <h3>Total Customers</h3>
            <p>{stats.total_customers}</p>
        </div>


        </section>
        <section className="admin-section" id="top-products">
    <h2>Top-Selling Products</h2>

    <table className="admin-table">
        <thead>
            <tr>
                
                <th>Product</th>
                <th>Category</th>
                <th>Price</th>
                <th>Units Sold</th>
            </tr>
        </thead>

        <tbody>
            {topProducts.map((product) => (
                <tr key={product.id}>
                    <td>{product.name}</td>
                    <td>{product.category}</td>
                    <td>₹{product.price}</td>
                    <td>{product.total_sold}</td>
                </tr>
            ))}
        </tbody>
    </table>
</section>
<section className="admin-section" id="products">
    <h2>Product Management</h2>
    <form className="admin-product-form" onSubmit={handleAddProduct}>
    <input
        type="text"
        placeholder="Product Name"
        value={newProduct.name}
        onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
        required
    />

    <input
        type="text"
        placeholder="Category"
        value={newProduct.category}
        onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
        required
    />

    <input
        type="number"
        placeholder="Price"
        value={newProduct.price}
        onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
        required
    />

    <button type="submit">Add Product</button>
</form>
{editProduct && (
    <form className="admin-product-form" onSubmit={handleEditProduct}>
        <h3>Edit Product: {editProduct.name}</h3>

        <input
            type="number"
            placeholder="New Price"
            value={editProduct.price}
            onChange={(e) => setEditProduct({
                ...editProduct,
                price: e.target.value
            })}
            required
        />

        <button type="submit">Save Changes</button>

        <button
            type="button"
            onClick={() => setEditProduct(null)}
        >
            Cancel
        </button>
    </form>
)}
    <table className="admin-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Action</th>
                <td>
</td>
            </tr>
        </thead>

        <tbody>
            {products.map((product) => (
                <tr key={product.id}>
                    <td>{product.id}</td>
                    <td>{product.name}</td>
                    <td>{product.category}</td>
                    <td>₹{product.price}</td>
                    <td>{product.stock}</td>
                    <td>
    <button
        onClick={() => setEditProduct({
            id: product.id,
            name: product.name,
            price: product.price
        })}
    >
        Edit
    </button>
    <button
  onClick={() => handleDeleteProduct(product.id)}
  style={{ background: '#a94455', marginLeft: '8px' }}
>
  Delete
</button>
</td>
                </tr>
            ))}
        </tbody>
    </table>
</section>
<section className="admin-section" id="orders">
    <h2>Order Management</h2>

    <div className="order-filters">
        {['All', 'Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'].map(status => (
            <button
                key={status}
                onClick={() => setOrderFilter(status)}
                className={orderFilter === status ? 'active' : ''}
            >
                {status}
            </button>
        ))}
    </div>

    <div className="admin-orders">
        {orders
            .filter(order =>
                orderFilter === 'All' || order.order_status === orderFilter
            )
            .map(order => (
                <div className="admin-order-card" key={order.id}>

                    <div className="admin-order-header">
                        <div>
                            <h3>Order #{order.id}</h3>
                            <p>
                                {new Date(order.created_at).toLocaleString('en-IN')}
                            </p>
                        </div>

                        <span className={`order-status ${order.order_status.toLowerCase()}`}>
                            {order.order_status}
                        </span>
                    </div>

                    <div className="admin-order-customer">
                        <p><strong>Customer:</strong> {order.customer_name || 'Guest'}</p>
                        <p><strong>Email:</strong> {order.email || 'Not available'}</p>
                        <p><strong>Phone:</strong> {order.phone || 'Not available'}</p>
                        <p><strong>Address:</strong> {order.address || 'Not available'}</p>
                    </div>

                    <div className="admin-order-products">
                        <h4>Products</h4>

                        {order.products.map((product, index) => (
                            <div key={index} className="admin-order-product">
                                <span>
                                    {product.product_name} × {product.quantity}
                                </span>
                                <span>₹{product.price * product.quantity}</span>
                            </div>
                        ))}
                    </div>

                    <div className="admin-order-footer">
                        <strong>Total: ₹{order.total_amount}</strong>

                        <select
                            value={order.order_status}
                            onChange={(e) =>
                                handleUpdateOrderStatus(order.id, e.target.value)
                            }
                        >
                            {['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'].map(status => (
                                <option key={status} value={status}>
                                    {status}
                                </option>
                            ))}
                        </select>
                    </div>

                </div>
            ))}
    </div>
</section>
{/* Sales Analytics */}
<section className="admin-section" id="analytics">
    <h2>Sales Analytics</h2>

    <div className="analytics-summary">
        <div className="analytics-card">
            <h3>Average Order Value</h3>
            <p>₹{salesAnalytics.average_order_value.toFixed(2)}</p>
        </div>

        <div className="analytics-card">
            <h3>Total Orders</h3>
            <p>
                {salesAnalytics.monthly_sales.reduce(
                    (total, item) => total + item.total_orders, 0
                )}
            </p>
        </div>
    </div>

    <div className="analytics-card">
        <h3>Monthly Sales</h3>

        {salesAnalytics.monthly_sales.length === 0 ? (
            <p>No sales data available.</p>
        ) : (
            salesAnalytics.monthly_sales.map((item) => (
                <div className="monthly-sale" key={item.month}>
                    <span>{item.month}</span>
                    <span>₹{item.revenue.toFixed(2)}</span>
                    <span>{item.total_orders} Orders</span>
                </div>
            ))
        )}
    </div>

    <div className="analytics-card">
        <h3>Order Status Breakdown</h3>

        {salesAnalytics.order_status_breakdown.map((item) => (
            <div className="monthly-sale" key={item.order_status}>
                <span>{item.order_status}</span>
                <span>{item.count} Orders</span>
            </div>
        ))}
    </div>
</section>

{/* Chat Logs */}
<section className="admin-section" id="chats">
    <h2>Customer Conversations 🎀</h2>
    <p>View conversations between customers and the CELESTE ROSE AI Assistant.</p>

    <div className="chat-logs-container">
        {chatLogs.length === 0 ? (
            <p>No chat conversations available.</p>
        ) : (
            chatLogs.map((log) => (
                <div className="chat-log-card" key={log.id}>
                    <div className="chat-log-header">
                        <strong>{log.customer_name}</strong>
                        <span>{log.role === 'user' ? 'Customer' : 'AI Assistant'}</span>
                    </div>

                    <p className="chat-log-message">{log.message}</p>

                    <div className="chat-log-footer">
                        <small>Session: {log.session_id}</small>
                        <small>
                            {new Date(log.created_at).toLocaleString('en-IN')}
                        </small>
                    </div>
                </div>
            ))
        )}
    </div>
</section>

        </main>

        </div>
    )                 
}

export default Admin