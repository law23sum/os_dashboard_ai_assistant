# API Keys Access Guide

Complete guide to obtaining API keys for all AI providers used by `cursor_ai` and `agents_ai`.

## Quick Start

```bash
# Run setup script to see all links
./setup_cursor_ai.sh --keys

# Check which keys are set
./setup_cursor_ai.sh --check

# Create .env template
./setup_cursor_ai.sh --template
```

---

## Primary AI Providers

### 1. OpenAI (GPT-4, GPT-4o, o1, ChatGPT Agents)

**API Keys:**
- 🔗 https://platform.openai.com/api-keys

**ChatGPT Assistants (Agents):**
- 🔗 https://platform.openai.com/assistants

**Billing:**
- 🔗 https://platform.openai.com/account/billing

**Setup:**
```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
```

**Models:** `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `o1-preview`, `o1-mini`

**Pricing:** Pay-per-use, ~$5-30/million tokens depending on model

---

### 2. Anthropic (Claude 3.5 Sonnet, Claude 4 Opus)

**API Keys:**
- 🔗 https://console.anthropic.com/settings/keys

**Billing:**
- 🔗 https://console.anthropic.com/settings/billing

**Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Models:** `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-haiku-20240307`

**Pricing:** Pay-per-use, ~$3-15/million tokens depending on model

---

### 3. Google (Gemini 2.0/2.5)

**API Keys:**
- 🔗 https://aistudio.google.com/app/apikey

**Google Cloud (Vertex AI):**
- 🔗 https://console.cloud.google.com/vertex-ai

**Setup:**
```bash
export GOOGLE_API_KEY="AIza-your-key-here"
```

**Models:** `gemini-2.5-flash`, `gemini-2.0-pro`, `gemini-1.5-pro`

**Pricing:** Free tier available (15 RPM), then pay-per-use

---

### 4. xAI (Grok 2, Grok 3)

**API Keys:**
- 🔗 https://console.x.ai/api-keys

**Setup:**
```bash
export XAI_API_KEY="xai-your-key-here"
```

**Models:** `grok-beta`, `grok-2`

**Pricing:** Pay-per-use

---

### 5. DeepSeek (R1)

**API Keys:**
- 🔗 https://platform.deepseek.com/api_keys

**Setup:**
```bash
export DEEPSEEK_API_KEY="sk-your-deepseek-key-here"
```

**Models:** `deepseek-reasoner`, `deepseek-chat`

**Pricing:** Pay-per-use, very competitive pricing

---

## Additional AI Providers

### Mistral AI
- 🔗 https://console.mistral.ai/api-keys
```bash
export MISTRAL_API_KEY="your-mistral-key-here"
```

### Cohere
- 🔗 https://dashboard.cohere.com/api-keys
```bash
export COHERE_API_KEY="your-cohere-key-here"
```
**Free tier available**

### Perplexity AI
- 🔗 https://www.perplexity.ai/settings/api
```bash
export PERPLEXITY_API_KEY="pplx-your-key-here"
```

### Together AI
- 🔗 https://api.together.xyz/settings/api-keys
```bash
export TOGETHER_API_KEY="your-together-key-here"
```

### OpenRouter (Access 100+ Models)
- 🔗 https://openrouter.ai/keys
```bash
export OPENROUTER_API_KEY="sk-or-your-key-here"
```

### Groq (Fast Inference)
- 🔗 https://console.groq.com/keys
```bash
export GROQ_API_KEY="gsk_your-groq-key-here"
```
**Free tier available**

### Fireworks AI
- 🔗 https://fireworks.ai/api-keys
```bash
export FIREWORKS_API_KEY="your-fireworks-key-here"
```

### Replicate
- 🔗 https://replicate.com/account/api-tokens
```bash
export REPLICATE_API_KEY="r8_your-replicate-key-here"
```

### Hugging Face
- 🔗 https://huggingface.co/settings/tokens
```bash
export HUGGINGFACE_API_KEY="hf_your-hf-key-here"
```
**Free tier available**

---

## Enterprise/Cloud Providers

### Azure OpenAI
- 🔗 https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-azure-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
export AZURE_OPENAI_API_VERSION="2024-02-01"
```

### AWS Bedrock
- 🔗 https://console.aws.amazon.com/bedrock

Requires AWS credentials configuration.

---

## Microsoft Graph API (Office 365 Integration)

**Register App:**
- 🔗 https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

**Get Tenant ID:**
- 🔗 https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Overview

```bash
export MS_GRAPH_CLIENT_ID="your-client-id"
export MS_GRAPH_TENANT_ID="your-tenant-id"
export MS_GRAPH_CLIENT_SECRET="your-client-secret"
```

---

## Google Cloud APIs

**OAuth Client:**
- 🔗 https://console.cloud.google.com/apis/credentials

**Service Account:**
- 🔗 https://console.cloud.google.com/iam-admin/serviceaccounts

```bash
export GOOGLE_CLIENT_SECRET_PATH="/path/to/client_secret.json"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
```

---

## GitHub Integration

**Personal Access Token:**
- 🔗 https://github.com/settings/tokens

**Permissions needed:**
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows
- `read:org` - Read organization data

```bash
export GITHUB_TOKEN="ghp_your-token-here"
export GIT_USERNAME="your-github-username"
export GIT_EMAIL="your-email@example.com"
```

---

## ChatGPT Agents (OpenAI Assistants)

Create custom AI agents at:
- 🔗 https://platform.openai.com/assistants

### Agent IDs for agents_ai:

```bash
# Core Agents
export OPENAI_ASSISTANT_ID_AIC="asst_your-aic-id"
export OPENAI_ASSISTANT_ID_ARIA="asst_your-aria-id"
export OPENAI_ASSISTANT_ID_SORA="asst_your-sora-id"

# Discipline Agents
export OPENAI_ASSISTANT_ID_BIOLOGIST="asst_your-biologist-id"
export OPENAI_ASSISTANT_ID_CHEMIST="asst_your-chemist-id"
export OPENAI_ASSISTANT_ID_PHYSICIST="asst_your-physicist-id"
export OPENAI_ASSISTANT_ID_MATHEMATICIAN="asst_your-mathematician-id"
export OPENAI_ASSISTANT_ID_PHILOSOPHER="asst_your-philosopher-id"
export OPENAI_ASSISTANT_ID_THEOLOGIAN="asst_your-theologian-id"
export OPENAI_ASSISTANT_ID_ACCOUNTANT="asst_your-accountant-id"
export OPENAI_ASSISTANT_ID_ECONOMIST="asst_your-economist-id"
export OPENAI_ASSISTANT_ID_LAWYER="asst_your-lawyer-id"
```

---

## Optional Integrations

### Notion
- 🔗 https://www.notion.so/my-integrations
```bash
export NOTION_API_KEY="secret_your-notion-key"
```

### Linear
- 🔗 https://linear.app/settings/api
```bash
export LINEAR_API_KEY="lin_api_your-key"
```

### Jira
- 🔗 https://id.atlassian.com/manage-profile/security/api-tokens
```bash
export JIRA_API_TOKEN="your-jira-token"
export JIRA_EMAIL="your-email@example.com"
export JIRA_DOMAIN="your-domain.atlassian.net"
```

### Slack
- 🔗 https://api.slack.com/apps
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx/xxx/xxx"
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
```

### Discord
- 🔗 https://discord.com/developers/applications
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/xxx"
export DISCORD_BOT_TOKEN="your-bot-token"
```

---

## Quick Setup

### Option 1: .env File (Recommended)

Create a `.env` file in the project root:

```bash
# Copy template
cp .env.template .env

# Edit with your keys
nano .env
```

### Option 2: Shell Export

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# AI Provider Keys
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export GOOGLE_API_KEY="your-google-key"
export XAI_API_KEY="xai-your-key"
```

### Option 3: Environment Manager

Use tools like `direnv` or `dotenv-cli`:

```bash
# Install direnv
brew install direnv  # macOS
apt install direnv   # Ubuntu

# Create .envrc
echo 'dotenv' > .envrc
direnv allow
```

---

## Security Best Practices

1. **Never commit API keys to git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates

2. **Use environment-specific keys**
   - Development, staging, production keys

3. **Rotate keys regularly**
   - Set calendar reminders
   - Monitor usage

4. **Set spending limits**
   - Configure billing alerts
   - Use rate limiting

5. **Use least privilege**
   - Only grant necessary permissions
   - Use scoped tokens

---

## Troubleshooting

### Check if keys are set:
```bash
./setup_cursor_ai.sh --check
# or
python3 cursor_ai.py --check-keys
```

### Test API connection:
```bash
# OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Common Issues:

1. **"API key not set"**
   - Ensure `.env` is in project root
   - Run `source ~/.bashrc` after adding exports

2. **"Invalid API key"**
   - Check for typos
   - Verify key hasn't expired
   - Check billing status

3. **"Rate limited"**
   - Wait and retry
   - Upgrade plan if needed
   - Implement backoff

---

## Support Links

| Provider | Documentation | Support |
|----------|--------------|---------|
| OpenAI | [docs.openai.com](https://platform.openai.com/docs) | [help.openai.com](https://help.openai.com) |
| Anthropic | [docs.anthropic.com](https://docs.anthropic.com) | [support.anthropic.com](https://support.anthropic.com) |
| Google | [ai.google.dev](https://ai.google.dev/docs) | [cloud.google.com/support](https://cloud.google.com/support) |
| xAI | [x.ai/docs](https://docs.x.ai) | [x.ai/contact](https://x.ai/contact) |

---

*Last updated: December 2024*
