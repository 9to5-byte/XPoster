# XPoster Architecture

## Overview

XPoster is designed as a modular system with clear separation of concerns. Each component handles a specific aspect of the automation pipeline.

## Components

### 1. Configuration (`src/config.py`)

**Responsibility**: Centralized configuration management

- Loads environment variables from `.env`
- Parses YAML configuration from `config/settings.yaml`
- Validates required credentials
- Provides configuration access to all modules

**Key Features**:
- Single source of truth for all settings
- Validation on startup
- Support for multiple AI providers
- Path management for data directories

### 2. AI Client (`src/ai_client.py`)

**Responsibility**: Unified interface to AI providers

- Abstracts OpenAI and Anthropic APIs
- Provides consistent interface for text generation
- Handles API authentication and requests

**Methods**:
- `generate()`: Generate text with custom parameters
- `analyze()`: Specialized for style analysis tasks

### 3. Style Analyzer (`src/style_analyzer/`)

**Responsibility**: Learn and apply writing style

#### `DocumentProcessor`
- Loads writing samples from files
- Splits text into analyzable segments
- Saves/loads training data
- Manages sample storage

#### `StyleAnalyzer`
- Analyzes writing samples using AI
- Extracts qualitative style features (tone, voice, personality)
- Calculates quantitative metrics (sentence length, word usage)
- Generates style prompts for content generation

**Analysis Dimensions**:
- Tone and voice
- Vocabulary level
- Sentence structure
- Punctuation patterns
- Emoji usage
- Hashtag style
- Common phrases
- Personality traits

### 4. Twitter Client (`src/twitter_client/`)

**Responsibility**: Interface with X/Twitter API

**Features**:
- Post tweets
- Reply to tweets
- Get mentions
- Search tweets
- Access home timeline
- Get user's recent posts

**Implementation**:
- Uses Tweepy library
- Handles both API v1.1 and v2
- Automatic rate limiting
- Error handling and logging

### 5. Content Generator (`src/content_generator/`)

**Responsibility**: Generate tweets and replies in learned style

**Capabilities**:
- Generate original tweets
- Generate contextual replies
- Generate topic ideas
- Apply style constraints
- Filter and clean output

**Generation Process**:
1. Receive topic/context
2. Build prompt with style requirements
3. Call AI provider
4. Apply post-processing
5. Ensure length and quality constraints

### 6. Scheduler (`src/scheduler/`)

**Responsibility**: Automate posting and engagement

**Features**:
- Scheduled tweet posting
- Mention monitoring
- Timeline monitoring
- Reply automation
- Daily limits and time windows

**Jobs**:
- `_post_tweet_job`: Posts tweets at intervals
- `_monitor_and_reply_job`: Checks for reply opportunities
- `_reset_daily_counter`: Resets daily post count

**Safety**:
- Respects daily limits
- Only posts during configured hours
- Probabilistic replies to avoid spam
- Keyword-based engagement

### 7. Main Application (`src/main.py`)

**Responsibility**: Orchestrate all components

**XPoster Class**:
- Initializes all components
- Manages application lifecycle
- Provides high-level operations
- Handles CLI commands

**Commands**:
- `init`: Initialize and validate setup
- `train`: Train style analyzer
- `post`: Post single tweet
- `start`: Start automation
- `add-sample`: Add writing sample

## Data Flow

### Training Flow

```
Writing Samples (files)
    ↓
DocumentProcessor.load_samples()
    ↓
StyleAnalyzer.analyze_samples()
    ↓
AI Client (GPT-4/Claude)
    ↓
Style Profile (JSON)
    ↓
Save to training_data/
```

### Posting Flow

```
Topic/Idea
    ↓
ContentGenerator.generate_tweet()
    ↓
StyleAnalyzer.get_style_prompt()
    ↓
AI Client.generate()
    ↓
Clean & Validate
    ↓
TwitterClient.post_tweet()
    ↓
X/Twitter API
```

### Reply Flow

```
Scheduler monitors timeline/mentions
    ↓
New tweet/mention detected
    ↓
ContentGenerator.should_reply_to_tweet()
    ↓ (if yes)
ContentGenerator.generate_reply()
    ↓
AI Client.generate()
    ↓
TwitterClient.reply_to_tweet()
```

## Automation Flow

```
Start Automation
    ↓
Load/Train Style
    ↓
Initialize Scheduler
    ↓
┌─────────────────────────────────┐
│  Background Jobs Running         │
│  ├── Post tweets (variable int)  │
│  ├── Check mentions (30 min)     │
│  └── Reset counter (midnight)    │
└─────────────────────────────────┘
    ↓
Run until stopped (Ctrl+C)
```

## Error Handling

Each component implements error handling:

1. **Configuration**: Validates on startup, fails fast
2. **API Calls**: Try-catch with logging, graceful degradation
3. **Content Generation**: Fallback to simple messages
4. **Scheduler**: Jobs continue running on individual failures

## Logging

Structured logging throughout:

- Console output: INFO level, formatted
- File logging: DEBUG level, rotated daily
- Per-component context in log messages

## Configuration Hierarchy

1. **Environment Variables** (`.env`): Secrets and credentials
2. **YAML Config** (`settings.yaml`): Behavior and preferences
3. **Code Defaults**: Sensible fallbacks

## Extensibility

### Adding New AI Providers

1. Implement generation method in `AIClient`
2. Add provider to config validation
3. Update environment template

### Adding New Features

1. Create new module in `src/`
2. Initialize in `XPoster.__init__`
3. Add CLI command if needed
4. Update configuration schema

### Custom Content Strategies

Extend `ContentGenerator` with new methods:
- Custom topic generation
- Different content types
- Enhanced filtering
- Multi-message threads

## Security Considerations

- API keys in environment variables only
- `.gitignore` excludes sensitive files
- No credentials in logs
- Rate limiting to prevent abuse
- Optional approval workflows

## Performance

- Asynchronous scheduling
- Efficient API usage
- Minimal memory footprint
- Lazy loading of resources
- Cache style profile after training

## Testing Strategy

Recommended testing approach:

1. **Unit Tests**: Individual components
2. **Integration Tests**: Component interactions
3. **Manual Testing**: Generated content quality
4. **Dry Run Mode**: Test without actual posting (future feature)

## Future Enhancements

Potential improvements:

- Database for tweet history
- Web dashboard for monitoring
- A/B testing for content styles
- Image generation and posting
- Thread creation
- Analytics and insights
- Multiple account support
