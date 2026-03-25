from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated, Optional, List 
from enum import Enum 

class Game(BaseModel):
    title: str = Field(alias="Title")
    app_id: str
    original_price: float = Field(alias="Original Price")
    discount: str = Field(alias="Discount")
    final_price: float = Field(alias="Final Price")

    model_config = {
        "populate_by_name": True
    }

class TitleRequest(BaseModel):
    title: str

class ListGame(BaseModel):
    title: str 
    app_id: int


class GameListResponse(BaseModel):
    games: List[Game]

class Period(str, Enum):
    daily = "daily"
    monthly = "monthly"
    yearly = "yearly"

class PricePoint(BaseModel):
    date: datetime = Field(...,description="Date of price")
    final_price: float = Field(...,ge=0,description="Game final price")

class PriceHistoryResponse(BaseModel):
    game_id: int = Field(...,description="Game ID") 
    period: Period = Field(...,description="Aggregation Period") 
    prices: List[PricePoint] = Field(...,description="Price History")

