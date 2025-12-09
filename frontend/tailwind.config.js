/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    dark: '#f8fafc',      // Slate-50 (Soft Off-White Background)
                    card: '#ffffff',      // Pure White Cards
                    surface: '#f1f5f9',   // Slate-100 (Inputs/Secondary)
                    accent: '#4f46e5',    // Indigo-600 (Vibrant, professional)
                    glow: '#818cf8',      // Indigo-400
                    text: '#0f172a',      // Slate-900 (High contrast dark text)
                    muted: '#64748b',     // Slate-500
                    success: '#059669',   // Emerald-600
                    error: '#dc2626',     // Red-600
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
