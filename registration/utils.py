from django.conf import settings
import json

def load_gand_data():
    try:
        with open(settings.BASE_DIR / 'gand_data.json', 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print("Error loading JSON file:", e)
        return {"members_in_good_standing": [], "members_not_in_good_standing": []}

def find_member_by_gand_number(gand_number):
    gand_data = load_gand_data()
    for member in gand_data['members_in_good_standing']:
        if member['GAND_number'] == gand_number:
            return member, True  # Member is in good standing
    for member in gand_data['members_not_in_good_standing']:
        if member['GAND_number'] == gand_number:
            return member, False  # Member is not in good standing
    return None, None  # Not found
