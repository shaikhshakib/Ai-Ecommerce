import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Account from './pages/Account'
import Home from './pages/Home'
import Register from './pages/Register'
import Login from './pages/Login'
import Shop from './pages/Shop'
import ProductDetails from './pages/ProductDetails'
import ChatAssistant from './pages/ChatAssistant'
import Admin from './pages/Admin'
import AdminRoute from './components/AdminRoute'
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin" element={
    <AdminRoute>
      <Admin />
    </AdminRoute>
  }
/>
        <Route path="/" element={<Home />} />
        <Route path="/shop" element={<Shop />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account />} />
        <Route path="/product/:id" element={<ProductDetails />} />
      </Routes>
      <ChatAssistant />
    </BrowserRouter>
  )
}

export default App