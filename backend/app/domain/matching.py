"""Offline matching of names and semantic stems, preserving request order."""

ALIASES = {
    "book": ["книг", "учеб", "обуч", "знан"],
    "phone": ["телефон", "связ", "цифр"],
    "puzzle": ["пазл", "решен", "иде", "задач"],
    "wallet": ["кошел", "день", "финанс"],
    "coin": ["монет", "доход", "финанс"],
    "lamp": ["ламп", "свет", "иде"],
    "folder": ["папк", "документ", "работ"],
    "pen": ["ручк", "пис", "творч"],
    "headphones": ["науш", "музык", "звук"],
    "tulips": ["цвет", "тюльпан", "празд"],
}


def match_objects(query):
    matches = [
        (min(query.find(alias) for alias in aliases if alias in query), obj)
        for obj, aliases in ALIASES.items()
        if any(alias in query for alias in aliases)
    ]
    return [obj for _, obj in sorted(matches)]
