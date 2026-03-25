from fastapi import APIRouter, Query,HTTPException
from utils.steam_scraper import get_steam_info, addGameToList, addGamePriceHistory, deletePriceHistoryForDeletedGame
from models import Game,GameListResponse,PricePoint,PriceHistoryResponse,Period,ListGame,TitleRequest
from typing import List
from utils.analyze_data import (load_price_history,filter_game_by_id,aggregate_prices)
from utils.list import save_game_to_list,load_list,delete_game_from_list

router = APIRouter()

# List of games to track
listTracker = []
results = []


# Get top 10 matching games
@router.get("/find")
async def find_games(title: str, response_mode=List[Game]):
    results = get_steam_info(title)
    print(results)

    normalized = [
        {
            "title": game["title"],
            "app_id": game["app_id"],
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
async def get_reviews(app_id: int):
    import requests

    url = f'https://store.steampowered.com/appreviews/{app_id}'

    params = {
        "json": 1,
        "language":"all",
        "purchase_type":"all"
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

# Get all game list 
@router.get("/list", response_model=list[ListGame])
async def get_list():
    return load_list()

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



    