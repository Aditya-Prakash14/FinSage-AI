import { useState } from 'react';
import {
    Sparkles,
    AlertTriangle,
    CheckCircle2,
    TrendingUp,
    Shield,
    PiggyBank,
    Activity,
    ArrowRight,
    ChevronDown,
    ChevronUp,
    Target,
    Zap,
    Award,
    TrendingDown,
    DollarSign
} from 'lucide-react';

function AgentAnalysis({ report }) {
    const [expandedSection, setExpandedSection] = useState('executive');

    if (!report) return null;

    const {
        executive_summary,
        financial_overview,
        budget_plan,
        risk_profile,
        savings_plan,
        alerts
    } = report;

    const toggleSection = (section) => {
        setExpandedSection(expandedSection === section ? null : section);
    };

    const SectionHeader = ({ id, title, icon: Icon, color, badge }) => (
        <button
            onClick={() => toggleSection(id)}
            className={`w-full flex items-center justify-between p-5 rounded-xl transition-all ${expandedSection === id
                    ? 'bg-white dark:bg-fintech-card shadow-lg scale-[1.02]'
                    : 'hover:bg-gray-50 dark:hover:bg-fintech-dark hover:shadow-md'
                }`}
        >
            <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${color}`}>
                    <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="text-left">
                    <span className="font-bold text-lg">{title}</span>
                    {badge && (
                        <span className="ml-2 px-2 py-1 text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full">
                            {badge}
                        </span>
                    )}
                </div>
            </div>
            {expandedSection === id ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
        </button>
    );

    // Get health score color
    const getHealthColor = (score) => {
        if (score >= 75) return 'text-green-600 dark:text-green-400';
        if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
        if (score >= 40) return 'text-orange-600 dark:text-orange-400';
        return 'text-red-600 dark:text-red-400';
    };

    const healthScore = executive_summary?.health_score || 0;

    return (
        <div className="space-y-6">
            {/* Hero Section with Health Score */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl">
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="relative p-8">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-3">
                                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                                    <Sparkles className="w-7 h-7 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold">AI Financial Analysis</h2>
                                    <p className="text-indigo-100 text-sm">
                                        Powered by Multi-Agent Intelligence System
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-indigo-100 mb-1">Health Score</div>
                            <div className="text-6xl font-bold">{healthScore}</div>
                            <div className="text-sm font-medium mt-1 bg-white/20 px-3 py-1 rounded-full inline-block">
                                {executive_summary?.overall_status}
                            </div>
                        </div>
                    </div>

                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white/10 backdrop-blur-sm rounded-xl p-5">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <TrendingUp className="w-4 h-4 text-green-300" />
                                <div className="text-xs text-indigo-200 uppercase">Income</div>
                            </div>
                            <div className="font-bold text-lg">₹{executive_summary?.key_metrics?.monthly_income?.toLocaleString()}</div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <TrendingDown className="w-4 h-4 text-red-300" />
                                <div className="text-xs text-indigo-200 uppercase">Expenses</div>
                            </div>
                            <div className="font-bold text-lg">₹{executive_summary?.key_metrics?.monthly_expenses?.toLocaleString()}</div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <PiggyBank className="w-4 h-4 text-blue-300" />
                                <div className="text-xs text-indigo-200 uppercase">Savings</div>
                            </div>
                            <div className="font-bold text-lg">{(executive_summary?.key_metrics?.savings_rate * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <Shield className="w-4 h-4 text-yellow-300" />
                                <div className="text-xs text-indigo-200 uppercase">Risk</div>
                            </div>
                            <div className="font-bold text-lg">{executive_summary?.risk_level}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Priority Actions */}
            {executive_summary?.priority_actions?.length > 0 && (
                <div className="card border-l-4 border-emerald-500 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center">
                            <Target className="w-5 h-5 text-emerald-500" />
                        </div>
                        <h3 className="font-bold text-xl">Priority Actions</h3>
                        <span className="ml-auto px-3 py-1 bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 rounded-full text-sm font-medium">
                            {executive_summary.priority_actions.length} Actions
                        </span>
                    </div>
                    <div className="space-y-3">
                        {executive_summary.priority_actions.map((action, idx) => (
                            <div key={idx} className="group flex items-start space-x-3 p-4 bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/10 dark:to-green-900/10 rounded-xl hover:shadow-md transition-all">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center flex-shrink-0 text-sm font-bold text-white shadow-lg">
                                    {idx + 1}
                                </div>
                                <p className="text-emerald-900 dark:text-emerald-100 flex-1 pt-1">{action}</p>
                                <CheckCircle2 className="w-5 h-5 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Critical Alerts */}
            {executive_summary?.critical_alerts?.length > 0 && (
                <div className="card border-l-4 border-red-500 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                            <AlertTriangle className="w-5 h-5 text-red-500" />
                        </div>
                        <h3 className="font-bold text-xl">Critical Alerts</h3>
                        <span className="ml-auto px-3 py-1 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-full text-sm font-medium">
                            Urgent
                        </span>
                    </div>
                    <div className="space-y-3">
                        {executive_summary.critical_alerts.map((alert, idx) => (
                            <div key={idx} className="flex items-start space-x-3 p-4 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/10 dark:to-orange-900/10 rounded-xl border border-red-200 dark:border-red-800">
                                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                    <p className="font-medium text-red-900 dark:text-red-100">{alert.message}</p>
                                    <p className="text-sm text-red-700 dark:text-red-300 mt-1">Severity: {alert.severity}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Detailed Sections */}
            <div className="space-y-3">
                {/* Financial Overview */}
                <div className="border border-gray-200 dark:border-fintech-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
                    <SectionHeader id="overview" title="Financial Overview" icon={Activity} color="from-blue-500 to-cyan-600" badge="AI Powered" />
                    {expandedSection === 'overview' && (
                        <div className="p-6 border-t border-gray-200 dark:border-fintech-border bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-900/5 dark:to-cyan-900/5">
                            <div className="space-y-4">
                                {financial_overview?.analysis?.insights?.key_findings?.map((finding, idx) => (
                                    <div key={idx} className="flex items-start space-x-3 p-3 bg-white dark:bg-fintech-dark rounded-lg">
                                        <Zap className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                                        <p className="text-gray-700 dark:text-gray-300">{finding}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Budget Plan */}
                <div className="border border-gray-200 dark:border-fintech-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
                    <SectionHeader id="budget" title="Smart Budget Plan" icon={DollarSign} color="from-purple-500 to-pink-600" badge="Optimized" />
                    {expandedSection === 'budget' && (
                        <div className="p-6 border-t border-gray-200 dark:border-fintech-border bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-900/5 dark:to-pink-900/5">
                            <div className="grid gap-3">
                                {Object.entries(budget_plan?.allocations || {}).map(([category, amount]) => (
                                    <div key={category} className="flex justify-between items-center p-4 bg-white dark:bg-fintech-dark rounded-xl hover:shadow-md transition-shadow">
                                        <span className="capitalize font-medium flex items-center gap-2">
                                            <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                                            {category.replace('_', ' ')}
                                        </span>
                                        <span className="font-bold text-purple-600 dark:text-purple-400">₹{amount.toLocaleString()}</span>
                                    </div>
                                ))}
                                {budget_plan?.ai_recommendations?.strategy_explanation && (
                                    <div className="mt-4 p-4 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl">
                                        <p className="text-sm text-purple-800 dark:text-purple-200">
                                            {budget_plan.ai_recommendations.strategy_explanation}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Risk Profile */}
                <div className="border border-gray-200 dark:border-fintech-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
                    <SectionHeader id="risk" title="Risk Assessment" icon={Shield} color="from-orange-500 to-red-600" badge="Live" />
                    {expandedSection === 'risk' && (
                        <div className="p-6 border-t border-gray-200 dark:border-fintech-border bg-gradient-to-br from-orange-50/50 to-red-50/50 dark:from-orange-900/5 dark:to-red-900/5">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {Object.entries(risk_profile?.risk_scores || {}).map(([risk, score]) => (
                                    <div key={risk} className="p-4 bg-white dark:bg-fintech-dark rounded-xl">
                                        <div className="flex justify-between mb-2">
                                            <span className="capitalize text-sm font-medium">{risk.replace('_', ' ')}</span>
                                            <span className={`text-sm font-bold ${score > 0.7 ? 'text-red-500' : score > 0.4 ? 'text-orange-500' : 'text-green-500'
                                                }`}>
                                                {(score * 100).toFixed(0)}% Risk
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                                            <div
                                                className={`h-2.5 rounded-full transition-all duration-500 ${score > 0.7 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                                                        score > 0.4 ? 'bg-gradient-to-r from-orange-500 to-orange-600' :
                                                            'bg-gradient-to-r from-green-500 to-green-600'
                                                    }`}
                                                style={{ width: `${score * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Savings Plan */}
                <div className="border border-gray-200 dark:border-fintech-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow">
                    <SectionHeader id="savings" title="Savings Strategy" icon={PiggyBank} color="from-green-500 to-emerald-600" badge="Personalized" />
                    {expandedSection === 'savings' && (
                        <div className="p-6 border-t border-gray-200 dark:border-fintech-border bg-gradient-to-br from-green-50/50 to-emerald-50/50 dark:from-green-900/5 dark:to-emerald-900/5">
                            <div className="text-center mb-6 p-6 bg-white dark:bg-fintech-dark rounded-xl">
                                <div className="text-sm text-gray-500 mb-2">Monthly Savings Target</div>
                                <div className="text-5xl font-bold text-green-600 dark:text-green-400">
                                    ₹{savings_plan?.strategy?.target_amount?.toLocaleString()}
                                </div>
                            </div>
                            <div className="space-y-3">
                                {savings_plan?.strategy?.milestones?.map((milestone, idx) => (
                                    <div key={idx} className="flex items-center space-x-3 p-4 bg-white dark:bg-fintech-dark rounded-xl border-2 border-green-100 dark:border-green-900/30 hover:border-green-300 dark:hover:border-green-700 transition-colors">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white font-bold shadow-lg">
                                            {idx + 1}
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-medium">{milestone.description}</p>
                                            <p className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1 mt-1">
                                                <Award className="w-4 h-4" />
                                                Reward: {milestone.reward}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AgentAnalysis;
