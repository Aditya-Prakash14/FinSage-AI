import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  Brain, 
  Shield, 
  Zap, 
  BarChart3, 
  Moon, 
  Sun,
  Sparkles,
  IndianRupee
} from 'lucide-react';

function LandingPage({ darkMode, setDarkMode }) {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Brain className="w-8 h-8" />,
      title: 'AI-Powered Insights',
      description: 'GPT-4 analyzes your spending and generates personalized financial recommendations',
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'Smart Forecasting',
      description: 'Prophet-based prediction of income and expenses with confidence intervals',
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'Budget Optimization',
      description: 'RL agent learns your patterns and suggests optimal budget allocations',
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Privacy First',
      description: 'Your data is encrypted and anonymized. We never share your information.',
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'Real-time Analysis',
      description: 'Instant anomaly detection and cash flow alerts to prevent shortfalls',
    },
    {
      icon: <IndianRupee className="w-8 h-8" />,
      title: 'Gig Worker Focused',
      description: 'Built specifically for unpredictable income patterns of freelancers',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-fintech-darker to-gray-900 text-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-8 h-8 text-primary-400" />
          <span className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-blue-500 bg-clip-text text-transparent">
            FinSage AI
          </span>
        </div>
        
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
        </button>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
            Your Personal
            <span className="block bg-gradient-to-r from-primary-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
              AI CFO
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
            Empowering Indian gig workers with AI-driven financial intelligence. 
            Predict income, optimize budgets, and achieve financial stability.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-primary px-10 py-4 text-lg shadow-glow hover:shadow-glow group"
            >
              Get Started
              <Zap className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button className="btn-secondary px-10 py-4 text-lg">
              Watch Demo
            </button>
          </div>

          <div className="mt-12 flex justify-center items-center space-x-8 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span>API Operational</span>
            </div>
            <span>•</span>
            <div>100% Free</div>
            <span>•</span>
            <div>No Credit Card</div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Intelligent Financial Management
          </h2>
          <p className="text-gray-400 text-lg">
            Powered by GPT-4, Prophet, and Reinforcement Learning
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:border-primary-500/50 transition-all duration-300 hover:shadow-glow-sm"
            >
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-gray-400 text-lg">
            Three simple steps to financial clarity
          </p>
        </div>

        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          {[
            { step: '01', title: 'Upload Transactions', desc: 'Import your bank statements in CSV format' },
            { step: '02', title: 'AI Analysis', desc: 'Our models predict income, expenses, and cash flow' },
            { step: '03', title: 'Take Action', desc: 'Follow personalized recommendations to save more' },
          ].map((item, index) => (
            <div key={index} className="text-center">
              <div className="text-6xl font-bold text-primary-500/20 mb-4">{item.step}</div>
              <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
              <p className="text-gray-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-r from-primary-600 to-blue-600 rounded-3xl p-12 shadow-glow">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Take Control of Your Finances?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of gig workers who've achieved financial stability with FinSage AI
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-white text-primary-600 hover:bg-gray-100 font-bold px-10 py-4 rounded-lg text-lg shadow-lg hover:shadow-xl transition-all"
          >
            Start Your Financial Journey
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-12 border-t border-white/10">
        <div className="flex flex-col md:flex-row justify-between items-center text-gray-400 text-sm">
          <div className="mb-4 md:mb-0">
            © 2025 FinSage AI. Built for Indian gig workers with ❤️
          </div>
          <div className="flex space-x-6">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
