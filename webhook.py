@webhook.route("/habitica-webhook", methods=["POST"])
def habitica_webhook():
    data = request.get_json()
    
    if data.get("type") != "scored":
        return "", 200
    
    direction = data.get("direction", "")
    if direction != "up":
        return "", 200
    
    task = data.get("task", {})
    user = data.get("user", {})
    
    username = user.get("profile", {}).get("name", "Quelqu'un")
    delta = round(data.get("delta", 0), 1)  # XP gagnés
    
    # Type de tâche en français
    task_type_map = {
        "daily": "📅 Quotidienne",
        "habit": "⚡ Habitude",
        "todo": "☑️ À faire",
        "reward": "🎁 Récompense"
    }
    task_type = task_type_map.get(task.get("type", ""), "Tâche")
    
    description = (
        f"**{username}** a accompli une {task_type}\n"
        f"✨ **+{delta} XP**"
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
