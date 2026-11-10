import { useState } from 'react'
import { Link } from 'react-router-dom'
import './Register.css'


function Register() {

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: ''
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

  if (formData.password !== formData.confirm_password) {
    setError('Passwords do not match. Please try again.')
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        full_name: formData.full_name,
        email: formData.email,
        phone: formData.phone,
        password: formData.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Registration failed')
    }

    setSuccess('Your account has been created successfully!')

    console.log(data)

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

        <p className="auth-subtitle">CREATE YOUR ACCOUNT</p>

        <h1>Join Our World</h1>

        <p className="auth-description">
          Create an account and discover timeless elegance.
        </p>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={formData.full_name}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="tel"
            name="phone"
            placeholder="Mobile Number"
            value={formData.phone}
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

          <input
            type="password"
            name="confirm_password"
            placeholder="Confirm Password"
            value={formData.confirm_password}
            onChange={handleChange}
            required
          />
        {error && <p className="form-error">{error}</p>}

        {success && <p className="form-success">{success}</p>}
          <button type="submit">
            Create Account
          </button>

        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>

      </div>

    </div>
  )
}

export default Register