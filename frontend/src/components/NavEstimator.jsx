import React, { useState } from 'react';
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
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Estimate NAV</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Fund Name</label>
                    <input
                        type="text"
                        name="fund_name"
                        value={formData.fund_name}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        placeholder="Exact fund name"
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Previous NAV</label>
                        <input
                            type="number"
                            step="0.0001"
                            name="prev_nav"
                            value={formData.prev_nav}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Investment Amount</label>
                        <input
                            type="number"
                            step="0.01"
                            name="investment"
                            value={formData.investment}
                            onChange={handleChange}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        />
                    </div>
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    {loading ? 'Calculating...' : 'Estimate'}
                </button>
            </form>

            {error && <p className="text-red-500 text-sm mt-4">{error}</p>}

            {result && (
                <div className="mt-6 p-4 bg-gray-50 rounded-md border border-gray-200">
                    <h3 className="font-semibold text-lg text-gray-900 mb-2">Estimation Results</h3>
                    <div className="grid grid-cols-2 gap-y-2 text-sm">
                        <span className="text-gray-600">Estimated NAV:</span>
                        <span className="font-bold text-gray-900">{result.estimated_nav}</span>

                        <span className="text-gray-600">Change %:</span>
                        <span className={`font-bold ${result['nav_change_%'] >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {result['nav_change_%']}%
                        </span>

                        <span className="text-gray-600">Current Value:</span>
                        <span className="font-bold text-gray-900">₹{result.current_value}</span>

                        <span className="text-gray-600">P&L:</span>
                        <span className={`font-bold ${result.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ₹{result.pnl} ({result.pnl_percentage}%)
                        </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Calculated at: {result.timestamp}</p>
                </div>
            )}
        </div>
    );
};

export default NavEstimator;
