import { useState } from 'react';
import { Sparkles, ThumbsUp, ThumbsDown, Lightbulb, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { financeAPI } from '../services/api';

function AIRecommendations({ insights, userId }) {
  const [feedback, setFeedback] = useState({});
  const [submitting, setSubmitting] = useState(false);

  if (!insights) return null;

  const handleFeedback = async (actionIndex, type) => {
    if (submitting) return;

    setSubmitting(true);
    setFeedback(prev => ({ ...prev, [actionIndex]: type }));

    try {
      await financeAPI.submitFeedback(
        `action_${actionIndex}`,
        type,
        userId
      );
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setTimeout(() => setSubmitting(false), 500);
    }
  };

  const { summary, insights: insightsList, action_items, warnings, confidence_score } = insights;

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="card bg-gradient-to-br from-primary-600 to-blue-600 text-white">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="w-6 h-6" />
              <h2 className="text-2xl font-bold">AI Financial Advisor</h2>
            </div>
            <p className="text-blue-100 leading-relaxed">
              {summary || 'Powered by GPT-4, analyzing your financial patterns to provide personalized guidance'}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100 mb-1">Confidence</div>
            <div className="text-3xl font-bold">{((confidence_score || 0.7) * 100).toFixed(0)}%</div>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <div className="card border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-900/10">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-orange-900 dark:text-orange-100 mb-2">Attention Required</h3>
              <ul className="space-y-2">
                {warnings.map((warning, index) => (
                  <li key={index} className="text-orange-800 dark:text-orange-200 text-sm">
                    {warning}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Insights */}
      {insightsList && insightsList.length > 0 && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <h3 className="text-xl font-bold">Key Insights</h3>
          </div>
          <div className="space-y-3">
            {insightsList.map((insight, index) => (
              <div 
                key={index}
                className="p-4 bg-gray-50 dark:bg-fintech-dark rounded-lg border border-gray-200 dark:border-fintech-border"
              >
                <p className="text-gray-900 dark:text-gray-100 leading-relaxed">
                  {insight}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items with Feedback */}
      {action_items && action_items.length > 0 && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <CheckCircle2 className="w-6 h-6 text-green-500" />
            <h3 className="text-xl font-bold">Recommended Actions</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">
            GPT-4 generated these personalized micro-actions to improve your financial health
          </p>

          <div className="space-y-4">
            {action_items.map((action, index) => (
              <div 
                key={index}
                className="group p-5 bg-gradient-to-r from-gray-50 to-white dark:from-fintech-dark dark:to-fintech-card rounded-xl border border-gray-200 dark:border-fintech-border hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-primary-600 dark:text-primary-400 font-bold text-sm">
                          {index + 1}
                        </span>
                      </div>
                      <p className="text-gray-900 dark:text-gray-100 leading-relaxed flex-1">
                        {action}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => handleFeedback(index, 'like')}
                      disabled={submitting}
                      className={`p-2 rounded-lg transition-all ${
                        feedback[index] === 'like'
                          ? 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                          : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-fintech-card hover:text-green-600'
                      }`}
                      aria-label="Like this recommendation"
                    >
                      <ThumbsUp className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleFeedback(index, 'dislike')}
                      disabled={submitting}
                      className={`p-2 rounded-lg transition-all ${
                        feedback[index] === 'dislike'
                          ? 'bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                          : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-fintech-card hover:text-red-600'
                      }`}
                      aria-label="Dislike this recommendation"
                    >
                      <ThumbsDown className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {feedback[index] && (
                  <div className="mt-3 text-sm text-gray-600 dark:text-gray-400 italic">
                    Thank you for your feedback! This helps improve our recommendations.
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Methodology */}
      <div className="card bg-gray-50 dark:bg-fintech-dark border-l-4 border-primary-500">
        <h4 className="font-bold mb-2 text-sm uppercase text-gray-600 dark:text-gray-400">
          How We Generate Recommendations
        </h4>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          Our AI analyzes your transaction patterns, income volatility, and spending habits using GPT-4. 
          Recommendations are personalized based on your unique financial situation and designed to be 
          actionable within the next 7 days. Your feedback helps us improve the model.
        </p>
      </div>
    </div>
  );
}

export default AIRecommendations;
