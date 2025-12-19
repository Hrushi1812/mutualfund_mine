import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import api from '../api';
import { AuthContext } from './AuthContext';

export const FyersContext = createContext();

/**
 * FyersProvider manages Fyers API connection state.
 * 
 * Key behaviors:
 * - On app load: checks Fyers status with live validation
 * - If token expired: shows banner but app continues working
 * - Provides reconnect flow for users
 * - Users can choose NOT to use Fyers (delayed results)
 */
export const FyersProvider = ({ children }) => {
    const { isAuthenticated } = useContext(AuthContext);
    
    // Fyers connection state
    const [fyersStatus, setFyersStatus] = useState({
        authenticated: false,
        configured: false,
        tokenExpiry: null,
        loading: true,
        error: null,
    });
    
    // User preference: opt out of Fyers
    const [userOptedOut, setUserOptedOut] = useState(() => {
        return localStorage.getItem('fyers_opted_out') === 'true';
    });

    /**
     * Check Fyers API status.
     * @param {boolean} validate - If true, performs live API validation
     */
    const checkFyersStatus = useCallback(async (validate = false) => {
        try {
            setFyersStatus(prev => ({ ...prev, loading: true, error: null }));
            const response = await api.get(`/api/fyers/status?validate=${validate}`);
            
            setFyersStatus({
                authenticated: response.data.authenticated,
                configured: response.data.configured,
                tokenExpiry: response.data.token_expiry,
                liveValidated: response.data.live_validated,
                loading: false,
                error: null,
            });
        } catch (err) {
            console.error('Fyers status check failed:', err);
            setFyersStatus(prev => ({
                ...prev,
                authenticated: false,
                loading: false,
                error: 'Failed to check Fyers status',
            }));
        }
    }, []);

    /**
     * Get OAuth authorization URL for connecting Fyers.
     */
    const getAuthUrl = async () => {
        try {
            const response = await api.get('/api/fyers/auth-url');
            return response.data.auth_url;
        } catch (err) {
            console.error('Failed to get Fyers auth URL:', err);
            throw err;
        }
    };

    /**
     * Disconnect Fyers (clear token).
     */
    const disconnectFyers = async () => {
        try {
            await api.get('/api/fyers/disconnect');
            setFyersStatus(prev => ({
                ...prev,
                authenticated: false,
                tokenExpiry: null,
            }));
        } catch (err) {
            console.error('Failed to disconnect Fyers:', err);
        }
    };

    /**
     * Toggle user opt-out preference.
     */
    const toggleOptOut = (optOut) => {
        setUserOptedOut(optOut);
        localStorage.setItem('fyers_opted_out', optOut.toString());
    };

    // Check Fyers status on mount (with live validation)
    // Skip if user has opted for delayed mode
    useEffect(() => {
        if (isAuthenticated && !userOptedOut) {
            checkFyersStatus(true); // Validate on startup
        } else {
            setFyersStatus(prev => ({ ...prev, loading: false }));
        }
    }, [isAuthenticated, userOptedOut, checkFyersStatus]);

    // No periodic checks needed - we know token expiry from initial check
    // Token typically valid for 24 hours, user will see banner on next app load if expired

    // Computed states
    const isConnected = fyersStatus.authenticated && !userOptedOut;
    const showBanner = isAuthenticated && !fyersStatus.loading && !fyersStatus.authenticated && !userOptedOut && fyersStatus.configured;
    const needsSetup = isAuthenticated && fyersStatus.configured === false;

    const value = {
        ...fyersStatus,
        isConnected,
        showBanner,
        needsSetup,
        userOptedOut,
        checkFyersStatus,
        getAuthUrl,
        disconnectFyers,
        toggleOptOut,
    };

    return (
        <FyersContext.Provider value={value}>
            {children}
        </FyersContext.Provider>
    );
};

/**
 * Hook to use Fyers context.
 */
export const useFyers = () => {
    const context = useContext(FyersContext);
    if (!context) {
        throw new Error('useFyers must be used within a FyersProvider');
    }
    return context;
};
