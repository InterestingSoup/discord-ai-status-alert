#!/home/qcloud/psn-alert/venv/bin/python

from psnawp_api.psnawp import PSNAWP
from openai import AzureOpenAI
import requests
import json
import os
import time
import tempfile
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/qcloud/psn-alert/.env")

# === CONFIG ===
NPSSO_TOKEN = os.getenv("NPSSO_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
ALERT_INTERVAL_FOUNDERS = int(os.getenv("ALERT_INTERVAL_FOUNDERS", 45 * 60))  # default 45 min
ALERT_INTERVAL_CLAN = int(os.getenv("ALERT_INTERVAL_CLAN", 120 * 60))        # default 2 hours
GROUP_ID = os.getenv("GROUP_ID")

# GPT-4o Configuration for Chat Completions
GPT_AZURE_OPENAI_API_KEY = os.getenv("GPT_AZURE_OPENAI_API_KEY")
GPT_AZURE_OPENAI_ENDPOINT = os.getenv("GPT_AZURE_OPENAI_ENDPOINT")
GPT_AZURE_DEPLOYMENT_NAME = os.getenv("GPT_AZURE_DEPLOYMENT_NAME")

ALERT_STATE_FILE_FOUNDERS = os.getenv("ALERT_STATE_FILE_FOUNDERS", ".last_founder_alert.json")
ALERT_STATE_FILE_CLAN = os.getenv("ALERT_STATE_FILE_CLAN", ".last_clan_alert.json")

FOUNDERS = [
    "ASamad89",
    "BrendanSoup",
    "mutasif",
    "moiiz41510",
    "killerx096",
    "nooramin40",
]

CLAN_MEMBERS = [
    "Hosty_66",
    "YoBoyKadendillon",
    "zChampionbwoyz",
    "IG_Juicy",
]

PROMPT_MAP = {
            "ASamad89": "Far left: A confident truck driver with a large semi-truck-themed helmet and an oil-stained jumpsuit.",
                "mutasif": "Second from left: A tall tech engineer with a friendly moose-style headgear, wearing a white lab coat and holding a glowing tablet.",
                    "Hosty_66": "Third from left: A gold ranked player with a biryani dish as his head, standing silently.",
                        "BrendanSoup": "Center left: A cheerful gamer wearing a bright hoodie with flame decals and visor shades, holding a neon controller.",
                            "moiiz41510": "Center right: A creative character with a soup can-style helmet and a multi-pocket vest, giving a thumbs-up.",
                                "killerx096": "Second from right: A strong figure with a cappuccino cup-style head, casually holding a protein shake and smiling.",
                                    "nooramin40": "Far right: A kind character with a stylized green-and-white abstract helmet, symbolizing harmony, in a green jacket waving.",
                                        "zChampionbwoyz": "Fourth from left: A cyber-enhanced warrior with a wolf head and a glowing red visor.",
                                                "YoBoyKadendillon": "Third from right: A cloaked highschooler with glowing eyes, a cap, and a playful puppy filter on his face.",
                                                    "IG_Juicy": "A laid-back character with a milk carton as his head, dressed in chill streetwear and leaning casually."
             }

GENERAL_PROMPT_TEMPLATE = (
    "Comic-style digital illustration of {count} characters standing side by side in a futuristic city at sunset. Full-body view, consistent art style, evenly spaced. From left to right:"
)

# DALL-E 3 client for image generation
dalle_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01"
)

# GPT-4o client for chat completions
gpt_client = AzureOpenAI(
    api_key=os.environ["GPT_AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["GPT_AZURE_OPENAI_ENDPOINT"],
    api_version="2025-01-01-preview"
)

def generate_iced_capp_story():
    """Generate an AI response for the iced capp story message"""
    try:
        response = gpt_client.chat.completions.create(
            model=os.environ["GPT_AZURE_DEPLOYMENT_NAME"],
            messages=[
                {
                    "role": "system",
                    "content": "You are an enthusiastic gamer who's friend loves iced cappuccinos. Generate a short, excited message (max 100 characters) about iced cappuccinos that would hype up your clan member Zubi. Be creative and use gaming references if possible. Include some emojis and exclamation marks!"
                },
                {
                    "role": "user",
                    "content": "Generate an excited message about iced cappuccinos for my gaming squad"
                }
            ],
            max_tokens=50,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Failed to generate AI response: {e}")
        return "ICED CAPP STORRRRRRY!!!!!"  # Fallback to original message

def load_last_alert(path):
    if not os.path.exists(path):
        return {"members": [], "timestamp": 0}
    with open(path, "r") as f:
        return json.load(f)

def save_last_alert(path, members):
    with open(path, "w") as f:
        json.dump({"members": members, "timestamp": time.time()}, f)

def generate_image(prompt):
    if len(prompt) > 1000:
        print("❌ Prompt too long, skipping image generation.")
        return None

    print(f"🧠 Prompt being sent to Azure OpenAI DALL·E 3:\n{prompt}\n")

    try:
        response = dalle_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"❌ Azure OpenAI DALL·E 3 failed: {e}")
        return None

def send_discord_alert(image_url, message):
    try:
        if image_url:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img_data = requests.get(image_url).content
                tmp.write(img_data)
                tmp_path = tmp.name

            with open(tmp_path, "rb") as f:
                response = requests.post(
                    DISCORD_WEBHOOK,
                    data={"content": message},
                    files={"file": ("clan_status.png", f, "image/png")},
                )

            os.remove(tmp_path)
        else:
            response = requests.post(
                DISCORD_WEBHOOK,
                json={"content": message}
            )

        print(f"[DEBUG] Discord POST Status: {response.status_code}")
        print(f"[DEBUG] Discord POST Response: {response.text}")

        if response.status_code >= 400:
            print(f"❌ Discord message failed! Code {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Error sending Discord message: {e}")

def check_and_alert(psnawp, members, last_alert_path, alert_title, alert_interval):
    online_players = []
    for online_id in members:
        try:
            user = psnawp.user(online_id=online_id)
            presence = user.get_presence()
            online_status = presence.get("basicPresence", {}).get("primaryPlatformInfo", {}).get("onlineStatus")
            if online_status == "online":
                online_players.append(user.online_id)
        except Exception as e:
            print(f"Error checking {online_id}: {e}")

    last_alert = load_last_alert(last_alert_path)
    last_members = sorted(last_alert["members"])
    current_members = sorted(online_players)
    print(f"[DEBUG] Online members: {current_members}")
    print(f"[DEBUG] Included in prompt: {[p for p in current_members if p in PROMPT_MAP]}")
    time_since_last = time.time() - last_alert["timestamp"]

    if len(current_members) >= 2:
        # Only trigger if new members joined (not fewer or same), and interval has passed
        if len(current_members) > len(last_members) and time_since_last >= alert_interval:
            member_prompts = [PROMPT_MAP[p] for p in current_members if p in PROMPT_MAP]
            character_count = len(member_prompts)
            general_prompt = GENERAL_PROMPT_TEMPLATE.format(count=character_count)
            formatted_characters = " ".join(member_prompts)
            raw_prompt = f"{general_prompt} {formatted_characters}"

            image_url = generate_image(raw_prompt)

            message = f"**🟢  {alert_title}:** {', '.join(current_members)} are online on PSN!"
            send_discord_alert(image_url, message)
            save_last_alert(last_alert_path, current_members)

            if alert_title == "Founders Online Alert" and "killerx096" in current_members and len(current_members) >= 4:
                group = psnawp.group(group_id=GROUP_ID)
                ai_message = generate_iced_capp_story()
                print(f"🤖 Sending AI-generated message: {ai_message}")
                group.send_message(ai_message)
        else:
            print(f"🚫 No new users joined or interval too short — {alert_title} alert skipped.")
            save_last_alert(last_alert_path, current_members)

    elif len(current_members) == 0 and last_members != []:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"**🔴  {alert_title.replace('Online', 'Offline')}:** No members online on PSN."
        })
        save_last_alert(last_alert_path, [])
    else:
        print(f"ℹ️ Only one user online — {alert_title} alert skipped.")
        save_last_alert(last_alert_path, current_members)


def main():
    psnawp = PSNAWP(npsso_cookie=NPSSO_TOKEN)
    check_and_alert(psnawp, FOUNDERS, ALERT_STATE_FILE_FOUNDERS, "Founders Online Alert", ALERT_INTERVAL_FOUNDERS)
    check_and_alert(psnawp, CLAN_MEMBERS, ALERT_STATE_FILE_CLAN, "Clan Members Online Alert", ALERT_INTERVAL_CLAN)

if __name__ == "__main__":
    main()
