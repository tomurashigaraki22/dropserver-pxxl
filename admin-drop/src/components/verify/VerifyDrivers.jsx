import React, { useEffect, useState } from 'react'
import { FaEye } from 'react-icons/fa'

function VerifyDrivers() {
  const [drivers, setDrivers] = useState([])
  const [verificationDetails, setVerificationDetails] = useState([])
  const [selectedImage, setSelectedImage] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDrivers()
    fetchVerificationDetails()
  }, [])

  const fetchDrivers = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-all-users')
      const data = await response.json()
      if (data.status === 200) {
        // Filter only drivers
        const driversList = data.data.filter(user => user.user_type === 'driver')
        setDrivers(driversList)
      }
    } catch (error) {
      console.error('Error fetching drivers:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchVerificationDetails = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/getVerificationDetails')
      const data = await response.json()
      if (data.verificationdetails) {
        console.log("data verification: ", data)
        setVerificationDetails(data.verificationdetails)
      }
    } catch (error) {
      console.error('Error fetching verification details:', error)
    }
  }

  const updateVerificationStatus = async (email, status) => {
    try {
      const response = await fetch(`https://716b-51-20-79-138.ngrok-free.app/updateVerificationStatus/${email}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
      })

      if (response.ok) {
        // Refresh the data after update
        fetchVerificationDetails()
        alert(`Driver ${status} successfully!`)
      } else {
        alert('Failed to update status')
      }
    } catch (error) {
      console.error('Error updating status:', error)
      alert('Error updating status')
    }
  }

  const viewImage = (imageUrl) => {
    setSelectedImage(imageUrl)
    setIsModalOpen(true)
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Driver Verification</h1>
      <div className="bg-white rounded-lg shadow-md">
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
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
                    Documents
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {verificationDetails.map((detail) => (
                  <tr key={detail.email}>
                    <td className="px-6 py-4 whitespace-nowrap">{detail.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{detail.phone_number}</td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-4">
                        <div className="flex flex-col items-center">
                          <p className="text-sm text-gray-500 mb-1">Driver</p>
                          {detail.driver_photo ? (
                            <button
                              onClick={() => viewImage(detail.driver_photo)}
                              className="text-blue-600 hover:text-blue-800"
                              title="View Driver Photo"
                            >
                              <FaEye className="w-5 h-5" />
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">No photo</span>
                          )}
                        </div>
                        <div className="flex flex-col items-center">
                          <p className="text-sm text-gray-500 mb-1">License</p>
                          {detail.license_photo ? (
                            <button
                              onClick={() => viewImage(detail.license_photo)}
                              className="text-blue-600 hover:text-blue-800"
                              title="View License Photo"
                            >
                              <FaEye className="w-5 h-5" />
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">No photo</span>
                          )}
                        </div>
                        <div className="flex flex-col items-center">
                          <p className="text-sm text-gray-500 mb-1">Car</p>
                          {detail.car_photo ? (
                            <button
                              onClick={() => viewImage(detail.car_photo)}
                              className="text-blue-600 hover:text-blue-800"
                              title="View Car Photo"
                            >
                              <FaEye className="w-5 h-5" />
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">No photo</span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${detail.status === 'approved' ? 'bg-green-100 text-green-800' : 
                          detail.status === 'rejected' ? 'bg-red-100 text-red-800' : 
                          'bg-yellow-100 text-yellow-800'}`}
                      >
                        {detail.status.charAt(0).toUpperCase() + detail.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {detail.status === 'pending' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => updateVerificationStatus(detail.email, 'approved')}
                            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => updateVerificationStatus(detail.email, 'rejected')}
                            className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                          >
                            Reject
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Image Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg max-w-2xl">
            <img src={selectedImage} alt="Document" className="max-h-[80vh]" />
            <button
              onClick={() => setIsModalOpen(false)}
              className="mt-4 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default VerifyDrivers