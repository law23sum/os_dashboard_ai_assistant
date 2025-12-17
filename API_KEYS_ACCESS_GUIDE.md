# API Keys Access Guide
## Direct Links to Get API Keys for cursor_ai

This guide provides direct links and instructions to obtain API keys for all AI providers supported by the `cursor_ai` command.

---

## 🔑 Quick Access Links

### 1. **Cursor IDE API Key**
**Direct Link:** https://cursor.com/dashboard

**Steps:**
1. Log in to your Cursor account
2. Navigate to **Settings** tab
3. Select **Cursor Admin API Keys**
4. Click **Create New API Key**
5. Copy the key immediately (it won't be shown again)

**Note:** Cursor API keys are primarily for team/analytics management. For chat functionality, use OpenAI or Anthropic keys (which Cursor uses internally).

---

### 2. **OpenAI API Key** (Recommended for GPT models)
**Direct Link:** https://platform.openai.com/api-keys

**Steps:**
1. Create account or log in at https://platform.openai.com
2. Go to **API Keys** section (or use direct link above)
3. Click **"Create new secret key"**
4. Name your key (e.g., "cursor_ai")
5. Copy the key immediately
6. **Important:** Add billing/payment method in **Billing** section first

**Billing Setup:** https://platform.openai.com/account/billing

**Documentation:** https://platform.openai.com/docs

---

### 3. **Anthropic API Key** (Recommended for Claude models)
**Direct Link:** https://console.anthropic.com/settings/keys

**Steps:**
1. Create account or log in at https://console.anthropic.com
2. Navigate to **API Keys** section (or use direct link above)
3. Click **"Create Key"**
4. Name your key (e.g., "cursor_ai")
5. Copy the key immediately
6. **Important:** Add billing/payment method first

**Billing Setup:** https://console.anthropic.com/settings/billing

**Documentation:** https://docs.anthropic.com

---

### 4. **Google Gemini API Key**
**Direct Link:** https://aistudio.google.com/app/apikey

**Steps:**
1. Create account or log in with Google account
2. Go to **Get API Key** (or use direct link above)
3. Select or create a Google Cloud project
4. Click **"Create API Key"**
5. Copy the key
6. **Note:** May require enabling Gemini API in Google Cloud Console

**Google AI Studio:** https://aistudio.google.com

**Documentation:** https://ai.google.dev/docs

---

### 5. **xAI (Grok) API Key**
**Direct Link:** https://console.x.ai/api-keys

**Steps:**
1. Create account or log in at https://console.x.ai
2. Navigate to **API Keys** section
3. Click **"Create API Key"**
4. Name your key
5. Copy the key immediately

**Documentation:** https://docs.x.ai

---

## 📝 How to Set API Keys

### Option 1: Environment Variables (Recommended)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_API_KEY="your-google-key-here"
export XAI_API_KEY="your-xai-key-here"
export CURSOR_API_KEY="your-cursor-key-here"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option 2: .env File (Project Directory)

Create a `.env` file in your project root:

```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
XAI_API_KEY=your-xai-key-here
CURSOR_API_KEY=your-cursor-key-here
```

The `cursor_ai.py` script will automatically load this file.

### Option 3: Check Current Keys

```bash
cursor_ai --check-keys
```

This shows which API keys are currently set.

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git:**
   - Add `.env` to `.gitignore`
   - Never share keys publicly
   - Use environment variables in production

2. **Rotate keys regularly:**
   - Change keys every 90 days
   - Revoke old keys when creating new ones

3. **Set usage limits:**
   - Configure spending limits in provider dashboards
   - Monitor usage regularly
   - Set up alerts for unusual activity

4. **Use separate keys:**
   - Different keys for development/production
   - Different keys for different projects

---

## 💰 Pricing Information

### OpenAI
- **Pricing:** Pay-per-use, varies by model
- **Free Tier:** Limited credits for new accounts
- **Link:** https://openai.com/pricing

### Anthropic (Claude)
- **Pricing:** Pay-per-use, varies by model
- **Free Tier:** Limited credits available
- **Link:** https://www.anthropic.com/pricing

### Google Gemini
- **Pricing:** Free tier available, pay-per-use for higher limits
- **Link:** https://ai.google.dev/pricing

### xAI (Grok)
- **Pricing:** Check current pricing at https://x.ai
- **Link:** https://docs.x.ai/pricing

---

## 🚀 Quick Start

1. **Get at least one API key** (OpenAI or Anthropic recommended)
2. **Set it as environment variable:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
3. **Test it:**
   ```bash
   cursor_ai --check-keys
   cursor_ai --provider openai
   ```

---

## 📚 Additional Resources

- **cursor_ai Documentation:** See `CURSOR_AI_README.md`
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Anthropic API Docs:** https://docs.anthropic.com
- **Google AI Docs:** https://ai.google.dev/docs
- **xAI Docs:** https://docs.x.ai

---

## ❓ Troubleshooting

### "API key not set" error
- Check key is set: `echo $OPENAI_API_KEY`
- Reload shell: `source ~/.zshrc`
- Check `.env` file exists and is in project root

### "Invalid API key" error
- Verify key is correct (no extra spaces)
- Check key hasn't expired
- Ensure billing is set up (for OpenAI/Anthropic)

### "Rate limit exceeded" error
- Check usage limits in provider dashboard
- Wait for rate limit to reset
- Consider upgrading plan if needed

---

**Last Updated:** December 17, 2025

