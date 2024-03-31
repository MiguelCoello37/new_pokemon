import requests
import random
import math
from functions import *

class Game:
    def __init__(self):
        self.level = self.choose_level()
        self.player_pokemon = self.choose_pokemon()
        print(f"Tenemos por un lado a {self.player_pokemon}, tipo {verbosize_list(self.player_pokemon.types)}.")
        self.rival_pokemon = self.choose_random_pokemon()
        print(f"Y por otro lado a {self.rival_pokemon}, tipo {verbosize_list(self.rival_pokemon.types)}.")
        self.battle()

    def choose_level(self):
        level = None
        while not level:
            try:
                level = int(input("¿A qué nivel quieres que estén los Pokémon?"))
            except(ValueError):
                print("Introduce un número entre 1 y 100.")
        
        return level
    
    def choose_pokemon(self):
        pokemon_name = input("Elige tu primer Pokemon!: ").lower()
        if pokemon_name == "random":
            pokemon_name = None
        
        pokemon = Pokemon(pokemon_name_or_id=pokemon_name, level=self.level)
        nickname = input(f"¿Cómo quieres llamar a tu {pokemon_name.capitalize()}?: ")
        pokemon.change_nickname(nickname)
        return pokemon
    
    def choose_random_pokemon(self):
        pokemon = Pokemon(level=self.level)
        return pokemon
    
    def battle(self):
        print("Que comience la batalla!")
        while self.player_pokemon.stats["hp"] > 0 and self.rival_pokemon.stats["hp"] > 0:
            player_move = None
            while not player_move:
                print(f"{self.player_pokemon.nickname} tiene los siguientes movimientos: {verbosize_list([move.name for move in self.player_pokemon.moves])}")
                player_choice = input("¿Qué movimiento quieres usar?")
                player_move = self.player_pokemon.is_able_to_use(player_choice)

            rival_move = self.rival_pokemon.use_random_move()
            if self.player_pokemon.stats["speed"] > self.rival_pokemon.stats["speed"]:
                self.player_pokemon.use_move(player_move, self.rival_pokemon)
                if self.rival_pokemon.stats["hp"] > 0:
                    self.rival_pokemon.use_move(rival_move, self.player_pokemon)

class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team

class Pokemon:
    def __init__(self, pokemon_name_or_id=None, nickname=None, level=None, ivs=None, evs=None, nature=None):
        pokemon_name_or_id = pokemon_name_or_id if pokemon_name_or_id else random.randint(1, 385)
        self.r_json = requests.get(url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name_or_id}").json()
        self.pokemon_name = self.r_json["name"]
        self.nickname = nickname if nickname else self.pokemon_name
        self.level = level if level else random.randint(1, 100)
        self.types = [type["type"]["name"] for type in self.r_json["types"]]
        self.moves = self.set_default_moves(version="emerald")
        self.base_stats = self.set_base_stats()
        self.ivs = ivs if ivs else RandomIVs().ivs
        self.evs = evs if evs else RandomEVs().evs
        self.nature = nature if nature else random.choice(["hardy", "lonely", "brave", "adamant", "naughty", "bold", "docile", "relaxed", "impish", "lax", "timid", "hasty", "serious", "jolly", "naive", "modest", "mild", "quiet", "bashful", "rash", "calm", "gentle", "sassy", "careful", "quirky"])
        self.stats = self.calculate_stats()

    def __str__(self):
        moves_names = [move.name for move in self.moves]
        return f"{self.nickname} es un {self.pokemon_name.capitalize()} de nivel {self.level} con los movimientos {verbosize_list(moves_names)}. Sus estadísticas base son: {self.base_stats}. Tiene los IVs {self.ivs}, los EVs {self.evs} y una naturaleza {self.nature}. Sus estadísticas actuales son: {self.stats}."
    
    def set_default_moves(self, version):
        all_moves = self.r_json["moves"]

        version_moves = []
        for move in all_moves:
            version_group_details = move["version_group_details"]
            for detail in version_group_details:
                if detail["version_group"]["name"] == version and detail["move_learn_method"]["name"] == "level-up":
                    move_level = detail["level_learned_at"]
                    move_url = move["move"]["url"]
                    version_moves.append({"level": move_level, "url": move_url})

        sorted_version_moves = sorted(version_moves, key=lambda x: x["level"], reverse=True)
        moves_under_level = [move for move in sorted_version_moves if move["level"] <= self.level]
        last_four_moves = moves_under_level[:4]

        moves = [Move(move["url"]) for move in last_four_moves]

        return moves
    
    def set_base_stats(self):
        stats = self.r_json["stats"]
        base_stats = {stat["stat"]["name"]: stat["base_stat"] for stat in stats}
        return base_stats
    
    def calculate_stats(self):
        stats = {}
        for stat, base_stat in self.base_stats.items():
            if stat == "hp":
                stats[stat] = math.floor(((2 * base_stat + self.ivs[stat] + math.floor(self.evs[stat] / 4)) * self.level) / 100 + self.level + 10)
            else:
                stats[stat] = math.floor((((2 * base_stat + self.ivs[stat] + math.floor(self.evs[stat] / 4)) * self.level) / 100 + 5)* self.calculate_nature(stat))
        stats["max_hp"] = stats["hp"]
        
        return stats

    def is_able_to_use(self, move_name):
        try:
            move_name = move_name.lower()
            move = list(filter(lambda x: x.name.lower() == move_name, self.moves))[0]
        except(IndexError):
            print(f"{self.nickname} no conoce el movimiento {move_name}.")
            return False

        if move.current_pp == 0:
            print(f"{self.nickname} no puede usar {move.name} porque no tiene PP suficientes.")
            return False
        
        else:
            return move
        
    def use_move(self, move, rival):
        print(f"{self.nickname} ha usado {move.name}!")
        move.lose_pp()

        accuracy_roll = random.randint(0, 100)
        if move.accuracy and accuracy_roll > move.accuracy:
            print(f"Pero {self.nickname} falló!")
        
        else:
            damage = self.calculate_damage(move, rival)
            rival.lose_hp(damage)
    
    def calculate_damage(self, move, rival):
        if move.damage_class == "status":
            return 0
        
        else:
            is_critical = 1
            attack_stat = self.stats["attack"] if move.damage_class == "physical" else self.stats["special-attack"]
            defense_stat = rival.stats["defense"] if move.damage_class == "physical" else rival.stats["special-defense"]
            damage = math.floor((((((2 * self.level / 5 + 2) * attack_stat * move.power / defense_stat) / 50) + 2) * self.calculate_modifier(move, rival)))
            return damage

    def calculate_modifier(self, move, rival):
        stab = 1.5 if move.type in self.types else 1
        type_effectiveness = self.calculate_type_effectiveness(move, rival)
        critical = 2 if random.randint(0, 100) < 6 else 1
        random_factor = random.randint(85, 100) / 100
        return stab * type_effectiveness * critical * random_factor

    def calculate_type_effectiveness(self, move, rival):
        type_effectiveness = 1
        for rival_type in rival.types:
            url = f"https://pokeapi.co/api/v2/type/{move.type}/"
            r_json = requests.get(url).json()
            damage_relations = r_json["damage_relations"]
            double_damage = [type["name"] for type in damage_relations["double_damage_to"]]
            half_damage = [type["name"] for type in damage_relations["half_damage_to"]]
            no_damage = [type["name"] for type in damage_relations["no_damage_to"]]

            if rival_type in double_damage:
                type_effectiveness *= 2
            elif rival_type in half_damage:
                type_effectiveness *= 0.5
            elif rival_type in no_damage:
                type_effectiveness *= 0

        return type_effectiveness
    
    def calculate_nature(self, stat):
        if stat == "attack":
            if self.nature == "lonely" or self.nature == "adamant" or self.nature == "naughty" or self.nature == "brave":
                return 1.1
            elif self.nature == "bold" or self.nature == "docile" or self.nature == "relaxed" or self.nature == "impish":
                return 0.9
            else:
                return 1
        elif stat == "defense":
            if self.nature == "bold" or self.nature == "impish" or self.nature == "lax" or self.nature == "relaxed":
                return 1.1
            elif self.nature == "lonely" or self.nature == "mild" or self.nature == "gentle" or self.nature == "hasty":
                return 0.9
            else:
                return 1
        elif stat == "special-attack":
            if self.nature == "modest" or self.nature == "mild" or self.nature == "rash" or self.nature == "quiet":
                return 1.1
            elif self.nature == "adamant" or self.nature == "impish" or self.nature == "careful" or self.nature == "jolly":
                return 0.9
            else:
                return 1
        elif stat == "special-defense":
            if self.nature == "calm" or self.nature == "gentle" or self.nature == "careful" or self.nature == "sassy":
                return 1.1
            elif self.nature == "lonely" or self.nature == "mild" or self.nature == "rash" or self.nature == "naive":
                return 0.9
            else:
                return 1
        elif stat == "speed":
            if self.nature == "timid" or self.nature == "hasty" or self.nature == "jolly" or self.nature == "naive":
                return 1.1
            elif self.nature == "brave" or self.nature == "relaxed" or self.nature == "quiet" or self.nature == "sassy":
                return 0.9
            else:
                return 1
            
    def use_random_move(self):
        move = random.choice(self.moves)
        return move

    def lose_hp(self, damage):
        if damage == 0:
            print(f"{self.nickname} no recibió daño!")

        else:
            print(f"{self.nickname} perdió {damage} PS!")
            if self.stats["hp"] <= damage:
                self.stats["hp"] = 0
                print(f"{self.nickname} se ha debilitado!")
            else:
                self.stats["hp"] -= damage
                print(f"{self.nickname} tiene {self.stats['hp']} de {self.stats['max_hp']} PS restantes.")

    def change_nickname(self, new_nickname):
        self.nickname = new_nickname

class Move:
    def __init__(self, url):
        self.r_json = requests.get(url).json()
        self.id = self.r_json["id"]
        self.name_object = list(filter(lambda x: x["language"]["name"] == "es", self.r_json["names"]))[0]
        self.name = self.name_object["name"]
        self.power = self.r_json["power"]
        self.max_pp = self.r_json["pp"]
        self.current_pp = self.max_pp
        self.accuracy = self.r_json["accuracy"]
        self.type = self.r_json["type"]["name"]
        self.priority = self.r_json["priority"]
        self.damage_class = self.r_json["damage_class"]["name"]
        self.target = self.r_json["target"]["name"]
        self.stat_change = self.r_json["stat_changes"]
        self.description = list(filter(lambda x: x["language"]["name"] == "es", self.r_json["flavor_text_entries"]))[0]["flavor_text"]
        self.effect_chance = self.r_json["effect_chance"]
        self.effect = " | ".join([effect["effect"] for effect in self.r_json["effect_entries"]])


    def __str__(self):
        return f"{self.name.capitalize()} es un movimiento de tipo {self.type} con {self.power} de poder y {self.max_pp} PP. Tiene una precisión de {self.accuracy} y una prioridad de {self.priority}. Es de clase {self.damage_class} y su objetivo es {self.target}. Puede cambiar las estadísticas del objetivo con {self.stat_change}. Su probabilidad de efecto es {self.effect_chance}. Descripción: {self.description}"
    
    def lose_pp(self, pp=1):
        self.current_pp -= pp

class RandomIVs:
    def __init__(self):
        self.ivs = {stat: random.randint(0, 31) for stat in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]}

class RandomEVs:
    def __init__(self):
        self.evs = {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
        evs_to_distribute = random.randint(0, 510)
        while evs_to_distribute > 0:
            stat = random.choice(list(self.evs.keys()))
            if self.evs[stat] <= 252:
                evs_to_distribute -= 1
                self.evs[stat] += 1

if __name__ == "__main__":
    game = Game()