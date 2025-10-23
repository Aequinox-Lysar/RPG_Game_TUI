class Spieler:
    def __init__(self, name):
        # Basiswerte
        self.name = name
        self.level = 1
        self.xp = 0
        self.geld = 500

        # Lebenspunkte & Kampfwerte
        self.max_hp = 30
        self.hp = self.max_hp
        self.attack = 5
        self.defense = 2

        # Inventar
        self.inventar = []
