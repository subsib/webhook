from flask import Flask, request
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
HABITICA_USER_ID = os.environ.get("HABITICA_USER_ID")
HABITICA_API_TOKEN = os.environ.get("HABITICA_API_TOKEN")
HABITICA_USER_NAME = os.environ.get("HABITICA_USER_NAME")


HABITICA_HEADERS = {
    "x-api-user": HABITICA_USER_ID,
    "x-api-key": HABITICA_API_TOKEN,
    "Content-Type": "application/json"
}


@app.route("/habitica-webhook", methods=["POST"])

# DEBUG : envoyer le JSON brut sur Discord  
# def habitica_webhook():
#     data = request.get_json()
    
    # payload_str = json.dumps(data, indent=2)
    # # Discord limite à 2000 caractères par message
    # requests.post(DISCORD_WEBHOOK_URL, json={
    #     "content": f"```json\n{payload_str[:1900]}\n```"
    # })
    
    # return "OK", 200

def habitica_webhook():
    data = request.get_json()
    
    if data.get("type") != "scored":
        return "", 200
    
    direction = data.get("direction", "")
    if direction != "up":
        return "", 200
    
    task = data.get("task", {})

    # Récupérer le profil du user qui a fait la tâche
    # user_id = data.get("user", {}).get("_id", "")
    # if user_id:
    #     r = requests.get(
    #         f"https://habitica.com/api/v3/members/{user_id}",
    #         headers=HABITICA_HEADERS
    #     )
    #     if r.status_code == 200:
    #         username = r.json().get("data", {}).get("profile", {}).get("name", "Quelqu'un")
    #     else:
    #         username = "Quelqu'un"
    # else:
    #     username = "Quelqu'un"
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
    
    description = (
        f"**{username}** a accompli une {task_type}\n"
        f"**+{delta} XP**\n"
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
