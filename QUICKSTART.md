# Quick Start Guide

Get up and running with XPoster in 5 minutes!

## Step 1: Get API Keys

### Twitter/X API
1. Go to https://developer.twitter.com/
2. Create a new project and app
3. Generate API keys and access tokens
4. Make sure to enable **Read and Write** permissions

### AI Provider (Choose one)

**Option A: OpenAI**
1. Go to https://platform.openai.com/
2. Create an API key
3. Add credits to your account

**Option B: Anthropic**
1. Go to https://console.anthropic.com/
2. Create an API key

## Step 2: Install

```bash
# Clone and enter directory
cd XPoster

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

## Step 4: Add Writing Samples

```bash
# Add your writing samples
cp your-blog-posts.txt data/writing_samples/
cp your-articles.md data/writing_samples/
```

Or create a new sample:

```bash
cat > data/writing_samples/my_style.txt << 'EOF'
[Paste your writing here - blog posts, articles, tweets, etc.]
EOF
```

## Step 5: Train

```bash
python xposter.py train
```

This analyzes your writing and creates a style profile.

## Step 6: Test

```bash
# Post a test tweet
python xposter.py post --topic "testing my new automation tool"
```

Check X/Twitter to see your generated post!

## Step 7: Automate

```bash
# Start automation
python xposter.py start
```

Press Ctrl+C to stop.

## Configuration Tips

Edit `config/settings.yaml` to customize:

```yaml
posting:
  max_posts_per_day: 3  # Start small!
  posting_hours:
    start: 10
    end: 18

replies:
  reply_probability: 0.2  # Reply to 20% of relevant tweets
  keywords_to_monitor:
    - "your topic"
    - "your interest"
```

## What's Next?

- Monitor the output for the first day
- Adjust settings based on results
- Add more writing samples to improve accuracy
- Increase posting frequency gradually
- Customize keywords for better engagement

## Need Help?

- Check the full [README.md](README.md)
- Review logs in `logs/xposter.log`
- Open an issue on GitHub

Happy posting! 🚀
