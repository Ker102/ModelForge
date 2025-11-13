<div align="center">

# 🔨 ModelForge

**AI-Powered Blender Assistant**

Transform your 3D workflow with AI-powered Blender automation. Create, modify, and enhance your Blender projects through natural conversation.

[![GitHub release](https://img.shields.io/github/v/release/Ker102/ModelForge?include_prereleases&style=flat-square)](https://github.com/Ker102/ModelForge/releases)
[![License](https://img.shields.io/github/license/Ker102/ModelForge?style=flat-square)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

[![GitHub issues](https://img.shields.io/github/issues/Ker102/ModelForge?style=flat-square)](https://github.com/Ker102/ModelForge/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Ker102/ModelForge?style=flat-square)](https://github.com/Ker102/ModelForge/pulls)
[![GitHub stars](https://img.shields.io/github/stars/Ker102/ModelForge?style=flat-square)](https://github.com/Ker102/ModelForge/stargazers)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing) • [Support](#-support)

</div>

---

## 🚀 Features

ModelForge is a comprehensive platform that brings AI capabilities to Blender through four integrated components:

### 🎨 AI-Orchestrated Scene Builder
- **Gemini 2.x Orchestration**: ReAct-style planner with per-step validation and fallback heuristics
- **Smart Material Application**: Automatic material assignment and validation
- **Scene Auditing**: Ensures lighting, camera, and base materials exist with auto-correction
- **Component Tracking**: Post-plan review cards with checklists, asset usage, and material assignments

### 🌐 Web Dashboard
- **User Authentication**: Secure NextAuth.js v5 authentication with Google OAuth support
- **Project Management**: Organize and track multiple Blender projects
- **Asset Integration Toggles**: Per-project controls for Hyper3D Rodin and Sketchfab
- **Conversation History**: Persistent chat history across web and desktop

### 🖥️ Desktop Application
- **Native MCP Connectivity**: Electron wrapper for seamless Blender integration
- **Unified Experience**: Same features as web dashboard with native performance
- **Configuration Bridge**: Simplified MCP server setup

### 🔌 Blender MCP Server Integration
- **Socket Bridge**: Executes generated Python directly in Blender
- **Real-time Communication**: Live feedback from Blender operations
- **External Integration**: Works with the open-source [blender-mcp](https://github.com/ahujasid/blender-mcp) project

## 🛠️ Technology Stack

<table>
<tr>
<td><b>Frontend</b></td>
<td>

![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css)

</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>

![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=node.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql)
![Prisma](https://img.shields.io/badge/Prisma-5.20-2D3748?style=flat-square&logo=prisma)

</td>
</tr>
<tr>
<td><b>Authentication</b></td>
<td>

![NextAuth.js](https://img.shields.io/badge/NextAuth.js-v5-000000?style=flat-square)

</td>
</tr>
<tr>
<td><b>UI Components</b></td>
<td>

![shadcn/ui](https://img.shields.io/badge/shadcn/ui-latest-000000?style=flat-square)
![Radix UI](https://img.shields.io/badge/Radix_UI-latest-111111?style=flat-square)

</td>
</tr>
<tr>
<td><b>Desktop</b></td>
<td>

![Electron](https://img.shields.io/badge/Electron-latest-47848F?style=flat-square&logo=electron)

</td>
</tr>
<tr>
<td><b>AI Integration</b></td>
<td>

![Google Gemini](https://img.shields.io/badge/Gemini_2.x-API-4285F4?style=flat-square&logo=google)

</td>
</tr>
</table>

## 📋 Quick Start

### Prerequisites

- Node.js 18+ 
- PostgreSQL 14+
- Blender 3.0+ (for MCP integration)
- Python 3.10+ (for Blender MCP server)
- [`uv`](https://docs.astral.sh/uv) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ker102/ModelForge.git
   cd ModelForge
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure:
   ```env
   # Database
   DATABASE_URL="postgresql://user:password@localhost:5432/modelforge"

   # NextAuth
   NEXTAUTH_URL="http://localhost:3000"
   NEXTAUTH_SECRET="<run: openssl rand -base64 32>"

   # LLM Provider
   GEMINI_API_KEY="your-gemini-api-key"

   # Blender MCP bridge
   BLENDER_MCP_HOST="127.0.0.1"
   BLENDER_MCP_PORT="9876"
   ```

4. **Set up PostgreSQL database**
   ```bash
   createdb modelforge
   psql -U postgres -d modelforge -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

5. **Run database migrations**
   ```bash
   npm run db:generate
   npm run db:push
   ```

6. **Start development server**
   ```bash
   npm run dev
   ```

7. **Open [http://localhost:3000](http://localhost:3000)** in your browser

### Optional: Create Test User

```bash
npm run test:user
```

This creates `test@modelforge.dev` / `TestPass123!` with an active subscription.

## 🔧 Configuration

### Asset Integrations

Configure external asset providers on a per-project basis:

- **Poly Haven**: Enabled by default (no API keys required)
- **Hyper3D Rodin**: Disabled by default (requires API credentials)
- **Sketchfab**: Disabled by default (requires API credentials)

Environment variables:
- `BLENDER_MCP_HOST` / `BLENDER_MCP_PORT` – MCP socket target (defaults to `127.0.0.1:9876`)
- `MODELFORGE_DESKTOP_START_URL` – Entry point for Electron shell

### Local LLM Mode

Free-tier accounts can use locally hosted LLMs:

**Supported Providers:**
- **Ollama**: Lightweight local runtime
- **LM Studio**: Desktop UI with OpenAI-compatible server

**Setup:**
1. Open **Settings → Local LLM Configuration**
2. Select your provider and enter base URL
3. Test connection and save

### Google OAuth Setup

1. Create OAuth client ID in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Add authorized redirect URIs:
   - Development: `http://localhost:3000/api/auth/callback/google`
   - Production: `https://your-domain.com/api/auth/callback/google`
3. Add credentials to `.env`:
   ```env
   GOOGLE_CLIENT_ID="your-client-id"
   GOOGLE_CLIENT_SECRET="your-client-secret"
   ```

### Optional: Web Research (Firecrawl)

Enable Firecrawl for web research capabilities:

1. Set `FIRECRAWL_API_KEY` in `.env.local`
2. Restart development server
3. Enable per-project in dashboard

## 🤖 Blender MCP Integration

ModelForge connects to Blender through the [blender-mcp](https://github.com/ahujasid/blender-mcp) project.

### Setup

1. **Install `uv` package manager**:
   ```bash
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # macOS (Homebrew)
   brew install uv
   
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install Blender addon**:
   - Download from `/downloads/blender-mcp-addon.py`
   - Install via Blender → Preferences → Add-ons → Install

3. **Start MCP server**:
   ```bash
   uvx blender-mcp
   ```

4. **Connect ModelForge**: The web and desktop clients automatically connect using configured host/port

> ⚠️ Only run **one** MCP instance at a time (Cursor, Claude, or ModelForge) to avoid port conflicts.

## 📊 Database Schema

Main tables:

- **users**: User accounts and authentication
- **projects**: Blender projects
- **conversations**: AI conversation history
- **messages**: Individual chat messages
- **project_snapshots**: Scene state snapshots
- **subscription_plans**: Pricing tiers
- **usage_logs**: API usage tracking

View complete schema in `prisma/schema.prisma`.

## 🔐 Authentication

NextAuth.js v5 with multiple providers:

- **Credentials**: Email/password authentication
- **Google OAuth**: Social login
- **Protected Routes**: Dashboard and settings require authentication

Passwords are hashed using bcryptjs with 10 salt rounds.

## 🧠 Orchestration Layer

The orchestration system in `lib/orchestration/` includes:

- **Planner** (`planner.ts`): Component-level plan generation with material guidelines
- **Executor** (`executor.ts`): MCP command execution with validation
- **Heuristics**: Guardrail scripts for common scenarios
- **Telemetry** (`monitor.ts`): Logging to `logs/orchestration.ndjson`
- **UI Integration**: Plan summaries and execution results in chat

## 🖥️ Desktop Application

Electron wrapper in the `desktop/` folder:

```bash
# Terminal 1: Web app
npm run dev

# Terminal 2: Desktop app
cd desktop
npm install  # first run only
npm run dev
```

The desktop app loads `MODELFORGE_DESKTOP_START_URL` (defaults to `http://localhost:3000/dashboard`).

## 📁 Project Structure

```
ModelForge/
├── app/                    # Next.js app directory
│   ├── (auth)/            # Auth routes (login, signup)
│   ├── api/               # API routes
│   ├── dashboard/         # Protected dashboard
│   └── page.tsx           # Homepage
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── landing/          # Landing page sections
│   ├── dashboard/        # Dashboard components
│   └── auth/             # Auth forms
├── lib/                   # Utility libraries
│   ├── orchestration/    # AI orchestration logic
│   ├── mcp/              # MCP client
│   ├── auth.ts           # NextAuth config
│   ├── db.ts             # Prisma client
│   └── utils.ts          # Helper functions
├── prisma/               # Database schema
├── desktop/              # Electron application
├── public/               # Static assets
├── scripts/              # Build and utility scripts
└── .github/              # GitHub templates and workflows
```

## 📝 Available Scripts

```bash
# Development
npm run dev              # Start dev server
npm run build           # Build for production
npm run start           # Start production server
npm run lint            # Run ESLint

# Database
npm run db:generate     # Generate Prisma client
npm run db:push         # Push schema to database
npm run db:migrate      # Run migrations
npm run db:studio       # Open Prisma Studio

# Testing & Analysis
npm run test:user       # Create test user
npm run analyze:orchestration  # Analyze orchestration logs
```

## 🔒 Security

ModelForge implements enterprise-grade security:

- ✅ No secrets in Git
- ✅ Environment variable isolation
- ✅ Password hashing (bcryptjs)
- ✅ Protected API routes
- ✅ CSRF protection (NextAuth)
- ✅ SQL injection prevention (Prisma)
- ✅ Dependency scanning (Dependabot)
- ✅ Code scanning (CodeQL)

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## 💰 Subscription Tiers

### Free Tier
- 5 AI requests per day
- 1 active project
- Basic MCP commands
- Community support

### Starter ($12/month or $99/year)
- 500 orchestrated requests/month
- 10 active projects
- All MCP commands
- Viewport analysis
- Email support

### Pro ($29/month or $249/year)
- Unlimited requests
- Unlimited projects
- Priority model access
- Asset library integration
- Priority support
- API access

## 🐛 Troubleshooting

### Database Connection

```bash
# Test PostgreSQL
psql -U postgres -d modelforge -c "SELECT version();"

# Verify pgvector
psql -U postgres -d modelforge -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Prisma Issues

```bash
# Reset database (WARNING: deletes all data)
npm run db:push -- --force-reset

# Regenerate client
npm run db:generate
```

## 🔄 Roadmap

- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] MCP orchestration logging
- [ ] Conversation memory with vector embeddings
- [ ] Viewport screenshot analysis
- [ ] Production desktop app packaging
- [ ] Team collaboration features

## 📚 Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Setup Guide](SETUP.md)
- [Blender MCP README](blendermcpreadme.md)
- [Orchestration Details](gemini-blender-orchestration.md)

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to your fork (`git push origin feat/amazing-feature`)
7. Open a Pull Request

See the [issue templates](.github/ISSUE_TEMPLATE) for reporting bugs or requesting features.

## 📧 Support

- 📖 [Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/Ker102/ModelForge/discussions)
- 🐛 [Report a Bug](https://github.com/Ker102/ModelForge/issues/new?template=bug_report.md)
- 💡 [Request a Feature](https://github.com/Ker102/ModelForge/issues/new?template=feature_request.md)

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - The React Framework
- [Blender MCP](https://github.com/ahujasid/blender-mcp) - Blender integration
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Prisma](https://www.prisma.io/) - Next-generation ORM
- [Google Gemini](https://ai.google.dev/) - AI orchestration

## ⭐ Star History

If you find ModelForge useful, please consider starring the repository!

[![Star History Chart](https://api.star-history.com/svg?repos=Ker102/ModelForge&type=Date)](https://star-history.com/#Ker102/ModelForge&Date)

---

<div align="center">

Built with ❤️ by the ModelForge community

[Website](#) • [Documentation](README.md) • [Discord](#) • [Twitter](#)

</div>
