import React, { useState } from 'react';
import { Calculator, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../api';

const NavEstimator = () => {
    const [formData, setFormData] = useState({
        fund_name: '',
        prev_nav: '',
        investment: '',
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        const data = new FormData();
        data.append('fund_name', formData.fund_name);
        data.append('prev_nav', formData.prev_nav);
        data.append('investment', formData.investment);

        try {
            const response = await api.post('/estimate-nav/', data);
            if (response.data.error) {
                setError(response.data.error);
            } else {
                setResult(response.data);
            }
        } catch (err) {
            console.error("Estimation error:", err);
            setError('Failed to estimate NAV. Check if fund name is correct.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-brand-card border border-white/5 rounded-2xl p-6 shadow-xl h-full"
        >
            <h2 className="text-xl font-bold text-brand-text mb-6 flex items-center gap-2">
                <Calculator className="w-5 h-5 text-brand-glow" />
                Live NAV Estimator
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Fund Name</label>
                    <input
                        type="text"
                        name="fund_name"
                        value={formData.fund_name}
                        onChange={handleChange}
                        className="w-full bg-brand-surface border border-white/10 rounded-lg px-4 py-3 text-brand-text placeholder-brand-muted/50 focus:outline-none focus:border-brand-glow transition-colors"
                        placeholder="Exact fund name"
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Previous NAV</label>
                        <div className="relative">
                            <Activity className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-muted" />
                            <input
                                type="number"
                                step="0.0001"
                                name="prev_nav"
                                value={formData.prev_nav}
                                onChange={handleChange}
                                className="w-full bg-brand-surface border border-white/10 rounded-lg pl-9 pr-4 py-3 text-brand-text focus:outline-none focus:border-brand-glow transition-colors"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Investment</label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-muted" />
                            <input
                                type="number"
                                step="0.01"
                                name="investment"
                                value={formData.investment}
                                onChange={handleChange}
                                className="w-full bg-brand-surface border border-white/10 rounded-lg pl-9 pr-4 py-3 text-brand-text focus:outline-none focus:border-brand-glow transition-colors"
                            />
                        </div>
                    </div>
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-brand-surface hover:bg-brand-surface/80 border border-brand-glow/30 text-brand-glow font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                    {loading ? 'Calculating...' : 'Run Simulation'}
                </button>
            </form>

            {error && (
                <div className="mt-4 p-3 bg-brand-error/10 text-brand-error text-sm rounded-lg border border-brand-error/20">
                    {error}
                </div>
            )}

            {result && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-6 p-5 bg-black/20 rounded-xl border border-white/5 space-y-4"
                >
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-xs text-brand-muted">Estimated NAV</p>
                            <p className="text-2xl font-bold text-white">{result.estimated_nav}</p>
                        </div>
                        <div className={`flex items-center gap-1 text-sm font-bold ${result['nav_change_%'] >= 0 ? 'text-brand-success' : 'text-brand-error'}`}>
                            {result['nav_change_%'] >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                            {result['nav_change_%']}%
                        </div>
                    </div>

                    <div className="pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-xs text-brand-muted">Current Value</p>
                            <p className="text-lg font-semibold text-brand-text">₹{result.current_value}</p>
                        </div>
                        <div>
                            <p className="text-xs text-brand-muted">Total P&L</p>
                            <p className={`text-lg font-semibold ${result.pnl >= 0 ? 'text-brand-success' : 'text-brand-error'}`}>
                                ₹{result.pnl}
                            </p>
                        </div>
                    </div>
                    <p className="text-[10px] text-brand-muted text-right">Updated: {result.timestamp}</p>
                </motion.div>
            )}
        </motion.div>
    );
};

export default NavEstimator;
