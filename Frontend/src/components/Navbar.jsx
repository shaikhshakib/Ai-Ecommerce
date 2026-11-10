import { Link } from 'react-router-dom'
import './Navbar.css'


function Navbar() {
    return (
        <nav className="navbar">
            <Link to="/" className="navbar-logo">CELESTE ROSE
            <span>Elegance in every detail</span>
            </Link>

            <div className="navbar-links">
                <Link to="/">Home</Link>
                <Link to="/shop">Shop</Link>
                <Link to="/login">Login</Link>
                <Link to="/register" className="nav-register">Sign Up</Link>
            </div>
        </nav>
    )
}

export default Navbar