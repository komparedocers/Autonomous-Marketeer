import { useQuery } from '@tanstack/react-query'
import { getAgentConfigs, getAgentRuns, getLLMStatus } from '../services/api'
import { Bot, Zap, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function Agents() {
  const { data: configs } = useQuery({
    queryKey: ['agent-configs'],
    queryFn: getAgentConfigs,
  })

  const { data: runs } = useQuery({
    queryKey: ['agent-runs'],
    queryFn: () => getAgentRuns(),
  })

  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: getLLMStatus,
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Agents</h1>
        <p className="text-gray-600 mt-2">
          Manage autonomous marketing agents and LLM configuration
        </p>
      </div>

      {/* LLM Configuration */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Zap className="w-6 h-6 text-primary-600" />
          LLM Configuration
        </h2>

        {llmStatus?.data && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">
                  Default Provider
                </span>
                <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                  {llmStatus.data.default_provider === 'local'
                    ? 'Local LLM'
                    : 'OpenAI'}
                </span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {/* OpenAI Status */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">OpenAI</h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      llmStatus.data.openai.enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {llmStatus.data.openai.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                {llmStatus.data.openai.enabled && (
                  <p className="text-sm text-gray-600">
                    Model: {llmStatus.data.openai.model}
                  </p>
                )}
              </div>

              {/* Local LLM Status */}
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">Local LLM</h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      llmStatus.data.local.enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {llmStatus.data.local.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                {llmStatus.data.local.enabled && (
                  <p className="text-sm text-gray-600">
                    Model: {llmStatus.data.local.model}
                  </p>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                💡 Configure LLM providers in the Settings page to enable/disable
                OpenAI or Local LLM
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Available Agents */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Available Agents
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {configs?.data?.map((agent: any) => (
            <div
              key={agent.name}
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-primary-600" />
                  <h3 className="font-medium text-gray-900">{agent.name}</h3>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    agent.enabled
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {agent.enabled ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="text-sm text-gray-600">{agent.description}</p>
              <div className="mt-3 pt-3 border-t border-gray-200">
                <span className="text-xs text-gray-500">
                  Provider: {agent.llm_provider}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Agent Runs */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Agent Runs
        </h2>

        {runs?.data?.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No agent runs yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {runs?.data?.slice(0, 10).map((run: any) => (
              <div
                key={run.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(run.status)}
                  <div>
                    <h4 className="font-medium text-gray-900">{run.agent}</h4>
                    <p className="text-sm text-gray-600">
                      {new Date(run.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {run.tokens_used} tokens
                  </p>
                  <p className="text-xs text-gray-500">
                    ${run.cost.toFixed(4)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
