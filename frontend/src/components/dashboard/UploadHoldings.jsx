import React, { useState } from 'react';
import { Upload, Calendar, FileSpreadsheet, CheckCircle2, AlertCircle, IndianRupee, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../api';

const UploadHoldings = ({ onUploadSuccess }) => {
    const [mode, setMode] = useState('lumpsum'); // 'lumpsum' | 'sip'
    const [file, setFile] = useState(null);
    const [fundName, setFundName] = useState('');
    const [investedAmount, setInvestedAmount] = useState('');
    const [investedDate, setInvestedDate] = useState('');

    const [dragOver, setDragOver] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleFileDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) setFile(droppedFile);
    };

    const handleRemoveFile = (e) => {
        e.stopPropagation(); // Prevent opening file dialog
        setFile(null);
    }

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
        formData.append('investment_type', mode);
        formData.append('fund_name', fundName);
        formData.append('file', file);
        formData.append('investment_type', mode);

        if (investedAmount) formData.append('invested_amount', investedAmount);
        if (investedDate) formData.append('invested_date', investedDate);

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
            let userMsg = 'Upload failed. Please check the file format.';

            if (error.response) {
                // Server responded with an error code
                if (error.response.data && error.response.data.detail) {
                    // FastAPI default error structure
                    userMsg = `Error: ${JSON.stringify(error.response.data.detail)}`;
                }
            } else if (error.request) {
                // Request made but no response (Network Error)
                userMsg = 'Cannot reach server. Please ensure the backend is running.';
            } else {
                userMsg = `Error: ${error.message}`;
            }

            setMessage({ type: 'error', text: userMsg });
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass p-8 rounded-3xl relative overflow-hidden"
        >
            {/* Glow Effect */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] -z-10"></div>

            <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-2">
                <div className="p-2 rounded-lg bg-primary/20 text-primary">
                    <Upload className="w-5 h-5" />
                </div>
                Upload Portfolio
            </h2>

            <form onSubmit={handleUpload} className="space-y-6">

                {/* 1. Fund Name */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Portfolio / Fund Name</label>
                    <input
                        type="text"
                        value={fundName}
                        onChange={(e) => setFundName(e.target.value)}
                        placeholder="e.g. My Bluechip Portfolio"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* 2. Excel Upload Area */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Holdings File (Excel)</label>
                    <div
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleFileDrop}
                        className={`
                            border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer relative group
                            ${dragOver ? 'border-primary bg-primary/10' : 'border-white/10 hover:border-zinc-500 hover:bg-white/5'}
                        `}
                    >
                        <input
                            type="file"
                            accept=".xlsx, .xls"
                            onChange={(e) => setFile(e.target.files[0])}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />

                        <div className="flex flex-col items-center gap-3">
                            <div className="p-3 bg-white/5 rounded-full group-hover:bg-primary/20 transition-colors">
                                <FileSpreadsheet className={`w-8 h-8 ${file ? 'text-green-500' : 'text-zinc-500 group-hover:text-white'}`} />
                            </div>
                            {file ? (
                                <div className="relative">
                                    <p className="text-sm font-medium text-white">{file.name}</p>
                                    <p className="text-xs text-green-400 mb-1">Ready to upload</p>
                                    <button
                                        type="button"
                                        onClick={handleRemoveFile}
                                        className="relative z-10 px-3 py-1 bg-white/10 hover:bg-red-500/20 text-zinc-300 hover:text-red-400 text-xs rounded-full border border-white/10 transition-colors flex items-center gap-1 mx-auto"
                                    >
                                        <X className="w-3 h-3" /> Remove
                                    </button>
                                </div>
                            ) : (
                                <div>
                                    <p className="text-sm font-medium text-white">Drop Excel file or click to browse</p>
                                    <p className="text-xs text-zinc-500 mt-1">Supports .xlsx, .xls</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* 3. Mode Selection (Radio) */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-3">Investment Mode</label>
                    <div className="flex bg-white/5 p-1 rounded-xl w-max border border-white/10">
                        <button
                            type="button"
                            onClick={() => setMode('lumpsum')}
                            className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'lumpsum' ? 'bg-primary text-white shadow-lg' : 'text-zinc-400 hover:text-white'}`}
                        >
                            Lumpsum
                        </button>
                        <button
                            type="button"
                            onClick={() => {
                                // setMode('sip'); 
                                setMessage({ type: 'info', text: 'SIP Mode Coming Soon!' });
                                setTimeout(() => setMessage({ type: '', text: '' }), 3000);
                            }}
                            className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'sip' ? 'bg-primary text-white shadow-lg' : 'text-zinc-400 hover:text-white cursor-not-allowed opacity-70'}`}
                        >
                            SIP
                        </button>
                    </div>
                </div>

                {/* 4. Details Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="relative">
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Invested Amount</label>
                        <div className="relative">
                            <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="number"
                                value={investedAmount}
                                onChange={(e) => setInvestedAmount(e.target.value)}
                                placeholder="0.00"
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Invested Date</label>
                        <div className="relative">
                            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="date"
                                value={investedDate}
                                onChange={(e) => setInvestedDate(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors [color-scheme:dark]"
                            />
                        </div>
                    </div>
                </div>

                {/* Submit Action */}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-primary hover:bg-blue-600 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-primary/25 flex items-center justify-center gap-2 group"
                >
                    {loading ? (
                        <span className="animate-pulse">Processing Portfolio...</span>
                    ) : (
                        <>Upload Portfolio <Upload className="w-4 h-4 group-hover:-translate-y-1 transition-transform" /></>
                    )}
                </button>

                {/* Messages */}
                <AnimatePresence>
                    {message.text && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className={`p-4 rounded-xl flex items-center gap-2 text-sm ${message.type === 'error' ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'bg-green-500/10 text-green-500 border border-green-500/20'}`}
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
