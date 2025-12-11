import React, { useState, useContext } from 'react';
import { LayoutDashboard, LogOut, PieChart, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import UploadHoldings from '../components/dashboard/UploadHoldings';
import FundList from '../components/dashboard/FundList';
import PortfolioAnalyzer from '../components/dashboard/PortfolioAnalyzer';
import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
    const navigate = useNavigate();
    const { user, logout } = useContext(AuthContext);
    const [selectedFund, setSelectedFund] = useState(null);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="min-h-screen bg-background text-foreground">
            {/* Header */}
            <header className="border-b border-white/5 bg-background/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-accent/20 rounded-lg">
                            <PieChart className="w-6 h-6 text-accent" />
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">Mutual Fund Tracker</h1>
                    </div>

                    <div className="flex items-center gap-6">
                        {user && (
                            <div className="flex items-center gap-2 text-sm font-medium text-white/80 bg-white/5 px-3 py-1.5 rounded-full border border-white/5">
                                <User className="w-4 h-4 text-brand-accent" />
                                <span>Hi, {user.username}</span>
                            </div>
                        )}
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors"
                        >
                            <LogOut className="w-4 h-4" />
                            Sign Out
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

                {/* Welcome Section */}
                <div>
                    <h2 className="text-2xl font-bold text-white">Portfolio Overview</h2>
                    <p className="text-zinc-400">Track your mutual funds and estimate daily NAV.</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left Column (Upload & Lists) - Weighted larger */}
                    <div className="lg:col-span-12 space-y-8">
                        <UploadHoldings />

                        {/* We'll wrap FundList in a similar card style later or now */}
                        <div className="bg-white/5 border border-white/5 rounded-2xl p-6 shadow-xl">
                            <FundList onSelect={(fund) => setSelectedFund(fund)} />
                        </div>
                    </div>
                </div>
            </main>

            {/* Analyzer Modal */}
            {selectedFund && (
                <PortfolioAnalyzer
                    fundId={selectedFund}
                    onClose={() => setSelectedFund(null)}
                />
            )}
        </div>
    );
};

export default Dashboard;
