import React from "react";
import { Zap, Clock, Shield, CheckCircle, ExternalLink } from "lucide-react";

const FyersInfo = () => {
    return (
        <section className="py-16 md:py-24 relative">
            <div className="container mx-auto px-6">
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto mb-12">
                    <span className="inline-block px-3 py-1 text-xs font-medium bg-primary/10 text-primary rounded-full mb-4">
                        Optional Enhancement
                    </span>
                    <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tighter">
                        Real-time Data with Fyers
                    </h2>
                    <p className="text-white/60">
                        Get live stock prices for more accurate NAV estimates. Completely optional - the app works great without it too!
                    </p>
                </div>

                {/* Comparison Cards */}
                <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                    {/* With Fyers */}
                    <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20 rounded-2xl p-6 relative overflow-hidden">
                        <div className="absolute top-4 right-4">
                            <span className="px-2 py-1 text-[10px] font-semibold bg-primary/20 text-primary rounded-full">
                                RECOMMENDED
                            </span>
                        </div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-3 bg-primary/20 rounded-xl">
                                <Zap className="w-6 h-6 text-primary" />
                            </div>
                            <h3 className="text-xl font-semibold text-white">With Fyers</h3>
                        </div>
                        <ul className="space-y-3 mb-6">
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>Real-time stock prices during market hours</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>More accurate intraday NAV estimates</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>100% free - just need a Fyers account</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>No trading or deposits required</span>
                            </li>
                        </ul>
                        <a
                            href="https://fyers.in"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
                        >
                            Create free Fyers account
                            <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                    </div>

                    {/* Without Fyers */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-3 bg-white/10 rounded-xl">
                                <Clock className="w-6 h-6 text-zinc-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white">Without Fyers</h3>
                        </div>
                        <ul className="space-y-3 mb-6">
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>Uses NSE website data (slightly delayed)</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>All features work normally</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>No account needed</span>
                            </li>
                            <li className="flex items-start gap-2 text-sm text-white/80">
                                <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                                <span>Great for end-of-day tracking</span>
                            </li>
                        </ul>
                        <p className="text-xs text-zinc-500">
                            Perfect if you don't need real-time updates
                        </p>
                    </div>
                </div>

                {/* Security Note */}
                <div className="mt-8 max-w-2xl mx-auto">
                    <div className="flex items-center justify-center gap-2 text-sm text-zinc-400 bg-white/5 rounded-xl p-4">
                        <Shield className="w-4 h-4 text-green-400" />
                        <span>
                            Fyers connection is secure via OAuth. We never see or store your Fyers password. 
                            Sessions expire every 24 hours for your security.
                        </span>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default FyersInfo;
