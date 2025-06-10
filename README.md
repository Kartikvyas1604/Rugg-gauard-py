# RUGGUARD X Bot

**Project RUGGUARD** is dedicated to building tools that help users assess the trustworthiness of token projects on the Solana Network. This X (formerly Twitter) bot analyzes account information and provides trustworthiness reports when triggered.

## 🚀 Features

- **Automated Monitoring**: Scans X replies for trigger phrases across all tweets
- **Smart Trigger Detection**: Responds to "@projectruggaurd riddle me this" mentions
- **Comprehensive Analysis**: Analyzes account age, follower ratios, bio content, engagement patterns, and content sentiment
- **Trusted Network Verification**: Cross-references accounts against a curated list of trusted followers
- **Real-time Reporting**: Posts detailed trustworthiness reports as replies
- **Web Dashboard**: Monitor bot status and activity through a user-friendly interface

## 🏗️ Architecture

The bot is built with a modular design for maintainability and scalability:

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

- Python 3.11+
- X Developer Account with API access
- Replit account for deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rugguard-bot
```

### 2. Configure API Keys

Set up your X API credentials in Replit Secrets:

- `X_API_KEY`: Your X API Key
- `X_API_SECRET`: Your X API Secret
- `X_ACCESS_TOKEN`: Your X Access Token
- `X_ACCESS_TOKEN_SECRET`: Your X Access Token Secret
- `X_BEARER_TOKEN`: Your X Bearer Token

**Getting X API Access:**
1. Visit [developer.x.com](https://developer.x.com/en/portal/petition/essential/basic-info)
2. Sign up for a free developer account
3. Create a new project and app
4. Generate your API keys and tokens

### 3. Install Dependencies

The bot automatically installs required packages when run on Replit:

- `tweepy` - X API client
- `textblob` - Text sentiment analysis
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests for trusted accounts list
- `statistics` - Statistical analysis

### 4. Configuration Options

You can customize the bot behavior by setting these environment variables:

```bash
TRIGGER_PHRASE="@projectruggaurd riddle me this"
MIN_TRUSTED_FOLLOWERS=3
POLLING_INTERVAL=60
MAX_RECENT_TWEETS=20
MIN_ACCOUNT_AGE_DAYS=30
```

## 🚀 Running the Bot

### On Replit (Recommended)

1. Fork this project to your Replit account
2. Set up your API keys in Secrets
3. Click "Run" or execute:

```bash
python main.py
```

### Local Development

1. Create a `.env` file with your API keys:

```bash
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
```

2. Run the bot:

```bash
python main.py
```

### Web Dashboard

Access the monitoring dashboard at the provided URL to:

- View bot status and configuration
- Monitor recent activity and logs
- Start/stop the bot remotely
- View analysis statistics

## 🔍 How It Works

### 1. Trigger Detection
The bot continuously monitors X for replies containing the exact phrase "@projectruggaurd riddle me this". When detected, it:

- Identifies the original tweet being replied to
- Extracts the user ID of the original tweet's author
- Initiates analysis for the original author (not the commenter)

### 2. Account Analysis

The bot performs comprehensive analysis including:

**Account Metrics:**
- Account age and creation date
- Follower to following ratio
- Profile completeness and bio analysis

**Engagement Analysis:**
- Average likes, retweets, and replies
- Posting frequency patterns
- Content sentiment analysis

**Trust Network Verification:**
- Cross-references against curated trusted accounts list
- Checks if account is followed by 3+ trusted accounts
- Direct trust list membership verification

### 3. Trust Score Calculation

Accounts receive trust scores based on:

- **Direct Trust**: Account is on the trusted list
- **Network Trust**: Followed by 3+ trusted accounts
- **Risk Factors**: New accounts, suspicious ratios, negative patterns
- **Engagement Quality**: Authentic vs. artificial engagement patterns

### 4. Report Generation

The bot generates concise reports including:

- Trust status and verification level
- Key risk indicators
- Account metrics summary
- Network backing information

## 🛡️ Trusted Accounts System

The bot uses a curated list of trusted accounts maintained at:
[https://github.com/devsyrem/turst-list/main/list](https://github.com/devsyrem/turst-list/main/list)

**Trust Levels:**
- **Directly Trusted**: Account is on the trusted list
- **Network Backed**: Followed by 3+ trusted accounts
- **Unverified**: Does not meet trust criteria

## 📊 Analysis Criteria

### Account Age
- **Established**: 30+ days old
- **New**: Less than 30 days old
- **Fresh**: Less than 7 days old

### Follower Ratios
- **Balanced**: Normal follower/following ratio
- **Suspicious**: Extremely high or low ratios
- **Bot-like**: Patterns indicating artificial growth

### Content Analysis
- **Sentiment**: Positive, neutral, or negative tone
- **Topics**: Crypto, finance, general content classification
- **Engagement**: Authentic vs. artificial interaction patterns

## 🔧 API Usage & Rate Limits

The bot efficiently manages X API usage:

- **Rate Limiting**: Built-in rate limit handling
- **Caching**: Reduces redundant API calls
- **Batch Processing**: Optimizes API request patterns
- **Error Handling**: Graceful degradation on API errors

## 📝 Logging & Monitoring

Comprehensive logging includes:

- Trigger detection events
- Analysis results
- API call tracking
- Error reporting
- Performance metrics

## 🚀 Deployment on Replit

The bot is fully configured for Replit deployment:

1. **Automatic Dependency Management**: No manual package installation required
2. **Environment Variables**: Use Replit Secrets for secure configuration
3. **Always-On**: Configure for continuous operation
4. **Web Interface**: Built-in dashboard for monitoring
5. **Database**: SQLite for data persistence

## 🤝 Contributing

This project follows best practices for code quality:

- **Modular Design**: Logical separation of concerns
- **Error Handling**: Comprehensive exception management
- **Documentation**: Well-commented codebase
- **Testing**: Built-in validation and monitoring

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Project RUGGUARD**: Building trust tools for the Solana ecosystem
- **X API Documentation**: [https://docs.x.com/x-api/fundamentals/data-dictionary#tweet](https://docs.x.com/x-api/fundamentals/data-dictionary#tweet)
- **Trusted Accounts List**: [https://github.com/devsyrem/turst-list/main/list](https://github.com/devsyrem/turst-list/main/list)

## 📞 Support

For support or questions regarding this implementation:
- Contact: @devsyrem on Telegram
- Issues: Use GitHub Issues for bug reports and feature requests