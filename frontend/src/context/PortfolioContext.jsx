import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api';
import { AuthContext } from './AuthContext';

export const PortfolioContext = createContext();

export const PortfolioProvider = ({ children }) => {
    const { isAuthenticated } = useContext(AuthContext);
    const [funds, setFunds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchFunds = async () => {
        if (!isAuthenticated) return;

        setLoading(true);
        setError(null);
        try {
            const response = await api.get('/funds/');
            setFunds(response.data.funds_available || []);
        } catch (err) {
            console.error("Error fetching funds:", err);
            setError("Failed to load portfolios.");
        } finally {
            setLoading(false);
        }
    };

    // Auto-fetch when authenticated
    useEffect(() => {
        if (isAuthenticated) {
            fetchFunds();
        } else {
            setFunds([]); // Clear on logout
        }
    }, [isAuthenticated]);

    return (
        <PortfolioContext.Provider value={{ funds, loading, error, fetchFunds }}>
            {children}
        </PortfolioContext.Provider>
    );
};
