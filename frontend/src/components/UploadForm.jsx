import React, { useState } from "react";
import { uploadAMCFile, createPortfolio } from "../services/api";

export default function UploadForm({ onPortfolioCreated }) {
  const [file, setFile] = useState(null);
  const [investedAmount, setInvestedAmount] = useState("");
  const [investmentDate, setInvestmentDate] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !investedAmount || !investmentDate) {
      alert("Please fill all fields");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    try {
      const holdingsResponse = await uploadAMCFile(formData);
      const holdings = holdingsResponse.data;

      const portfolioData = {
        invested_amount: parseFloat(investedAmount),
        investment_date: investmentDate,
        holdings,
      };

      const portfolioResponse = await createPortfolio(portfolioData);
      onPortfolioCreated(portfolioResponse.data.portfolio_id);
    } catch (error) {
      alert("Error uploading file or creating portfolio");
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <input
        type="number"
        placeholder="Total Invested Amount"
        value={investedAmount}
        onChange={(e) => setInvestedAmount(e.target.value)}
      />
      <input
        type="date"
        value={investmentDate}
        onChange={(e) => setInvestmentDate(e.target.value)}
      />
      <button type="submit">Upload & Create Portfolio</button>
    </form>
  );
}