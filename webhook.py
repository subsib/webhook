from flask import Flask, request
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

@app.route("/habitica-webhook", methods=["POST"])
def habitica_webhook():
    data = request.get_json()
    print("JSON reçu :", data)  # ← ajoute cette ligne
    
    # On filtre uniquement les tâches complétées
    if data.get("type") != "scored":
        return "", 200
    
    task = data.get("task", {})
    user = data.get("user", {})
    
    # Récupération des infos
    task_text = task.get("text", "Tâche inconnue")
    username = user.get("profile", {}).get("name", "Quelqu'un")
    direction = data.get("direction", "")
    
    # On vérifie que c'est bien un "up" (accompli)
    if direction != "up":
        return "", 200
    
    # Construction du message Discord
    message = {
        "embeds": [{
            "title": "✅ Tâche accomplie sur Habitica !",
            "description": f"**{username}** vient de compléter :\n> {task_text}",
            "color": 0x9b59b6,  # Violet, couleur d'Habitica
            "footer": {
                "text": "Habitica → Discord"
            }
        }]
    }
    
    # Envoi vers Discord
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    
    if response.status_code == 204:
        return "", 200
    else:
        return "Erreur Discord", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
