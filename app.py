import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
import time
import random

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_fund_details():
    """
    Ask the user for:
    - Yesterday's NAV of the MUTUAL FUND (not stock price)
    - Investment amount
    Then compute units = investment / previous NAV.
    """
    try:
        print("Enter yesterday's NAV of the MUTUAL FUND (not stock price).")
        prev_nav = float(input("Yesterday's NAV: ").strip())
        investment_amount = float(input("Enter your investment amount: ").strip())
        units = investment_amount / prev_nav

        logger.info(f"Previous NAV (MF): ₹{prev_nav:.2f}")
        logger.info(f"Investment amount: ₹{investment_amount:.2f}")
        logger.info(f"Number of units: {units:.4f}")
        return prev_nav, investment_amount, units

    except Exception as e:
        logger.error(f"Error reading NAV/investment inputs: {str(e)}")
        raise


def calculate_pnl(df, prev_nav, investment_amount, units):
    """Calculate P&L and generate report"""
    # Total weighted return (approx NAV % move)
    estimated_return = df["Weighted Return"].sum()
    df_sorted = df.sort_values("Weighted Return", ascending=False)

    # Calculate NAV and P&L
    estimated_nav = prev_nav * (1 + estimated_return / 100.0)
    current_value = units * estimated_nav
    absolute_pnl = current_value - investment_amount
    percentage_pnl = (absolute_pnl / investment_amount) * 100.0

    # Print detailed report
    print("\n=== Fund Performance Estimation ===")
    print(f"Time of Estimation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nPrevious NAV: ₹{prev_nav:.2f}")
    print(f"Estimated Current NAV: ₹{estimated_nav:.2f}")
    print(f"NAV Change: {estimated_return:.2f}%")
    print("\n=== Your Investment ===")
    print(f"Investment Amount: ₹{investment_amount:.2f}")
    print(f"Units Held: {units:.4f}")
    print(f"Estimated Current Value: ₹{current_value:.2f}")
    print(f"Estimated P&L: ₹{absolute_pnl:.2f} ({percentage_pnl:+.2f}%)")

    # Print top contributors
    print("\n=== Top Contributors to P&L ===")
    print(df_sorted[["Name of the Instrument", "Daily Change (%)", "Weighted Return"]].head())

    return estimated_nav, absolute_pnl, percentage_pnl


def main():
    try:
        # --- Step 1: Read Excel file ---
        file_path = "nav4.xlsx"
        df = pd.read_excel(file_path)
        logger.info("Available columns in Excel file:")
        logger.info(df.columns.tolist())

        # --- Step 2: Keep only required columns (INCLUDING Symbol) ---
        df = df[["Name of the Instrument", "% to NAV", "Symbol"]]

        # Clean data
        df["Name of the Instrument"] = df["Name of the Instrument"].astype(str).str.strip()
        df["Symbol"] = df["Symbol"].astype(str).str.strip()
        df["% to NAV"] = pd.to_numeric(df["% to NAV"], errors="coerce")

        # Drop rows where any of the important fields are missing
        df = df.dropna(subset=["Name of the Instrument", "% to NAV", "Symbol"]).reset_index(drop=True)

        if df.empty:
            logger.error("No valid rows left after cleaning. Check Excel data.")
            return

        coverage = df["% to NAV"].sum()
        logger.info(f"Total % to NAV covered by symbols in Excel: {coverage:.2f}%")

        # --- Step 3: Get MF NAV + investment from user ---
        prev_nav, investment_amount, units = get_fund_details()

        # --- Step 4: Fetch stock price changes from Yahoo ---
        df["Daily Change (%)"] = 0.0

        for idx, row in df.iterrows():
            sym = row["Symbol"]
            try:
                logger.info(f"\nProcessing {sym}")
                data = yf.download(sym, period="5d", interval="1d", progress=False)

                if len(data) >= 2:
                    closes = data["Close"].dropna()
                    if len(closes) >= 2:
                        prev_close = float(closes.iloc[-2])
                        last_close = float(closes.iloc[-1])
                        pct_change = ((last_close - prev_close) / prev_close) * 100.0
                        df.loc[idx, "Daily Change (%)"] = pct_change
                        logger.info(f"{sym} change: {pct_change:.2f}%")
                    else:
                        logger.warning(f"Not enough valid closing prices for {sym}")
                else:
                    logger.warning(f"Not enough data points for {sym}")

            except Exception as e:
                logger.error(f"Error processing {sym}: {str(e)}")

            # Sleep a bit to avoid hammering Yahoo (rate limiting)
            time.sleep(0.4 + random.uniform(0, 0.4))

        # --- Step 5: Compute weighted return ---
        df["Weighted Return"] = (df["% to NAV"] * df["Daily Change (%)"]) / 100.0

        # --- Step 6: Generate report ---
        estimated_nav, absolute_pnl, percentage_pnl = calculate_pnl(
            df, prev_nav, investment_amount, units
        )

        # --- Step 7: Export results to Excel ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fund_estimation_{timestamp}.xlsx"

        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name="Details", index=False)

            summary_data = {
                "Metric": ["Previous NAV", "Estimated NAV", "P&L Amount", "P&L Percentage"],
                "Value": [
                    f"₹{prev_nav:.2f}",
                    f"₹{estimated_nav:.2f}",
                    f"₹{absolute_pnl:.2f}",
                    f"{percentage_pnl:+.2f}%",
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        logger.info(f"\nDetailed report saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")


if __name__ == "__main__":
    main()
