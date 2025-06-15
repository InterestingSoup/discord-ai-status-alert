# 🎮 Discord AI Status Alert Bot

Automatically monitors your PSN clan and founders for online presence and posts visual alerts to Discord — powered by Azure OpenAI (GPT-4o + DALL·E 3) and PSNAWP.

## 🚀 Features

- Detects when multiple members are online on PSN.
- Generates custom AI artwork using DALL·E 3 based on who's online.
- Posts alerts with images to your Discord via webhook.
- Sends hype messages when specific founders are online together.
- Tracks state to prevent duplicate alerts.
- Runs perfectly on [Coolify](https://coolify.io) or any Docker-based host.

---

## 📁 Project Structure

```
psn-alert/
├── ai-alert.py              # Main bot script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image setup
├── .gitignore               # Ignore sensitive/generated files
└── README.md                # This file
```

---

## 🔧 Environment Variables

Set these in `.env` for local testing or in Coolify’s **Environment** tab:

```env
# PSN + Discord
NPSSO_TOKEN=your_psnawp_npsso_token
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# Azure OpenAI (DALL·E 3)
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com

# Azure GPT-4o
GPT_AZURE_OPENAI_API_KEY=...
GPT_AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
GPT_AZURE_DEPLOYMENT_NAME=gpt-4o

# PSN Group ID
GROUP_ID=your_psn_group_id

# Alert state files (inside container or mounted volume)
ALERT_STATE_FILE_FOUNDERS=.last_founder_alert.json
ALERT_STATE_FILE_CLAN=.last_clan_alert.json

# Optional override for timing (in seconds)
ALERT_INTERVAL_FOUNDERS=2700      # 45 minutes
ALERT_INTERVAL_CLAN=7200          # 2 hours
```

---

## 🧠 How It Works

1. Fetches online status from PSN using `psnawp`.
2. If 2+ members are online, it:
   - Builds a prompt for DALL·E 3 based on who’s online.
   - Sends image + message to Discord.
3. Sends a bonus GPT-4o-generated message when a key founder group is online.

---

## 🗃️ Coolify Setup

1. **Add a new App** pointing to your GitHub repo or zip.
2. Set environment variables in **Environment** tab.
3. Under **Volumes**, add:
   ```
   /app
   ```
   This will persist `.last_founder_alert.json` and `.last_clan_alert.json`.
4. Deploy and you're live! 🎉

---

## 📸 Example Discord Output

- **Image**: DALL·E 3-generated based on active usernames
- **Message**: `"🟢 Founders Online Alert: ASamad89, BrendanSoup are online on PSN!"`

---

## 🧪 Local Dev

```bash
# Setup virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python ai-alert.py
```

---

## ❗ Disclaimer

This is a community-built PSN tool. Please follow Sony's terms of use and OpenAI API usage guidelines. Use responsibly.

---

## 📬 Questions or Contributions?

Open an issue or PR on [GitHub](https://github.com/InterestingSoup/discord-ai-status-alert) or message us on [Discord](https://discord.gg/BeWdfJkFqr)!

