def neues_item(spieler, item):
    spieler.inventar.append(item)

def benutze_item(spieler, item_id, items_data):
    for i, item in enumerate(spieler.inventar):
        if item["id"] == item_id:
            if item["effect"] == "heal":
                spieler.hp = min(spieler.max_hp, spieler.hp + item["value"])
            del spieler.inventar[i]
            return f"{item['name']} benutzt!"
    return "Item nicht gefunden!"
