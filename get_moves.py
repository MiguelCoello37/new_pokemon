from main import Move

def get_moves():
    moves = []
    base_url = "https://pokeapi.co/api/v2/move/"
    id = 0
    while True:
        id += 1
        print(id)
        try:
            move = Move(f"{base_url}{id}")
            moves.append([move.name, move.power, move.accuracy, move.damage_class, move.description])
        except:
            break

            with open("moves.txt", "w") as f:
                for move in moves:
                    f.write(f"{move[0]}\n{move[1]}\n{move[2]}\n{move[3]}\n{move[4]}\n\n")

if __name__ == "__main__":
    get_moves()
