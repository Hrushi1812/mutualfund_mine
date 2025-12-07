import React, { useEffect, useState } from 'react';
import api from '../api';

const FundList = () => {
    const [funds, setFunds] = useState([]);

    const fetchFunds = async () => {
        try {
            const response = await api.get('/funds/');
            setFunds(response.data.funds_available);
        } catch (error) {
            console.error("Error fetching funds:", error);
        }
    };

    useEffect(() => {
        fetchFunds();
    }, []);

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Available Funds</h2>
            {funds.length === 0 ? (
                <p className="text-gray-500">No funds found. Please upload holdings.</p>
            ) : (
                <ul className="space-y-2">
                    {funds.map((fund, index) => (
                        <li key={index} className="p-3 bg-gray-50 rounded-md border border-gray-200 text-gray-700">
                            {fund}
                        </li>
                    ))}
                </ul>
            )}
            <button
                onClick={fetchFunds}
                className="mt-4 text-sm text-blue-600 hover:text-blue-800 underline"
            >
                Refresh List
            </button>
        </div>
    );
};

export default FundList;
