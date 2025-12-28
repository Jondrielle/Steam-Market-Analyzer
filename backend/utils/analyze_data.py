import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

prices_df = pd.read_csv("price_history.csv")

# Convert to numeric safely
prices_df["Final Price"] = pd.to_numeric(
    prices_df["Final Price"].str.replace("$","", regex=False), 
    errors="coerce"
)
prices_df["Original Price"] = pd.to_numeric(
    prices_df["Original Price"].str.replace("$","", regex=False), 
    errors="coerce"
)

# Fill NaN if needed
prices_df["Final Price"].fillna(0, inplace=True)
prices_df["Original Price"].fillna(prices_df["Final Price"], inplace=True)

# Convert Date
prices_df["Date"] = pd.to_datetime(prices_df["Date"])

# Select game data to extract
game_name = input("Select a game to extract its data\n").upper()

# Filter one game
game_data = prices_df[prices_df["Title"] == game_name]

# Define the month range
start_date = pd.to_datetime("2025-12-01")
end_date   = pd.to_datetime("2025-12-31")

# Filter the data
game_data = game_data[(game_data["Date"] >= start_date) & (game_data["Date"] <= end_date)]

if game_data.empty:
    print(f"{game_name} does not exist in the dataframe")
else:
    # --- Daily plot ---
    ax = game_data.plot(x="Date", y="Final Price", kind="line", marker='o', title=f"{game_name} Price History (Nov–Dec)")

    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)

    # Limit x-axis to your custom range
    plt.xlim(start_date, end_date)

    # Format x-axis nicely
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # every 3 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)

    plt.show()


    # --- Monthly aggregation ---
    game_data["Month"] = game_data["Date"].dt.to_period("M")
    monthly_data = game_data.groupby("Month")["Final Price"].mean().reset_index()

    # Convert Month to readable string and round prices
    monthly_data["Month"] = monthly_data["Month"].dt.to_timestamp()
    monthly_data["Month_str"] = monthly_data["Month"].dt.strftime("%Y-%m")
    monthly_data["Final Price"] = monthly_data["Final Price"].round(2)

    # Print clean table
    print("\nMonthly Average Price Table:")
    print(monthly_data[["Month_str", "Final Price"]].to_string(index=False))

    # --- Plot ---
    fig, ax = plt.subplots()
    ax.plot(monthly_data["Month"], monthly_data["Final Price"], marker='o', label="Avg Price")
    plt.title(f"{game_name} Monthly Avg Price")
    plt.ylabel("Average Price ($)")
    plt.xlabel("Month")
    plt.grid(True)

    # Set x-axis limits exactly to first and last month in your data
    start_month = monthly_data["Month"].min()
    end_month = monthly_data["Month"].max()
    ax.set_xlim(start_month, end_month)

    # Set ticks for each month in the data
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)

    plt.show()
