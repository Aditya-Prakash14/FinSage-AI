import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle } from 'lucide-react';
import { parseForecastData, formatCurrency } from '../utils/helpers';

function ForecastCharts({ forecast }) {
  if (!forecast) return null;

  const incomeData = parseForecastData(forecast.income_forecast);
  const expenseData = parseForecastData(forecast.expense_forecast);
  
  // Combine for net cash flow chart
  const cashFlowData = forecast.net_cash_flow?.map((item, index) => ({
    date: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
    netFlow: item.net_flow,
    income: incomeData[index]?.value || 0,
    expense: expenseData[index]?.value || 0,
  })) || [];

  const totalPredictedIncome = incomeData.reduce((sum, d) => sum + d.value, 0);
  const totalPredictedExpense = expenseData.reduce((sum, d) => sum + d.value, 0);
  const netCashFlow = totalPredictedIncome - totalPredictedExpense;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-fintech-card border border-gray-200 dark:border-fintech-border rounded-lg p-3 shadow-lg">
          <p className="font-semibold mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="stat-card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Predicted Income</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {formatCurrency(totalPredictedIncome)}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div className="flex items-center text-sm">
            <span className="text-green-600 dark:text-green-400 font-medium">
              Next 7 days
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Predicted Expenses</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {formatCurrency(totalPredictedExpense)}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
          <div className="flex items-center text-sm">
            <span className="text-red-600 dark:text-red-400 font-medium">
              Next 7 days
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Net Cash Flow</p>
              <p className={`text-2xl font-bold ${netCashFlow >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400'}`}>
                {formatCurrency(netCashFlow)}
              </p>
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${netCashFlow >= 0 ? 'bg-blue-100 dark:bg-blue-900/20' : 'bg-orange-100 dark:bg-orange-900/20'}`}>
              {netCashFlow >= 0 ? (
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              )}
            </div>
          </div>
          <div className="flex items-center text-sm">
            <span className={netCashFlow >= 0 ? 'text-blue-600 dark:text-blue-400 font-medium' : 'text-orange-600 dark:text-orange-400 font-medium'}>
              {netCashFlow >= 0 ? 'Surplus' : 'Deficit'}
            </span>
          </div>
        </div>
      </div>

      {/* Income Forecast Chart */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Income Forecast</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={incomeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `₹${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 4 }}
              name="Predicted Income"
            />
            {incomeData[0]?.upper && (
              <>
                <Line 
                  type="monotone" 
                  dataKey="upper" 
                  stroke="#10b981" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Upper Bound"
                />
                <Line 
                  type="monotone" 
                  dataKey="lower" 
                  stroke="#10b981" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Lower Bound"
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Expense Forecast Chart */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Expense Forecast</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={expenseData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `₹${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#ef4444" 
              strokeWidth={2}
              dot={{ fill: '#ef4444', r: 4 }}
              name="Predicted Expense"
            />
            {expenseData[0]?.upper && (
              <>
                <Line 
                  type="monotone" 
                  dataKey="upper" 
                  stroke="#ef4444" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Upper Bound"
                />
                <Line 
                  type="monotone" 
                  dataKey="lower" 
                  stroke="#ef4444" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Lower Bound"
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Net Cash Flow Chart */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Net Cash Flow</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={cashFlowData}>
            <defs>
              <linearGradient id="colorNetFlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `₹${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="netFlow" 
              stroke="#3b82f6" 
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorNetFlow)"
              name="Net Cash Flow"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Indicator */}
      {forecast.risk_level && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold mb-2">Income Volatility</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Based on your income patterns over the last 60 days
              </p>
            </div>
            <div className="text-right">
              <div className={`text-3xl font-bold mb-1 ${
                forecast.risk_level === 'low' ? 'text-green-600' :
                forecast.risk_level === 'medium' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {(forecast.volatility_score * 100).toFixed(0)}%
              </div>
              <div className={`text-sm font-medium uppercase ${
                forecast.risk_level === 'low' ? 'text-green-600' :
                forecast.risk_level === 'medium' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {forecast.risk_level} Risk
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ForecastCharts;
