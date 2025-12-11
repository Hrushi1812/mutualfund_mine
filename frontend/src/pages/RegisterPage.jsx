import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, User, Mail, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { AuthContext } from '../context/AuthContext';

const RegisterPage = () => {
    const navigate = useNavigate();
    const { register } = useContext(AuthContext);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const result = await register(formData.username, formData.email, formData.password);

        setLoading(false);
        if (result.success) {
            navigate('/login');
        } else {
            setError(result.message);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-brand-accent/20 rounded-full blur-[128px]"></div>
                <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-brand-glow/10 rounded-full blur-[128px]"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-brand-card/50 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-white/10 w-full max-w-md relative z-10"
            >
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-text to-brand-muted">
                        Create Account
                    </h1>
                    <p className="text-brand-muted text-sm mt-2">Start tracking your portfolio today</p>
                </div>

                {error && <div className="mb-4 text-red-500 text-sm text-center bg-red-500/10 p-2 rounded">{error}</div>}

                <form onSubmit={handleRegister} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-brand-muted uppercase tracking-wider">Username</label>
                        <div className="relative group">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-muted group-focus-within:text-brand-glow transition-colors" />
                            <input
                                type="text"
                                required
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                className="w-full bg-brand-surface border border-white/5 rounded-lg py-3 pl-10 pr-4 text-brand-text focus:outline-none focus:border-brand-glow/50 focus:ring-1 focus:ring-brand-glow/50 transition-all placeholder:text-gray-600"
                                placeholder="Choose a username"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-brand-muted uppercase tracking-wider">Email</label>
                        <div className="relative group">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-muted group-focus-within:text-brand-glow transition-colors" />
                            <input
                                type="email"
                                required
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full bg-brand-surface border border-white/5 rounded-lg py-3 pl-10 pr-4 text-brand-text focus:outline-none focus:border-brand-glow/50 focus:ring-1 focus:ring-brand-glow/50 transition-all placeholder:text-gray-600"
                                placeholder="your@email.com"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-brand-muted uppercase tracking-wider">Password</label>
                        <div className="relative group">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-brand-muted group-focus-within:text-brand-glow transition-colors" />
                            <input
                                type="password"
                                required
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                className="w-full bg-brand-surface border border-white/5 rounded-lg py-3 pl-10 pr-4 text-brand-text focus:outline-none focus:border-brand-glow/50 focus:ring-1 focus:ring-brand-glow/50 transition-all placeholder:text-gray-600"
                                placeholder="Create a password"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-brand-accent to-brand-glow hover:opacity-90 text-white font-semibold py-3 px-4 rounded-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 group shadow-lg shadow-brand-accent/25 mt-6"
                    >
                        {loading ? (
                            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                        ) : (
                            <>
                                Register <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>

                    <div className="text-center mt-4">
                        <p className="text-brand-muted text-sm">
                            Already have an account?{' '}
                            <Link to="/login" className="text-brand-accent hover:text-brand-glow transition-colors">
                                Sign In
                            </Link>
                        </p>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default RegisterPage;
