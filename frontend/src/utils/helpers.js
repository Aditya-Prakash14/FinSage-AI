/**
 * Format currency in Indian Rupees
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format date for display
 */
export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

/**
 * Calculate summary statistics from transactions
 */
export function calculateStats(transactions) {
  const credits = transactions.filter(t => t.type === 'credit');
  const debits = transactions.filter(t => t.type === 'debit');
  
  const totalIncome = credits.reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const totalExpense = debits.reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const netSavings = totalIncome - totalExpense;
  const savingsRate = totalIncome > 0 ? (netSavings / totalIncome) * 100 : 0;
  
  return {
    totalIncome,
    totalExpense,
    netSavings,
    savingsRate,
    transactionCount: transactions.length,
    avgIncome: totalIncome / Math.max(credits.length, 1),
    avgExpense: totalExpense / Math.max(debits.length, 1),
  };
}

/**
 * Get risk level color
 */
export function getRiskColor(riskLevel) {
  const colors = {
    low: 'text-green-500',
    medium: 'text-yellow-500',
    high: 'text-red-500',
  };
  return colors[riskLevel] || 'text-gray-500';
}

/**
 * Parse forecast data for charting
 */
export function parseForecastData(forecast) {
  if (!forecast || !Array.isArray(forecast)) return [];
  
  return forecast.map(point => ({
    date: new Date(point.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
    value: point.predicted_value,
    lower: point.lower_bound,
    upper: point.upper_bound,
    confidence: point.confidence,
  }));
}
