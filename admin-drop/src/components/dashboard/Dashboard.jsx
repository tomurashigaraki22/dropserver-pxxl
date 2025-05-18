import React, { useEffect, useState } from 'react'
import { Line, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function Dashboard() {
  const [monthlySignups, setMonthlySignups] = useState([])

  const [subscriptionRevenue, setSubscriptionRevenue] = useState({
    monthly: { revenue: 0, drivers: 0 },
    yearly: { revenue: 0, drivers: 0 }
  })
  const [dashboardStats, setDashboardStats] = useState({
    totalUsers: 0,
    totalRides: 0,
    activeDrivers: 0,
    revenue: subscriptionRevenue.yearly.revenue.toLocaleString(),
    completedRides: 0,
    cancelledRides: 0,
    activeUsers: 0
  })
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    fetchMonthlySignups()
    fetchDashboardStats()
    fetchSubscriptionRevenue()
  }, [])

  const fetchSubscriptionRevenue = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-subscription-revenue')
      const data = await response.json()
      if (data.status === 200) {
        setSubscriptionRevenue(data.data)
      }
    } catch (error) {
      console.error('Error fetching subscription revenue:', error)
    }
  }

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-dashboard-stats')
      const data = await response.json()
      if (data.status === 200) {
        console.log("Dash stats: ", data)
        setDashboardStats(data.data)
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
    }
  }

  const fetchMonthlySignups = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-monthly-signups')
      const data = await response.json()
      if (data.status === 200) {
        setMonthlySignups(data.data)
      }
    } catch (error) {
      console.error('Error fetching monthly signups:', error)
    }
  }

  const chartData = {
    labels: monthlySignups.map(item => item.month),
    datasets: [
      {
        label: 'Monthly Signups',
        data: monthlySignups.map(item => item.count),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: 'Monthly User Signups'
      }
    }
  }

  const revenueChartData = {
    labels: ['Monthly Revenue', 'Rest of Year'],
    datasets: [{
      data: [
        subscriptionRevenue.monthly.revenue,
        subscriptionRevenue.yearly.revenue - subscriptionRevenue.monthly.revenue
      ],
      backgroundColor: ['rgb(153, 102, 255)', 'rgb(200, 200, 200)']
    }]
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Total Users</h2>
          <p className="text-4xl font-bold text-primary">{dashboardStats.totalUsers}</p>
          <p className="text-sm text-gray-500 mt-2">Active: {dashboardStats.activeUsers}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Total Rides</h2>
          <p className="text-4xl font-bold text-primary">{dashboardStats.totalRides}</p>
          <div className="flex justify-between text-sm text-gray-500 mt-2">
            <span>Completed: {dashboardStats.completedRides}</span>
            <span>Cancelled: {dashboardStats.cancelledRides}</span>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Active Drivers</h2>
          <p className="text-4xl font-bold text-primary">{dashboardStats.activeDrivers}</p>
          <p className="text-sm text-gray-500 mt-2">Online now</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Total Revenue</h2>
          <p className="text-4xl font-bold text-primary">₦{dashboardStats.revenue.toLocaleString()}</p>
          <p className="text-sm text-gray-500 mt-2">From all transactions</p>
        </div>
      </div>
      
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="h-[400px]">
            {isMobile ? (
              <Pie 
                data={{
                  labels: monthlySignups.map(item => item.month),
                  datasets: [{
                    data: monthlySignups.map(item => item.count),
                    backgroundColor: [
                      'rgb(75, 192, 192)',
                      'rgb(255, 99, 132)',
                      'rgb(54, 162, 235)',
                      'rgb(255, 206, 86)',
                      'rgb(153, 102, 255)'
                    ]
                  }]
                }}
                options={chartOptions}
              />
            ) : (
              <Line data={chartData} options={chartOptions} />
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="text-center mb-4">
            <h2 className="text-xl font-semibold">Yearly Subscription Revenue</h2>
            <p className="text-3xl font-bold text-primary mt-2">
              ₦{subscriptionRevenue.yearly.revenue.toLocaleString()}
            </p>
            <p className="text-gray-500">Total Subscribed Drivers: {subscriptionRevenue.yearly.drivers}</p>
          </div>
          <div className="h-[300px]">
            <Pie 
              data={revenueChartData} 
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top'
                  },
                  title: {
                    display: true,
                    text: 'Revenue Distribution'
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard