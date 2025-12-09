import React, { useEffect, useState } from 'react';
import { Database, RefreshCw, ChevronRight } from 'lucide-react';
import api from '../api';

const FundList = () => {
    const [funds, setFunds] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchFunds = async () => {
        setLoading(true);
        try {
            const response = await api.get('/funds/');
            setFunds(response.data.funds_available);
        } catch (error) {
            console.error("Error fetching funds:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFunds();
    }, []);

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-brand-text flex items-center gap-2">
                    <Database className="w-5 h-5 text-brand-accent" />
                    Your Portfolios
                </h2>
                <button
                    onClick={fetchFunds}
                    className="p-2 hover:bg-brand-surface rounded-full transition-colors text-brand-muted hover:text-white"
                    title="Refresh List"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {funds.length === 0 ? (
                <div className="text-center py-10 border-2 border-dashed border-white/5 rounded-xl">
                    <p className="text-brand-muted">No portfolios found. Upload one to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {funds.map((fund, index) => (
                        <div key={index} className="bg-brand-surface/50 border border-white/5 hover:border-brand-accent/50 p-4 rounded-xl transition-all cursor-pointer group">
                            <div className="flex justify-between items-center">
                                <div className="flex-1">
                                    <h3 className="font-semibold text-brand-text truncate pr-2">{fund}</h3>
                                    <p className="text-xs text-brand-muted mt-1">Last updated: Today</p>
                                </div>
                                <ChevronRight className="w-5 h-5 text-brand-muted group-hover:text-brand-accent transition-colors" />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FundList;
