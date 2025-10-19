/**
 * Generate sample transaction data for demo purposes
 */
export function generateSampleTransactions(days = 60) {
  const transactions = [];
  const today = new Date();
  
  const categories = {
    credit: ['Freelance Payment', 'Uber Earnings', 'Food Delivery', 'Consulting Fee', 'Project Payment'],
    debit: ['Groceries', 'Transport', 'Rent', 'Utilities', 'Food', 'Entertainment', 'Healthcare', 'Mobile Recharge']
  };

  for (let i = 0; i < days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Random 2-4 transactions per day
    const numTransactions = Math.floor(Math.random() * 3) + 2;
    
    for (let j = 0; j < numTransactions; j++) {
      const isCredit = Math.random() > 0.3; // 70% expenses, 30% income
      const type = isCredit ? 'credit' : 'debit';
      const categoryList = categories[type];
      const category = categoryList[Math.floor(Math.random() * categoryList.length)];
      
      let amount;
      if (isCredit) {
        // Income: ₹500 - ₹5000
        amount = Math.floor(Math.random() * 4500) + 500;
      } else {
        // Expenses: ₹50 - ₹2000
        amount = Math.floor(Math.random() * 1950) + 50;
      }
      
      transactions.push({
        date: date.toISOString(),
        amount: isCredit ? amount : -amount,
        type,
        category,
        description: `${category} - ${date.toLocaleDateString()}`,
        source: isCredit ? 'Payment App' : 'Card Payment'
      });
    }
  }
  
  return transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
}

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
