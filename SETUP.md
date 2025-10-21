# ModelForge - Quick Setup Guide

## Prerequisites

Before you start, make sure you have:
- Node.js 18+ installed
- PostgreSQL 14+ installed and running
- A Stripe account (for payment integration)
- Git for version control

## Local Development Setup

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example
cp .env.example .env
```

Then edit `.env` and fill in these values:

```env
# Database - Update with your PostgreSQL credentials
DATABASE_URL="postgresql://user:password@localhost:5432/modelforge"

# NextAuth - Your local URL and a random secret
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="<run: openssl rand -base64 32>"

# Stripe - Get from https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."

# Stripe Price IDs - Create products in Stripe Dashboard
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

### 2. Database Setup

```bash
# Create the database
createdb modelforge

# Or using psql
psql -U postgres
CREATE DATABASE modelforge;

# Enable pgvector extension
psql -U postgres -d modelforge
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Initialize the Project

```bash
# Install dependencies
npm install

# Generate Prisma client
npm run db:generate

# Push database schema (for development)
npm run db:push

# Or run migrations (for production)
npm run db:migrate
```

### 4. Set Up Stripe

1. **Create a Stripe Account**: https://dashboard.stripe.com/register

2. **Get API Keys**:
   - Go to Developers → API keys
   - Copy your keys to `.env`

3. **Create Products**:
   - Go to Products → Add Product
   - Create "ModelForge Starter"
     - Monthly price: $12
     - Yearly price: $99
   - Create "ModelForge Pro"
     - Monthly price: $29
     - Yearly price: $249
   - Copy all price IDs to `.env`

4. **Set Up Webhooks**:
   - Go to Developers → Webhooks
   - Add endpoint: `http://localhost:3000/api/webhooks/stripe`
   - Select events:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `checkout.session.completed`
   - Copy webhook signing secret to `.env`

5. **Test Webhooks Locally**:
   ```bash
   # Install Stripe CLI
   stripe listen --forward-to localhost:3000/api/webhooks/stripe
   ```

### 5. Start Development Server

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see your app!

## Project Structure

```
modelforge/
├── app/                 # Next.js app directory
│   ├── api/            # API routes
│   ├── dashboard/      # Protected dashboard pages
│   ├── login/          # Authentication pages
│   └── page.tsx        # Homepage
├── components/         # React components
│   ├── ui/            # shadcn/ui components
│   ├── landing/       # Landing page sections
│   ├── dashboard/     # Dashboard components
│   └── auth/          # Auth forms
├── lib/               # Utility libraries
│   ├── auth.ts       # NextAuth config
│   ├── db.ts         # Prisma client
│   ├── stripe.ts     # Stripe client
│   └── utils.ts      # Helper functions
├── prisma/
│   └── schema.prisma # Database schema
└── README.md         # Full documentation
```

## Common Tasks

```bash
# Development
npm run dev              # Start dev server
npm run build           # Build for production
npm run start           # Start production server
npm run lint            # Run ESLint

# Database
npm run db:generate     # Generate Prisma client
npm run db:push         # Push schema changes (dev)
npm run db:migrate      # Run migrations (prod)
npm run db:studio       # Open Prisma Studio
```

## Testing the Application

1. **Sign Up**: Go to `/signup` and create an account
2. **Login**: Go to `/login` and sign in
3. **Dashboard**: View your projects at `/dashboard`
4. **Create Project**: Click "New Project" button
5. **Settings**: Manage subscription at `/dashboard/settings`

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -U postgres -d modelforge -c "SELECT version();"

# Check pgvector
psql -U postgres -d modelforge -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Prisma Issues

```bash
# Reset database (WARNING: deletes all data)
npm run db:push -- --force-reset

# Regenerate client
npm run db:generate
```

### Stripe Webhook Issues

- Make sure webhook endpoint is accessible
- Verify webhook secret matches dashboard
- Use Stripe CLI for local testing:
  ```bash
  stripe listen --forward-to localhost:3000/api/webhooks/stripe
  ```

## Blender MCP Bridge

To enable direct Blender automation you will need the community [blender-mcp](https://github.com/ahujasid/blender-mcp) addon and server:

1. Install Blender ≥ 3.0, Python ≥ 3.10, and the [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager.
2. Download the latest `addon.py` from the upstream repository, then install it via Blender → Preferences → Add-ons → Install.
3. Launch the MCP server with `uvx blender-mcp` (consult the upstream README for IDE integrations). Keep the `.env` variables `BLENDER_MCP_HOST` and `BLENDER_MCP_PORT` aligned with the server.
4. Start Blender, enable the addon, and click **Connect to Claude** (or the ModelForge desktop app once available).

See `blendermcpreadme.md` in this repository for a full offline copy of the official setup guide.

### Installing `uv`

Install `uv` before running `uvx blender-mcp`:

- **Linux**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Add the path printed by the installer (commonly `~/.cargo/bin` or `~/.local/bin`) to your `PATH`.

- **macOS**
  ```bash
  brew install uv
  ```
  or use the same curl script as Linux if you prefer.

- **Windows**
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  Then append `%USERPROFILE%\.local\bin` to your `PATH`.

Confirm the installation with:

```bash
uv --version
```

## Next Steps

Phase 1 is complete! Here's what comes next:

- [ ] Deploy to DigitalOcean
- [ ] Set up production database
- [ ] Configure production Stripe webhooks
- [ ] Build Electron desktop app (Phase 2)
- [ ] Integrate Blender MCP server
- [ ] Implement AI chat with Gemini
- [ ] Add vector embeddings for project memory

## Need Help?

Check the [full README](./README.md) for comprehensive documentation, or open an issue on GitHub.

---

Built with Next.js, PostgreSQL, and Stripe
