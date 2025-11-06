import { useQuery } from '@tanstack/react-query'
import { getAnalyticsSummary, getFunnel } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Analytics() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => getAnalyticsSummary(),
  })

  const { data: funnel } = useQuery({
    queryKey: ['funnel'],
    queryFn: () => getFunnel({ steps: 'pageview,click,conversion' }),
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">
          Deep dive into your marketing performance
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Sessions</h3>
          <p className="text-3xl font-bold text-gray-900">
            {summary?.data?.sessions?.toLocaleString() || '0'}
          </p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Page Views</h3>
          <p className="text-3xl font-bold text-gray-900">
            {summary?.data?.pageviews?.toLocaleString() || '0'}
          </p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Revenue</h3>
          <p className="text-3xl font-bold text-gray-900">
            ${summary?.data?.revenue?.toFixed(2) || '0.00'}
          </p>
        </div>
      </div>

      {/* Conversion Funnel */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Conversion Funnel
        </h2>

        {funnel?.data?.funnel && (
          <div className="space-y-4">
            {funnel.data.funnel.map((step: any, index: number) => (
              <div key={step.step}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 capitalize">
                    {index + 1}. {step.step}
                  </span>
                  <div className="text-right">
                    <span className="font-semibold text-gray-900">
                      {step.count.toLocaleString()}
                    </span>
                    <span className="text-sm text-gray-600 ml-2">
                      ({step.conversion_rate}%)
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-primary-600 h-3 rounded-full transition-all"
                    style={{ width: `${step.conversion_rate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Performance Chart */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Performance Overview
        </h2>

        {summary?.data && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                {
                  name: 'Clicks',
                  value: summary.data.clicks,
                },
                {
                  name: 'Conversions',
                  value: summary.data.conversions,
                },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
