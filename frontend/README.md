# Kubernetes Agent Dashboard Frontend

A React-based dashboard for monitoring and interacting with AI-powered Kubernetes agents.

## Prerequisites

You'll need Node.js and npm installed. Here are a few options:

### Option 1: Install via Homebrew (Recommended for macOS)
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js and npm
brew install node
```

### Option 2: Install via Node Version Manager (nvm)
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart your terminal or run:
source ~/.zshrc

# Install and use the latest LTS version of Node.js
nvm install --lts
nvm use --lts
```

### Option 3: Download from Official Website
Visit [nodejs.org](https://nodejs.org/) and download the LTS version for macOS.

## Getting Started

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   The app will automatically open at `http://localhost:3000`

## Features

- **Cluster Overview**: Real-time metrics for nodes, pods, and agents
- **AI Agent Monitoring**: Status and current tasks of AI agents
- **Event Stream**: Recent cluster events and activities
- **Chat Interface**: Interactive chat with AI-powered infrastructure assistant
- **Responsive Design**: Works on desktop and mobile devices

## Current Status

- ✅ Single-page React application
- ✅ Mock data for immediate testing
- ✅ Responsive Tailwind CSS styling
- ✅ Interactive chat interface
- 🔄 Backend integration (planned)
- 🔄 Real-time WebSocket connection (planned)
- 🔄 k8sgpt integration (planned)

## Development

The frontend is designed to be easily extensible. When you're ready to add more functionality:

1. **Add real backend integration** by uncommenting WebSocket code
2. **Break into components** for better organization
3. **Add more dashboard widgets** as needed
4. **Integrate with FastAPI backend** for real k8sgpt data

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/     # (Future component organization)
│   ├── contexts/       # (Future state management)
│   ├── App.js         # Main application component
│   ├── index.js       # React entry point
│   └── index.css      # Tailwind CSS styles
├── package.json       # Dependencies and scripts
└── README.md         # This file
```

## Next Steps

1. Install Node.js using one of the methods above
2. Run `npm install` to install dependencies
3. Run `npm start` to start the development server
4. Open `http://localhost:3000` to view the dashboard

The dashboard will show mock data initially. Later, we can connect it to the FastAPI backend for real Kubernetes data and k8sgpt integration.
