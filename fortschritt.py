def erhöhe_xp(spieler, menge):
    spieler.xp += menge
    if spieler.xp >= spieler.level * 10:  # z.B. 10 XP pro Level
      print(level_up(spieler))

def level_up(spieler):
    spieler.level += 1
    spieler.max_hp += 5
    spieler.attack += 1
    spieler.defense += 1
    spieler.hp = spieler.max_hp
    return f"{spieler.name} erreicht Level {spieler.level}!"
