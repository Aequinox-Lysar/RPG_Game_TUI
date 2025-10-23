import random

def angriff(attacker, defender):
    """Berechnet Schaden eines Angriffs"""
    damage = max(0, attacker.attack - defender.defense + random.randint(-1, 2))
    defender.hp = max(0, defender.hp - damage)
    return damage

def ist_geschlagen(entity):
    """Prüft ob ein Spieler oder Gegner besiegt ist"""
    return entity.hp <= 0
