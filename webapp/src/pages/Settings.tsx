import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getLLMStatus } from '../services/api'
import { Settings as SettingsIcon, Zap, Database, Bell } from 'lucide-react'

export default function Settings() {
  const { data: llmStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: getLLMStatus,
  })

  const [openaiEnabled, setOpenaiEnabled] = useState(
    llmStatus?.data?.openai?.enabled || false
  )
  const [localEnabled, setLocalEnabled] = useState(
    llmStatus?.data?.local?.enabled || true
  )
  const [defaultProvider, setDefaultProvider] = useState(
    llmStatus?.data?.default_provider || 'local'
  )

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Configure your platform preferences
        </p>
      </div>

      {/* LLM Provider Settings */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
          <Zap className="w-6 h-6 text-primary-600" />
          LLM Provider Configuration
        </h2>

        <div className="space-y-6">
          {/* Default Provider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Default LLM Provider
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => setDefaultProvider('local')}
                className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                  defaultProvider === 'local'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-gray-900">Local LLM</div>
                <div className="text-sm text-gray-600 mt-1">
                  Use local model (privacy, cost-effective)
                </div>
              </button>
              <button
                onClick={() => setDefaultProvider('openai')}
                className={`flex-1 p-4 border-2 rounded-lg transition-all ${
                  defaultProvider === 'openai'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-gray-900">OpenAI</div>
                <div className="text-sm text-gray-600 mt-1">
                  Use OpenAI API (higher quality, paid)
                </div>
              </button>
            </div>
          </div>

          {/* OpenAI Configuration */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-medium text-gray-900">OpenAI</h3>
                <p className="text-sm text-gray-600">
                  Connect to OpenAI API for high-quality responses
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={openaiEnabled}
                  onChange={(e) => setOpenaiEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {openaiEnabled && (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <input
                    type="password"
                    placeholder="sk-..."
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Model
                  </label>
                  <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500">
                    <option>gpt-4-turbo-preview</option>
                    <option>gpt-4</option>
                    <option>gpt-3.5-turbo</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Local LLM Configuration */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-medium text-gray-900">Local LLM</h3>
                <p className="text-sm text-gray-600">
                  Use locally hosted language model
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localEnabled}
                  onChange={(e) => setLocalEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            {localEnabled && (
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500">
                  <option>mistralai/Mistral-7B-Instruct-v0.2</option>
                  <option>meta-llama/Llama-2-7b-chat-hf</option>
                  <option>tiiuae/falcon-7b-instruct</option>
                </select>
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="pt-4">
            <button className="btn-primary">Save LLM Configuration</button>
            <p className="text-xs text-gray-500 mt-2">
              Note: Configuration changes require environment variable updates and service restart
            </p>
          </div>
        </div>
      </div>

      {/* Other Settings */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-gray-600" />
            Data & Storage
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Manage your data retention and storage preferences
          </p>
          <button className="btn-secondary">Configure</button>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-gray-600" />
            Notifications
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Set up alerts for campaign performance and agent activity
          </p>
          <button className="btn-secondary">Configure</button>
        </div>
      </div>
    </div>
  )
}
