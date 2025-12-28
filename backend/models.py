from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated, Optional, List 

class Game(BaseModel):
    title: str = Field(alias="Title")
    app_id: str = Field(alias="AppID")
    original_price: str = Field(alias="Original Price")
    discount: str = Field(alias="Discount")
    final_price: str = Field(alias="Final Price")

    model_config = {
        "populate_by_name": True
    }


class GameListResponse(BaseModel):
    games: List[Game]
