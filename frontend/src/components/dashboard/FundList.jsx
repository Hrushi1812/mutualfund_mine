import React, { useContext } from 'react';
import { Database, RefreshCw, ChevronRight, Trash2, AlertCircle } from 'lucide-react';
import api from '../../api';
import { PortfolioContext } from '../../context/PortfolioContext';

const FundList = ({ onSelect }) => {
    const { funds, loading, fetchFunds } = useContext(PortfolioContext);

    const handleDelete = async (e, fundId, fundName) => {
        e.stopPropagation(); // Prevent opening the analyzer
        if (window.confirm(`Are you sure you want to delete "${fundName}"?`)) {
            try {
                await api.delete(`/funds/${fundId}`);
                fetchFunds(); // Refresh globally
            } catch (error) {
                console.error("Failed to delete fund:", error);
                alert("Failed to delete fund. Please try again.");
            }
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                    <Database className="w-5 h-5 text-accent" />
                    Your Portfolios
                </h2>
                <button
                    onClick={fetchFunds}
                    className="p-2 hover:bg-white/5 rounded-full transition-colors text-zinc-400 hover:text-white"
                    title="Refresh List"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {funds.length === 0 ? (
                <div className="text-center py-10 border-2 border-dashed border-white/5 rounded-xl">
                    <p className="text-zinc-400">No portfolios found. Upload one to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {funds.map((fund, index) => (
                        <div
                            key={fund.id}
                            onClick={() => onSelect && onSelect(fund.id)}
                            className="bg-white/5 border border-white/5 hover:border-accent/50 p-4 rounded-xl transition-all cursor-pointer group active:scale-[0.98] relative"
                        >
                            <div className="flex justify-between items-center">
                                <div className="flex-1 overflow-hidden">
                                    <h3 className="font-semibold text-foreground truncate pr-8">
                                        {fund.nickname || fund.fund_name}
                                    </h3>
                                    {fund.nickname && (
                                        <p className="text-xs text-zinc-500 truncate mb-1">
                                            {fund.fund_name}
                                        </p>
                                    )}
                                    <p className="text-xs text-zinc-400 mt-1 flex items-center gap-2">
                                        {fund.invested_amount ? (
                                            <>
                                                <span className="text-zinc-300">₹{fund.invested_amount} invested</span>
                                                <span className="w-1 h-1 rounded-full bg-zinc-600"></span>
                                            </>
                                        ) : null}
                                        {fund.invested_date ? (
                                            <span>Started {fund.invested_date}</span>
                                        ) : (
                                            <span>Click to Analyze</span>
                                        )}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={(e) => handleDelete(e, fund.id, fund.fund_name)}
                                        className="p-2 hover:bg-red-500/20 text-zinc-500 hover:text-red-500 rounded-lg transition-colors z-10"
                                        title="Delete Portfolio"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                    <ChevronRight className="w-5 h-5 text-zinc-400 group-hover:text-accent transition-colors" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FundList;
