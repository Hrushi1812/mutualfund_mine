/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#09090b", // zinc-950
                foreground: "#fafafa", // zinc-50
                primary: "#3b82f6", // blue-500
                secondary: "#a1a1aa", // zinc-400
                accent: "#6366f1", // indigo-500
                card: "rgba(255, 255, 255, 0.05)",
                "card-hover": "rgba(255, 255, 255, 0.1)",
            },
            fontFamily: {
                sans: ["Inter", "sans-serif"],
            },
            animation: {
                "float": "float 6s ease-in-out infinite",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translateY(0)" },
                    "50%": { transform: "translateY(-20px)" },
                },
            },
        },
    },
    plugins: [],
}
