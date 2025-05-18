import React, { useEffect, useState } from 'react'
import { Line, Bar, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
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
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

function Analytics2() {
  const [analyticsData, setAnalyticsData] = useState({
    ridesOverview: [],
    revenueTrends: [],
    userGrowth: [],
    popularRoutes: []
  })
  const [revenueView, setRevenueView] = useState('yearly') // default to yearly view
  const [subscriptionRevenue, setSubscriptionRevenue] = useState({
    monthly: { revenue: 0, drivers: 0 },
    yearly: { revenue: 0, drivers: 0 },
    monthly_breakdown: []
  })
  const [driverStats, setDriverStats] = useState({
    total_drivers: 0,
    verified_drivers: 0,
    unverified_drivers: 0
  })

  useEffect(() => {
    fetchAnalyticsData()
    fetchSubscriptionRevenue()
    fetchDriverStats()
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-analytics-data')
      const data = await response.json()
      if (data.status === 200) {
        setAnalyticsData(data.data)
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error)
    }
  }

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

  const fetchDriverStats = async () => {
    try {
      const response = await fetch('https://716b-51-20-79-138.ngrok-free.app/get-driver-verification-stats')
      const data = await response.json()
      if (data.status === 200) {
        setDriverStats(data.data)
      }
    } catch (error) {
      console.error('Error fetching driver stats:', error)
    }
  }

  const driverVerificationData = {
    labels: ['Verified Drivers', 'Unverified Drivers'],
    datasets: [{
      data: [driverStats.verified_drivers, driverStats.unverified_drivers],
      backgroundColor: ['rgb(75, 192, 192)', 'rgb(255, 99, 132)']
    }]
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
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

  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Analytics</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Rides Overview</h2>
          <div className={`${isMobile ? 'h-[500px]' : 'h-[400px]'}`}>
            {isMobile ? (
              <Pie 
                data={{
                  labels: analyticsData.ridesOverview.map(item => item.date),
                  datasets: [{
                    data: analyticsData.ridesOverview.map(item => item.count),
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
              <Line 
                data={{
                  labels: analyticsData.ridesOverview.map(item => item.date),
                  datasets: [{
                    label: 'Total Rides',
                    data: analyticsData.ridesOverview.map(item => item.count),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                  }]
                }} 
                options={chartOptions} 
              />
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">User Growth</h2>
          <div className="h-64">
            {isMobile ? (
              <Pie 
                data={{
                  labels: analyticsData.userGrowth.map(item => item.date),
                  datasets: [{
                    data: analyticsData.userGrowth.map(item => item.count),
                    backgroundColor: [
                      'rgb(255, 99, 132)',
                      'rgb(54, 162, 235)',
                      'rgb(255, 206, 86)',
                      'rgb(75, 192, 192)',
                      'rgb(153, 102, 255)'
                    ]
                  }]
                }}
                options={chartOptions}
              />
            ) : (
              <Line 
                data={{
                  labels: analyticsData.userGrowth.map(item => item.date),
                  datasets: [{
                    label: 'New Users',
                    data: analyticsData.userGrowth.map(item => item.count),
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                  }]
                }}
                options={chartOptions}
              />
            )}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Popular Routes</h2>
          <div className="h-64">
            <Bar 
              data={{
                labels: analyticsData.popularRoutes.map(item => item.route),
                datasets: [{
                  label: 'Number of Rides',
                  data: analyticsData.popularRoutes.map(item => item.count),
                  backgroundColor: 'rgb(54, 162, 235)'
                }]
              }} 
              options={chartOptions} 
            />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Revenue Overview</h2>
            <select
              value={revenueView}
              onChange={(e) => setRevenueView(e.target.value)}
              className="px-3 py-1 border rounded-md"
            >
              <option value="yearly">Yearly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div className="text-center mb-4">
            <p className="text-3xl font-bold text-primary">
              ₦{revenueView === 'yearly' ? subscriptionRevenue.yearly.revenue.toLocaleString() : subscriptionRevenue.monthly.revenue.toLocaleString()}
            </p>
            <p className="text-gray-500">{revenueView === 'yearly' ? 'Total Year Revenue' : 'Total Month Revenue'}</p>
          </div>
          <div className="h-64">
            <Pie data={revenueChartData} options={chartOptions} />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Driver Verification Status</h2>
          </div>
          <div className="text-center mb-4">
            <p className="text-3xl font-bold text-primary">
              {driverStats.total_drivers}
            </p>
            <p className="text-gray-500">Total Drivers</p>
          </div>
          <div className="h-64">
            <Pie 
              data={driverVerificationData} 
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top'
                  },
                  title: {
                    display: true,
                    text: 'Driver Verification Distribution'
                  }
                }
              }} 
            />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Subscription Revenue</h2>
          </div>
          <div className="text-center mb-4">
            <p className="text-3xl font-bold text-primary">
              ₦{subscriptionRevenue.yearly.revenue.toLocaleString()}
            </p>
            <p className="text-gray-500">Total Year Revenue</p>
          </div>
          <div className="h-64">
            <Line 
              data={{
                labels: subscriptionRevenue.monthly_breakdown.map(item => item.month),
                datasets: [{
                  label: 'Monthly Revenue',
                  data: subscriptionRevenue.monthly_breakdown.map(item => item.revenue),
                  borderColor: 'rgb(153, 102, 255)',
                  tension: 0.1
                }]
              }} 
              options={chartOptions} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics2