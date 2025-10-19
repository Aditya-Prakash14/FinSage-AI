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
  Loader2
} from 'lucide-react';

import TransactionUpload from '../components/TransactionUpload';
import ForecastCharts from '../components/ForecastCharts';
import AIRecommendations from '../components/AIRecommendations';
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
      
      // Generate forecast
      const forecastData = await financeAPI.generateForecast(userId, 7, true);
      setForecast(forecastData);
      
      // Get AI insights
      const insightsData = await financeAPI.getInsights(userId, 'New user seeking financial guidance');
      setInsights(insightsData);
      
      setActiveTab('forecast');
    } catch (err) {
      console.error('Error processing transactions:', err);
      setError(err.response?.data?.detail || 'Failed to process transactions. Using demo data.');
      
      // Fallback to demo mode
      const calculatedStats = calculateStats(uploadedTransactions);
      setStats(calculatedStats);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'insights', label: 'AI Insights', icon: Sparkles },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-fintech-darker">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white dark:bg-fintech-dark border-r border-gray-200 dark:border-fintech-border z-10">
        <div className="p-6">
          <div className="flex items-center space-x-2 mb-8">
            <Sparkles className="w-8 h-8 text-primary-500" />
            <span className="text-xl font-bold">FinSage AI</span>
          </div>

          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-fintech-card'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="mt-auto pt-8">
            <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-fintech-card transition-all">
              <Settings className="w-5 h-5" />
              <span className="font-medium">Settings</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-white dark:bg-fintech-dark border-b border-gray-200 dark:border-fintech-border px-8 py-4 sticky top-0 z-10">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Financial Dashboard</h1>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                Monitor your cash flow and get AI-powered recommendations
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
