import React from "react";

const Footer = () => {
    return (
        <footer className="py-12 border-t border-white/5 relative z-10 glass">
            <div className="container mx-auto px-6 text-center">
                <h3 className="text-xl font-bold tracking-tighter mb-4 text-white">
                    Mutual Fund Tracker<span className="text-primary">.</span>
                </h3>
                <p className="text-white/40 text-sm mb-8 max-w-md mx-auto">
                    A simple, modern way to track your mutual fund performance with elegance and precision.
                </p>

                <p className="text-xs text-white/20">
                    &copy; {new Date().getFullYear()} Mutual Fund Tracker. All rights reserved.
                </p>
            </div>
        </footer>
    );
};

export default Footer;
