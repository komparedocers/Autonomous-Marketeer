import { useQuery } from '@tanstack/react-query'
import { getAnalyticsSummary, getCampaigns, getLLMStatus } from '../services/api'
import {
  TrendingUp,
  DollarSign,
  MousePointerClick,
  Target,
  Activity,
  Zap,
} from 'lucide-react'

export default function Dashboard() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => getAnalyticsSummary(),
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns'],
    queryFn: getCampaigns,
  })

  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: getLLMStatus,
  })

  const stats = [
    {
      name: 'Total Clicks',
      value: summary?.data?.clicks?.toLocaleString() || '0',
      icon: MousePointerClick,
      color: 'bg-blue-500',
    },
    {
      name: 'Conversions',
      value: summary?.data?.conversions?.toLocaleString() || '0',
      icon: Target,
      color: 'bg-green-500',
    },
    {
      name: 'CTR',
      value: `${summary?.data?.ctr?.toFixed(2) || '0.00'}%`,
      icon: TrendingUp,
      color: 'bg-purple-500',
    },
    {
      name: 'CVR',
      value: `${summary?.data?.cvr?.toFixed(2) || '0.00'}%`,
      icon: Activity,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of your marketing performance
        </p>
      </div>

      {/* LLM Status Banner */}
      {llmStatus?.data && (
        <div className="card mb-6 bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className="w-6 h-6 text-primary-600" />
              <div>
                <h3 className="font-semibold text-gray-900">LLM Status</h3>
                <p className="text-sm text-gray-600">
                  Active Provider:{' '}
                  <span className="font-medium text-primary-700">
                    {llmStatus.data.default_provider === 'local'
                      ? 'Local LLM'
                      : 'OpenAI'}
                  </span>
                </p>
              </div>
            </div>
            <div className="flex gap-4 text-sm">
              <div>
                <span className="text-gray-600">OpenAI: </span>
                <span
                  className={`font-medium ${llmStatus.data.openai.enabled ? 'text-green-600' : 'text-gray-400'}`}
                >
                  {llmStatus.data.openai.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <div>
                <span className="text-gray-600">Local: </span>
                <span
                  className={`font-medium ${llmStatus.data.local.enabled ? 'text-green-600' : 'text-gray-400'}`}
                >
                  {llmStatus.data.local.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Campaigns */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Campaigns
        </h2>

        {campaigns?.data?.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No campaigns yet</p>
            <a
              href="/campaigns"
              className="text-primary-600 hover:text-primary-700 font-medium mt-2 inline-block"
            >
              Create your first campaign →
            </a>
          </div>
        ) : (
          <div className="space-y-3">
            {campaigns?.data?.slice(0, 5).map((campaign: any) => (
              <div
                key={campaign.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div>
                  <h3 className="font-medium text-gray-900">{campaign.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">
                    {campaign.objective} · {campaign.status}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    ${campaign.budget_daily || campaign.budget_total || 0}
                  </p>
                  <p className="text-xs text-gray-500">Budget</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
