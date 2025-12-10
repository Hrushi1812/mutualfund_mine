import React, { useState } from 'react';
import { Calculator, TrendingUp, TrendingDown, IndianRupee, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../../api';

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
            className="glass p-8 rounded-3xl h-full flex flex-col"
        >
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <div className="p-2 rounded-lg bg-accent/20 text-accent">
                    <Calculator className="w-5 h-5" />
                </div>
                Live NAV Estimator
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4 flex-grow">
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Fund Name</label>
                    <input
                        type="text"
                        name="fund_name"
                        value={formData.fund_name}
                        onChange={handleChange}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-accent transition-colors"
                        placeholder="Exact fund name"
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Previous NAV</label>
                        <div className="relative">
                            <Activity className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="number"
                                step="0.0001"
                                name="prev_nav"
                                value={formData.prev_nav}
                                onChange={handleChange}
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Investment</label>
                        <div className="relative">
                            <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="number"
                                step="0.01"
                                name="investment"
                                value={formData.investment}
                                onChange={handleChange}
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                            />
                        </div>
                    </div>
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2 mt-4"
                >
                    {loading ? 'Calculating...' : 'Run Simulation'}
                </button>
            </form>

            {error && (
                <div className="mt-4 p-3 bg-red-500/10 text-red-500 text-sm rounded-xl border border-red-500/20">
                    {error}
                </div>
            )}

            {result && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-6 p-5 bg-black/40 rounded-2xl border border-white/5 space-y-4"
                >
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-xs text-zinc-400">Estimated NAV</p>
                            <p className="text-2xl font-bold text-white">{result.estimated_nav}</p>
                        </div>
                        <div className={`flex items-center gap-1 text-sm font-bold ${result['nav_change_%'] >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {result['nav_change_%'] >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                            {result['nav_change_%']}%
                        </div>
                    </div>

                    <div className="pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-xs text-zinc-400">Current Value</p>
                            <p className="text-lg font-semibold text-white">₹{result.current_value}</p>
                        </div>
                        <div>
                            <p className="text-xs text-zinc-400">Total P&L</p>
                            <p className={`text-lg font-semibold ${result.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                ₹{result.pnl}
                            </p>
                        </div>
                    </div>
                    <p className="text-[10px] text-zinc-500 text-right">Updated: {result.timestamp}</p>
                </motion.div>
            )}
        </motion.div>
    );
};

export default NavEstimator;
