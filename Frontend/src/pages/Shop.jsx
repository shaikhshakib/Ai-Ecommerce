import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import './Shop.css'

function Shop() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortOrder, setSortOrder] = useState('default')

  useEffect(() => {
    async function fetchProducts() {
      try {
        const response = await fetch('http://127.0.0.1:8000/products')

        if (!response.ok) {
          throw new Error('Unable to fetch products')
        }

        const data = await response.json()
        setProducts(data)

      } catch (error) {
        setError(error.message)

      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  // Apply search and category filters
  const filteredProducts = products
  .filter((product) => {
    const matchesCategory =
      selectedCategory === 'All' ||
      product.category.toLowerCase() === selectedCategory.toLowerCase()

    return matchesCategory
  })
  .map((product) => {
    const search = searchTerm.toLowerCase().trim()
    const name = product.name.toLowerCase()
    const category = product.category.toLowerCase()
    const color = (product.color || '').toLowerCase()

    let priority = 5

    if (name.startsWith(search)) {
      priority = 1
    } else if (name.includes(search)) {
      priority = 2
    } else if (category.includes(search)) {
      priority = 3
    } else if (color.includes(search)) {
      priority = 4
    }

    return { ...product, searchPriority: priority }
  })
  .filter((product) => {
    return (
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (product.color || '').toLowerCase().includes(searchTerm.toLowerCase())
    )
  })
  .sort((a, b) => a.searchPriority - b.searchPriority)
  const sortedProducts = [...filteredProducts].sort((a, b) => {
  if (sortOrder === 'low-to-high') {
    return Number(a.price) - Number(b.price)
  }

  if (sortOrder === 'high-to-low') {
    return Number(b.price) - Number(a.price)
  }

  return 0
})
  return (
    <div className="shop-page">
      <Navbar />

      <section className="shop-header">
        <p>CURATED WITH LOVE</p>
        <h1>Our Collection</h1>
        <span>Discover jewellery that celebrates your elegance.</span>
      </section>

      {/* Search Bar */}
      <div className="shop-search">
        <input
          type="text"
          placeholder="Search jewellery by name or colour..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
    {/* Price Sorting */}
<div className="shop-sorting">
  <label htmlFor="sort-price">Sort by:</label>

  <select
    id="sort-price"
    value={sortOrder}
    onChange={(e) => setSortOrder(e.target.value)}
  >
    <option value="default">Default</option>
    <option value="low-to-high">Price: Low to High</option>
    <option value="high-to-low">Price: High to Low</option>
  </select>
</div>
      {/* Category Filters */}
      <div className="shop-filters">
        {['All', 'Pendant', 'Bracelet', 'Bangles', 'Earrings', 'Ring', 'Other'].map((item) => (
          <button
            key={item}
            className={selectedCategory === item ? 'active' : ''}
            onClick={() => setSelectedCategory(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <section className="shop-products">
        {loading && <p>Loading products...</p>}

        {error && <p>{error}</p>}

        {!loading && !error && (
          <>
            <p className="product-count">
              Showing {filteredProducts.length} products
            </p>

            {filteredProducts.length === 0 ? (
              <p className="no-products">No matching products found.</p>
            ) : (
              <div className="product-grid">
                {sortedProducts.map((product) => (
                  <div className="shop-product-card" key={product.id}>
                    <div className="product-image-placeholder">
                      <span>CELESTE ROSE</span>
                    </div>

                    <div className="shop-product-info">
                      <p>{product.category}</p>
                      <h3>{product.name}</h3>
                      <strong>₹{Number(product.price).toFixed(2)}</strong>
                      <button>View Product</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </div>
  )
}

export default Shop