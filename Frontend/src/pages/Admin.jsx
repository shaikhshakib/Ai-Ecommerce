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
        <section className="admin-section" id="analytics">
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
        </main>

        </div>
    )                 
}

export default Admin