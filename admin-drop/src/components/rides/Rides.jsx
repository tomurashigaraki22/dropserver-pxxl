import React, { useEffect, useState } from 'react'

function Rides() {
  const [rides, setRides] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchRides()
  }, [])

  const fetchRides = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-all-rides')
      const data = await response.json()
      if (data.status === 200) {
        setRides(data.data)
      }
    } catch (error) {
      console.error('Error fetching rides:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearchTerm(e.target.value)
  }

  const handleStatusFilter = (e) => {
    setStatusFilter(e.target.value)
  }

  const filteredRides = rides.filter(ride => {
    const matchesSearch = 
      ride.id.toString().includes(searchTerm.toLowerCase()) ||
      ride.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ride.driver_name.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = !statusFilter || ride.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Rides Management</h1>
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <input
              type="search"
              placeholder="Search rides..."
              className="px-4 py-2 border rounded-md w-64"
              value={searchTerm}
              onChange={handleSearch}
            />
            <div className="flex gap-2">
              <select 
                className="px-4 py-2 border rounded-md"
                value={statusFilter}
                onChange={handleStatusFilter}
              >
                <option value="">All Status</option>
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ride ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Driver
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredRides.length > 0 ? (
                    filteredRides.map(ride => (
                      <tr key={ride.id}>
                        <td className="px-6 py-4 whitespace-nowrap">{ride.id}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{ride.user_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{ride.driver_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{ride.status}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{new Date(ride.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap" colSpan="5">No rides found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Rides