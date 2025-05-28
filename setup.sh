#!/bin/bash

echo "🎯 Vibe Project Setup Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js found: $(node -v)${NC}"

# Function to create .env file from example
create_env_file() {
    local dir=$1
    local server_name=$2
    
    if [ -f "$dir/.env.example" ]; then
        if [ ! -f "$dir/.env" ]; then
            cp "$dir/.env.example" "$dir/.env"
            echo -e "${YELLOW}📝 Created .env file for $server_name. Please edit $dir/.env with your credentials.${NC}"
        else
            echo -e "${GREEN}✅ .env file already exists for $server_name${NC}"
        fi
    fi
}

# Install dependencies
echo ""
echo "📦 Installing dependencies..."

# Root dependencies
echo "Installing root dependencies..."
npm install

# Install MCP server dependencies
servers=(
    "figma-mcp-server"
    "github-mcp-server"
    "supabase-mcp-server"
    "dashboard-mcp-server"
    "taskmanager-mcp-server"
    "context7-mcp-server"
)

for server in "${servers[@]}"; do
    if [ -d "$server" ]; then
        echo ""
        echo "Installing dependencies for $server..."
        cd "$server"
        npm install
        cd ..
        
        # Create .env files
        create_env_file "$server" "$server"
    fi
done

echo ""
echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p workflows
mkdir -p figma-components
mkdir -p src/components/generated

echo -e "${GREEN}✅ Directories created!${NC}"

# Environment setup instructions
echo ""
echo "🔧 Environment Setup Required:"
echo "=============================="
echo ""
echo "Please configure the following .env files with your credentials:"
echo ""
echo "1. ${YELLOW}figma-mcp-server/.env${NC}"
echo "   - FIGMA_TOKEN: Get from https://www.figma.com/developers/api#access-tokens"
echo "   - FIGMA_FILE_KEY: Extract from your Figma file URL"
echo ""
echo "2. ${YELLOW}github-mcp-server/.env${NC}"
echo "   - GITHUB_TOKEN: Get from https://github.com/settings/tokens"
echo "   - Required scopes: repo, workflow"
echo ""
echo "3. ${YELLOW}supabase-mcp-server/.env${NC}"
echo "   - SUPABASE_URL: Your Supabase project URL"
echo "   - SUPABASE_ANON_KEY: Your Supabase anon key"
echo ""
echo "4. ${YELLOW}dashboard-mcp-server/.env${NC} (optional)"
echo "   - WS_PORT: WebSocket port (default: 3001)"
echo ""

# Test script
echo ""
echo "🧪 To test the setup, run:"
echo "   ${GREEN}npm run test:integration${NC}"
echo ""
echo "🚀 To start the development server:"
echo "   ${GREEN}npm run dev${NC}"
echo ""
echo "📊 To start the dashboard WebSocket server:"
echo "   ${GREEN}cd dashboard-mcp-server && npm start${NC}"
echo ""
echo "✨ Setup complete! Happy coding!"