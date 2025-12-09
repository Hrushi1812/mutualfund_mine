import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { useNavigate } from "react-router-dom";
import ThreeDElement from "./ThreeDElement";
import Button from "../ui/Button";

const Hero = () => {
    const navigate = useNavigate();

    return (
        <section className="relative h-screen flex items-center justify-center overflow-hidden">
            {/* Background Gradients */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl -z-10 animate-float" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl -z-10 animate-float" style={{ animationDelay: "2s" }} />

            <div className="container mx-auto px-6 grid md:grid-cols-2 gap-12 items-center relative z-10">
                <div className="text-left space-y-6">
                    <div className="inline-block px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-blue-300">
                        ✨ Smart Portfolio Tracking
                    </div>
                    <h1 className="text-4xl md:text-7xl font-bold leading-tight tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        Master Your Mutual Funds
                    </h1>
                    <p className="text-base md:text-lg text-white/60 max-w-lg leading-relaxed">
                        Track, analyze, and optimize your investments with a beautiful, modern dashboard designed for clarity and growth.
                    </p>
                    <div className="flex flex-wrap gap-4 pt-4">
                        <Button variant="primary" onClick={() => navigate('/login')}>Start Tracking</Button>
                        <Button variant="secondary" onClick={() => document.getElementById("demo")?.scrollIntoView({ behavior: 'smooth' })}>View Demo</Button>
                    </div>
                </div>

                <div className="h-[300px] md:h-[600px] w-full relative">
                    <Canvas className="w-full h-full" camera={{ position: [0, 0, 5] }}>
                        {/* <ambientLight intensity={0.5} /> */}
                        {/* <directionalLight position={[10, 10, 5]} intensity={1} /> */}
                        <Environment preset="city" />
                        <ThreeDElement />
                        {/* <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} /> */}
                    </Canvas>
                </div>
            </div>

            {/* Scroll Indicator */}
            <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce opacity-50">
                <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center pt-2">
                    <div className="w-1 h-3 bg-white/50 rounded-full" />
                </div>
            </div>
        </section>
    );
};

export default Hero;
