import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Register.css'

function Login() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  function handleChange(e) {
  setFormData({
    ...formData,
    [e.target.name]: e.target.value
  })
}
  async function handleSubmit(e) {
  e.preventDefault()

  setError('')
  setSuccess('')

  try {
    const response = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify({
        email: formData.email,
        password: formData.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed')
    }

    localStorage.setItem('access_token', data.access_token)

// Create a customer-specific cart session
    localStorage.setItem('session_id', `user-${data.user.id}`)

    navigate('/account')

  } catch (error) {
    setError(error.message)
  }
}

  return (
    <div className="auth-page">

      <div className="auth-card">

        <Link to="/" className="auth-logo">
          CELESTE ROSE
        </Link>

        <p className="auth-subtitle">WELCOME BACK</p>

        <h1>Welcome Back</h1>

        <p className="auth-description">
          Sign in to continue your journey with us.
        </p>

        <form onSubmit={handleSubmit}>

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        {error && <p className="form-error">{error}</p>}

        {success && <p className="form-success">{success}</p>}
          <button type="submit">
            Login
          </button>

        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Create Account</Link>
        </p>

      </div>

    </div>
  )
}

export default Login