import React from "react";
import { useNavigate } from "react-router-dom";
import Button from "../ui/Button";

const CTA = () => {
    const navigate = useNavigate();

    return (
        <section className="py-20 md:py-32 relative overflow-hidden">
            {/* Background glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[120px] -z-10" />

            <div className="container mx-auto px-6 text-center">
                <h2 className="text-3xl md:text-6xl font-bold tracking-tighter mb-8 max-w-3xl mx-auto">
                    Ready to take control of your future?
                </h2>
                <p className="text-xl text-white/50 mb-10 max-w-2xl mx-auto">
                    Join thousands of investors who are tracking their funds smarter, faster, and better.
                </p>
                <div className="flex flex-col sm:flex-row justify-center gap-4">
                    <Button className="px-10 py-4 text-lg" onClick={() => navigate('/login')}>Start Tracking Now</Button>
                </div>
            </div>
        </section>
    );
};

export default CTA;
