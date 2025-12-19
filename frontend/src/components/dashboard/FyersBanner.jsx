import React, { useState, useEffect } from 'react';
import { AlertTriangle, X, ExternalLink, Zap, Clock, Info, CheckCircle } from 'lucide-react';
import { useFyers } from '../../context/FyersContext';

/**
 * FyersBanner - Shows when Fyers connection is needed/expired.
 * 
 * Behaviors:
 * - Shows reconnect CTA when token expired
 * - Dismissible (but comes back on reload)
 * - Option to opt-out and use delayed data
 * - Explains what Fyers provides and how to set it up
 * - App NEVER blocks - just shows informational banner
 */
const FyersBanner = () => {
    const { showBanner, needsSetup, getAuthUrl, toggleOptOut, checkFyersStatus, authenticated } = useFyers();
    const [dismissed, setDismissed] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showDetails, setShowDetails] = useState(false);
    const [authInProgress, setAuthInProgress] = useState(false);

    // Poll for status after OAuth window is opened (every 10 seconds)
    // Stops when authenticated or timeout
    useEffect(() => {
        if (!authInProgress) return;
        
        // Stop polling if already authenticated
        if (authenticated) {
            setAuthInProgress(false);
            return;
        }
        
        const pollInterval = setInterval(async () => {
            await checkFyersStatus(false);
        }, 10000);
        
        // Stop polling after 2 minutes
        const timeout = setTimeout(() => {
            setAuthInProgress(false);
        }, 120000);
        
        return () => {
            clearInterval(pollInterval);
            clearTimeout(timeout);
        };
    }, [authInProgress, authenticated, checkFyersStatus]);

    if (dismissed || (!showBanner && !needsSetup)) {
        return null;
    }

    const handleConnect = async () => {
        try {
            setLoading(true);
            const authUrl = await getAuthUrl();
            // Open in new tab for OAuth flow
            window.open(authUrl, '_blank', 'width=600,height=700');
            setAuthInProgress(true);
        } catch (err) {
            console.error('Failed to start Fyers auth:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleOptOut = () => {
        toggleOptOut(true);
        setDismissed(true);
    };

    return (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 mb-6">
            <div className="flex items-start gap-3">
                <div className="p-2 bg-amber-500/20 rounded-lg shrink-0">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                </div>
                
                <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-4">
                        <h3 className="font-semibold text-amber-200">
                            {needsSetup ? 'Enhance with Real-time Stock Data' : 'Live Stock Data Unavailable'}
                        </h3>
                        <button
                            onClick={() => setDismissed(true)}
                            className="text-amber-500/60 hover:text-amber-500 transition-colors shrink-0"
                            title="Dismiss for this session"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    
                    <p className="text-sm text-amber-200/70 mt-1">
                        {needsSetup 
                            ? 'Connect Fyers for real-time stock prices, or continue with previous day\'s data (slightly delayed but still accurate).'
                            : 'Your Fyers session has expired. Reconnect for live data, or continue using cached/delayed results.'
                        }
                    </p>
                    
                    {/* Expandable Details */}
                    <button
                        onClick={() => setShowDetails(!showDetails)}
                        className="text-xs text-amber-300/60 hover:text-amber-300 mt-2 flex items-center gap-1 transition-colors"
                    >
                        <Info className="w-3.5 h-3.5" />
                        {showDetails ? 'Hide details' : 'What is Fyers? How does this work?'}
                    </button>
                    
                    {showDetails && (
                        <div className="mt-3 p-3 bg-black/20 rounded-lg text-xs space-y-2 text-amber-100/70">
                            <p className="font-medium text-amber-200">About Fyers Integration:</p>
                            <ul className="space-y-1.5 list-none">
                                <li className="flex items-start gap-2">
                                    <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0 mt-0.5" />
                                    <span><strong>Fyers</strong> is a free Indian stockbroker. You only need a free account - no trading or deposits required.</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0 mt-0.5" />
                                    <span><strong>With Fyers:</strong> Get real-time stock prices for more accurate intraday NAV estimates.</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0 mt-0.5" />
                                    <span><strong>Without Fyers:</strong> App uses NSE website scraping - slightly delayed but still accurate for NAV estimation.</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0 mt-0.5" />
                                    <span><strong>Sessions expire daily</strong> (~24 hrs) for security. Just reconnect when prompted - takes 10 seconds.</span>
                                </li>
                            </ul>
                            <p className="text-amber-300/60 pt-1 border-t border-amber-500/20">
                                Your app <strong>never stops working</strong> if Fyers is unavailable - it gracefully falls back to delayed data.
                            </p>
                        </div>
                    )}
                    
                    <div className="flex flex-wrap items-center gap-3 mt-3">
                        <button
                            onClick={handleConnect}
                            disabled={loading || authInProgress}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black font-medium text-sm rounded-lg transition-colors disabled:opacity-50"
                        >
                            <Zap className="w-4 h-4" />
                            {authInProgress ? 'Waiting for login...' : loading ? 'Opening...' : needsSetup ? 'Connect Fyers (Free)' : 'Reconnect Fyers'}
                            <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                        
                        <button
                            onClick={handleOptOut}
                            className="inline-flex items-center gap-2 px-4 py-2 text-amber-200/70 hover:text-amber-200 text-sm transition-colors"
                        >
                            <Clock className="w-4 h-4" />
                            Use delayed data instead
                        </button>
                    </div>
                    
                    {authInProgress && (
                        <p className="text-xs text-amber-300/50 mt-2">
                            Complete the login in the popup window. This will auto-detect when you're done.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FyersBanner;
