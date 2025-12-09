import React from "react";
import Navbar from "../layout/Navbar";
import Footer from "../layout/Footer";
import Hero from "./Hero";
import Features from "./Features";
import HowItWorks from "./HowItWorks";
import DemoSection from "./DemoSection";
import CTA from "./CTA";

const LandingPage = () => {
    return (
        <div className="bg-background text-foreground min-h-screen selection:bg-primary selection:text-white">
            <Navbar />
            <main>
                <Hero />
                <Features />
                <HowItWorks />
                <DemoSection />
                <CTA />
            </main>
            <Footer />
        </div>
    );
};

export default LandingPage;
