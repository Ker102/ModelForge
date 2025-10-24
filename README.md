# ModelForge - AI-Powered Blender Assistant

Transform your 3D workflow with AI-powered Blender automation. Create, modify, and enhance your Blender projects through natural conversation.

## 🚀 Project Overview

ModelForge is a comprehensive platform that brings AI capabilities to Blender through:
- **Marketing Website** (Phase 1 - Current): User authentication, project management, subscription handling
- **Desktop Application** (Phase 2 - Coming Soon): AI chat interface with MCP integration
- **Blender MCP Server** (External): Connects Blender to ModelForge

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

## 🔄 Next Steps (Phase 2)

- [x] Build Gemini-backed AI chat with streaming responses
- [x] Scaffold MCP command planning stubs
- [x] Build Electron desktop application shell
- [ ] Implement production MCP client execution
- [ ] Persist conversation memory with vector embeddings
- [ ] Add viewport screenshot analysis
- [ ] Deliver real-time Blender command execution

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js Documentation](https://next-auth.js.org)
- [Stripe Documentation](https://stripe.com/docs)
- [Blender MCP Server](https://github.com/ahujasid/blender-mcp)

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📧 Support

For questions or issues:
- Check the [documentation](/docs)
- Open a GitHub issue
- Contact support@modelforge.ai (if applicable)

---

Built with ❤️ using Next.js, PostgreSQL, and Stripe
