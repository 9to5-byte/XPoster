# XPoster

**Automated X (Twitter) posting and reply tool with personalized writing style learning.**

XPoster is an intelligent automation tool that learns your writing style from your documents and uses AI to generate authentic tweets and replies that sound like you. It can automatically post tweets throughout the day and engage with your timeline and mentions.

## Features

- **Writing Style Learning**: Analyzes your writing samples to understand your unique voice, tone, and style
- **AI-Powered Generation**: Uses GPT-4 or Claude to generate tweets and replies in your style
- **Automated Posting**: Schedules and posts tweets automatically throughout the day
- **Smart Replies**: Monitors mentions and timeline, replies intelligently to relevant tweets
- **Keyword Monitoring**: Tracks specific keywords to engage with relevant conversations
- **Configurable Schedule**: Set posting hours, frequency, and reply behavior
- **Safety Features**: Built-in filters and approval workflows

## Installation

### Prerequisites

- Python 3.8 or higher
- X/Twitter Developer Account with API credentials
- OpenAI API key or Anthropic API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd XPoster
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:
- Twitter/X API credentials (get from https://developer.twitter.com/)
- OpenAI or Anthropic API key
- Configure your preferred AI provider

5. (Optional) Customize settings in `config/settings.yaml`

## Getting Started

### 1. Add Writing Samples

XPoster learns your writing style from documents you provide. Add your writing samples to the `data/writing_samples/` directory:

```bash
# Add text or markdown files
cp your-blog-posts.txt data/writing_samples/
cp your-articles.md data/writing_samples/
```

The more diverse samples you provide, the better XPoster will understand your writing style. Include:
- Blog posts
- Articles
- Previous tweets or social media posts
- Emails
- Any text written in your voice

### 2. Train the Style Model

Run the training command to analyze your writing style:

```bash
python xposter.py train
```

This will:
- Analyze your writing samples
- Extract style characteristics (tone, vocabulary, sentence structure, etc.)
- Create a style profile for content generation
- Save the profile for future use

### 3. Test with a Manual Post

Try posting a single tweet to test the system:

```bash
# Post about a random topic
python xposter.py post

# Post about a specific topic
python xposter.py post --topic "artificial intelligence"
```

### 4. Start Automated Mode

Once you're satisfied with the results, start the automation:

```bash
python xposter.py start
```

This will:
- Post tweets automatically based on your schedule
- Monitor mentions and reply to them
- Engage with tweets in your timeline based on keywords
- Run continuously until you stop it (Ctrl+C)

## Usage

### Commands

#### Initialize
```bash
python xposter.py init
```
Initialize the application and verify configuration.

#### Train Style Model
```bash
python xposter.py train
```
Analyze writing samples and create/update style profile.

#### Post Single Tweet
```bash
# Random topic
python xposter.py post

# Specific topic
python xposter.py post --topic "your topic here"
```

#### Add Writing Sample
```bash
python xposter.py add-sample --file path/to/your/document.txt
```

#### Start Automation
```bash
python xposter.py start
```

## Configuration

### Environment Variables (.env)

Key configuration options:

```env
# Twitter API Credentials
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# AI Provider (openai or anthropic)
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4-turbo-preview

# Application Settings
LOG_LEVEL=INFO
```

### Settings File (config/settings.yaml)

Customize behavior:

```yaml
posting:
  enabled: true
  max_posts_per_day: 10
  posting_hours:
    start: 9   # 9 AM
    end: 21    # 9 PM

replies:
  enabled: true
  check_interval_minutes: 30
  reply_probability: 0.3
  keywords_to_monitor:
    - "AI"
    - "technology"
    - "your keywords here"

content_generation:
  temperature: 0.8
  include_hashtags: true
  max_hashtags: 3
  include_emojis: true
```

## How It Works

### Style Analysis

XPoster analyzes your writing samples to extract:

1. **Tone & Voice**: Formal, casual, humorous, etc.
2. **Vocabulary**: Word choice patterns and complexity
3. **Sentence Structure**: Length and complexity preferences
4. **Punctuation Style**: How you use punctuation marks
5. **Emoji Usage**: Frequency and patterns
6. **Hashtag Style**: How you use hashtags
7. **Common Phrases**: Your frequent expressions
8. **Personality Traits**: Characteristics evident in writing

### Content Generation

When generating content, XPoster:

1. Considers your style profile
2. Uses AI to generate authentic-sounding text
3. Applies your vocabulary and sentence patterns
4. Includes emojis and hashtags matching your style
5. Ensures content is engaging and relevant

### Automation

The scheduler:

1. Posts tweets at random intervals during your specified hours
2. Monitors mentions and replies automatically
3. Scans timeline for relevant conversations
4. Uses keyword matching to find engagement opportunities
5. Respects daily limits to avoid spam-like behavior

## Safety & Best Practices

### Safety Features

- **Daily Limits**: Prevents excessive posting
- **Time Windows**: Only posts during configured hours
- **Approval Workflows**: Option to require manual approval
- **Content Filters**: Blocks sensitive topics (configurable)
- **Rate Limiting**: Respects Twitter API limits

### Best Practices

1. **Start Slow**: Begin with low daily limits and increase gradually
2. **Monitor Output**: Review generated content regularly
3. **Update Samples**: Add new writing samples periodically to keep style current
4. **Test First**: Use manual posting to verify quality before automation
5. **Engage Authentically**: Configure keywords that match your genuine interests
6. **Review Settings**: Adjust reply probability to avoid over-engagement

## Troubleshooting

### Common Issues

**"No writing samples found"**
- Add .txt or .md files to `data/writing_samples/`
- Ensure files contain substantial text (100+ characters)

**"Configuration validation failed"**
- Check that all required API keys are in `.env`
- Verify Twitter API credentials are correct
- Ensure you have proper Twitter API access level

**"Failed to post tweet"**
- Verify Twitter API credentials
- Check that you have write permissions
- Ensure you haven't exceeded rate limits

**Generated content doesn't match style**
- Add more diverse writing samples
- Retrain the style model with `python xposter.py train`
- Adjust `temperature` in settings (lower = more conservative)

## Advanced Usage

### Custom Topics

Create a list of topics in your configuration for more focused content:

```yaml
topics_of_interest:
  - "Artificial Intelligence"
  - "Software Development"
  - "Your specific interests"
```

### Integration with Other Tools

XPoster can be integrated into larger workflows:

```python
from src.main import XPoster

app = XPoster()
app.initialize()
app.load_style()

# Generate custom content
tweet = app.content_generator.generate_tweet(topic="your topic")
```

## Architecture

```
XPoster/
├── src/
│   ├── ai_client.py           # AI provider wrapper
│   ├── config.py              # Configuration management
│   ├── main.py                # Main application
│   ├── style_analyzer/        # Writing style analysis
│   │   ├── analyzer.py
│   │   └── document_processor.py
│   ├── twitter_client/        # Twitter API integration
│   │   └── client.py
│   ├── content_generator/     # Content generation
│   │   └── generator.py
│   └── scheduler/             # Automation scheduler
│       └── scheduler.py
├── data/
│   ├── writing_samples/       # Your writing samples
│   └── training_data/         # Generated style profiles
├── config/
│   └── settings.yaml          # Application settings
└── xposter.py                 # CLI entry point
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational and productivity purposes. Always:
- Comply with X/Twitter's Terms of Service and API usage guidelines
- Respect others in your automated interactions
- Monitor your automated accounts regularly
- Use responsibly and ethically

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

Built with ❤️ using Python, Tweepy, OpenAI/Anthropic APIs
