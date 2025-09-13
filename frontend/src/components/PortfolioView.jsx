import React, { useEffect, useState } from "react";
import { getPortfolio, refreshPortfolio } from "../services/api";
import { Pie, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from "chart.js";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

export default function PortfolioView({ portfolioId }) {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchPortfolio = async () => {
    setLoading(true);
    try {
      const response = await getPortfolio(portfolioId);
      setPortfolio(response.data);
    } catch (error) {
      alert("Error fetching portfolio");
      console.error(error);
    }
    setLoading(false);
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const response = await refreshPortfolio(portfolioId);
      setPortfolio(response.data);
    } catch (error) {
      alert("Error refreshing portfolio");
      console.error(error);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (portfolioId) {
      fetchPortfolio();
    }
  }, [portfolioId]);

  if (loading) return <p>Loading...</p>;
  if (!portfolio) return <p>No portfolio found.</p>;

  // Prepare data for pie chart (top sectors)
  const sectorLabels = Object.keys(portfolio.top_sectors || {});
  const sectorValues = Object.values(portfolio.top_sectors || {});

  const pieData = {
    labels: sectorLabels,
    datasets: [
      {
        label: "% Allocation by Sector",
        data: sectorValues,
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
        hoverOffset: 4,
      },
    ],
  };

  // Prepare data for NAV trend line chart
  const navDates = portfolio.nav_history.map((h) =>
    new Date(h.date).toLocaleDateString()
  );
  const navValues = portfolio.nav_history.map((h) => h.nav);

  const lineData = {
    labels: navDates,
    datasets: [
      {
        label: "NAV Over Time",
        data: navValues,
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  return (
    <div>
      <h2>Portfolio Summary</h2>
      <p>
        Invested Amount: ₹{portfolio.invested_amount.toLocaleString()}
        <br />
        Current Value: ₹{portfolio.current_value?.toLocaleString() || "N/A"}
        <br />
        Profit/Loss: ₹{portfolio.profit_loss?.toLocaleString() || "N/A"} (
        {portfolio.profit_loss_percent?.toFixed(2) || "0"}%)
      </p>

      <button onClick={handleRefresh}>Refresh Prices & NAV</button>

      <h3>Holdings</h3>
      <table border="1" cellPadding="5" cellSpacing="0">
        <thead>
          <tr>
            <th>Instrument Name</th>
            <th>ISIN</th>
            <th>Industry</th>
            <th>Quantity</th>
            <th>Market Value (lakhs)</th>
            <th>% to NAV</th>
            <th>Current Price</th>
            <th>Price Change %</th>
          </tr>
        </thead>
        <tbody>
          {portfolio.holdings.map((h) => (
            <tr key={h.isin}>
              <td>{h.instrument_name}</td>
              <td>{h.isin}</td>
              <td>{h.industry}</td>
              <td>{h.quantity}</td>
              <td>{h.market_value_lakhs}</td>
              <td>{h.percentage_to_nav}</td>
              <td>{h.current_price?.toFixed(2) || "N/A"}</td>
              <td>{h.price_change_percent?.toFixed(2) || "N/A"}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Sector Allocation</h3>
      <Pie data={pieData} />

      <h3>NAV Trend</h3>
      <Line data={lineData} />
    </div>
  );
}