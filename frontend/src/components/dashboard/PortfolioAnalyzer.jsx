import React, { useState } from 'react';
import { X, Calculator, Calendar, IndianRupee, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../api';

const PortfolioAnalyzer = ({ fundId, onClose }) => {
    // State for Analysis Results
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true); // Start loading immediately
    const [error, setError] = useState(null);

    const hasFetched = React.useRef(false);

    // Auto-analyze on mount
    React.useEffect(() => {
        if (!hasFetched.current) {
            handleAnalyze();
            hasFetched.current = true;
        }
    }, []);

    const handleAnalyze = async () => {
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('fund_id', fundId);
        // No longer sending amount/date manually

        try {
            const response = await api.post('/analyze-portfolio', formData);
            if (response.data.error) {
                setError(response.data.error);
            } else if (response.data && response.data.pnl !== undefined) {
                setResult(response.data);
            } else {
                setError("No valid analysis data returned.");
            }
        } catch (err) {
            console.error("Analysis Failed:", err);
            setError("Failed to connect to server.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                    className="bg-[#1a1b1e] border border-white/10 rounded-3xl w-full max-w-md overflow-hidden shadow-2xl"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/5 flex justify-between items-start">
                        <div>
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <Calculator className="w-5 h-5 text-accent" />
                                Portfolio Analysis
                            </h2>
                            <p className="text-sm text-zinc-400 mt-1">
                                {result?.nickname || result?.fund_name || "Loading..."}
                            </p>
                        </div>
                        <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors">
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-10 space-y-4">
                                <div className="relative">
                                    <div className="w-16 h-16 border-4 border-white/10 border-t-accent rounded-full animate-spin"></div>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="w-8 h-8 bg-accent/20 rounded-full animate-pulse"></div>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <p className="text-white font-medium">Analyzing Portfolio...</p>
                                    <p className="text-sm text-zinc-500 mt-1">Fetching real-time NAV and calculating P&L</p>
                                </div>
                            </div>
                        ) : error ? (
                            <div className="flex flex-col items-center justify-center py-6 text-center">
                                <div className="p-3 bg-red-500/10 rounded-full mb-3 text-red-500 border border-red-500/20">
                                    <TrendingDown className="w-8 h-8" />
                                </div>
                                <h3 className="text-lg font-bold text-white mb-2">Analysis Failed</h3>
                                <p className="text-sm text-zinc-400 mb-6">{error}</p>
                                <button
                                    onClick={onClose}
                                    className="px-6 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors border border-white/5"
                                >
                                    Close
                                </button>
                            </div>
                        ) : result ? (
                            // Results View
                            <div className="space-y-6">
                                {/* Key Metrics Grid - Creative Redesign */}
                                <div className="grid grid-cols-3 gap-4 mb-6">
                                    {/* Invested */}
                                    <div className="flex flex-col">
                                        <span className="text-xs text-zinc-500 mb-1 font-medium tracking-wide">Invested value</span>
                                        <span className="text-lg font-bold text-white tracking-tight">₹{result.invested_amount}</span>
                                    </div>

                                    {/* 1D Returns */}
                                    <div className="flex flex-col items-center">
                                        <span className="text-xs text-zinc-500 mb-1 font-medium tracking-wide">1D returns</span>
                                        <div className={`flex flex-col items-center leading-tight ${result.day_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                            <span className="text-sm font-bold whitespace-nowrap">
                                                {result.day_pnl >= 0 ? '+' : ''}₹{Math.abs(result.day_pnl)}
                                            </span>
                                            <span className="text-xs font-medium opacity-80 whitespace-nowrap">
                                                ({result.day_pnl >= 0 ? '+' : ''}{result.day_pnl_pct}%)
                                            </span>
                                        </div>
                                    </div>

                                    {/* Total Returns */}
                                    <div className="flex flex-col items-end">
                                        <span className="text-xs text-zinc-500 mb-1 font-medium tracking-wide">Total returns</span>
                                        <div className={`flex flex-col items-end leading-tight ${result.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                            <span className="text-sm font-bold whitespace-nowrap">
                                                {result.pnl >= 0 ? '+' : ''}₹{Math.abs(result.pnl)}
                                            </span>
                                            <span className="text-xs font-medium opacity-80 whitespace-nowrap">
                                                ({result.pnl >= 0 ? '+' : ''}{result.pnl_pct}%)
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Secondary Info Card */}
                                <div className="bg-white/5 rounded-2xl p-4 border border-white/5 space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-zinc-400">Current Value</span>
                                        <span className="font-mono font-bold text-xl text-white">₹{result.current_value}</span>
                                    </div>
                                    <div className="h-px bg-white/5 w-full my-2"></div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-zinc-400">Live NAV (Est)</span>
                                        <span className="font-mono text-white">₹{result.current_nav}</span>
                                    </div>
                                </div>

                                {/* Note */}
                                <div className="text-[10px] text-center text-zinc-600 px-4">
                                    {result.note}
                                    <br />
                                    Last Updated: {result.last_updated}
                                </div>
                            </div>
                        ) : null}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default PortfolioAnalyzer;
