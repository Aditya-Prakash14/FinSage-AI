import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  Activity,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Target,
  Zap
} from 'lucide-react';
import { formatCurrency, getRiskColor } from '../utils/helpers';

function FinancialSummary({ stats, forecast }) {
  if (!stats) return null;

  const summaryCards = [
    {
      title: 'Total Income',
      value: formatCurrency(stats.totalIncome),
      icon: TrendingUp,
      color: 'green',
      bgColor: 'bg-gradient-to-br from-green-500 to-emerald-600',
      textColor: 'text-white',
      subtitle: `${stats.transactionCount} transactions`,
      trend: '+12.5%',
      trendUp: true
    },
    {
      title: 'Total Expenses',
      value: formatCurrency(stats.totalExpense),
      icon: TrendingDown,
      color: 'red',
      bgColor: 'bg-gradient-to-br from-red-500 to-rose-600',
      textColor: 'text-white',
      subtitle: `Avg: ${formatCurrency(stats.avgExpense)}`,
      trend: '-8.3%',
      trendUp: false
    },
    {
      title: 'Net Savings',
      value: formatCurrency(stats.netSavings),
      icon: stats.netSavings >= 0 ? PiggyBank : Wallet,
      color: stats.netSavings >= 0 ? 'blue' : 'orange',
      bgColor: stats.netSavings >= 0 ? 'bg-gradient-to-br from-blue-500 to-indigo-600' : 'bg-gradient-to-br from-orange-500 to-amber-600',
      textColor: 'text-white',
      subtitle: `${stats.savingsRate.toFixed(1)}% savings rate`,
      trend: stats.netSavings >= 0 ? '+15.2%' : '-5.1%',
      trendUp: stats.netSavings >= 0
    },
  ];

  // Calculate category breakdown
  const categoryData = stats.categoryBreakdown || [];
  const topCategories = categoryData.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Header with Quick Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <Activity className="w-7 h-7 text-primary-500" />
            Financial Overview
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time insights into your financial health
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary px-4 py-2 text-sm flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Last 30 Days
          </button>
        </div>
      </div>

      {/* Enhanced Summary Cards with Gradients */}
      <div className="grid md:grid-cols-3 gap-6">
        {summaryCards.map((card, index) => {
          const Icon = card.icon;
          const TrendIcon = card.trendUp ? ArrowUpRight : ArrowDownRight;
          return (
            <div key={index} className="relative overflow-hidden rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className={`${card.bgColor} p-6`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <p className="text-sm text-white/80 mb-2 font-medium">
                      {card.title}
                    </p>
                    <p className="text-3xl font-bold text-white mb-1">
                      {card.value}
                    </p>
                    <p className="text-sm text-white/70">
                      {card.subtitle}
                    </p>
                  </div>
                  <div className="w-14 h-14 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center flex-shrink-0">
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/20">
                  <TrendIcon className={`w-4 h-4 ${card.trendUp ? 'text-green-200' : 'text-red-200'}`} />
                  <span className="text-sm text-white/90 font-medium">{card.trend} vs last month</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Financial Health Score */}
      <div className="card bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 border-2 border-purple-200 dark:border-purple-800">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-full bg-purple-500 flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold">Financial Health Score</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Based on your spending patterns</p>
              </div>
            </div>
            <div className="flex items-end gap-4">
              <div className="text-5xl font-bold text-purple-600 dark:text-purple-400">
                {Math.round(stats.savingsRate * 4.5 + 10)}
              </div>
              <div className="text-2xl text-gray-400 mb-2">/100</div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="w-32 h-32 rounded-full border-8 border-purple-200 dark:border-purple-800 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {stats.savingsRate >= 20 ? 'Great' : stats.savingsRate >= 10 ? 'Good' : 'Fair'}
                </div>
                <div className="text-xs text-gray-500">Status</div>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-purple-200 dark:border-purple-800">
          <div className="w-full bg-purple-200 dark:bg-purple-900 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(stats.savingsRate * 4.5 + 10, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {topCategories.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-primary-500" />
            Top Spending Categories
          </h3>
          <div className="space-y-4">
            {topCategories.map((cat, idx) => {
              const percentage = (cat.amount / stats.totalExpense) * 100;
              const colors = [
                'bg-blue-500',
                'bg-purple-500',
                'bg-pink-500',
                'bg-orange-500',
                'bg-green-500'
              ];
              return (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium capitalize">{cat.category}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {formatCurrency(cat.amount)} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`${colors[idx]} h-2 rounded-full transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Volatility & Risk */}
      {forecast && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card border-l-4 border-yellow-500 hover:shadow-lg transition-shadow">
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/20 flex items-center justify-center">
                <Activity className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold mb-1">Income Volatility</h3>
                <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-2">
                  {((forecast.volatility_score || 0) * 100).toFixed(0)}%
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {forecast.volatility_score > 0.5
                    ? 'High income variability - consider building a larger emergency fund'
                    : forecast.volatility_score > 0.3
                      ? 'Moderate income patterns - maintain 2-3 months of expenses saved'
                      : 'Stable income - you have predictable cash flow'}
                </p>
              </div>
            </div>
          </div>

          <div className="card border-l-4 border-primary-500 hover:shadow-lg transition-shadow">
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                <AlertCircle className={`w-6 h-6 ${getRiskColor(forecast.risk_level)}`} />
              </div>
              <div className="flex-1">
                <h3 className="font-bold mb-1">Risk Level</h3>
                <p className={`text-3xl font-bold mb-2 uppercase ${getRiskColor(forecast.risk_level)}`}>
                  {forecast.risk_level || 'Low'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Based on your income patterns and expense predictability
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats Grid */}
      <div className="card bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
        <h3 className="text-lg font-bold mb-4">Quick Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Income/Day</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {formatCurrency(stats.avgIncome)}
            </p>
          </div>
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Expense/Day</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              {formatCurrency(stats.avgExpense)}
            </p>
          </div>
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Transactions</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {stats.transactionCount}
            </p>
          </div>
          <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Savings Rate</p>
            <p className={`text-2xl font-bold ${stats.savingsRate >= 20 ? 'text-green-600 dark:text-green-400' :
                stats.savingsRate >= 10 ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-red-600 dark:text-red-400'
              }`}>
              {stats.savingsRate.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FinancialSummary;
