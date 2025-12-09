import React from "react";

const Button = ({ children, variant = "primary", className = "", ...props }) => {
    const baseStyles = "px-6 py-3 rounded-full font-medium transition-all duration-300 transform active:scale-95";

    const variants = {
        primary: "bg-primary text-white hover:bg-blue-600 shadow-[0_0_20px_rgba(59,130,246,0.5)] hover:shadow-[0_0_30px_rgba(59,130,246,0.7)]",
        secondary: "bg-white/10 text-white hover:bg-white/20 backdrop-blur-md border border-white/10",
        outline: "border border-white/20 text-white hover:bg-white/10",
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;
