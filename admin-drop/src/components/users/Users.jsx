import React, { useEffect, useState } from 'react'

function Users() {
  const [users, setUsers] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-all-users')
      const data = await response.json()
      console.log("data: ", data)
      console.log("response: ", response)
      if (data.status === 200) {
        setUsers(data.data)
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearchTerm(e.target.value)
  }

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getVerificationStatus = (user) => {
    if (user.user_type === 'driver') {
      return user.status
    }
    return 'Not Applicable'
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Users Management</h1>
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <input
              type="search"
              placeholder="Search users..."
              className="px-4 py-2 border rounded-md w-64"
              value={searchTerm}
              onChange={handleSearch}
            />
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
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Verification Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.length > 0 ? (
                    filteredUsers.map(user => (
                      <tr key={user.email}>
                        <td className="px-6 py-4 whitespace-nowrap">{user.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{user.phone_number}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{user.user_type}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{getVerificationStatus(user)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="px-6 py-4 whitespace-nowrap" colSpan="4">No users found</td>
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

export default Users