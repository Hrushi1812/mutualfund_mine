import React, { useContext, useState } from 'react';
import { Database, RefreshCw, ChevronRight, Trash2, AlertCircle, Zap, Clock } from 'lucide-react';
import api from '../../api';
import { PortfolioContext } from '../../context/PortfolioContext';
import { FyersContext } from '../../context/FyersContext';

const FundList = ({ onSelect }) => {
    const { funds, loading, fetchFunds } = useContext(PortfolioContext);
    const fyersContext = useContext(FyersContext);
    const isLiveData = fyersContext?.isConnected;
    const userOptedOut = fyersContext?.userOptedOut;
    const [connectingFyers, setConnectingFyers] = useState(false);

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

    const handleConnectFyers = async () => {
        if (!fyersContext) return;
        try {
            setConnectingFyers(true);
            // First, opt back in if user had opted out
            if (userOptedOut) {
                fyersContext.toggleOptOut(false);
            }
            const authUrl = await fyersContext.getAuthUrl();
            window.open(authUrl, '_blank', 'width=600,height=700');
            // No polling here - FyersConnectionCard handles polling when user clicks there
            // User can refresh or the banner will show status
        } catch (err) {
            console.error('Failed to start Fyers auth:', err);
        } finally {
            setConnectingFyers(false);
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                        <Database className="w-5 h-5 text-accent" />
                        Your Portfolios
                    </h2>
                    {/* Data source indicator - clickable when in delayed mode */}
                    {isLiveData ? (
                        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                            <Zap className="w-3 h-3" />
                            Live
                        </div>
                    ) : (
                        <button
                            onClick={handleConnectFyers}
                            disabled={connectingFyers}
                            className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-zinc-500/10 text-zinc-400 border border-zinc-500/20 hover:bg-amber-500/10 hover:text-amber-400 hover:border-amber-500/20 transition-colors cursor-pointer"
                            title="Click to connect Fyers for live data"
                        >
                            <Clock className="w-3 h-3" />
                            {connectingFyers ? 'Connecting...' : 'Delayed · Upgrade'}
                        </button>
                    )}
                </div>
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
                                    <h3 className="font-semibold text-foreground truncate pr-8 flex items-center gap-2">
                                        {fund.nickname || fund.fund_name}
                                        {fund.is_stale && (
                                            <div className="group/tooltip relative">
                                                <AlertCircle className="w-4 h-4 text-amber-500" />
                                                <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-zinc-800 text-white rounded opacity-0 group-hover/tooltip:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none">
                                                    Update Required
                                                </span>
                                            </div>
                                        )}
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
