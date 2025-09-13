import React, { useState } from "react";
import UploadForm from "../components/UploadForm";
import PortfolioView from "../components/PortfolioView";

export default function Dashboard() {
  const [portfolioId, setPortfolioId] = useState(null);

  return (
    <div>
      <h1>Dashboard</h1>
      {!portfolioId ? (
        <UploadForm onPortfolioCreated={setPortfolioId} />
      ) : (
        <PortfolioView portfolioId={portfolioId} />
      )}
    </div>
  );
}