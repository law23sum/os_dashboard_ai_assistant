# API Keys Access Guide

This guide provides direct links to obtain API keys for all supported AI providers in the OS Dashboard AI Assistant and cursor_ai system.

## 🤖 AI Chat Providers

### 1. OpenAI (GPT Models)
**Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, o1, o1-mini

**Get API Key**: https://platform.openai.com/api-keys

**Billing Dashboard**: https://platform.openai.com/account/billing

**Documentation**: https://platform.openai.com/docs/api-reference

**Pricing**: https://openai.com/pricing

**Environment Variable**: `OPENAI_API_KEY`

**Setup**:
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

---

### 2. Anthropic (Claude)
**Models**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku

**Get API Key**: https://console.anthropic.com/settings/keys

**Billing Dashboard**: https://console.anthropic.com/settings/billing

**Documentation**: https://docs.anthropic.com/claude/reference/getting-started-with-the-api

**Pricing**: https://www.anthropic.com/pricing

**Environment Variable**: `ANTHROPIC_API_KEY`

**Setup**:
```bash
export ANTHROPIC_API_KEY='sk-ant-REDACTED'
```

---

### 3. Google AI (Gemini)
**Models**: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash

**Get API Key**: https://aistudio.google.com/app/apikey

**Documentation**: https://ai.google.dev/docs

**Pricing**: https://ai.google.dev/pricing

**Environment Variable**: `GOOGLE_API_KEY`

**Setup**:
```bash
export GOOGLE_API_KEY='your-google-api-key'
```

---

### 4. xAI (Grok)
**Models**: Grok Beta, Grok 2

**Get API Key**: https://console.x.ai/api-keys

**Documentation**: https://docs.x.ai/

**Billing**: https://console.x.ai/billing

**Environment Variable**: `XAI_API_KEY`

**Setup**:
```bash
export XAI_API_KEY='xai-REDACTED'
```

---

### 5. Perplexity AI
**Models**: Perplexity Sonar, Codellama, Llama

**Get API Key**: https://www.perplexity.ai/settings/api

**Documentation**: https://docs.perplexity.ai/

**Environment Variable**: `PERPLEXITY_API_KEY`

**Setup**:
```bash
export PERPLEXITY_API_KEY='pplx-your-key-here'
```

---

### 6. Cohere
**Models**: Command, Command R, Command R+, Embed

**Get API Key**: https://dashboard.cohere.com/api-keys

**Documentation**: https://docs.cohere.com/

**Pricing**: https://cohere.com/pricing

**Environment Variable**: `COHERE_API_KEY`

**Setup**:
```bash
export COHERE_API_KEY='your-cohere-key'
```

---

### 7. Mistral AI
**Models**: Mistral Large, Mistral Medium, Mistral Small

**Get API Key**: https://console.mistral.ai/api-keys/

**Documentation**: https://docs.mistral.ai/

**Pricing**: https://mistral.ai/technology/#pricing

**Environment Variable**: `MISTRAL_API_KEY`

**Setup**:
```bash
export MISTRAL_API_KEY='your-mistral-key'
```

---

### 8. Together AI
**Models**: Various open-source models (Llama, Mixtral, etc.)

**Get API Key**: https://api.together.xyz/settings/api-keys

**Documentation**: https://docs.together.ai/

**Pricing**: https://www.together.ai/pricing

**Environment Variable**: `TOGETHER_API_KEY`

**Setup**:
```bash
export TOGETHER_API_KEY='your-together-key'
```

---

### 9. Replicate
**Models**: Various open-source models

**Get API Key**: https://replicate.com/account/api-tokens

**Documentation**: https://replicate.com/docs

**Environment Variable**: `REPLICATE_API_TOKEN`

**Setup**:
```bash
export REPLICATE_API_TOKEN='r8_your-token'
```

---

### 10. Hugging Face
**Models**: Thousands of open-source models

**Get API Key**: https://huggingface.co/settings/tokens

**Documentation**: https://huggingface.co/docs/api-inference/

**Environment Variable**: `HUGGINGFACE_API_KEY`

**Setup**:
```bash
export HUGGINGFACE_API_KEY='hf_your-key'
```

---

## 🔗 Integration Services

### 11. Microsoft Graph API (Office 365)
**Services**: Word, Excel, PowerPoint, OneNote, Outlook, OneDrive

**Setup Guide**: https://learn.microsoft.com/en-us/graph/auth-register-app-v2

**Azure Portal**: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

**Documentation**: https://learn.microsoft.com/en-us/graph/

**Environment Variables**:
- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `MICROSOFT_TENANT_ID`

**Setup Steps**:
1. Go to Azure Portal
2. Navigate to "App registrations"
3. Create a new registration
4. Generate client secret under "Certificates & secrets"
5. Configure API permissions for Microsoft Graph

---

### 12. Google Workspace (Gmail, Calendar, Drive)
**Setup Guide**: https://console.cloud.google.com/

**Create Project**: https://console.cloud.google.com/projectcreate

**Enable APIs**: https://console.cloud.google.com/apis/library

**Credentials**: https://console.cloud.google.com/apis/credentials

**Documentation**: https://developers.google.com/workspace

**Environment Variables**:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_CREDENTIALS_FILE` (path to credentials.json)

**Setup Steps**:
1. Create a Google Cloud project
2. Enable Gmail API, Calendar API, Drive API
3. Create OAuth 2.0 credentials
4. Download credentials.json
5. Complete OAuth flow

---

### 13. GitHub
**Get Token**: https://github.com/settings/tokens

**Create Fine-Grained Token**: https://github.com/settings/tokens?type=beta

**Documentation**: https://docs.github.com/en/rest

**Environment Variables**:
- `GITHUB_TOKEN`
- `GITHUB_USERNAME`

**Setup**:
```bash
export GITHUB_TOKEN='ghp_your-token-here'
export GITHUB_USERNAME='your-username'
```

**Scopes Needed**:
- `repo` (Full control of private repositories)
- `read:org` (Read org and team membership)
- `gist` (Create gists)

---

### 14. GitLab
**Get Token**: https://gitlab.com/-/profile/personal_access_tokens

**Documentation**: https://docs.gitlab.com/ee/api/

**Environment Variable**: `GITLAB_TOKEN`

---

### 15. Adobe PDF Services
**Get Credentials**: https://developer.adobe.com/console

**Documentation**: https://developer.adobe.com/document-services/docs/overview/

**Environment Variables**:
- `ADOBE_CLIENT_ID`
- `ADOBE_CLIENT_SECRET`
- `ADOBE_ORGANIZATION_ID`

---

### 16. Slack
**Create App**: https://api.slack.com/apps

**Documentation**: https://api.slack.com/

**Environment Variables**:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

---

### 17. Discord
**Create Application**: https://discord.com/developers/applications

**Documentation**: https://discord.com/developers/docs/intro

**Environment Variable**: `DISCORD_BOT_TOKEN`

---

### 18. Notion
**Get Integration Token**: https://www.notion.so/my-integrations

**Documentation**: https://developers.notion.com/

**Environment Variable**: `NOTION_API_KEY`

---

### 19. Airtable
**Get API Key**: https://airtable.com/account

**Documentation**: https://airtable.com/developers/web/api/introduction

**Environment Variable**: `AIRTABLE_API_KEY`

---

### 20. Pinecone (Vector Database)
**Get API Key**: https://app.pinecone.io/

**Documentation**: https://docs.pinecone.io/

**Environment Variables**:
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`

---

## 📊 Analytics & Monitoring

### 21. Datadog
**Get API Key**: https://app.datadoghq.com/organization-settings/api-keys

**Environment Variable**: `DATADOG_API_KEY`

---

### 22. New Relic
**Get API Key**: https://one.newrelic.com/api-keys

**Environment Variable**: `NEW_RELIC_API_KEY`

---

## 💾 Databases & Storage

### 23. Supabase
**Get Keys**: https://app.supabase.com/project/_/settings/api

**Environment Variables**:
- `SUPABASE_URL`
- `SUPABASE_KEY`

---

### 24. MongoDB Atlas
**Get Connection String**: https://cloud.mongodb.com/

**Environment Variable**: `MONGODB_URI`

---

## 🔍 Search & Knowledge

### 25. Brave Search API
**Get API Key**: https://brave.com/search/api/

**Documentation**: https://brave.com/search/api/

**Environment Variable**: `BRAVE_API_KEY`

---

### 26. SerpAPI (Google Search)
**Get API Key**: https://serpapi.com/manage-api-key

**Documentation**: https://serpapi.com/docs

**Environment Variable**: `SERPAPI_KEY`

---

### 27. Wolfram Alpha
**Get App ID**: https://developer.wolframalpha.com/portal/myapps/

**Documentation**: https://products.wolframalpha.com/api/

**Environment Variable**: `WOLFRAM_APP_ID`

---

## 🎨 Image & Media AI

### 28. Stability AI (Stable Diffusion)
**Get API Key**: https://platform.stability.ai/account/keys

**Documentation**: https://platform.stability.ai/docs

**Environment Variable**: `STABILITY_API_KEY`

---

### 29. DALL-E (OpenAI)
**Same as OpenAI**: Uses `OPENAI_API_KEY`

---

### 30. Eleven Labs (Voice)
**Get API Key**: https://elevenlabs.io/app/settings/api-keys

**Documentation**: https://elevenlabs.io/docs/api-reference

**Environment Variable**: `ELEVEN_LABS_API_KEY`

---

## 📝 Quick Setup Script

Create a `.env` file in your project root:

```bash
# AI Chat Providers
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-REDACTED
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=xai-your-key
PERPLEXITY_API_KEY=pplx-your-key
COHERE_API_KEY=your-cohere-key
MISTRAL_API_KEY=your-mistral-key
TOGETHER_API_KEY=your-together-key
REPLICATE_API_TOKEN=r8_your-token
HUGGINGFACE_API_KEY=hf_your-key

# Microsoft Graph
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id

# Google Workspace
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_CREDENTIALS_FILE=credentials.json

# GitHub
GITHUB_TOKEN=ghp_your-token
GITHUB_USERNAME=your-username

# Additional Services
ADOBE_CLIENT_ID=your-adobe-client-id
ADOBE_CLIENT_SECRET=your-adobe-secret
SLACK_BOT_TOKEN=xoxb-your-token
NOTION_API_KEY=secret_your-key
PINECONE_API_KEY=your-pinecone-key
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use different keys** for development and production
3. **Rotate keys regularly** (every 90 days)
4. **Set up billing alerts** on all services
5. **Use environment-specific keys** when deploying
6. **Enable IP restrictions** where available
7. **Monitor API usage** regularly

## 📚 Additional Resources

- **API Status Pages**: Check service health before debugging
  - OpenAI: https://status.openai.com/
  - Anthropic: https://status.anthropic.com/
  - Google: https://status.cloud.google.com/

- **Rate Limits**: Be aware of rate limits for each service
- **Cost Optimization**: Monitor usage and set budget alerts

## 🆘 Troubleshooting

### Common Issues:

1. **"API key not valid"**
   - Verify key is copied correctly (no extra spaces)
   - Check if key is active in provider dashboard
   - Ensure billing is set up (if required)

2. **"Rate limit exceeded"**
   - Check your usage tier
   - Implement exponential backoff
   - Consider upgrading your plan

3. **"Insufficient credits"**
   - Add payment method
   - Check billing dashboard
   - Top up account balance

For more help, see the documentation links for each service.
