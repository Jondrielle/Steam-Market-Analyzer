from fastapi import APIRouter, Query,HTTPException
from utils.steam_scraper import get_current_prices,retrievePriceFile,retrieveGameFile, get_steam_info, addGameToList, addGamePriceHistory, deletePriceHistoryForDeletedGame
from models import Game,GameListResponse,PricePoint,PriceHistoryResponse,Period,ListGame,TitleRequest
from typing import List
from utils.analyze_data import (load_price_history,filter_game_by_id,aggregate_prices)
from utils.list import game_exists,save_game_to_list,load_list,delete_game_from_list
from datetime import datetime

router = APIRouter()

# List of games to track
listTracker = []
results = []


# Get top 10 matching games
@router.get("/find")
async def find_games(title: str, response_mode=List[Game]):
	results = get_steam_info(title)

	normalized = [
		{
			"title": game["title"],
			"app_id": game["app_id"],
			"image_url": game["image_url"],
			"original_price": game["original_price"],
			"discount": game["discount"],
			"final_price": game["final_price"]
		}
		for game in results[:10]
	]
	return normalized

# Add game to csv games list
@router.post("/add", response_model=Game)
async def add_game(request: TitleRequest):

	results = get_steam_info(request.title)

	if not results:
		raise HTTPException(status_code=404, detail="Game not found")

	game = results[0]


	if game_exists(game["app_id"]):
		return {"message":  "Game already exists"}\

	save_game_to_list({
	   	"title": game["title"],
		"app_id": game["app_id"]
	})

	addGamePriceHistory(game)

	return game

@router.get("/list", response_model=list[ListGame])
async def get_list():
	return load_list()

@router.get("/reviews/{app_id}")
def get_reviews(app_id: int):
	import requests

	url = f"https://store.steampowered.com/appreviews/{app_id}"

	params = {
		"json": 1,
		"language": "all",
		"purchase_type": "all"
	}

	response = requests.get(url, params=params)
	return response.json()

# Delete game from list tracker 
@router.delete("/delete/{game_id}")
async def delete_game(game_id: str):
	deletePriceHistoryForDeletedGame(game_id)
	success = delete_game_from_list(game_id)

	if not success:
		raise HTTPException(status_code=404, detail="Game not found")
	return {"message": "Game removed"}


# Aggregrate price trend
@router.get("/games/{game_id}/price-history", response_model=PriceHistoryResponse)
async def retrieve_trend(game_id: int, period: Period = Period.daily):
	
	df = load_price_history()
	game_df = filter_game_by_id(df, game_id)

	if game_df.empty:
		raise HTTPException(status_code=404, detail="No price history found")

	prices = aggregate_prices(game_df, period)
	return {
		"game_id": game_id,
		"period": period, 
		"prices": prices
	}


@router.post("/update-prices")
async def update_prices():
	games = load_list()  # your tracked games list

	if not games:
		return {"message": "No games to update"}

	today = datetime.now().date().isoformat()

	def safe_get_price(app_id, retries=3):
		for attempt in range(retries):
			try:
				price = get_current_prices(app_id)
				if price is not None:
					return price
			except Exception as e:
				print(f"[{app_id}] attempt {attempt + 1} failed: {e}")
				time.sleep(2)

		print(f"[{app_id}] FAILED after retries")
		return None

	success_count = 0
	failed = []

	for game in games:
		app_id = game["app_id"]

		current_price = safe_get_price(app_id)

		if current_price is None:
			failed.append(app_id)
			continue

		game_data = {
			"title": game.get("title", "Unknown"),
			"app_id": app_id,
			"image_url": "",
			"original_price": current_price,
			"discount": "0%",
			"final_price": current_price
		}

		addGamePriceHistory(game_data)
		success_count += 1

	return {
		"message": "update complete",
		"updated": success_count,
		"failed": failed,
		"date": today
	}