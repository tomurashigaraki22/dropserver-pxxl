import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/auth/Login'
import Dashboard from './components/dashboard/Dashboard'
import Users from './components/users/Users'
import Analytics2 from './components/analytics/Analytics2'
import Rides from './components/rides/Rides'
import Sidebar from './components/Sidebar'
import VerifyDrivers from './components/verify/VerifyDrivers'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const auth = localStorage.getItem('isAuthenticated')
    const authToken = localStorage.getItem('authToken')
    
    // Check both authentication flag and token
    if (auth === 'true' && authToken) {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogout = () => {
    setIsAuthenticated(false)
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('authToken')
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {!isAuthenticated ? (
          <Login setIsAuthenticated={setIsAuthenticated} />
        ) : (
          <div className="flex h-screen overflow-hidden">
            <Sidebar handleLogout={handleLogout} />
            <main className="flex-1 overflow-y-auto p-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/users" element={<Users />} />
                <Route path="/drop-analytics" element={<Analytics2 />} />
                <Route path="/rides" element={<Rides />} />
                <Route path="*" element={<Navigate to="/" />} />
                <Route path='/verify-drivers' element={<VerifyDrivers/>} />
              </Routes>
            </main>
          </div>
        )}
      </div>
    </Router>
  )
}

export default App
