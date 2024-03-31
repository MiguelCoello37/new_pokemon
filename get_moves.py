from main import Move
import pandas as pd

def get_moves():
    moves = []
    base_url = "https://pokeapi.co/api/v2/move/"
    id = 0
    while True:
        id += 1
        print(id)
        try:
            move = Move(f"{base_url}{id}")
            moves.append([move.name, move.power, move.accuracy, move.damage_class, move.description, move.effect])
        except:
            break

    print(moves)
    df = pd.DataFrame(moves, columns=["Name", "Power", "Accuracy", "Damage Class", "Description", "Effect"])
    print(df)
    df.to_csv("moves.csv", index=False)
            
if __name__ == "__main__":
    get_moves()
