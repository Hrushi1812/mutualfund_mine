import React, { useState } from 'react';
import api from '../api';

const UploadHoldings = ({ onUploadSuccess }) => {
    const [fundName, setFundName] = useState('');
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!fundName || !file) {
            setMessage('Please provide both fund name and file.');
            return;
        }

        const formData = new FormData();
        formData.append('fund_name', fundName);
        formData.append('file', file);

        setLoading(true);
        setMessage('');

        try {
            const response = await api.post('/upload-holdings/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(response.data.message || 'Upload successful!');
            if (onUploadSuccess) onUploadSuccess();
            setFundName('');
            setFile(null);
        } catch (error) {
            console.error("Upload error:", error);
            setMessage('Error uploading file. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Upload Holdings</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Fund Name</label>
                    <input
                        type="text"
                        value={fundName}
                        onChange={(e) => setFundName(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
                        placeholder="e.g., Bluechip Fund"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Holdings Excel File</label>
                    <input
                        type="file"
                        onChange={handleFileChange}
                        accept=".xlsx, .xls"
                        className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                    />
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    {loading ? 'Uploading...' : 'Upload'}
                </button>
                {message && (
                    <p className={`text-sm mt-2 ${message.includes('Error') ? 'text-red-600' : 'text-green-600'}`}>
                        {message}
                    </p>
                )}
            </form>
        </div>
    );
};

export default UploadHoldings;
