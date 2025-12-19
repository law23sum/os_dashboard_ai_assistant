#!/bin/bash
# =============================================================================
# Cursor AI Setup Script - Multi-Provider AI Environment Configuration
# =============================================================================
# This script sets up API keys for all AI providers used by cursor_ai and agents_ai
# It creates aliases, wrapper scripts, and helps configure environment variables
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_AI_SCRIPT="$SCRIPT_DIR/cursor_ai.py"
AGENTS_AI_SCRIPT="$SCRIPT_DIR/agents_ai.py"
ENV_FILE="$SCRIPT_DIR/.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${CYAN}=============================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}=============================================================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# =============================================================================
# API KEY CONFIGURATION - ALL PROVIDERS
# =============================================================================
# Get your API keys from these links:

declare -A API_PROVIDERS=(
    # Primary AI Providers
    ["OPENAI_API_KEY"]="OpenAI (GPT-4, GPT-4o, o1)|https://platform.openai.com/api-keys|Pay-per-use"
    ["ANTHROPIC_API_KEY"]="Anthropic (Claude 3.5/4)|https://console.anthropic.com/settings/keys|Pay-per-use"
    ["GOOGLE_API_KEY"]="Google (Gemini 2.0)|https://aistudio.google.com/app/apikey|Free tier available"
    ["XAI_API_KEY"]="xAI (Grok 2/3)|https://console.x.ai/api-keys|Pay-per-use"
    
    # Additional AI Providers
    ["DEEPSEEK_API_KEY"]="DeepSeek (R1)|https://platform.deepseek.com/api_keys|Pay-per-use"
    ["MISTRAL_API_KEY"]="Mistral AI|https://console.mistral.ai/api-keys|Pay-per-use"
    ["COHERE_API_KEY"]="Cohere (Command)|https://dashboard.cohere.com/api-keys|Free tier available"
    ["PERPLEXITY_API_KEY"]="Perplexity AI|https://www.perplexity.ai/settings/api|Pay-per-use"
    ["TOGETHER_API_KEY"]="Together AI|https://api.together.xyz/settings/api-keys|Pay-per-use"
    ["OPENROUTER_API_KEY"]="OpenRouter (Multi-model)|https://openrouter.ai/keys|Pay-per-use"
    ["GROQ_API_KEY"]="Groq (Fast inference)|https://console.groq.com/keys|Free tier available"
    ["FIREWORKS_API_KEY"]="Fireworks AI|https://fireworks.ai/api-keys|Pay-per-use"
    ["REPLICATE_API_KEY"]="Replicate|https://replicate.com/account/api-tokens|Pay-per-use"
    ["HUGGINGFACE_API_KEY"]="Hugging Face|https://huggingface.co/settings/tokens|Free tier available"
    
    # Microsoft/Azure
    ["AZURE_OPENAI_API_KEY"]="Azure OpenAI|https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI|Pay-per-use"
    ["AZURE_OPENAI_ENDPOINT"]="Azure OpenAI Endpoint|https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI|Required for Azure"
    ["MS_GRAPH_CLIENT_ID"]="Microsoft Graph API|https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade|Free"
    ["MS_GRAPH_CLIENT_SECRET"]="Microsoft Graph Secret|https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade|Required for MS APIs"
    ["MS_GRAPH_TENANT_ID"]="Microsoft Tenant ID|https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Overview|Required for MS APIs"
    
    # Google Cloud
    ["GOOGLE_APPLICATION_CREDENTIALS"]="Google Cloud Service Account|https://console.cloud.google.com/iam-admin/serviceaccounts|Free tier available"
    ["GOOGLE_CLIENT_SECRET_PATH"]="Google OAuth Client|https://console.cloud.google.com/apis/credentials|Free"
    
    # GitHub
    ["GITHUB_TOKEN"]="GitHub Personal Token|https://github.com/settings/tokens|Free"
    ["GITHUB_API_KEY"]="GitHub API Key|https://github.com/settings/tokens|Free"
    
    # Other Services
    ["ADOBE_CLIENT_ID"]="Adobe API|https://developer.adobe.com/console|Free tier available"
    ["ADOBE_CLIENT_SECRET"]="Adobe Client Secret|https://developer.adobe.com/console|Required for Adobe"
    ["SLACK_WEBHOOK_URL"]="Slack Webhook|https://api.slack.com/apps|Free"
    ["DISCORD_WEBHOOK_URL"]="Discord Webhook|https://discord.com/developers/applications|Free"
    ["NOTION_API_KEY"]="Notion API|https://www.notion.so/my-integrations|Free"
    ["LINEAR_API_KEY"]="Linear API|https://linear.app/settings/api|Free"
    ["JIRA_API_TOKEN"]="Jira API|https://id.atlassian.com/manage-profile/security/api-tokens|Free"
)

# ChatGPT/OpenAI Agents (Assistants API)
declare -A CHATGPT_AGENTS=(
    ["OPENAI_ASSISTANT_ID_AIC"]="ChatGPT Agent: AIC (Software Systems)|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_ARIA"]="ChatGPT Agent: Aria (Philosophy)|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_SORA"]="ChatGPT Agent: Sora (Logic/Math)|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_BIOLOGIST"]="ChatGPT Agent: Biologist|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_CHEMIST"]="ChatGPT Agent: Chemist|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_PHYSICIST"]="ChatGPT Agent: Physicist|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_MATHEMATICIAN"]="ChatGPT Agent: Mathematician|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_PHILOSOPHER"]="ChatGPT Agent: Philosopher|Create at https://platform.openai.com/assistants"
    ["OPENAI_ASSISTANT_ID_THEOLOGIAN"]="ChatGPT Agent: Theologian|Create at https://platform.openai.com/assistants"
)

# =============================================================================
# FUNCTIONS
# =============================================================================

show_api_links() {
    print_header "🔑 API Keys - Quick Access Links"
    
    print_section "Primary AI Providers"
    echo ""
    echo -e "  ${GREEN}1. OpenAI (GPT-4, GPT-4o, o1, ChatGPT Agents)${NC}"
    echo "     API Keys: https://platform.openai.com/api-keys"
    echo "     Assistants: https://platform.openai.com/assistants"
    echo "     Billing: https://platform.openai.com/account/billing"
    echo ""
    echo -e "  ${GREEN}2. Anthropic (Claude 3.5 Sonnet, Claude 4 Opus)${NC}"
    echo "     API Keys: https://console.anthropic.com/settings/keys"
    echo "     Billing: https://console.anthropic.com/settings/billing"
    echo ""
    echo -e "  ${GREEN}3. Google (Gemini 2.0 Flash/Pro, Gemini 2.5)${NC}"
    echo "     API Keys: https://aistudio.google.com/app/apikey"
    echo "     Vertex AI: https://console.cloud.google.com/vertex-ai"
    echo ""
    echo -e "  ${GREEN}4. xAI (Grok 2, Grok 3)${NC}"
    echo "     API Keys: https://console.x.ai/api-keys"
    echo ""
    echo -e "  ${GREEN}5. DeepSeek (DeepSeek R1)${NC}"
    echo "     API Keys: https://platform.deepseek.com/api_keys"
    echo ""
    
    print_section "Additional AI Providers"
    echo ""
    echo "  • Mistral AI: https://console.mistral.ai/api-keys"
    echo "  • Cohere: https://dashboard.cohere.com/api-keys"
    echo "  • Perplexity: https://www.perplexity.ai/settings/api"
    echo "  • Together AI: https://api.together.xyz/settings/api-keys"
    echo "  • OpenRouter: https://openrouter.ai/keys"
    echo "  • Groq: https://console.groq.com/keys"
    echo "  • Fireworks: https://fireworks.ai/api-keys"
    echo "  • Replicate: https://replicate.com/account/api-tokens"
    echo "  • Hugging Face: https://huggingface.co/settings/tokens"
    echo ""
    
    print_section "Enterprise/Cloud Providers"
    echo ""
    echo "  • Azure OpenAI: https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI"
    echo "  • Microsoft Graph: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
    echo "  • Google Cloud: https://console.cloud.google.com/apis/credentials"
    echo "  • AWS Bedrock: https://console.aws.amazon.com/bedrock"
    echo ""
    
    print_section "Developer Tools"
    echo ""
    echo "  • GitHub: https://github.com/settings/tokens"
    echo "  • Notion: https://www.notion.so/my-integrations"
    echo "  • Linear: https://linear.app/settings/api"
    echo "  • Jira: https://id.atlassian.com/manage-profile/security/api-tokens"
    echo "  • Slack: https://api.slack.com/apps"
    echo "  • Discord: https://discord.com/developers/applications"
    echo ""
}

check_api_keys() {
    print_header "🔍 API Key Status Check"
    
    echo -e "${YELLOW}Checking environment for API keys...${NC}"
    echo ""
    
    # Primary AI Providers
    print_section "Primary AI Providers"
    check_key "OPENAI_API_KEY" "OpenAI (GPT)"
    check_key "ANTHROPIC_API_KEY" "Anthropic (Claude)"
    check_key "GOOGLE_API_KEY" "Google (Gemini)"
    check_key "XAI_API_KEY" "xAI (Grok)"
    check_key "DEEPSEEK_API_KEY" "DeepSeek"
    
    # Additional Providers
    print_section "Additional AI Providers"
    check_key "MISTRAL_API_KEY" "Mistral AI"
    check_key "COHERE_API_KEY" "Cohere"
    check_key "GROQ_API_KEY" "Groq"
    check_key "TOGETHER_API_KEY" "Together AI"
    check_key "OPENROUTER_API_KEY" "OpenRouter"
    check_key "PERPLEXITY_API_KEY" "Perplexity"
    check_key "HUGGINGFACE_API_KEY" "Hugging Face"
    
    # ChatGPT Agents
    print_section "ChatGPT Agents (Assistants)"
    check_key "OPENAI_ASSISTANT_ID_AIC" "Agent: AIC"
    check_key "OPENAI_ASSISTANT_ID_ARIA" "Agent: Aria"
    check_key "OPENAI_ASSISTANT_ID_SORA" "Agent: Sora"
    
    # Cloud Services
    print_section "Cloud Services"
    check_key "AZURE_OPENAI_API_KEY" "Azure OpenAI"
    check_key "MS_GRAPH_CLIENT_ID" "Microsoft Graph"
    check_key "GITHUB_TOKEN" "GitHub"
    
    # .env file status
    print_section "Configuration Files"
    if [ -f "$ENV_FILE" ]; then
        echo -e "  ${GREEN}✓${NC} .env file found at: $ENV_FILE"
    else
        echo -e "  ${YELLOW}⚠${NC} .env file not found at: $ENV_FILE"
    fi
    echo ""
}

check_key() {
    local key_name="$1"
    local display_name="$2"
    local value="${!key_name}"
    
    if [ -n "$value" ]; then
        # Mask the key for display
        local masked="${value:0:8}...${value: -4}"
        echo -e "  ${GREEN}✓${NC} ${display_name:0:25}$(printf '%*s' $((25-${#display_name})) '') ${GREEN}SET${NC} ($masked)"
    else
        echo -e "  ${RED}✗${NC} ${display_name:0:25}$(printf '%*s' $((25-${#display_name})) '') ${RED}NOT SET${NC}"
    fi
}

create_env_template() {
    print_header "📝 Creating .env Template"
    
    local template_file="$SCRIPT_DIR/.env.template"
    
    cat > "$template_file" << 'ENVTEMPLATE'
# =============================================================================
# OS Dashboard AI Assistant - Environment Configuration
# =============================================================================
# Copy this file to .env and fill in your API keys
# Get API keys from: cursor_ai --get-keys
# =============================================================================

# -----------------------------------------------------------------------------
# PRIMARY AI PROVIDERS
# -----------------------------------------------------------------------------

# OpenAI (GPT-4, GPT-4o, o1, ChatGPT Agents)
# Get key: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o
OPENAI_ORG_ID=

# Anthropic (Claude 3.5 Sonnet, Claude 4 Opus)
# Get key: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google (Gemini 2.0/2.5)
# Get key: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-2.5-flash

# xAI (Grok)
# Get key: https://console.x.ai/api-keys
XAI_API_KEY=xai-your-grok-key-here
XAI_MODEL=grok-beta

# DeepSeek (R1)
# Get key: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
DEEPSEEK_MODEL=deepseek-reasoner

# -----------------------------------------------------------------------------
# ADDITIONAL AI PROVIDERS
# -----------------------------------------------------------------------------

# Mistral AI
# Get key: https://console.mistral.ai/api-keys
MISTRAL_API_KEY=your-mistral-key-here

# Cohere
# Get key: https://dashboard.cohere.com/api-keys
COHERE_API_KEY=your-cohere-key-here

# Perplexity AI
# Get key: https://www.perplexity.ai/settings/api
PERPLEXITY_API_KEY=pplx-your-key-here

# Together AI
# Get key: https://api.together.xyz/settings/api-keys
TOGETHER_API_KEY=your-together-key-here

# OpenRouter (Access multiple models)
# Get key: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-your-key-here

# Groq (Fast inference)
# Get key: https://console.groq.com/keys
GROQ_API_KEY=gsk_your-groq-key-here

# Fireworks AI
# Get key: https://fireworks.ai/api-keys
FIREWORKS_API_KEY=your-fireworks-key-here

# Replicate
# Get key: https://replicate.com/account/api-tokens
REPLICATE_API_KEY=r8_your-replicate-key-here

# Hugging Face
# Get key: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=hf_your-hf-key-here

# -----------------------------------------------------------------------------
# CHATGPT AGENTS (OpenAI Assistants API)
# -----------------------------------------------------------------------------
# Create assistants at: https://platform.openai.com/assistants
# These are persistent agents with specialized roles

# Core Agents (AIC, Aria, Sora)
OPENAI_ASSISTANT_ID_AIC=asst_your-aic-assistant-id
OPENAI_ASSISTANT_ID_ARIA=asst_your-aria-assistant-id
OPENAI_ASSISTANT_ID_SORA=asst_your-sora-assistant-id

# Discipline Agents
OPENAI_ASSISTANT_ID_BIOLOGIST=asst_your-biologist-id
OPENAI_ASSISTANT_ID_CHEMIST=asst_your-chemist-id
OPENAI_ASSISTANT_ID_PHYSICIST=asst_your-physicist-id
OPENAI_ASSISTANT_ID_MATHEMATICIAN=asst_your-mathematician-id
OPENAI_ASSISTANT_ID_PHILOSOPHER=asst_your-philosopher-id
OPENAI_ASSISTANT_ID_THEOLOGIAN=asst_your-theologian-id
OPENAI_ASSISTANT_ID_ACCOUNTANT=asst_your-accountant-id
OPENAI_ASSISTANT_ID_ECONOMIST=asst_your-economist-id
OPENAI_ASSISTANT_ID_LAWYER=asst_your-lawyer-id

# -----------------------------------------------------------------------------
# AZURE OPENAI
# -----------------------------------------------------------------------------
# Portal: https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI

AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01

# -----------------------------------------------------------------------------
# MICROSOFT GRAPH API
# -----------------------------------------------------------------------------
# Register app: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

MS_GRAPH_CLIENT_ID=your-client-id
MS_GRAPH_TENANT_ID=common
MS_GRAPH_CLIENT_SECRET=your-client-secret

# -----------------------------------------------------------------------------
# GOOGLE CLOUD
# -----------------------------------------------------------------------------
# Console: https://console.cloud.google.com/apis/credentials

GOOGLE_CLIENT_SECRET_PATH=/path/to/client_secret.json
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json

# -----------------------------------------------------------------------------
# GITHUB
# -----------------------------------------------------------------------------
# Tokens: https://github.com/settings/tokens

GITHUB_TOKEN=ghp_your-github-token
GIT_USERNAME=your-github-username
GIT_EMAIL=your-email@example.com

# -----------------------------------------------------------------------------
# OPTIONAL INTEGRATIONS
# -----------------------------------------------------------------------------

# Adobe
ADOBE_CLIENT_ID=your-adobe-client-id
ADOBE_CLIENT_SECRET=your-adobe-secret

# Notion
NOTION_API_KEY=secret_your-notion-key

# Linear
LINEAR_API_KEY=lin_api_your-key

# Jira
JIRA_API_TOKEN=your-jira-token
JIRA_EMAIL=your-email@example.com
JIRA_DOMAIN=your-domain.atlassian.net

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/xxx
DISCORD_BOT_TOKEN=your-bot-token

# -----------------------------------------------------------------------------
# DISPLAY & UI SETTINGS
# -----------------------------------------------------------------------------

# X11 Display for GUI applications
DISPLAY=:0

# Terminal settings
TERM=xterm-256color

# -----------------------------------------------------------------------------
# AGENT SYSTEM SETTINGS
# -----------------------------------------------------------------------------

# Agent communication mode: direct, message_queue, shared_memory
AGENT_COMM_MODE=direct

# Agent workspace root
AGENT_WORKSPACE_ROOT=/workspace

# Enable agent file operations
AGENT_FILE_OPS_ENABLED=true

# Agent display access (for screen viewing)
AGENT_DISPLAY_ACCESS=true

# -----------------------------------------------------------------------------
# SECURITY & ENCRYPTION
# -----------------------------------------------------------------------------

SECRET_KEY=your-secret-key-for-encryption
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key

# -----------------------------------------------------------------------------
# MONITORING & LOGGING
# -----------------------------------------------------------------------------

LOG_LEVEL=INFO
SENTRY_DSN=
PROMETHEUS_PORT=9201

ENVTEMPLATE

    echo -e "${GREEN}✓${NC} Created .env template at: $template_file"
    echo ""
    echo "To use:"
    echo "  cp $template_file $ENV_FILE"
    echo "  # Edit .env and add your API keys"
    echo ""
}

setup_shell() {
    print_header "🔧 Setting Up Shell Integration"
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    if [ "$SHELL_NAME" = "zsh" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ "$SHELL_NAME" = "bash" ]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    echo "Detected shell: $SHELL_NAME"
    echo "Config file: $SHELL_RC"
    echo ""
    
    # Create aliases
    CURSOR_ALIAS="alias cursor_ai='python3 \"$CURSOR_AI_SCRIPT\"'"
    AGENTS_ALIAS="alias agents_ai='python3 \"$AGENTS_AI_SCRIPT\"'"
    
    # Add cursor_ai alias
    if grep -q "alias cursor_ai=" "$SHELL_RC" 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} cursor_ai alias already exists in $SHELL_RC"
    else
        echo "" >> "$SHELL_RC"
        echo "# Cursor AI commands" >> "$SHELL_RC"
        echo "$CURSOR_ALIAS" >> "$SHELL_RC"
        echo -e "${GREEN}✓${NC} Added cursor_ai alias to $SHELL_RC"
    fi
    
    # Add agents_ai alias
    if grep -q "alias agents_ai=" "$SHELL_RC" 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} agents_ai alias already exists in $SHELL_RC"
    else
        echo "$AGENTS_ALIAS" >> "$SHELL_RC"
        echo -e "${GREEN}✓${NC} Added agents_ai alias to $SHELL_RC"
    fi
    
    # Create local bin directory
    LOCAL_BIN="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN"
    
    # Create wrapper script for cursor_ai
    cat > "$LOCAL_BIN/cursor_ai" << EOF
#!/bin/bash
# Wrapper script for cursor_ai
exec python3 "$CURSOR_AI_SCRIPT" "\$@"
EOF
    chmod +x "$LOCAL_BIN/cursor_ai"
    
    # Create wrapper script for agents_ai
    cat > "$LOCAL_BIN/agents_ai" << EOF
#!/bin/bash
# Wrapper script for agents_ai
exec python3 "$AGENTS_AI_SCRIPT" "\$@"
EOF
    chmod +x "$LOCAL_BIN/agents_ai"
    
    echo -e "${GREEN}✓${NC} Created wrapper scripts in $LOCAL_BIN"
    
    # Check if local bin is in PATH
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        echo ""
        echo -e "${YELLOW}💡 Tip:${NC} Add $LOCAL_BIN to your PATH:"
        echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> $SHELL_RC"
    fi
    
    echo ""
    echo "Run: source $SHELL_RC"
    echo ""
}

install_dependencies() {
    print_header "📦 Installing Python Dependencies"
    
    echo "Installing required packages..."
    echo ""
    
    pip install --upgrade pip
    
    # Core AI packages
    pip install openai anthropic google-genai
    
    # Additional useful packages
    pip install python-dotenv rich prompt_toolkit
    
    # Optional: Install more providers if user wants
    read -p "Install additional AI providers (mistral, cohere, etc.)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install mistralai cohere together groq replicate huggingface_hub
    fi
    
    echo ""
    echo -e "${GREEN}✓${NC} Dependencies installed"
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

print_header "🤖 Cursor AI & Agents AI Setup"

# Parse arguments
case "${1:-}" in
    --keys|--get-keys|-k)
        show_api_links
        ;;
    --check|-c)
        # Load .env if exists
        if [ -f "$ENV_FILE" ]; then
            set -a
            source "$ENV_FILE"
            set +a
        fi
        check_api_keys
        ;;
    --template|-t)
        create_env_template
        ;;
    --install|-i)
        install_dependencies
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --keys, -k       Show API key links for all providers"
        echo "  --check, -c      Check which API keys are set"
        echo "  --template, -t   Create .env template file"
        echo "  --install, -i    Install Python dependencies"
        echo "  --help, -h       Show this help message"
        echo ""
        echo "Without options, runs full setup."
        ;;
    *)
        # Full setup
        show_api_links
        
        # Load .env if exists
        if [ -f "$ENV_FILE" ]; then
            set -a
            source "$ENV_FILE"
            set +a
        fi
        
        check_api_keys
        
        # Create template if .env doesn't exist
        if [ ! -f "$ENV_FILE" ]; then
            create_env_template
        fi
        
        setup_shell
        
        print_header "✅ Setup Complete!"
        echo "Available commands:"
        echo "  cursor_ai              # Interactive AI chat"
        echo "  cursor_ai --provider openai"
        echo "  cursor_ai --get-keys   # Show API key links"
        echo "  cursor_ai --check-keys # Check API key status"
        echo ""
        echo "  agents_ai              # Multi-agent system"
        echo "  agents_ai --list       # List available agents"
        echo "  agents_ai --agent aic  # Use specific agent"
        echo ""
        ;;
esac

