import React, { useState, useEffect, useContext } from "react";
import { Menu, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";

const Navbar = () => {
    const [scrolled, setScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);
    const navigate = useNavigate();
    const { isAuthenticated, logout } = useContext(AuthContext);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navLinks = [
        { name: "Features", href: "#features" },
        { name: "How it Works", href: "#how-it-works" },
        { name: "Demo", href: "#demo" },
    ];

    const handleGetStarted = () => {
        navigate('/login');
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "glass py-4" : "bg-transparent py-6"
                }`}
        >
            <div className="container mx-auto px-6 flex justify-between items-center">
                <a href="#" className="text-2xl font-bold tracking-tighter text-white">
                    Mutual Fund Tracker<span className="text-primary">.</span>
                </a>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center space-x-8">
                    {navLinks.map((link) => (
                        <a
                            key={link.name}
                            href={link.href}
                            className="text-white/70 hover:text-white transition-colors text-sm font-medium"
                        >
                            {link.name}
                        </a>
                    ))}
                    {isAuthenticated ? (
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="bg-white/10 text-white px-5 py-2 rounded-full font-medium hover:bg-white/20 transition-colors text-sm"
                            >
                                Dashboard
                            </button>
                            <button
                                onClick={handleLogout}
                                className="bg-red-500/80 text-white px-5 py-2 rounded-full font-medium hover:bg-red-600/80 transition-colors text-sm"
                            >
                                Logout
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={handleGetStarted}
                            className="bg-white text-black px-5 py-2 rounded-full font-medium hover:bg-gray-100 transition-colors text-sm"
                        >
                            Get Started
                        </button>
                    )}
                </div>

                {/* Mobile Toggle */}
                <button
                    className="md:hidden text-white"
                    onClick={() => setMobileOpen(!mobileOpen)}
                >
                    {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Nav */}
            {mobileOpen && (
                <div className="md:hidden absolute top-full left-0 w-full glass bg-black/90 border-t border-white/10 p-6 flex flex-col space-y-4 shadow-2xl h-screen">
                    {navLinks.map((link) => (
                        <a
                            key={link.name}
                            href={link.href}
                            className="text-white/80 hover:text-white text-xl font-medium py-2 border-b border-white/5"
                            onClick={() => setMobileOpen(false)}
                        >
                            {link.name}
                        </a>
                    ))}
                    <button
                        onClick={() => { setMobileOpen(false); handleGetStarted(); }}
                        className="bg-primary text-white py-4 rounded-xl font-bold text-lg w-full mt-4 shadow-lg shadow-primary/25"
                    >
                        Get Started
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
