from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os
import pandas as pd


GAMES_FILE = "games.csv"
PRICE_HISTORY_FILE = "price_history.csv"

def clean_price(price: str) -> float:
    if not price:
        return 0.0

    price = price.strip()

    if price.lower() in ["free", "no price"]:
        return 0.0

    # Remove currency symbols and commas
    price = price.replace("$", "").replace(",", "").strip()

    try:
        return float(price)
    except ValueError:
        return 0.0
        
def get_steam_info(game_name: str):
    search_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    wrapper = soup.find("div", id="search_resultsRows")
    if not wrapper:
        return []

    results = []
    rows = wrapper.find_all("a", class_="search_result_row")

    for row in rows:
        img_tag = row.find("img")
        image_url = img_tag["src"] if img_tag else None

        title_span = row.find("span", class_="title")
        if not title_span:
            continue

        title = title_span.text.strip()
        appid = row.get("data-ds-appid")
        if not appid:
            continue


        # -------------------- PRICE -------------------- 
        price_block = row.find("div", class_="search_price_discount_combined")

        final_price = 0.0
        original_price = 0.0
        discount = "0%"

        if price_block:
            final_price_div = price_block.find("div", class_="discount_final_price")
            if final_price_div:
                final_price = clean_price(final_price_div.text)

            discount_div = price_block.find("div", class_="discount_pct")
            if discount_div:
                discount = discount_div.text.strip()

            original_price_div = price_block.find("div", class_="discount_original_price")
            if original_price_div:
                original_price = clean_price(original_price_div.text)
            else:
                original_price = final_price


        results.append({
            "title": title,
            "app_id": appid,
            "image_url": image_url,
            "original_price": original_price,
            "discount": discount,
            "final_price": final_price
        })

    return results

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
    today = datetime.utcnow().strftime("%Y-%m-%d")

    file_exists = os.path.exists(PRICE_HISTORY_FILE)

    if file_exists:
        df = pd.read_csv(PRICE_HISTORY_FILE)

        if not df.empty:
            df["date"] = df["date"].astype(str)

            exists = df[
                (df["app_id"].astype(str) == str(game_info["app_id"])) &
                (df["date"] == today)
            ]

            if not exists.empty:
                print("Already logged today for this game")
                return 

    with open(PRICE_HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "date",
            "title",
            "app_id",
            "image_url",
            "original_price",
            "discount",
            "final_price"
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists or os.path.getsize(PRICE_HISTORY_FILE) == 0:
            writer.writeheader()

        writer.writerow({
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "title": game_info["title"],
            "app_id": game_info["app_id"],
            "image_url": game_info["image_url"],
            "original_price": game_info["original_price"],
            "discount": game_info["discount"],
            "final_price": game_info["final_price"]
        })


def deletePriceHistoryForDeletedGame(app_id):
    if not os.path.exists(PRICE_HISTORY_FILE):
        return

    rows = []

    with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["app_id"] != app_id:  
                rows.append(row)

    with open(PRICE_HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "date",
            "title",
            "app_id",
            "image_url",
            "original_price",
            "discount",
            "final_price"
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# --- MAIN ---
if __name__ == "__main__":
    while True:
        game_name = input("Enter the game name (or 'done' to finish): ")
        if game_name.lower() == "done":
            break

        results = get_steam_info(game_name)

        if not results:
            print("No games found.\n")
            continue

        # Show top 10 results
        for i, game in enumerate(results[:10], 1):
            print(f"{i}) {game['Title']}")

        choice = input("Select a game number to add (or press Enter to skip): ")
        if not choice:
            print("Skipped.\n")
            continue

        try:
            selected = results[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice, skipped.\n")
            continue

        # Save selected game
        addGamePriceHistory(selected)
        addGameToList(selected)

        print("Saved to games list and daily price log.\n")