import json

with open('2023_epl_fixtures.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("✅ Loaded data")
print("Total matches:", len(data['response']))

first = data['response'][0]
print("First match:", first['teams']['home']['name'], "vs", first['teams']['away']['name'])
print("Score:", first['goals']['home'], "-", first['goals']['away'])
print("Status:", first['fixture']['status']['long'])