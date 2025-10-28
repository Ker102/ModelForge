# ModelForge - AI-Powered Blender Assistant

Transform your 3D workflow with AI-powered Blender automation. Create, modify, and enhance your Blender projects through natural conversation.

## 🚀 Project Overview

ModelForge is a comprehensive platform that brings AI capabilities to Blender through:
- **AI-Orchestrated Scene Builder** (Current focus): Gemini-driven planning + execution layer that decomposes complex requests, applies materials, and validates results in Blender.
- **Web Dashboard**: Authentication, project history, asset integration toggles, orchestration insights.
- **Desktop Application**: Electron wrapper over the web dashboard for native MCP connectivity.
- **Blender MCP Server** (External): Socket bridge that executes generated Python inside Blender.

## ✅ Current Capabilities
- Gemini 2.x orchestration with a ReAct-style planner, per-step validation, and fallback heuristics for common Blender tasks.
- Post-plan review cards inside the chat UI showing component checklists, asset usage, and material assignments.
- Automatic scene audits that ensure lighting, camera, and base materials exist (with corrective scripts when missing).
- Per-project toggles for Hyper3D Rodin and Sketchfab assets so AI calls respect a user’s configured API keys.
- Shared conversation history, project management, and usage tracking across the web and desktop experiences.

## 📋 Phase 1 - Marketing Website (Current)

This repository contains the Next.js 14 marketing website and user platform.

### Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js v5
- **Payments**: Stripe
- **UI**: Tailwind CSS + shadcn/ui
- **Deployment**: DigitalOcean App Platform

## 🛠️ Local Development Setup

### Prerequisites

- Node.js 18+ 
- PostgreSQL 14+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd BlenderAI
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your values:
   ```env
   # Database
   DATABASE_URL="postgresql://user:password@localhost:5432/modelforge"

   # NextAuth
   NEXTAUTH_URL="http://localhost:3000"
   NEXTAUTH_SECRET="<run: openssl rand -base64 32>"

   # Stripe (get from https://dashboard.stripe.com)
   STRIPE_SECRET_KEY="sk_test_..."
   STRIPE_WEBHOOK_SECRET="whsec_..."
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."

   # Stripe Price IDs (create products in Stripe Dashboard)
   STRIPE_STARTER_MONTHLY_PRICE_ID="price_..."
   STRIPE_STARTER_YEARLY_PRICE_ID="price_..."
   STRIPE_PRO_MONTHLY_PRICE_ID="price_..."
   STRIPE_PRO_YEARLY_PRICE_ID="price_..."

   # LLM Provider
   GEMINI_API_KEY="your-gemini-api-key"

   # Blender MCP bridge
   BLENDER_MCP_HOST="127.0.0.1"
   BLENDER_MCP_PORT="9876"
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb modelforge

   # Or using psql
   psql -U postgres
   CREATE DATABASE modelforge;
   ```

5. **Enable pgvector extension**
   ```bash
   psql -U postgres -d modelforge
   CREATE EXTENSION IF NOT EXISTS vector;
   \q
   ```

6. **Run database migrations**
   ```bash
   npm run db:generate
   npm run db:push
   ```

7. **Start development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

8. **Seed a local Pro test user** (optional but handy for QA)
   ```bash
   npm run test:user
   ```
   This creates `test@modelforge.dev` / `TestPass123!` with an active subscription.

## 🔧 Asset Integrations & MCP Settings

Configure external asset providers on a per-project basis from the dashboard. Poly Haven is **enabled by default** (no API keys required) so users can browse HDRIs, textures, and models immediately. Hyper3D Rodin and Sketchfab remain **disabled by default** to prevent accidental API calls—enable them only after valid credentials are entered inside the Blender add-on sidebar.

Environment variables:
- `BLENDER_MCP_HOST` / `BLENDER_MCP_PORT` – MCP socket target (defaults to `127.0.0.1:9876`).
- `MODELFORGE_DESKTOP_START_URL` – entry point for the Electron shell.

In Blender, launch the MCP server with `uvx blender-mcp` and keep only **one** MCP client running (Cursor, Claude, or ModelForge) to avoid port conflicts.

## 🤖 Local LLM Mode

Free-tier accounts run entirely on a locally hosted LLM. Configure yours from **Dashboard → Settings → Local LLM Configuration**.

Supported providers:

- **Ollama** – Lightweight local runtime. After installing, run `ollama serve` and pull a model (e.g. `ollama pull llama3.1`). Default base URL: `http://localhost:11434`.
- **LM Studio** – Desktop UI with an OpenAI-compatible server. Enable the server in the app, copy the base URL (usually `http://localhost:1234`), and paste it into ModelForge. Provide the API key only if you enabled authentication inside LM Studio.

Workflow:

1. Open **Settings → Local LLM Configuration**.
2. Pick your provider, base URL, and model name exactly as exposed by Ollama/LM Studio (e.g. `llama3.1` or `Meta-Llama-3-8B-Instruct`).
3. Click **Test connection** to verify the server responds.
4. Save the configuration. Free-tier users must keep a local provider active; Pro subscribers can switch between hosted Gemini and their local model per request.

ModelForge only proxies your request metadata; local responses never leave your machine. Clearing the form removes any stored API key.

## 📊 Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts with authentication and subscription info
- **projects**: User projects linked to Blender work
- **conversations**: AI conversation history per project
- **messages**: Individual messages in conversations
- **project_snapshots**: Scene state for context memory
- **subscription_plans**: Available pricing tiers
- **usage_logs**: Track API usage for billing

View the complete schema in `prisma/schema.prisma`.

## 🔐 Authentication

The app uses NextAuth.js v5 with credentials provider:

- **Sign up**: `/signup` - Create new account
- **Login**: `/login` - Authenticate existing user
- **Protected routes**: Dashboard and settings require authentication

### Google OAuth

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials), create an OAuth client ID (type **Web application**).
2. Add these URIs:
   - **Authorized JavaScript origins**: `http://localhost:3000` (plus your production origin when ready)
   - **Authorized redirect URIs**: `http://localhost:3000/api/auth/callback/google` (plus the production callback)
3. Copy the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` into your `.env`.
4. Restart `npm run dev` (and the desktop shell) so NextAuth picks up the new credentials.

Passwords are hashed using bcryptjs with 10 salt rounds.

## 💳 Stripe Integration

### Setting Up Stripe

1. **Create a Stripe account**: https://dashboard.stripe.com/register

2. **Get your API keys**:
   - Go to Developers → API keys
   - Copy Secret key to `STRIPE_SECRET_KEY`
   - Copy Publishable key to `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

3. **Create Products and Prices**:
   ```
   Products:
   - ModelForge Starter (Monthly: $12, Yearly: $99)
   - ModelForge Pro (Monthly: $29, Yearly: $249)
   ```
   Copy the price IDs to your `.env` file.

4. **Set up webhooks**:
   - Go to Developers → Webhooks
   - Add endpoint: `https://your-domain.com/api/webhooks/stripe`
   - Select events:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `checkout.session.completed`
   - Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

### Testing Webhooks Locally

Use Stripe CLI to forward webhooks to localhost:

```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

## 🎨 UI Components

The app uses shadcn/ui components with Tailwind CSS. Add new components:

```bash
npx shadcn-ui@latest add <component-name>
```

All UI components are in `/components/ui/`.

## 📁 Project Structure

```
/
├── app/                      # Next.js 14 app directory
│   ├── (auth)/              # Auth route group
│   │   ├── login/
│   │   └── signup/
│   ├── dashboard/           # Protected dashboard
│   │   ├── projects/[id]/
│   │   └── settings/
│   ├── api/                 # API routes
│   │   ├── auth/
│   │   ├── projects/
│   │   ├── user/
│   │   └── webhooks/
│   ├── docs/
│   ├── download/
│   └── page.tsx             # Homepage
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── landing/             # Landing page sections
│   ├── dashboard/           # Dashboard components
│   └── auth/                # Auth forms
├── lib/                     # Utility libraries
│   ├── auth.ts             # NextAuth config
│   ├── db.ts               # Prisma client
│   ├── stripe.ts           # Stripe client
│   └── utils.ts            # Helper functions
├── prisma/
│   └── schema.prisma       # Database schema
└── public/                  # Static assets
```

## 🚀 Deployment to DigitalOcean

### 1. Set up Managed PostgreSQL Database

1. Create a new managed PostgreSQL database in DigitalOcean
2. Enable pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy the connection string to your environment variables

### 2. Deploy App Platform

1. Connect your GitHub repository
2. Configure build settings:
   - **Build Command**: `npm run build`
   - **Run Command**: `npm start`
3. Add environment variables (same as `.env`)
4. Deploy!

### 3. Post-Deployment

1. Run migrations:
   ```bash
   npm run db:migrate
   ```

2. Test Stripe webhooks with your production URL

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
```

## 🔒 Security Best Practices

- ✅ No secrets committed to Git
- ✅ Environment variables for all sensitive data
- ✅ Stripe webhook signature verification
- ✅ Password hashing with bcryptjs
- ✅ Protected API routes with authentication
- ✅ CSRF protection via NextAuth
- ✅ SQL injection prevention (Prisma)

## 💰 Subscription Tiers

### Free Tier
- 5 AI requests per day
- 1 active project
- Basic MCP commands
- Community support

### Starter ($12/month or $99/year)
- 500 AI requests per month
- 10 active projects
- All MCP commands
- Viewport analysis
- Email support
- Export project history

### Pro ($29/month or $249/year)
- Unlimited AI requests
- Unlimited projects
- Priority model access
- Advanced viewport analysis
- Asset library integration
- Priority support
- API access
- Team collaboration (coming soon)

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U postgres -d modelforge -c "SELECT version();"

# Check if pgvector is installed
psql -U postgres -d modelforge -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Prisma Issues

```bash
# Reset database (WARNING: deletes all data)
npm run db:push -- --force-reset

# Regenerate Prisma client
npm run db:generate
```

### Stripe Webhook Issues

- Ensure webhook endpoint is publicly accessible
- Verify webhook secret matches Stripe dashboard
- Check webhook event types are selected
- Use Stripe CLI for local testing

## 🧠 Orchestration Layer

ModelForge’s orchestration stack lives in `lib/orchestration/` and includes:

- **Planner (`planner.ts`)** – Generates a component-level plan with material guidelines, object counts, and asset restrictions (Hyper3D/Sketchfab). Plans are rejected unless they meet minimum complexity and material requirements, and malformed responses trigger structured retries.
- **Executor (`executor.ts`)** – Executes each MCP command, validates object creation, and audits the final scene. Missing lighting/camera/materials are auto-added as fallbacks, and audit failures feed a recovery prompt before completion.
- **Heuristics (`buildCommandStubs` in API)** – Provide guardrail scripts (e.g., car scaffold, door fixer) when Gemini needs extra help or a recovery path.
- **Telemetry (`monitor.ts`)** – Every request writes NDJSON lines to `logs/orchestration.ndjson`. Summaries can be generated with `npm run analyze:orchestration`.
- **UI surfacing** – Plan summaries, component checklists, and execution logs render beside the chat so users can review what happened and retry specific steps.

The chat UI shows plan summaries, component checklists, and execution results so users understand what occurred.

## 🧩 Blender MCP Integration

ModelForge connects to Blender through the open-source [blender-mcp](https://github.com/ahujasid/blender-mcp) project. A copy of the upstream README is available at `blendermcpreadme.md` for offline reference.

Key steps:

1. **Install prerequisites**:
   - Blender ≥ 3.0 (download from [blender.org](https://www.blender.org/download/))
   - Python ≥ 3.10 (via package manager, Homebrew, or [python.org](https://www.python.org/downloads/))
   - Git ([git-scm.com](https://git-scm.com/downloads))
   - [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (see instructions below)
2. **Install the Blender addon**: Either download it directly from this project at [`/downloads/blender-mcp-addon.py`](/downloads/blender-mcp-addon.py) or clone the upstream repo and use the bundled `addon.py`. Install it via Blender → Preferences → Add-ons → Install.
3. **Configure the MCP server**:
   - Environment variables (already covered in `.env.example`):
     - `BLENDER_MCP_HOST` (defaults to `127.0.0.1`)
     - `BLENDER_MCP_PORT` (defaults to `9876`)
   - Start the MCP server with `uvx blender-mcp` (per upstream docs).
4. **Connect ModelForge**: The web and desktop clients will read the host/port from environment variables and route MCP commands through the shared client in `lib/mcp`.

> ⚠️ Only run **one** MCP instance at a time (Cursor, Claude, or ModelForge) to avoid port conflicts.

Consult `blendermcpreadme.md` for detailed screenshots, IDE integrations, and troubleshooting tips.

### Install `uv`

The Blender MCP server is distributed via the [`uv`](https://docs.astral.sh/uv) package manager. Install it once per machine:

- **Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Then add `~/.cargo/bin` (or the path printed by the installer) to your `PATH`.
- **macOS** (Homebrew):
  ```bash
  brew install uv
  ```
  or use the same curl script as Linux.
- **Windows** (PowerShell):
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  Afterwards, ensure `%USERPROFILE%\.local\bin` is in your `PATH`.

Git is only required if you prefer cloning the upstream repository instead of using the direct download.

You only need to install `uv` once. After that, run the MCP server with:

```bash
uvx blender-mcp
```

### Local test account

Need a Pro-tier account for QA? Seed one with:

```bash
npm run test:user
```

This creates (or updates) `test@modelforge.dev` with password `TestPass123!`. Override credentials via `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`, and `TEST_USER_NAME` environment variables when running the script.

## 🖥️ Desktop App (Electron)

A lightweight Electron shell lives in the `desktop/` folder. It wraps the Next.js web UI and exposes native integrations (MCP configuration bridge, future filesystem access, etc.).

### Run in development

```bash
# Terminal 1
npm run dev

# Terminal 2
cd desktop
npm install   # first run only (requires internet access)
npm run dev
```

The desktop window loads `MODELFORGE_DESKTOP_START_URL` (defaults to `http://localhost:3000/dashboard`). MCP host/port values are read from the same `.env` file used by the web app, keeping configuration in one place.

## 🔄 Next Steps

- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] MCP orchestration logging + analyzer script
- [ ] Persist conversation memory with vector embeddings
- [ ] Viewport screenshot analysis & critiques
- [ ] Production packaging for the desktop app

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js Documentation](https://next-auth.js.org)
- [Stripe Documentation](https://stripe.com/docs)
- [Blender MCP Server](https://github.com/ahujasid/blender-mcp)

## 📄 License

[Your License Here]

## 🤝 Contributing

We welcome pull requests! Read [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, coding standards, and testing steps. Use the GitHub issue templates when reporting bugs or proposing enhancements.

## 📧 Support

For questions or issues:
- Check the [documentation](/docs)
- Open a GitHub issue
- Contact support@modelforge.ai (if applicable)

---

Built with ❤️ using Next.js, PostgreSQL, and Stripe
