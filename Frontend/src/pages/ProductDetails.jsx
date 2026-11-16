import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import './ProductDetails.css'

function ProductDetails() {
  const { id } = useParams()
  
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchProduct() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/products/${id}`
        )

        if (!response.ok) {
          throw new Error('Product not found')
        }

        const data = await response.json()
        setProduct(data)

      } catch (error) {
        setError(error.message)

      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  if (loading) {
    return <p className="product-loading">Loading product...</p>
  }

  if (error) {
    return <p className="product-error">{error}</p>
  }

  return (
    <div className="product-details-page">
      <Navbar />

      <div className="product-details-container">

        <div className="product-details-image">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} />
          ) : (
            <div className="image-placeholder">
              <span>CELESTE ROSE</span>
              <p>Elegance in every detail</p>
            </div>
          )}
        </div>

        <div className="product-details-info">

          <p className="product-category">
            {product.category}
          </p>

          <h1>{product.name}</h1>

          <p className="product-sku">
            Product Code: {product.sku}
          </p>

          <div className="product-price">
            ₹{Number(product.price).toFixed(2)}
          </div>

          {product.discount_percent > 0 && (
            <p className="product-discount">
              {product.discount_percent}% OFF
            </p>
          )}

          <div className="product-divider"></div>

          <p className="product-color">
            Colour: <strong>{product.color || 'Not specified'}</strong>
          </p>

          <p className="product-description">
            {product.description || 'A beautiful addition to your jewellery collection.'}
          </p>

          <p className="product-stock">
            {product.stock > 0
              ? `In Stock (${product.stock} available)`
              : 'Currently Out of Stock'}
          </p>

<button
  className="add-to-cart-button"
  disabled={product.stock <= 0}
  onClick={() => {
  window.dispatchEvent(new CustomEvent('celeste:add-to-cart', {
    detail: {
      message: `I want to add ${product.name} to my cart.`
    }
  }))
}}
>
  
             {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
          </button>

        </div>
      </div>
    </div>
  )
}

export default ProductDetails