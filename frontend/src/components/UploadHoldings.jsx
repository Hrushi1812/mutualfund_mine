import React, { useState } from 'react';
import { Upload, Calendar, DollarSign, FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';

const UploadHoldings = ({ onUploadSuccess }) => {
    const [mode, setMode] = useState('lumpsum'); // 'lumpsum' | 'sip'
    const [file, setFile] = useState(null);
    const [fundName, setFundName] = useState('');
    const [investedAmount, setInvestedAmount] = useState('');
    const [investedDate, setInvestedDate] = useState('');

    const [drapOver, setDragOver] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleFileDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) setFile(droppedFile);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file || !fundName) {
            setMessage({ type: 'error', text: 'Please provide Fund Name and Excel File' });
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('fund_name', fundName);
        formData.append('file', file);
        // Note: Backend might not accept these yet, but sending for completeness or future use
        formData.append('investment_type', mode);
        formData.append('invested_amount', investedAmount);
        formData.append('invested_date', investedDate);

        try {
            await api.post('/upload-holdings/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setMessage({ type: 'success', text: 'Portfolio uploaded successfully!' });
            if (onUploadSuccess) onUploadSuccess();
            // Reset form
            setFile(null);
            setFundName('');
            setInvestedAmount('');
            setInvestedDate('');
        } catch (error) {
            console.error(error);
            setMessage({ type: 'error', text: 'Upload failed. Please check the file format.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-brand-card border border-white/5 rounded-2xl p-6 shadow-xl relative overflow-hidden"
        >
            {/* Glow Effect */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-glow/5 rounded-full blur-[80px] -z-10"></div>

            <h2 className="text-xl font-bold text-brand-text mb-6 flex items-center gap-2">
                <Upload className="w-5 h-5 text-brand-accent" />
                Upload Holdings
            </h2>

            <form onSubmit={handleUpload} className="space-y-6">

                {/* 1. Fund Name */}
                <div>
                    <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Portfolio / Fund Name</label>
                    <input
                        type="text"
                        value={fundName}
                        onChange={(e) => setFundName(e.target.value)}
                        placeholder="e.g. My Bluechip Portfolio"
                        className="w-full bg-brand-surface border border-white/10 rounded-lg px-4 py-3 text-brand-text placeholder-brand-muted/50 focus:outline-none focus:border-brand-accent transition-colors"
                    />
                </div>

                {/* 2. Excel Upload Area */}
                <div>
                    <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Holdings File (Excel)</label>
                    <div
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleFileDrop}
                        className={`
                            border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer relative group
                            ${drapOver ? 'border-brand-accent bg-brand-accent/10' : 'border-white/10 hover:border-brand-muted hover:bg-white/5'}
                        `}
                    >
                        <input
                            type="file"
                            accept=".xlsx, .xls"
                            onChange={(e) => setFile(e.target.files[0])}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />

                        <div className="flex flex-col items-center gap-3">
                            <div className="p-3 bg-brand-surface rounded-full group-hover:bg-brand-accent/20 transition-colors">
                                <FileSpreadsheet className={`w-6 h-6 ${file ? 'text-brand-success' : 'text-brand-muted group-hover:text-brand-text'}`} />
                            </div>
                            {file ? (
                                <div>
                                    <p className="text-sm font-medium text-brand-text">{file.name}</p>
                                    <p className="text-xs text-brand-success">Ready to upload</p>
                                </div>
                            ) : (
                                <div>
                                    <p className="text-sm font-medium text-brand-text">Drop Excel file or click to browse</p>
                                    <p className="text-xs text-brand-muted mt-1">Supports .xlsx, .xls</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* 3. Mode Selection (Radio) */}
                <div>
                    <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-3">Investment Mode</label>
                    <div className="flex bg-brand-surface p-1 rounded-lg w-max border border-white/5">
                        <button
                            type="button"
                            onClick={() => setMode('lumpsum')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${mode === 'lumpsum' ? 'bg-brand-accent text-white shadow-lg' : 'text-brand-muted hover:text-brand-text'}`}
                        >
                            Lumpsum
                        </button>
                        <button
                            type="button"
                            onClick={() => setMode('sip')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${mode === 'sip' ? 'bg-brand-accent text-white shadow-lg' : 'text-brand-muted hover:text-brand-text'}`}
                        >
                            SIP
                        </button>
                    </div>
                </div>

                {/* 4. Details Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="relative">
                        <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Invested Amount</label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-muted" />
                            <input
                                type="number"
                                value={investedAmount}
                                onChange={(e) => setInvestedAmount(e.target.value)}
                                placeholder="0.00"
                                className="w-full bg-brand-surface border border-white/10 rounded-lg pl-9 pr-4 py-3 text-brand-text placeholder-brand-muted/50 focus:outline-none focus:border-brand-accent transition-colors"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase tracking-wider mb-2">Invested Date</label>
                        <div className="relative">
                            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-muted" />
                            <input
                                type="date"
                                value={investedDate}
                                onChange={(e) => setInvestedDate(e.target.value)}
                                className="w-full bg-brand-surface border border-white/10 rounded-lg pl-9 pr-4 py-3 text-brand-text placeholder-brand-muted/50 focus:outline-none focus:border-brand-accent transition-colors [color-scheme:dark]"
                            />
                        </div>
                    </div>
                </div>

                {/* Submit Action */}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-brand-accent to-brand-glow hover:opacity-90 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <span className="animate-pulse">Processing Portfolio...</span>
                    ) : (
                        <>Analyze Portfolio <Upload className="w-4 h-4" /></>
                    )}
                </button>

                {/* Messages */}
                <AnimatePresence>
                    {message.text && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className={`p-3 rounded-lg flex items-center gap-2 text-sm ${message.type === 'error' ? 'bg-brand-error/10 text-brand-error' : 'bg-brand-success/10 text-brand-success'}`}
                        >
                            {message.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                            {message.text}
                        </motion.div>
                    )}
                </AnimatePresence>

            </form>
        </motion.div>
    );
};

export default UploadHoldings;
