import React from "react";

const GlassCard = ({ children, className = "", hoverEffect = true }) => {
    return (
        <div
            className={`glass p-6 rounded-2xl transition-all duration-300 ${hoverEffect ? "glass-hover hover:-translate-y-1 hover:shadow-2xl" : ""
                } ${className}`}
        >
            {children}
        </div>
    );
};

export default GlassCard;
