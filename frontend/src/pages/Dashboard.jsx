import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Home,
  TrendingUp,
  Upload,
  BarChart3,
  Settings,
  Moon,
  Sun,
  Sparkles,
  AlertCircle,
  Loader2,
  Bot,
  Activity
} from 'lucide-react';

import TransactionUpload from '../components/TransactionUpload';
import ForecastCharts from '../components/ForecastCharts';
import AIRecommendations from '../components/AIRecommendations';
import AgentAnalysis from '../components/AgentAnalysis';
import FinancialSummary from '../components/FinancialSummary';
import { financeAPI } from '../services/api';
import { calculateStats } from '../utils/helpers';

function Dashboard({ darkMode, setDarkMode }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Data state
  const [transactions, setTransactions] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [insights, setInsights] = useState(null);
  const [agentReport, setAgentReport] = useState(null);
  const [stats, setStats] = useState(null);

  const userId = 'demo_user_001'; // In production, this would come from auth

  useEffect(() => {
    if (transactions.length > 0) {
      const calculatedStats = calculateStats(transactions);
      setStats(calculatedStats);
    }
  }, [transactions]);

  const handleTransactionsUploaded = async (uploadedTransactions) => {
    setTransactions(uploadedTransactions);
    setLoading(true);
    setError(null);

    try {
      // Upload to backend
      await financeAPI.uploadTransactions(userId, uploadedTransactions);
      console.log('✅ Transactions uploaded successfully');

      // Try to generate forecast
      try {
        const forecastData = await financeAPI.generateForecast(userId, 7, true);
        setForecast(forecastData);
        console.log('✅ Forecast generated successfully');
      } catch (forecastErr) {
        console.warn('⚠️ Forecast generation failed:', forecastErr.message);
        setError('AI forecasting unavailable. Showing transaction summary only.');
      }

      // Try to get AI insights
      try {
        const insightsData = await financeAPI.getInsights(userId, 'New user seeking financial guidance');
        setInsights(insightsData);
        console.log('✅ Insights generated successfully');
      } catch (insightErr) {
        console.warn('⚠️ Insights generation failed:', insightErr.message);
      }

      // Try to get Agent Analysis
      try {
        const report = await financeAPI.getAgentAnalysis(userId, 30);
        setAgentReport(report);
        console.log('✅ Agent analysis generated successfully');
      } catch (agentErr) {
        console.warn('⚠️ Agent analysis failed:', agentErr.message);
      }

      // Calculate local stats regardless of API success
      const calculatedStats = calculateStats(uploadedTransactions);
      setStats(calculatedStats);

      setActiveTab('overview');
    } catch (err) {
      console.error('❌ Error uploading transactions:', err);
      setError(err.response?.data?.detail || 'Failed to upload transactions. Please check your data format.');

      // Still calculate local stats for display
      const calculatedStats = calculateStats(uploadedTransactions);
      setStats(calculatedStats);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'agent', label: 'Agent Analysis', icon: Bot },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'insights', label: 'Quick Insights', icon: Sparkles },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-fintech-darker">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-gray-900 to-gray-800 border-r border-gray-700 z-10 shadow-2xl">
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-8 pb-6 border-b border-gray-700">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold text-white">FinSage AI</span>
              <p className="text-xs text-gray-400">Your Personal CFO</p>
            </div>
          </div>

          <nav className="space-y-1.5">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all group ${activeTab === tab.id
                    ? 'bg-gradient-to-r from-primary-600 to-purple-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                >
                  <Icon className={`w-5 h-5 ${activeTab === tab.id ? '' : 'group-hover:scale-110 transition-transform'}`} />
                  <span className="font-medium">{tab.label}</span>
                  {activeTab === tab.id && (
                    <div className="ml-auto w-2 h-2 rounded-full bg-white"></div>
                  )}
                </button>
              );
            })}
          </nav>

          <div className="mt-auto pt-8 border-t border-gray-700">
            <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-300 hover:bg-gray-800 hover:text-white transition-all group">
              <Settings className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span className="font-medium">Settings</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-white dark:bg-fintech-dark border-b border-gray-200 dark:border-fintech-border px-8 py-6 sticky top-0 z-10 backdrop-blur-sm bg-white/95 dark:bg-fintech-dark/95">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">Financial Dashboard</h1>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-2 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Real-time AI-powered financial intelligence
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-fintech-card transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              <button
                onClick={() => navigate('/')}
                className="btn-secondary px-4 py-2 text-sm"
              >
                Back to Home
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="p-8">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
              <span className="ml-4 text-lg">Processing your data...</span>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-400 dark:border-yellow-700 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-800 dark:text-yellow-200 font-medium">Warning</p>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {!transactions.length ? (
                <div className="text-center py-20">
                  <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold mb-2">Get Started</h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Upload your transactions or generate sample data to see AI-powered insights
                  </p>
                  <TransactionUpload onTransactionsUploaded={handleTransactionsUploaded} />
                </div>
              ) : (
                <>
                  <FinancialSummary stats={stats} forecast={forecast} />
                  <TransactionUpload onTransactionsUploaded={handleTransactionsUploaded} />
                </>
              )}
            </div>
          )}

          {/* Agent Analysis Tab */}
          {activeTab === 'agent' && (
            <div className="space-y-6">
              {agentReport ? (
                <AgentAnalysis report={agentReport} />
              ) : (
                <div className="card text-center py-20">
                  <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Upload transactions to generate comprehensive multi-agent analysis
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Forecast Tab */}
          {activeTab === 'forecast' && (
            <div className="space-y-6">
              {forecast ? (
                <ForecastCharts forecast={forecast} />
              ) : (
                <div className="card text-center py-20">
                  <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Upload transactions to generate forecasts
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Insights Tab */}
          {activeTab === 'insights' && (
            <div className="space-y-6">
              {insights ? (
                <AIRecommendations insights={insights} userId={userId} />
              ) : (
                <div className="card text-center py-20">
                  <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Upload transactions to get AI insights
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="card text-center py-20">
              <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                Advanced analytics coming soon
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
