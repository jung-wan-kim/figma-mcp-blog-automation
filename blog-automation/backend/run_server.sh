#!/bin/bash
cd /Users/jung-wankim/Project/figma-mcp-blog-automation/blog-automation/backend
echo "Starting backend server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000