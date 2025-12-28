from fastapi import APIRouter, Query
from utils.steam_scraper import get_steam_info, addGameToList, addGamePriceHistory
from models import Game,GameListResponse
from typing import List

router = APIRouter()

# List of games to track
listTracker = []
results = []


# Get top 10 matching games
@router.get("/find", response_model=list[Game])
async def find_games(title: str):
    results = get_steam_info(title)
    print(results)
    top10 = results[:10]
    return top10

# Add game to csv games list
@router.post("/add", response_model=Game)
async def add_game(game: Game):
    # Convert Pydantic model to dict
    game_info = game.dict()

    # Add to CSV-tracked games
    addGameToList({
        "Title": game_info["title"],
        "AppID": game_info["app_id"]
    })

    # Add price to CSV
    addGamePriceHistory({
        "Title": game_info["title"],
        "AppID": game_info["app_id"],
        "Original Price": game_info["original_price"],
        "Discount": game_info["discount"],
        "Final Price": game_info["final_price"]
    })

    # Optionally add to in-memory list
    listTracker.append(game_info)

    return game

# Delete game from list tracker 
@router.delete("/delete/{game_name}")
async def delete_game(game_name: str):
    for i, game in enumerate(listTracker):
        if game["title"].lower() == game_name.lower():
            print(f"{game["title"].lower()} and {game_name.lower()}")
            listTracker.pop(i)
            return {"Message: " : "Game was removed"}
    raise HTTPException(status_code=404,detail="Game not found")


# Get all game list 
@router.get("/list", response_model=list[Game])
async def get_list():
    return listTracker