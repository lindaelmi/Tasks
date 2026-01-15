# -*- coding: utf-8 -*-
"""
Извлечение структурированных сущностей из news.txt (local)
Avec Yargy : nom + interprétation complète
Correction : .interpretation(Person) sur la racine
"""

from yargy import Parser, rule, and_, not_
from yargy.interpretation import fact
from yargy.predicates import gram
from yargy.relations import gnc_relation
from dataclasses import dataclass
from typing import Optional, List
import re
import json
import os

# ---------- Structures ----------
Name = fact('Name', ['first', 'last'])
Person = fact('Person', ['name', 'birth_date', 'birth_place'])

# ---------- Grammaire : Nom ----------
gnc = gnc_relation()

FIRST = and_(gram('Name'), not_(gram('Abbr'))).interpretation(Name.first).match(gnc)
LAST = and_(gram('Surn'), not_(gram('Abbr'))).interpretation(Name.last).match(gnc)
NAME = rule(FIRST, LAST).interpretation(Name)

# ---------- Dates (regex) ----------
DATE_PATTERN = re.compile(
    r'\b([1-3]?\d)\s(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s(\d{4})\b',
    re.IGNORECASE
)

# ---------- Lieux (liste) ----------
CITIES = ['Москва', 'Санкт-Петербург', 'Казань', 'Минск', 'Генуя', 'Париж', 'Лондон', 'Киев', 'Симферополь', 'Нью-Йорк', 'Рим', 'Варшава', 'Берлин']

def extract_place(text: str) -> Optional[str]:
    for city in CITIES:
        if re.search(rf'\b(?:в|на)\s{city}\b', text):
            return city
    return None

# ---------- Prénoms russes courants ----------
RUSSIAN_FIRST_NAMES = {
    'Александр', 'Алексей', 'Андрей', 'Антон', 'Артём', 'Борис', 'Вадим', 'Валентин', 'Василий', 'Виктор', 'Владимир', 'Владислав', 'Геннадий', 'Георгий', 'Даниил', 'Денис', 'Дмитрий', 'Евгений', 'Иван', 'Игорь', 'Илья', 'Кирилл', 'Константин', 'Леонид', 'Максим', 'Михаил', 'Никита', 'Николай', 'Олег', 'Павел', 'Пётр', 'Роман', 'Сергей', 'Станислав', 'Степан', 'Тимур', 'Фёдор', 'Юрий', 'Ярослав',
    'Анна', 'Валентина', 'Вера', 'Виктория', 'Галина', 'Дарья', 'Екатерина', 'Елена', 'Зоя', 'Ирина', 'Ксения', 'Лариса', 'Людмила', 'Маргарита', 'Мария', 'Наталья', 'Оксана', 'Ольга', 'Светлана', 'Софья', 'Татьяна', 'Юлия', 'Яна'
}

def is_likely_person(name: str) -> bool:
    parts = name.split()
    if len(parts) != 2:
        return False
    first, last = parts
    return (first in RUSSIAN_FIRST_NAMES) or (last in RUSSIAN_FIRST_NAMES)

# ---------- Grammaire : Nom + interprétation complète ----------
PERSON_NAME = rule(NAME.interpretation(Person.name)).interpretation(Person)

parser = Parser(PERSON_NAME)

# ---------- Traitement ----------
FILE_PATH = r"C:\Users\pc\Desktop\Bigdata\mat mercredi\news.txt"
OUTPUT_PATH = r"C:\Users\pc\Desktop\Bigdata\mat mercredi\entries.json"

print("Читаем файл...", FILE_PATH)
all_results = []

with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) != 3:
            continue
        category, title, text = parts

        # Yargy : noms uniquement
        for match in parser.findall(text):
            p = match.fact
            if p.name and is_likely_person(f"{p.name.first} {p.name.last}"):
                # on rajoute la date via regex SI présente
                date_match = re.search(DATE_PATTERN, text)
                place_match = extract_place(text)
                entry = {
                    "name": f"{p.name.first} {p.name.last}",
                    "birth_date": date_match.group(0) if date_match else None,
                    "birth_place": place_match
                }
                all_results.append(entry)

# ---------- Sauvegarde ----------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"✅ Сохранено {len(all_results)} записей →", OUTPUT_PATH)