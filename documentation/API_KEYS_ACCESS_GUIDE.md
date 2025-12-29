# API Keys Access Guide

This guide provides direct links and instructions for obtaining API keys for all supported AI providers.

## Quick Access Links

### 1. OpenAI (GPT models)
- **Get API Key**: https://platform.openai.com/api-keys
- **Billing**: https://platform.openai.com/account/billing
- **Documentation**: https://platform.openai.com/docs
- **Environment Variable**: `OPENAI_API_KEY`
- **Description**: Access to GPT-4, GPT-3.5, and other OpenAI models
- **Setup**: 
  1. Sign up at https://platform.openai.com
  2. Go to API Keys section
  3. Create a new secret key
  4. Copy and set: `export OPENAI_API_KEY='sk-your-key-here'`

### 2. Anthropic (Claude)
- **Get API Key**: https://console.anthropic.com/settings/keys
- **Billing**: https://console.anthropic.com/settings/billing
- **Documentation**: https://docs.anthropic.com
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Description**: Access to Claude 3.5 Sonnet, Opus, and other Claude models
- **Setup**:
  1. Sign up at https://console.anthropic.com
  2. Navigate to Settings > API Keys
  3. Create a new key
  4. Copy and set: `export ANTHROPIC_API_KEY='sk-ant-REDACTED'`

### 3. Google (Gemini)
- **Get API Key**: https://aistudio.google.com/app/apikey
- **Billing**: https://console.cloud.google.com/billing
- **Documentation**: https://ai.google.dev/docs
- **Environment Variable**: `GOOGLE_API_KEY`
- **Description**: Access to Gemini 2.5 Flash, Pro, and other Google AI models
- **Setup**:
  1. Go to https://aistudio.google.com
  2. Click "Get API Key"
  3. Create a new project or select existing
  4. Copy and set: `export GOOGLE_API_KEY='your-google-key'`

### 4. xAI (Grok)
- **Get API Key**: https://console.x.ai/api-keys
- **Billing**: https://console.x.ai/billing
- **Documentation**: https://docs.x.ai
- **Environment Variable**: `XAI_API_KEY`
- **Description**: Access to Grok models
- **Setup**:
  1. Sign up at https://console.x.ai
  2. Navigate to API Keys
  3. Create a new key
  4. Copy and set: `export XAI_API_KEY='your-grok-key'`

### 5. Mistral AI
- **Get API Key**: https://console.mistral.ai/api-keys
- **Billing**: https://console.mistral.ai/billing
- **Documentation**: https://docs.mistral.ai
- **Environment Variable**: `MISTRAL_API_KEY`
- **Description**: Access to Mistral Large, Medium, and other models
- **Setup**:
  1. Sign up at https://console.mistral.ai
  2. Go to API Keys section
  3. Create a new key
  4. Copy and set: `export MISTRAL_API_KEY='your-mistral-key'`

### 6. Cohere
- **Get API Key**: https://dashboard.cohere.com/api-keys
- **Billing**: https://dashboard.cohere.com/billing
- **Documentation**: https://docs.cohere.com
- **Environment Variable**: `COHERE_API_KEY`
- **Description**: Access to Command R+, Command R, and other Cohere models
- **Setup**:
  1. Sign up at https://dashboard.cohere.com
  2. Navigate to API Keys
  3. Create a new key
  4. Copy and set: `export COHERE_API_KEY='your-cohere-key'`

### 7. Perplexity AI
- **Get API Key**: https://www.perplexity.ai/settings/api
- **Billing**: https://www.perplexity.ai/settings/billing
- **Documentation**: https://docs.perplexity.ai
- **Environment Variable**: `PERPLEXITY_API_KEY`
- **Description**: Access to Perplexity's online models with real-time web search
- **Setup**:
  1. Sign up at https://www.perplexity.ai
  2. Go to Settings > API
  3. Generate a new API key
  4. Copy and set: `export PERPLEXITY_API_KEY='your-perplexity-key'`

### 8. Together AI
- **Get API Key**: https://api.together.xyz/settings/api-keys
- **Billing**: https://api.together.xyz/settings/billing
- **Documentation**: https://docs.together.ai
- **Environment Variable**: `TOGETHER_API_KEY`
- **Description**: Access to various open-source models (Llama, Mistral, etc.)
- **Setup**:
  1. Sign up at https://api.together.xyz
  2. Navigate to Settings > API Keys
  3. Create a new key
  4. Copy and set: `export TOGETHER_API_KEY='your-together-key'`

### 9. DeepSeek
- **Get API Key**: https://platform.deepseek.com/api_keys
- **Billing**: https://platform.deepseek.com/billing
- **Documentation**: https://platform.deepseek.com/docs
- **Environment Variable**: `DEEPSEEK_API_KEY`
- **Description**: Access to DeepSeek Chat and Coder models
- **Setup**:
  1. Sign up at https://platform.deepseek.com
  2. Go to API Keys section
  3. Create a new key
  4. Copy and set: `export DEEPSEEK_API_KEY='your-deepseek-key'`

### 10. Cursor IDE
- **Dashboard**: https://cursor.com/dashboard
- **Billing**: https://cursor.com/settings/billing
- **Environment Variable**: `CURSOR_API_KEY` (or use `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`)
- **Description**: Cursor IDE uses OpenAI/Anthropic keys internally
- **Note**: For chat functionality, set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` instead

## Setup Methods

### Method 1: Environment Variables (Recommended for Development)

Add to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export OPENAI_API_KEY='sk-your-key-here'
export ANTHROPIC_API_KEY='sk-ant-REDACTED'
export GOOGLE_API_KEY='your-google-key'
export XAI_API_KEY='your-grok-key'
export MISTRAL_API_KEY='your-mistral-key'
export COHERE_API_KEY='your-cohere-key'
export PERPLEXITY_API_KEY='your-perplexity-key'
export TOGETHER_API_KEY='your-together-key'
export DEEPSEEK_API_KEY='your-deepseek-key'
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Method 2: .env File (Recommended for Projects)

Create a `.env` file in your project root:

```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-REDACTED
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=your-grok-key
MISTRAL_API_KEY=your-mistral-key
COHERE_API_KEY=your-cohere-key
PERPLEXITY_API_KEY=your-perplexity-key
TOGETHER_API_KEY=your-together-key
DEEPSEEK_API_KEY=your-deepseek-key

# Optional: Model Preferences
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
GOOGLE_MODEL=gemini-2.5-flash
XAI_MODEL=grok-beta
MISTRAL_MODEL=mistral-large-latest
COHERE_MODEL=command-r-plus
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
TOGETHER_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
DEEPSEEK_MODEL=deepseek-chat
```

**Important**: Add `.env` to your `.gitignore` to avoid committing secrets!

### Method 3: Check Current Keys

Use the scripts to check which keys are set:

```bash
# Check cursor_ai keys
python3 cursor_ai.py --check-keys

# Get links to all API key pages
python3 cursor_ai.py --get-keys
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or `.env` files (and add `.env` to `.gitignore`)
3. **Rotate keys regularly** if exposed
4. **Use separate keys** for development and production
5. **Set usage limits** in provider dashboards
6. **Monitor usage** regularly to detect unexpected activity

## Troubleshooting

### Key Not Working
- Verify the key is correctly set: `echo $OPENAI_API_KEY`
- Check for extra spaces or quotes
- Ensure the key hasn't expired or been revoked
- Verify billing is set up and account has credits

### Import Errors
- Install required packages: `pip install openai anthropic google-genai cohere`
- For agents: `pip install openai-agents`

### Permission Errors
- Ensure the key has the correct permissions/scopes
- Check provider-specific documentation for required permissions

## Cost Considerations

Most providers offer:
- **Free tiers** with limited usage
- **Pay-as-you-go** pricing
- **Usage-based billing**

Check each provider's pricing page for current rates:
- OpenAI: https://openai.com/pricing
- Anthropic: https://www.anthropic.com/pricing
- Google: https://ai.google.dev/pricing
- Others: Check their respective pricing pages

## Support

For provider-specific issues:
- Check provider documentation
- Contact provider support
- Review provider status pages

For script issues:
- Check script help: `python3 cursor_ai.py --help`
- Review script documentation
- Check GitHub issues (if applicable)

