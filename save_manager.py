# save_manager.py
import json
import os

SAVE_FILE = "save_data.json"

# Структура за замовчуванням 
DEFAULT_DATA = {
    "stats": {
        "total_games": 0,
        "total_kills": 0,
        "deaths": 0
    },
    "campaign_progress": {
        "EASY": 1,
        "NORMAL": 1,
        "HARD": 1,
        "HARDCORE": 1
    },
    "classic_progress": {
        "EASY": 1,
        "NORMAL": 1,
        "HARD": 1,
        "HARDCORE": 1
    }
}

def load_data():
    if not os.path.exists(SAVE_FILE):
        return DEFAULT_DATA.copy()
    
    with open(SAVE_FILE, "r") as file_path:
        data = json.load(file_path)
            
        if "stats" not in data: 
            data["stats"] = DEFAULT_DATA["stats"].copy()
        if "campaign_progress" not in data: 
            data["campaign_progress"] = DEFAULT_DATA["campaign_progress"].copy()

        if "classic_progress" not in data: 
            data["classic_progress"] = DEFAULT_DATA["classic_progress"].copy()

        return data

def save_data(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Помилка при збереженні даних: {e}")

def update_progress(game_mode, difficulty, level_num):

    data = load_data()
    
    # Визначаємо, в яку секцію писати дані
    if game_mode == "CLASSIC":
        dict_key = "classic_progress"
    else:
        dict_key = "campaign_progress"
    
    # Отримуємо поточний рекорд для цієї складності
    current_best = data[dict_key].get(difficulty, 1)
    
    if level_num > current_best:
        data[dict_key][difficulty] = level_num
        save_data(data)
        return True
        
    return False

def add_stats(kills=0, deaths=0, games=0):
    data = load_data()
    data["stats"]["total_kills"] += kills
    data["stats"]["deaths"] += deaths
    data["stats"]["total_games"] += games
    save_data(data)