import { Link, useLocation, useNavigate } from 'react-router-dom'
import './Navbar.css'

function Navbar() {
    const location = useLocation()
    const navigate = useNavigate()

    const isLoggedIn = !!localStorage.getItem('access_token')

    function handleLogout() {
        localStorage.removeItem('access_token')

        const guestSessionId = crypto.randomUUID()
        localStorage.setItem('session_id', guestSessionId)

        navigate('/')
    }

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-logo">
                CELESTE ROSE
                <span>Elegance in every detail</span>
            </Link>

            <div className="navbar-links">
                <Link to="/">Home</Link>
                <Link to="/shop">Shop</Link>

                {isLoggedIn ? (
                    <>
                        <Link to="/account">My Account</Link>
                        <button className="logout-button" onClick={handleLogout}>
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login">Login</Link>
                        <Link to="/register" className="nav-register">
                            Sign Up
                        </Link>
                    </>
                )}
            </div>
        </nav>
    )
}

export default Navbar