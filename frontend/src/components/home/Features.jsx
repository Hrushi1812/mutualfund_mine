import React from "react";
import GlassCard from "../ui/GlassCard";
import { TrendingUp, PieChart, Clock, Shield, Zap } from "lucide-react";

const FeatureItem = ({ icon: Icon, title, description, badge }) => (
    <GlassCard className="flex flex-col items-start gap-4 relative">
        {badge && (
            <span className="absolute top-4 right-4 text-[10px] font-medium px-2 py-0.5 bg-primary/20 text-primary rounded-full">
                {badge}
            </span>
        )}
        <div className="p-3 rounded-xl bg-primary/10 text-primary">
            <Icon size={24} />
        </div>
        <h3 className="text-xl font-semibold text-white">{title}</h3>
        <p className="text-white/60 text-sm leading-relaxed">{description}</p>
    </GlassCard>
);

const Features = () => {
    const features = [
        {
            icon: TrendingUp,
            title: "Real-time NAV Tracking",
            description: "Stay updated with the latest Net Asset Values of your mutual funds instantly.",
        },
        {
            icon: Zap,
            title: "Live Stock Prices",
            description: "Optionally connect Fyers (free) for real-time stock prices, or use delayed data - your choice. App works either way!",
            badge: "Optional",
        },
        {
            icon: PieChart,
            title: "Portfolio Analysis",
            description: "Deep dive into your portfolio allocation and performance metrics.",
        },
        {
            icon: Clock,
            title: "Historical Data",
            description: "Analyze past performance trends to make informed investment decisions.",
        },
        {
            icon: Shield,
            title: "Secure & Private",
            description: "Your financial data is encrypted and stored locally for maximum privacy.",
        },
    ];

    return (
        <section id="features" className="py-16 md:py-24 relative">
            <div className="container mx-auto px-6">
                <div className="text-center max-w-2xl mx-auto mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tighter">
                        Everything you need to grow
                    </h2>
                    <p className="text-white/60">
                        Powerful tools packaged in a simple, intuitive interface designed for modern investors.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                    {features.map((feature, index) => (
                        <FeatureItem key={index} {...feature} />
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
