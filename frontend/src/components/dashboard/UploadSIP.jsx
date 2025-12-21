import React, { useState, useContext, useRef } from 'react';
import { Upload, Calendar, FileSpreadsheet, CheckCircle2, AlertCircle, IndianRupee, X, Loader2, RefreshCw, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../api';
import { PortfolioContext } from '../../context/PortfolioContext';

const UploadSIP = () => {
    const { fetchFunds } = useContext(PortfolioContext);
    const [file, setFile] = useState(null);
    const [fundName, setFundName] = useState('');
    const [nickname, setNickname] = useState('');
    const [sipAmount, setSipAmount] = useState('');
    const [startDate, setStartDate] = useState('');
    const [sipDay, setSipDay] = useState('');
    const [totalUnits, setTotalUnits] = useState('');
    const [totalInvestedAmount, setTotalInvestedAmount] = useState('');
    const fileInputRef = useRef(null);

    // Step-Up SIP State
    const [stepupEnabled, setStepupEnabled] = useState(false);
    const [stepupType, setStepupType] = useState('percentage');
    const [stepupValue, setStepupValue] = useState('');
    const [stepupFrequency, setStepupFrequency] = useState('Annual');

    // Ambiguity Handling
    const [showModal, setShowModal] = useState(false);
    const [candidates, setCandidates] = useState([]);
    const [pendingFundId, setPendingFundId] = useState(null);
    const [selectedScheme, setSelectedScheme] = useState(null);

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
        e.stopPropagation();
        setFile(null);
    }

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file || !fundName || !sipAmount || !startDate) {
            setMessage({ type: 'error', text: 'Please provide all mandatory fields: Fund Name, File, SIP Amount, and Start Date.' });
            return;
        }

        if (!sipDay || sipDay < 1 || sipDay > 31) {
            setMessage({ type: 'error', text: 'Please enter a valid SIP day (1-31).' });
            return;
        }
        if (!totalUnits || parseFloat(totalUnits) < 0) {
            setMessage({ type: 'error', text: 'Please enter your total units held (from CAS). Enter 0 if starting fresh.' });
            return;
        }
        if (!totalInvestedAmount || parseFloat(totalInvestedAmount) < 0) {
            setMessage({ type: 'error', text: 'Please enter total invested amount till now (from CAS). Enter 0 if starting fresh.' });
            return;
        }

        // Step-up validation
        if (stepupEnabled && (!stepupValue || parseFloat(stepupValue) <= 0)) {
            setMessage({ type: 'error', text: 'Please enter a valid step-up value.' });
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('fund_name', fundName);
        formData.append('file', file);
        formData.append('investment_type', 'sip');
        formData.append('invested_amount', sipAmount);
        formData.append('sip_amount', sipAmount);

        // Convert YYYY-MM-DD to DD-MM-YYYY
        const [year, month, day] = startDate.split('-');
        const formattedDate = `${day}-${month}-${year}`;
        formData.append('invested_date', formattedDate);

        formData.append('sip_day', sipDay);
        formData.append('total_units', totalUnits);
        formData.append('total_invested_amount', totalInvestedAmount);

        // Step-Up SIP fields
        formData.append('stepup_enabled', stepupEnabled ? 'true' : 'false');
        formData.append('stepup_type', stepupType);
        formData.append('stepup_value', stepupValue || '');
        formData.append('stepup_frequency', stepupFrequency);

        if (nickname) formData.append('nickname', nickname);

        try {
            const response = await api.post('/upload-holdings/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const data = response.data;

            if (data.upload_status && data.upload_status.requires_selection) {
                setPendingFundId(data.upload_status.id);
                setCandidates(data.upload_status.candidates || []);
                setShowModal(true);
                setMessage({ type: '', text: '' });
            } else {
                setMessage({ type: 'success', text: 'SIP registered successfully!' });
                fetchFunds();
                resetForm();
            }
        } catch (error) {
            console.error(error);
            let userMsg = 'Upload failed. Please check the file format.';

            if (error.response) {
                if (error.response.data && error.response.data.detail) {
                    const detail = error.response.data.detail;
                    userMsg = `Error: ${typeof detail === 'object' ? JSON.stringify(detail) : detail}`;
                }
            } else if (error.request) {
                userMsg = 'Cannot reach server. Please ensure the backend is running.';
            } else {
                userMsg = `Error: ${error.message}`;
            }

            setMessage({ type: 'error', text: userMsg });
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        setFundName('');
        setNickname('');
        setSipAmount('');
        setStartDate('');
        setSipDay('');
        setTotalUnits('');
        setTotalInvestedAmount('');
        // Reset step-up fields
        setStepupEnabled(false);
        setStepupType('percentage');
        setStepupValue('');
        setStepupFrequency('Annual');
        // Reset modal state
        setPendingFundId(null);
        setCandidates([]);
        setSelectedScheme(null);
        setShowModal(false);
    }

    const handleSchemeSelection = async (schemeCode) => {
        setSelectedScheme(schemeCode);
        setLoading(true);
        try {
            await api.patch(`/funds/${pendingFundId}/scheme`, { scheme_code: schemeCode });
            setMessage({ type: 'success', text: 'Scheme selected and SIP registered!' });
            fetchFunds();
            resetForm();
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to update scheme selection.' });
            setSelectedScheme(null);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="space-y-6">
            {/* SIP Info Banner */}
            <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <RefreshCw className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                        <h4 className="text-sm font-semibold text-white mb-1">SIP Tracking</h4>
                        <p className="text-xs text-zinc-400">
                            The app will track your SIP installments automatically. Mark each installment as paid or skipped when due.
                        </p>
                    </div>
                </div>
            </div>

            <form onSubmit={handleUpload} className="space-y-6">

                {/* Fund Name */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">SIP Fund Name <span className="text-red-500">*</span></label>
                    <input
                        type="text"
                        value={fundName}
                        onChange={(e) => setFundName(e.target.value)}
                        placeholder="e.g. Parag Parikh Flexi Cap Fund"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* Nickname (Optional) */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Nickname (Optional)</label>
                    <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        placeholder="e.g. Monthly SIP"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                    />
                </div>

                {/* Excel Upload Area */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Holdings File (Excel) <span className="text-red-500">*</span></label>
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
                            ref={fileInputRef}
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
                    <p className="text-xs text-zinc-500 mt-2">
                        Check monthly portfolio disclosures from your fund house (via email)
                    </p>
                </div>

                {/* SIP Amount & Start Date */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="relative">
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                            SIP Amount (Monthly) <span className="text-red-500">*</span>
                        </label>
                        <div className="relative">
                            <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="number"
                                value={sipAmount}
                                onChange={(e) => setSipAmount(e.target.value)}
                                placeholder="5000"
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                            SIP Start Date <span className="text-red-500">*</span>
                        </label>
                        <div className="relative">
                            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors [color-scheme:dark]"
                            />
                        </div>
                    </div>
                </div>

                {/* SIP Day & Total Units */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">SIP Date (Day of Month) <span className="text-red-500">*</span></label>
                        <input
                            type="number"
                            min="1"
                            max="31"
                            value={sipDay}
                            onChange={(e) => setSipDay(e.target.value)}
                            placeholder="e.g. 5"
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Total Units Held Till Date <span className="text-red-500">*</span></label>
                        <input
                            type="number"
                            value={totalUnits}
                            onChange={(e) => setTotalUnits(e.target.value)}
                            placeholder="Total accumulated units"
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                        />
                        <p className="text-[10px] text-zinc-500 mt-1">
                            From CAS (<a href="https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">CAMS</a>) or email. Enter 0 if starting fresh.
                        </p>
                    </div>
                </div>

                {/* Total Invested Amount */}
                <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Total Invested Amount Till Upload <span className="text-red-500">*</span></label>
                    <div className="relative">
                        <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input
                            type="number"
                            value={totalInvestedAmount}
                            onChange={(e) => setTotalInvestedAmount(e.target.value)}
                            placeholder="e.g. 500000"
                            className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-primary transition-colors"
                        />
                    </div>
                    <p className="text-[10px] text-zinc-500 mt-1">From CAS or email. App tracks new investments separately.</p>
                </div>

                {/* Step-Up SIP Configuration */}
                <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-4 space-y-4">
                    <label className="flex items-center gap-3 cursor-pointer">
                        <div className="relative">
                            <input
                                type="checkbox"
                                checked={stepupEnabled}
                                onChange={(e) => setStepupEnabled(e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-white/10 rounded-full peer peer-checked:bg-purple-500 transition-colors" />
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                        </div>
                        <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-medium text-white">Enable Step-Up SIP</span>
                        </div>
                    </label>

                    <AnimatePresence>
                        {stepupEnabled && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="space-y-4 overflow-hidden"
                            >
                                {/* Step-up Type */}
                                <div className="grid grid-cols-2 gap-2">
                                    <button
                                        type="button"
                                        onClick={() => setStepupType('percentage')}
                                        className={`py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${stepupType === 'percentage'
                                                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                                                : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                                            }`}
                                    >
                                        Percentage (%)
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setStepupType('amount')}
                                        className={`py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${stepupType === 'amount'
                                                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                                                : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                                            }`}
                                    >
                                        Fixed Amount (₹)
                                    </button>
                                </div>

                                {/* Step-up Value & Frequency */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                                            {stepupType === 'percentage' ? 'Increase by (%)' : 'Increase by (₹)'}
                                        </label>
                                        <div className="relative">
                                            {stepupType === 'amount' && (
                                                <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                                            )}
                                            <input
                                                type="number"
                                                value={stepupValue}
                                                onChange={(e) => setStepupValue(e.target.value)}
                                                placeholder={stepupType === 'percentage' ? '10' : '500'}
                                                className={`w-full bg-white/5 border border-white/10 rounded-xl ${stepupType === 'amount' ? 'pl-10' : 'pl-4'} pr-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-colors`}
                                            />
                                            {stepupType === 'percentage' && (
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500">%</span>
                                            )}
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">Frequency</label>
                                        <select
                                            value={stepupFrequency}
                                            onChange={(e) => setStepupFrequency(e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-purple-500 transition-colors appearance-none cursor-pointer"
                                        >
                                            <option value="Annual" className="bg-zinc-900">Annual</option>
                                            <option value="Half-Yearly" className="bg-zinc-900">Half-Yearly</option>
                                            <option value="Quarterly" className="bg-zinc-900">Quarterly</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Preview */}
                                {sipAmount && stepupValue && (
                                    <div className="bg-black/20 rounded-lg p-3 border border-white/5">
                                        <p className="text-xs text-zinc-400 mb-1">💡 Preview (Next 3 periods)</p>
                                        <p className="text-sm text-white font-mono">
                                            {(() => {
                                                const base = parseFloat(sipAmount) || 0;
                                                const val = parseFloat(stepupValue) || 0;
                                                const calc = (period) => {
                                                    if (stepupType === 'percentage') {
                                                        return Math.round(base * Math.pow(1 + val / 100, period));
                                                    }
                                                    return Math.round(base + val * period);
                                                };
                                                return `₹${base.toLocaleString()} → ₹${calc(1).toLocaleString()} → ₹${calc(2).toLocaleString()}`;
                                            })()}
                                        </p>
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Submit Action */}
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-purple-500/25 flex items-center justify-center gap-2 group"
                >
                    {loading ? (
                        <span className="animate-pulse">Processing...</span>
                    ) : (
                        <>Register SIP <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" /></>
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

            {/* AMBIGUITY MODAL */}
            <AnimatePresence>
                {showModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-zinc-900 border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl"
                        >
                            <h3 className="text-xl font-bold text-white mb-2">Select Fund Scheme</h3>
                            <p className="text-sm text-zinc-400 mb-4">We found multiple matching schemes. Please select the correct one:</p>

                            <div className="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                                {candidates.map((c) => {
                                    const isSelected = selectedScheme === c.schemeCode;
                                    const isBusy = loading && isSelected;

                                    return (
                                        <button
                                            key={c.schemeCode}
                                            onClick={() => handleSchemeSelection(c.schemeCode)}
                                            disabled={loading}
                                            className={`
                                                w-full text-left p-3 rounded-lg border transition-all text-sm group
                                                ${isSelected
                                                    ? 'bg-primary/20 border-primary text-white shadow-[0_0_15px_rgba(var(--primary),0.3)]'
                                                    : 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-primary/50 text-zinc-300 hover:text-white'
                                                }
                                                ${loading && !isSelected ? 'opacity-40 cursor-not-allowed' : ''}
                                            `}
                                        >
                                            <div className="flex justify-between items-center">
                                                <div className="flex items-center gap-2">
                                                    {isBusy && <Loader2 className="w-3 h-3 animate-spin text-primary" />}
                                                    <span className={`font-medium ${isSelected ? 'text-primary-foreground' : ''}`}>
                                                        {c.schemeName}
                                                        {isBusy && <span className="ml-2 text-xs text-primary font-normal">Uploading...</span>}
                                                    </span>
                                                </div>
                                                <span className={`text-xs px-2 py-1 rounded ml-2 ${isSelected ? 'bg-primary/30 text-white' : 'bg-black/20 text-zinc-500'}`}>
                                                    {c.schemeCode}
                                                </span>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>

                            <button
                                onClick={resetForm}
                                className="mt-4 w-full py-2 bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white rounded-lg transition-colors text-sm"
                            >
                                Cancel Upload
                            </button>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default UploadSIP;
