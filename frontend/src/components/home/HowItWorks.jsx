import React from "react";

const Step = ({ number, title, description }) => (
    <div className="flex flex-col items-center text-center space-y-4 relative z-10">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-primary/20">
            {number}
        </div>
        <h3 className="text-xl font-bold text-white">{title}</h3>
        <p className="text-white/50 text-sm max-w-xs">{description}</p>
    </div>
);

const HowItWorks = () => {
    return (
        <section id="how-it-works" className="py-24 relative overflow-hidden">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-[40%] left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent -z-0" />

            <div className="container mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tighter">
                        Simple as 1-2-3
                    </h2>
                </div>

                <div className="grid md:grid-cols-3 gap-12">
                    <Step
                        number="1"
                        title="Add Your Funds"
                        description="Input your mutual fund schemes and units. We support all major fund houses."
                    />
                    <Step
                        number="2"
                        title="Track Performance"
                        description="Visualise your portfolio's growth with interactive charts and real-time updates."
                    />
                    <Step
                        number="3"
                        title="Optimize & Grow"
                        description="Get insights on where to rebalance and how to maximize your returns."
                    />
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
