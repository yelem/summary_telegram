# AI Telegram News Aggregator

A smart, serverless Python bot that acts as your personal news editor. It reads multiple Telegram channels, uses the **Mistral AI** to filter out ads and gossip, and delivers a clean, formatted, and strictly summarized daily digest directly to your personal Telegram chat.

## Features

- **Smart AI Filtering:** Uses `Mistral-Nemo` to detect and ignore promotional posts, gossip, and clickbait.
- **Strict Formatting & Translation:** Forces the LLM to output summaries strictly in Ukrainian with consistent Markdown formatting (Headers, Bullet points, Emojis).
- **Adaptive Length Handling:** Automatically bypasses Telegram's 4096-character limit by smartly splitting long digests at paragraph breaks without breaking links.
- **Zero Background Resource Usage:** Designed as a "Run & Done" script. It connects, processes the news, sends the digest, and gracefully disconnects. No infinite loops eating up your RAM.

## Tech Stack

- **Language:** Python 3.10+
- **Telegram API:** `Telethon` (for reading channels and sending via bot)
- **AI / LLM:** `OpenAI` Python SDK (routing to Mistral API)
- **Other:** `pytz`, `asyncio`

## Setup and Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/yelem/summary_telegram.git](https://github.com/yelem/summary_telegram.git)
cd summary_telegram

2. Install dependencies:
It is recommended to use a virtual environment.

pip install -r requirements.txt

3. Get your API Keys:

Telegram API_ID & API_HASH: Get them from my.telegram.org.

Bot Token: Create a bot via @BotFather in Telegram.

Mistral API Key: Get your free API key from console.mistral.ai.

4. Configuration:
Open summary_telegram.py and replace the placeholder variables in the # SETTINGS block with your actual keys and target channels.

Python
API_ID = 1234567        
API_HASH = 'your_api_hash'   
BOT_TOKEN = 'your_bot_token' 
MISTRAL_API_KEY = 'your_mistral_key'
MY_CHAT_ID = 123456789 # Your personal Telegram ID
CHANNELS = ['@channel1', '@channel2']

Usage
Simply run the script from your terminal:

Bash
python summary_telegram.py
The script will authenticate, parse the latest posts from your selected channels, process them through Mistral AI, send the digest to your DMs, and exit automatically.

License
MIT License