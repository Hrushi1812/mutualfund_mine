import React, { useState } from 'react';
import FundList from './components/FundList';
import UploadHoldings from './components/UploadHoldings';
import NavEstimator from './components/NavEstimator';

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    // Refresh the fund list after successful upload
    setRefreshKey(oldKey => oldKey + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-blue-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Mutual Fund NAV Estimator
          </h1>
          <p className="mt-5 max-w-xl mx-auto text-xl text-gray-500">
            Upload holdings portfolio and estimate daily NAV changes based on real-time stock data.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column: Upload & List */}
          <div className="space-y-8">
            <UploadHoldings onUploadSuccess={handleUploadSuccess} />
            <FundList key={refreshKey} />
          </div>

          {/* Right Column: Estimator */}
          <div>
            <NavEstimator />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
