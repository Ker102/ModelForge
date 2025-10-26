# Contributing to ModelForge

Thanks for helping us build a better AI assistant for Blender! This guide is intentionally short so you can get productive fast. If you need deeper details, check the code comments and `gemini-blender-orchestration.md`.

## Quick start
1. **Fork & clone**
   ```bash
   git clone https://github.com/<your-handle>/BlenderAI.git
   cd BlenderAI
   npm install
   ```
2. **Copy env vars**
   ```bash
   cp .env.example .env
   ```
   Fill in database, Stripe, and Gemini credentials.
3. **Sync the database**
   ```bash
   npm run db:generate
   npm run db:push
   ```
4. **Launch the stack**
   ```bash
   npm run dev                      # Web app
   cd desktop && npm run dev        # Electron shell (optional)
   ```
5. **Run the Blender MCP bridge** whenever you test orchestration:
   ```bash
   uvx blender-mcp
   ```

## Pull request checklist
- Create a feature branch (`git checkout -b feat/my-change`).
- Keep orchestration logic inside `lib/orchestration/` and surface new planner metadata in the UI.
- Run quality checks before pushing:
  ```bash
  npm run lint
  npm run analyze:orchestration   # optional but helpful for MCP changes
  ```
- Test at least one full chat prompt with Blender connected to confirm geometry/material updates still work.
- Reference related issues and describe how you validated the change in your PR body.

## Project layout (cheat sheet)
```
app/                # Next.js routes and API handlers
components/         # React + UI components
desktop/            # Electron shell
lib/                # Shared libraries (auth, MCP, orchestration, etc.)
prisma/             # Prisma schema & migrations
public/downloads/   # Files exposed to users (e.g. Blender addon)
scripts/            # Tooling like orchestration log analyzers
```

## Coding standards
- TypeScript with App Router conventions.
- Prefer `async/await`, avoid mixing promise styles.
- Tailwind + shadcn/ui for styling consistency.
- Planner/executor updates should include meaningful telemetry via `logs/orchestration.ndjson`.
- Document non-obvious logic with concise comments.

## Reporting issues & feature ideas
Use the GitHub issue templates (bug reports or improvements). Include:
- Steps to reproduce
- Relevant logs (`npm run dev` output, `logs/orchestration.ndjson`, Blender console)
- Whether you were in the web app or desktop shell

## Code of conduct
We expect respectful, inclusive communication. If something goes wrong, reach out to the maintainers privately so we can help.

Thanks again for contributing 🙌
