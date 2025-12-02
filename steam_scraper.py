from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os


GAMES_FILE = "games.csv"
PRICE_HISTORY_FILE = "price_history.csv"

def get_steam_info(game_name):
    search_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    wrapper = soup.find("div", id="search_resultsRows")
    result = wrapper.find("a", class_="search_result_row")
    
    title = result.find("span", class_="title").text.strip()
    appid = result.get("data-ds-appid") or "UNKNOWN"

    price_block = result.find("div", class_="search_price_discount_combined")
    final_price_div = price_block.find("div", class_="discount_final_price")
    final_price = final_price_div.text.strip() if final_price_div else "No price"

    discount_div = price_block.find("div", class_="discount_pct")
    discount_pct = discount_div.text.strip() if discount_div else "0%"

    original_price_div = price_block.find("div", class_="discount_original_price")
    if discount_pct == "0%" or not original_price_div:
        original_price = final_price
    else:
        original_price = original_price_div.text.strip()

    return {
        "Title": title,
        "AppID": appid,
        "Original Price": original_price,
        "Discount": discount_pct,
        "Final Price": final_price
    }

def addGameToList(game_info):
    existing = set()

    # 1. Read existing entries first
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "AppID" in row and row["AppID"]:  # <-- check key exists
                    existing.add(row["AppID"])   # store AppIDs only

    # 2. Append new entry
    with open(GAMES_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title","AppID"])
        if f.tell() == 0:
            writer.writeheader()

        if game_info["AppID"] not in existing:
            writer.writerow({
                "Title": game_info["Title"],
                "AppID": game_info["AppID"]
            })
            print(f"Added: {game_info['Title']}")
        else:
            print(f"Skipped duplicate: {game_info['Title']}")

def addGamePriceHistory(game_info):
    with open(PRICE_HISTORY_FILE,mode="a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=["Date","Title","AppID","Original Price", "Discount", "Final Price"])
        if f.tell() == 0:
            writer.writeheader()

        writer.writerow({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            **game_info
        })

def deleteGameRowFromGameListFile():
    return

def deletePriceHistoryRowFromPriceHistoryFile():
    return

# --- MAIN ---
if __name__ == "__main__":
    while True:
        game_name = input("Enter the game name (or 'done' to finish): ")
        if game_name.lower() == "done":
            break

        info = get_steam_info(game_name)
        print(f"Found: {info['Title']}")

        addGamePriceHistory(info)
        addGameToList(info)
        
        print("Saved to games list and daily price log.\n")
