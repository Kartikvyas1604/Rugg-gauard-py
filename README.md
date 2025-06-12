# RUGGUARD X Bot

**Project RUGGUARD** is dedicated to building tools that help users assess the trustworthiness of token projects on the Solana Network. This X (formerly Twitter) bot analyzes account information and provides trustworthiness reports when triggered.

## 🚀 Features

* **Automated Monitoring**: Scans X replies for trigger phrases across all tweets
* **Smart Trigger Detection**: Responds to "@projectruggaurd riddle me this" mentions
* **Comprehensive Analysis**: Analyzes account age, follower ratios, bio content, engagement patterns, and content sentiment
* **Trusted Network Verification**: Cross-references accounts against a curated list of trusted followers
* **Real-time Reporting**: Posts detailed trustworthiness reports as replies
* **Web Dashboard**: Monitor bot status and activity through a user-friendly interface

## 🏗️ Architecture

```
RugguardBot/
├── main.py                 # Main entry point and bot coordinator
├── config.py              # Configuration management
├── models.py              # Database operations and data persistence
├── app.py                 # Web interface entry point
├── web_app.py             # Dashboard server implementation
└── bot/
    ├── monitor.py         # X platform monitoring and trigger detection
    ├── analyzer.py        # Account analysis engine
    ├── trusted_accounts.py # Trust network verification
    ├── report_generator.py # Response generation
    └── utils.py           # Utility functions and helpers
```

## ⚙️ Setup Instructions

### Prerequisites

* Python 3.11+
* X Developer Account with API access

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rugguard-bot
```

### 2. Configure API Keys

Set your X API credentials as environment variables:

```bash
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_BEARER_TOKEN=your_bearer_token
```

### 3. Install Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

**Requirements include:**

* `tweepy`
* `textblob`
* `python-dotenv`
* `requests`
* `statistics`

### 4. Configuration Options

Customize bot behavior via environment variables:

```bash
TRIGGER_PHRASE="@projectruggaurd riddle me this"
MIN_TRUSTED_FOLLOWERS=3
POLLING_INTERVAL=60
MAX_RECENT_TWEETS=20
MIN_ACCOUNT_AGE_DAYS=30
```

## 🚀 Running the Bot

### Local Development

1. Create a `.env` file and add your keys:

```env
X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
X_BEARER_TOKEN=...
```

2. Run the bot:

```bash
python main.py
```

### Web Dashboard

The bot includes a web dashboard to:

* Monitor status and logs
* View recent activity
* Start/stop the bot
* Analyze statistics

Launch it by running:

```bash
python app.py
```

## 🔍 How It Works

### 1. Trigger Detection

Bot scans X for the phrase "@projectruggaurd riddle me this", then:

* Identifies the original tweet
* Extracts the original author’s user ID
* Initiates account analysis

### 2. Account Analysis

Includes:

* **Account Age, Follower Ratios, Bio Check**
* **Engagement Stats**: Likes, retweets, replies
* **Sentiment**: Using TextBlob
* **Trusted Network Cross-Check**

### 3. Trust Score Calculation

Scoring based on:

* **Direct Trust**: In curated list
* **Network Trust**: Followed by 3+ trusted users
* **Risk Factors**: New, low engagement, weird ratios
* **Engagement Quality**: Spammy or natural

### 4. Report Generation

Bot replies with:

* Trust status
* Risk flags
* Account metrics
* Network trust evidence

## 🛡️ Trusted Accounts System

Uses a curated list:

🔗 [Trusted List GitHub](https://github.com/devsyrem/turst-list/main/list)

**Levels:**

* **Direct Trust**: Listed directly
* **Network Backed**: Followed by 3+ listed users
* **Unverified**: Does not meet criteria

## 📊 Analysis Criteria

### Account Age

* ✅ Established: 30+ days
* ⚠️ New: <30 days
* ❗ Fresh: <7 days

### Follower Ratios

* ✅ Balanced: Normal
* ⚠️ Suspicious: High/low extremes
* ❗ Bot-like: Artificial signs

### Content Sentiment

* Positive/neutral/negative
* Crypto, financial, or general content detection
* Real vs. spam engagement

## 🔧 API Usage & Rate Limits

Efficient API handling:

* Handles rate limits gracefully
* Caching to reduce API calls
* Batching for optimization
* Error handling included

## 📝 Logging & Monitoring

Comprehensive logs include:

* Trigger detections
* Trust analysis reports
* API call tracking
* Error logs and performance metrics

## 🙌 Contributing

* Modular, clean codebase
* Exception handling included
* Open for contributions via GitHub
* MIT Licensed

## 🔗 Links

* **Project RUGGUARD**: Tools for Solana trust analysis
* **X API Docs**: [https://docs.x.com/x-api/fundamentals/data-dictionary#tweet](https://docs.x.com/x-api/fundamentals/data-dictionary#tweet)
* **Trusted List**: [https://github.com/devsyrem/turst-list/main/list](https://github.com/devsyrem/turst-list/main/list)
