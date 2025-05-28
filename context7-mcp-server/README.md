# Context7 MCP Server

Context7 integration MCP Server for enhanced context management.

## Features

- **context7_search**: Search for relevant context in Context7
- **context7_create**: Create new context entries
- **context7_update**: Update existing context entries
- **context7_get**: Retrieve specific context by ID
- **context7_delete**: Delete context entries
- **context7_link**: Create relationships between contexts

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your Context7 API key
```

3. Run the server:
```bash
npm start
```

## Configuration

Create a `.env` file with the following variables:

```env
CONTEXT7_API_KEY=your_context7_api_key_here
CONTEXT7_BASE_URL=https://api.context7.com  # Optional, defaults to https://api.context7.com
```

## Usage

### Search Context
```json
{
  "tool": "context7_search",
  "arguments": {
    "query": "search term",
    "filters": {
      "type": "note",
      "tags": ["important"],
      "date_from": "2024-01-01",
      "date_to": "2024-12-31"
    }
  }
}
```

### Create Context
```json
{
  "tool": "context7_create",
  "arguments": {
    "title": "My Context",
    "content": "Context content here",
    "type": "note",
    "tags": ["tag1", "tag2"],
    "metadata": {
      "custom": "data"
    }
  }
}
```

### Update Context
```json
{
  "tool": "context7_update",
  "arguments": {
    "id": "context-id",
    "updates": {
      "title": "Updated Title",
      "content": "Updated content",
      "tags": ["new-tag"]
    }
  }
}
```

### Get Context
```json
{
  "tool": "context7_get",
  "arguments": {
    "id": "context-id"
  }
}
```

### Delete Context
```json
{
  "tool": "context7_delete",
  "arguments": {
    "id": "context-id"
  }
}
```

### Link Contexts
```json
{
  "tool": "context7_link",
  "arguments": {
    "source_id": "source-context-id",
    "target_id": "target-context-id",
    "relationship": "related"
  }
}
```

## Development

Run in development mode with auto-reload:
```bash
npm run dev
```

Run tests:
```bash
npm test
```

## Integration

This MCP server is designed to work with the master orchestrator and other MCP servers in the VIBE project ecosystem.