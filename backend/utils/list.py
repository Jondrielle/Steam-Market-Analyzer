import pandas as pd
import os

LIST_FILE = "list.csv"

def load_list():
    if not os.path.exists(LIST_FILE):
        return []

    df = pd.read_csv(LIST_FILE)

    if df.empty:
        return []

    return df.to_dict(orient="records")


def save_game_to_list(game_data):
    df = pd.DataFrame([game_data])

    if os.path.exists(LIST_FILE):
        df.to_csv(LIST_FILE, mode="a", header=False, index=False)

        values = (df.astype(str)).to_numpy()

    else:
        df.to_csv(LIST_FILE, index=False)

def game_exists(game_title):
    df = pd.read_csv(LIST_FILE)

    return (df["title"].astype(str) == str(game_title)).any()

def delete_game_from_list(game_id):
    if not os.path.exists(LIST_FILE):
        return False

    df = pd.read_csv(LIST_FILE)

    df = df[df["app_id"].astype(str) != str(game_id)]

    df.to_csv(LIST_FILE, index=False)
    return True