import React from "react";
import GlassCard from "../ui/GlassCard";

const DemoSection = () => {
    return (
        <section id="demo" className="py-16 md:py-24 bg-white/5 relative">
            <div className="container mx-auto px-6">
                <div className="flex flex-col md:flex-row items-center gap-12">
                    <div className="w-full md:w-1/2 space-y-6">
                        <h2 className="text-3xl md:text-4xl font-bold tracking-tighter">
                            See your money in a new light
                        </h2>
                        <p className="text-white/60 text-lg">
                            Ditch the spreadsheets. Our interactive dashboard gives you a crystal clear view of your financial health at a glance.
                        </p>
                        <ul className="space-y-3 text-white/70">
                            <li className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-primary" /> CLEAN visualisations
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-primary" /> Historical performance charts
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-primary" /> Asset allocation breakdowns
                            </li>
                        </ul>
                    </div>

                    <div className="w-full md:w-1/2">
                        <GlassCard className="p-8 aspect-video flex flex-col justify-center items-center relative overflow-hidden group">
                            {/* Abstract UI representation */}
                            <div className="absolute inset-x-12 top-12 bottom-0 bg-white/5 rounded-t-xl border border-white/10 p-4 transition-transform duration-500 group-hover:-translate-y-2">
                                <div className="flex gap-4 mb-4">
                                    <div className="w-1/3 h-20 bg-white/5 rounded-lg animate-pulse" />
                                    <div className="w-1/3 h-20 bg-white/5 rounded-lg animate-pulse delay-100" />
                                    <div className="w-1/3 h-20 bg-primary/20 rounded-lg animate-pulse delay-200" />
                                </div>
                                <div className="w-full h-32 bg-white/5 rounded-lg" />
                            </div>

                            <div className="absolute bottom-6 right-6">
                                <div className="px-4 py-2 bg-primary rounded-lg text-xs font-bold text-white shadow-lg shadow-primary/20">
                                    +12.5% vs Last Year
                                </div>
                            </div>
                        </GlassCard>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default DemoSection;
