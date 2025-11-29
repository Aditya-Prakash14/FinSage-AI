import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const questions = [
  {
    id: 'work_type',
    question: 'What best describes your work situation?',
    type: 'single-choice',
    options: [
      { value: 'freelancer', label: 'Freelancer', icon: '💻', description: 'Project-based work' },
      { value: 'gig_worker', label: 'Gig Worker', icon: '🚗', description: 'Uber, Zomato, etc.' },
      { value: 'contractor', label: 'Contractor', icon: '🔧', description: 'Fixed-term contracts' },
      { value: 'part_time', label: 'Part-time', icon: '⏰', description: 'Multiple part-time jobs' },
      { value: 'self_employed', label: 'Self-Employed', icon: '🏪', description: 'Own business' },
    ],
  },
  {
    id: 'income_stability',
    question: 'How would you describe your income?',
    type: 'single-choice',
    options: [
      { value: 'very_stable', label: 'Very Stable', icon: '📈', description: 'Predictable monthly income' },
      { value: 'mostly_stable', label: 'Mostly Stable', icon: '📊', description: 'Some variation month-to-month' },
      { value: 'variable', label: 'Variable', icon: '🎢', description: 'Significant ups and downs' },
      { value: 'very_variable', label: 'Very Variable', icon: '🌊', description: 'Highly unpredictable' },
    ],
  },
  {
    id: 'monthly_income',
    question: 'What\'s your average monthly income?',
    subtitle: 'This helps us provide better recommendations',
    type: 'slider',
    min: 10000,
    max: 200000,
    step: 5000,
    unit: '₹',
  },
  {
    id: 'monthly_expenses',
    question: 'What are your typical monthly expenses?',
    type: 'slider',
    min: 5000,
    max: 150000,
    step: 5000,
    unit: '₹',
  },
  {
    id: 'financial_goals',
    question: 'What are your main financial goals?',
    subtitle: 'Select all that apply',
    type: 'multiple-choice',
    options: [
      { value: 'emergency_fund', label: 'Build Emergency Fund', icon: '🛡️' },
      { value: 'save_more', label: 'Save More Money', icon: '💰' },
      { value: 'reduce_expenses', label: 'Reduce Expenses', icon: '📉' },
      { value: 'invest', label: 'Start Investing', icon: '📈' },
      { value: 'debt_free', label: 'Become Debt-Free', icon: '🎯' },
      { value: 'retirement', label: 'Plan for Retirement', icon: '🏖️' },
    ],
  },
  {
    id: 'biggest_challenge',
    question: 'What\'s your biggest financial challenge?',
    type: 'single-choice',
    options: [
      { value: 'irregular_income', label: 'Irregular Income', icon: '💸' },
      { value: 'high_expenses', label: 'High Expenses', icon: '🛒' },
      { value: 'no_savings', label: 'Can\'t Save', icon: '💔' },
      { value: 'debt', label: 'Managing Debt', icon: '📊' },
      { value: 'planning', label: 'Financial Planning', icon: '📅' },
      { value: 'tracking', label: 'Tracking Spending', icon: '🔍' },
    ],
  },
  {
    id: 'current_savings',
    question: 'Do you have an emergency fund?',
    subtitle: 'Ideally 3-6 months of expenses',
    type: 'single-choice',
    options: [
      { value: 'none', label: 'No Savings', icon: '❌' },
      { value: 'under_1_month', label: 'Less than 1 month', icon: '📦' },
      { value: '1_3_months', label: '1-3 months', icon: '📦📦' },
      { value: '3_6_months', label: '3-6 months', icon: '✅' },
      { value: 'over_6_months', label: 'More than 6 months', icon: '🏆' },
    ],
  },
  {
    id: 'budget_experience',
    question: 'Have you used a budget before?',
    type: 'single-choice',
    options: [
      { value: 'never', label: 'Never', icon: '🆕', description: 'First time budgeting' },
      { value: 'tried', label: 'Tried Before', icon: '🔄', description: 'Didn\'t stick with it' },
      { value: 'sometimes', label: 'Occasionally', icon: '📋', description: 'Use it sporadically' },
      { value: 'always', label: 'Always', icon: '✅', description: 'Regular budgeter' },
    ],
  },
  {
    id: 'risk_tolerance',
    question: 'How do you feel about financial risk?',
    subtitle: 'This affects our savings and investment recommendations',
    type: 'single-choice',
    options: [
      { value: 'very_conservative', label: 'Very Conservative', icon: '🛡️', description: 'Safety first' },
      { value: 'conservative', label: 'Conservative', icon: '🔐', description: 'Prefer low risk' },
      { value: 'moderate', label: 'Moderate', icon: '⚖️', description: 'Balanced approach' },
      { value: 'aggressive', label: 'Aggressive', icon: '🚀', description: 'Higher risk OK' },
    ],
  },
  {
    id: 'notification_preferences',
    question: 'How often should we send you insights?',
    type: 'single-choice',
    options: [
      { value: 'daily', label: 'Daily', icon: '📅' },
      { value: 'weekly', label: 'Weekly', icon: '📆' },
      { value: 'monthly', label: 'Monthly', icon: '🗓️' },
      { value: 'only_important', label: 'Only Important Alerts', icon: '🔔' },
    ],
  },
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const { updateUserProfile, user } = useAuth();
  const navigate = useNavigate();

  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;

  const handleAnswer = (value) => {
    if (currentQuestion.type === 'multiple-choice') {
      const currentValues = answers[currentQuestion.id] || [];
      const newValues = currentValues.includes(value)
        ? currentValues.filter((v) => v !== value)
        : [...currentValues, value];
      setAnswers({ ...answers, [currentQuestion.id]: newValues });
    } else {
      setAnswers({ ...answers, [currentQuestion.id]: value });
      // Auto-advance for single-choice questions
      if (currentQuestion.type === 'single-choice') {
        setTimeout(() => handleNext(), 300);
      }
    }
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    // Prepare profile data
    const profileData = {
      userId: user?.id || user?.email,
      onboarding_completed: true,
      ...answers,
    };

    const result = await updateUserProfile(profileData);

    if (result.success) {
      navigate('/dashboard');
    }

    setLoading(false);
  };

  const isAnswered = () => {
    if (currentQuestion.type === 'multiple-choice') {
      return answers[currentQuestion.id]?.length > 0;
    }
    return answers[currentQuestion.id] !== undefined;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50 flex flex-col">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 h-2 bg-gray-200 z-50">
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Header */}
      <div className="container mx-auto px-4 py-6 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <div className="text-sm font-semibold gradient-text">FinSage AI</div>
            <div className="text-xs text-gray-500">
              Question {currentStep + 1} of {questions.length}
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate('/dashboard')}
          className="text-sm text-gray-500 hover:text-gray-700 font-medium"
        >
          Skip for now
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="max-w-3xl w-full">
          {/* Question */}
          <div className="mb-12 animate-slide-up">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 font-display">
              {currentQuestion.question}
            </h2>
            {currentQuestion.subtitle && (
              <p className="text-xl text-gray-500">{currentQuestion.subtitle}</p>
            )}
          </div>

          {/* Answer Options */}
          <div className="animate-fade-in">
            {currentQuestion.type === 'single-choice' && (
              <div className="space-y-3">
                {currentQuestion.options.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleAnswer(option.value)}
                    className={`w-full text-left p-6 rounded-2xl border-2 transition-all duration-200 ${
                      answers[currentQuestion.id] === option.value
                        ? 'border-primary-500 bg-primary-50 shadow-lg transform scale-105'
                        : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <span className="text-4xl">{option.icon}</span>
                      <div className="flex-1">
                        <div className="font-semibold text-lg text-gray-900">{option.label}</div>
                        {option.description && (
                          <div className="text-sm text-gray-500 mt-1">{option.description}</div>
                        )}
                      </div>
                      {answers[currentQuestion.id] === option.value && (
                        <svg className="w-6 h-6 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {currentQuestion.type === 'multiple-choice' && (
              <div className="space-y-3">
                {currentQuestion.options.map((option) => {
                  const isSelected = answers[currentQuestion.id]?.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      onClick={() => handleAnswer(option.value)}
                      className={`w-full text-left p-6 rounded-2xl border-2 transition-all duration-200 ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50 shadow-lg'
                          : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <span className="text-3xl">{option.icon}</span>
                        <div className="flex-1 font-semibold text-lg text-gray-900">{option.label}</div>
                        <div
                          className={`w-6 h-6 rounded-md border-2 flex items-center justify-center ${
                            isSelected ? 'bg-primary-600 border-primary-600' : 'border-gray-300'
                          }`}
                        >
                          {isSelected && (
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {currentQuestion.type === 'slider' && (
              <div className="bg-white p-8 rounded-2xl border-2 border-gray-200 shadow-lg">
                <div className="mb-8">
                  <div className="text-center mb-6">
                    <span className="text-6xl font-bold gradient-text">
                      {currentQuestion.unit}
                      {(answers[currentQuestion.id] || currentQuestion.min).toLocaleString('en-IN')}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={currentQuestion.min}
                    max={currentQuestion.max}
                    step={currentQuestion.step}
                    value={answers[currentQuestion.id] || currentQuestion.min}
                    onChange={(e) => handleAnswer(parseInt(e.target.value))}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                    style={{
                      background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${
                        ((answers[currentQuestion.id] || currentQuestion.min) - currentQuestion.min) /
                        (currentQuestion.max - currentQuestion.min) *
                        100
                      }%, #e5e7eb ${
                        ((answers[currentQuestion.id] || currentQuestion.min) - currentQuestion.min) /
                        (currentQuestion.max - currentQuestion.min) *
                        100
                      }%, #e5e7eb 100%)`,
                    }}
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-2">
                    <span>
                      {currentQuestion.unit}
                      {currentQuestion.min.toLocaleString('en-IN')}
                    </span>
                    <span>
                      {currentQuestion.unit}
                      {currentQuestion.max.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className="btn-ghost disabled:opacity-30 disabled:cursor-not-allowed flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>

          {currentQuestion.type !== 'single-choice' && (
            <button
              onClick={handleNext}
              disabled={!isAnswered() || loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </>
              ) : currentStep === questions.length - 1 ? (
                <>
                  Complete
                  <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </>
              ) : (
                <>
                  Continue
                  <svg className="w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
