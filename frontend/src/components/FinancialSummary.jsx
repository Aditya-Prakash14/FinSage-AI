import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  PiggyBank,
  Activity,
  AlertCircle
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
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      textColor: 'text-green-600 dark:text-green-400',
      subtitle: `${stats.transactionCount} transactions`,
    },
    {
      title: 'Total Expenses',
      value: formatCurrency(stats.totalExpense),
      icon: TrendingDown,
      color: 'red',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
      textColor: 'text-red-600 dark:text-red-400',
      subtitle: `Avg: ${formatCurrency(stats.avgExpense)}`,
    },
    {
      title: 'Net Savings',
      value: formatCurrency(stats.netSavings),
      icon: stats.netSavings >= 0 ? PiggyBank : Wallet,
      color: stats.netSavings >= 0 ? 'blue' : 'orange',
      bgColor: stats.netSavings >= 0 ? 'bg-blue-100 dark:bg-blue-900/20' : 'bg-orange-100 dark:bg-orange-900/20',
      textColor: stats.netSavings >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400',
      subtitle: `${stats.savingsRate.toFixed(1)}% savings rate`,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Financial Overview</h2>
        <p className="text-gray-600 dark:text-gray-400">
          Summary of your financial activity over the last 60 days
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {summaryCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="stat-card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {card.title}
                  </p>
                  <p className={`text-3xl font-bold ${card.textColor} mb-1`}>
                    {card.value}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {card.subtitle}
                  </p>
                </div>
                <div className={`w-12 h-12 rounded-full ${card.bgColor} flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-6 h-6 ${card.textColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Volatility & Risk (if forecast available) */}
      {forecast && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card border-l-4 border-yellow-500">
            <div className="flex items-start space-x-3">
              <Activity className="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
              <div>
                <h3 className="font-bold mb-1">Income Volatility</h3>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mb-2">
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

          <div className="card border-l-4 border-primary-500">
            <div className="flex items-start space-x-3">
              <AlertCircle className={`w-6 h-6 flex-shrink-0 ${getRiskColor(forecast.risk_level)}`} />
              <div>
                <h3 className="font-bold mb-1">Risk Level</h3>
                <p className={`text-2xl font-bold mb-2 uppercase ${getRiskColor(forecast.risk_level)}`}>
                  {forecast.risk_level || 'Unknown'}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Based on your income patterns and expense predictability
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/10 dark:to-blue-900/10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Income/Day</p>
            <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {formatCurrency(stats.avgIncome)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Expense/Day</p>
            <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {formatCurrency(stats.avgExpense)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Transactions</p>
            <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {stats.transactionCount}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Savings Rate</p>
            <p className={`text-xl font-bold ${
              stats.savingsRate >= 20 ? 'text-green-600 dark:text-green-400' :
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
