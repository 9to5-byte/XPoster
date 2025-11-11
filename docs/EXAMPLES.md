# XPoster Examples

## Basic Usage Examples

### Example 1: Simple Setup and First Post

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 2. Add a writing sample
cat > data/writing_samples/my_writing.txt << 'EOF'
I love working with new technologies. There's something exciting about
building tools that make people's lives easier. Today I spent some time
exploring AI and automation - the possibilities are endless!

The best part about software development is the creative problem solving.
Every challenge is a puzzle waiting to be solved. And when you finally
get it working, that feeling is incredible! 🚀

Looking forward to sharing more of my journey. Follow along if you're
interested in tech, AI, and building cool stuff!
EOF

# 3. Train the model
python xposter.py train

# 4. Post your first tweet
python xposter.py post --topic "excited about AI"
```

### Example 2: Multiple Writing Samples

```bash
# Add blog post
cat > data/writing_samples/blog_post.md << 'EOF'
# My Thoughts on AI Development

The rapid evolution of AI tools has been fascinating to watch. As a developer,
I see both the opportunities and challenges ahead.

What excites me most is accessibility. These tools are no longer just for
researchers - they're available to anyone with an internet connection.

But with great power comes great responsibility. We need to think carefully
about how we build and deploy these systems.
EOF

# Add social media style
cat > data/writing_samples/social_posts.txt << 'EOF'
Just shipped a new feature! The team crushed it this sprint 💪

Hot take: The best code is the code you don't have to write.

Coffee + coding = perfect morning ☕️

Debugging is like being a detective, except you're also the criminal.
EOF

# Retrain with new samples
python xposter.py train
```

### Example 3: Programmatic Usage

Create a Python script `my_automation.py`:

```python
#!/usr/bin/env python3
from src.main import XPoster

# Initialize
app = XPoster()
if not app.initialize():
    print("Failed to initialize")
    exit(1)

# Load existing style or train new one
if not app.load_style():
    print("Training new style...")
    app.train_style()

# Generate and post a custom tweet
topic = "machine learning in production"
result = app.post_now(topic=topic)

if result:
    print(f"✓ Posted successfully!")
else:
    print("✗ Failed to post")
```

Run it:
```bash
python my_automation.py
```

### Example 4: Monitoring Specific Keywords

Edit `config/settings.yaml`:

```yaml
replies:
  enabled: true
  check_interval_minutes: 15
  reply_probability: 0.5
  keywords_to_monitor:
    - "python"
    - "AI automation"
    - "developer tools"
    - "machine learning"
```

Start monitoring:
```bash
python xposter.py start
```

Now XPoster will reply to tweets containing these keywords.

### Example 5: Custom Posting Schedule

Edit `config/settings.yaml` for a professional schedule:

```yaml
posting:
  enabled: true
  max_posts_per_day: 5
  posting_hours:
    start: 8   # 8 AM
    end: 18    # 6 PM
  timezone: "America/New_York"

content_generation:
  temperature: 0.7  # More conservative
  include_hashtags: true
  max_hashtags: 2
  include_emojis: false  # Professional tone
```

### Example 6: Testing Before Going Live

```bash
# 1. Generate without posting (manual review)
python xposter.py post --topic "testing"
# Review the output on Twitter

# 2. If satisfied, start with low volume
# Edit config/settings.yaml:
#   max_posts_per_day: 2
#   reply_probability: 0.1

# 3. Start automation
python xposter.py start

# 4. Monitor logs
tail -f logs/xposter.log

# 5. After 24 hours, review output
# 6. Gradually increase volume if satisfied
```

## Advanced Examples

### Example 7: Integration with Content Calendar

Create `post_schedule.py`:

```python
from src.main import XPoster
from datetime import datetime

# Your content calendar
content_calendar = {
    "Monday": "productivity tips",
    "Tuesday": "tech news commentary",
    "Wednesday": "coding insights",
    "Thursday": "industry trends",
    "Friday": "weekly reflection"
}

app = XPoster()
app.initialize()
app.load_style()

# Get today's topic
day = datetime.now().strftime("%A")
topic = content_calendar.get(day, "general thoughts")

# Post
app.post_now(topic=topic)
```

### Example 8: A/B Testing Content Styles

```python
from src.main import XPoster

app = XPoster()
app.initialize()
app.load_style()

# Generate multiple versions
topic = "artificial intelligence"

# Professional version
app.config.settings["content_generation"]["temperature"] = 0.5
app.config.settings["content_generation"]["include_emojis"] = False
professional = app.content_generator.generate_tweet(topic=topic)

# Casual version
app.config.settings["content_generation"]["temperature"] = 0.9
app.config.settings["content_generation"]["include_emojis"] = True
casual = app.content_generator.generate_tweet(topic=topic)

print("Professional:", professional)
print("Casual:", casual)

# Post your preferred version
app.twitter_client.post_tweet(professional)
```

### Example 9: Batch Processing Ideas

```python
from src.main import XPoster

app = XPoster()
app.initialize()
app.load_style()

# Generate multiple tweet ideas
ideas = app.content_generator.generate_tweet_ideas(count=10)

print("Today's tweet ideas:")
for i, idea in enumerate(ideas, 1):
    print(f"{i}. {idea}")

# Select and post your favorite
selected = ideas[0]
tweet = app.content_generator.generate_tweet(topic=selected)
app.twitter_client.post_tweet(tweet)
```

### Example 10: Style Evolution Tracking

```python
import json
from pathlib import Path
from datetime import datetime
from src.main import XPoster

app = XPoster()
app.initialize()

# Train and save with timestamp
app.train_style()

# Save versioned style profile
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_profile = app.style_analyzer.style_profile

output_file = f"style_profile_{timestamp}.json"
app.document_processor.save_training_data(current_profile, output_file)

print(f"Style profile saved: {output_file}")
print(f"Tone: {current_profile.get('tone')}")
print(f"Avg sentence length: {current_profile.get('avg_sentence_length')}")
```

## Troubleshooting Examples

### Example 11: Debug Mode

```python
import logging
from src.main import XPoster

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

app = XPoster()
app.initialize()

# This will show detailed API calls and processing
app.train_style()
```

### Example 12: Dry Run (Test Without Posting)

```python
from src.main import XPoster

app = XPoster()
app.initialize()
app.load_style()

# Generate but don't post
tweet = app.content_generator.generate_tweet(topic="test")
print(f"Would post: {tweet}")
print(f"Length: {len(tweet)} characters")

# Verify it looks good before actually posting
if input("Post this? (y/n): ").lower() == 'y':
    app.twitter_client.post_tweet(tweet)
```

## Integration Examples

### Example 13: Webhook Integration

```python
from flask import Flask, request
from src.main import XPoster

app_flask = Flask(__name__)
xposter = XPoster()
xposter.initialize()
xposter.load_style()

@app_flask.route('/post', methods=['POST'])
def webhook_post():
    data = request.json
    topic = data.get('topic', '')

    result = xposter.post_now(topic=topic)

    if result:
        return {"status": "success", "tweet_id": result["id"]}
    return {"status": "error"}, 500

if __name__ == '__main__':
    app_flask.run(port=5000)
```

Call it:
```bash
curl -X POST http://localhost:5000/post \
  -H "Content-Type: application/json" \
  -d '{"topic": "exciting news"}'
```

### Example 14: Cron Job Setup

Add to crontab:
```bash
# Post at 9 AM, 1 PM, and 5 PM every day
0 9,13,17 * * * cd /path/to/XPoster && /path/to/venv/bin/python xposter.py post

# Train weekly on Sunday at midnight
0 0 * * 0 cd /path/to/XPoster && /path/to/venv/bin/python xposter.py train
```

## Tips & Tricks

### Getting Better Results

1. **More samples = better style matching**
   - Add 10-20 diverse writing samples
   - Include different contexts and topics

2. **Tune temperature**
   - Lower (0.5-0.7): More conservative and on-brand
   - Higher (0.8-1.0): More creative and varied

3. **Monitor and adjust**
   - Review first 10-20 posts manually
   - Adjust settings based on quality
   - Retrain periodically with new samples

4. **Start small**
   - Begin with 2-3 posts per day
   - Low reply probability (0.1-0.2)
   - Increase gradually

5. **Use keywords strategically**
   - Focus on your genuine interests
   - Avoid overly broad terms
   - 3-5 specific keywords work best
