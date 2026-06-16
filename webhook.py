from flask import Flask, request
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
HABITICA_USER_ID = os.environ.get("HABITICA_USER_ID")
HABITICA_API_TOKEN = os.environ.get("HABITICA_API_TOKEN")
HABITICA_USER_NAME = os.environ.get("HABITICA_USER_NAME")
HABITICA_X_CLIENT = os.environ.get("HABITICA_X_CLIENT")


HABITICA_HEADERS = {
    "x-api-user": HABITICA_USER_ID,
    "x-api-key": HABITICA_API_TOKEN,
    "x-client": HABITICA_X_CLIENT,
    "Content-Type": "application/json"
}


@app.route("/habitica-webhook", methods=["POST"])

def habitica_webhook():
    data = request.get_json()
    
    if data.get("type") != "scored":
        return "", 200
    
    direction = data.get("direction", "")
    if direction != "up":
        return "", 200
    
    task = data.get("task", {})

    username = HABITICA_USER_NAME
    delta = round(data.get("delta", 0), 1)  # XP gagnés
    
    # Type de tâche en français
    task_type_map = {
        "daily": "Quotidienne",
        "habit": "Habitude",
        "todo": "À faire",
        "reward": "Récompense"
    }
    task_type = task_type_map.get(task.get("type", ""), "Tâche")
    


    quest_remark = "rien"
    boss_name = "John Doe"
    party_name = "party null"
    quest_key = -1
    try:
        party = requests.get("https://habitica.com/api/v3/groups/party", headers=HABITICA_HEADERS).json()["data"]
        quest = party["quest"]
        party_name = party["name"]
        content_quest = requests.get("https://habitica.com/api/v3/content", headers=HABITICA_HEADERS).json()["data"]

        if quest.get("active"):
            quest_key = quest["key"]
            boss_name = content["quests"][quest_key]["boss"]["name"]
            if "hp" in quest["progress"]:
                boss_hp = quest["progress"]["hp"]   # PV restants du boss
                quest_remark = f"*Le boss {boss_name} a encore {boss_hp:.1f} PV*\n"
            else:
                boss_hp = quest["progress"]["collect"]
                quest_remark = f"*Le boss {boss_name} a encore {boss_hp} objets à collecter*\n"
        else:
            quest_remark = "Pas de quête active\n"    
    except Exception as e:
        quest_remark = e

    description = (
        f"**{username}** a accompli une tâche {task_type}\n"
        f"**+{delta} XP**\n"
        f"**{quest_remark}**\n"
        # f"et les data : {data}"
    )
    message = {
        "embeds": [{
            "title": "✅ Tâche accomplie sur Habitica !",
            "description": description,
            "color": 0x9b59b6,
            "footer": {"text": "Habitica → Discord"}
        }]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    return "", 200 if response.status_code == 204 else 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
