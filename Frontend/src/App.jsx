import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Account from './pages/Account'
import Home from './pages/Home'
import Register from './pages/Register'
import Login from './pages/Login'
import Shop from './pages/Shop'

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Home />} />
        <Route path="/shop" element={<Shop />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account />} />
        
      </Routes>
    </BrowserRouter>
  )
}

export default App