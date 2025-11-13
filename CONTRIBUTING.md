# Contributing to ModelForge

Thank you for your interest in contributing to ModelForge! This guide will help you get started with contributing to the project. We welcome contributions of all kinds - bug fixes, new features, documentation improvements, and more.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Project Structure](#project-structure)
- [Testing Guidelines](#testing-guidelines)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-handle>/ModelForge.git
   cd ModelForge
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Ker102/ModelForge.git
   ```

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- PostgreSQL 14+
- Git
- Blender 3.0+ (for testing MCP integration)
- Python 3.10+ (for Blender MCP server)
- `uv` package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Local Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your values (database, authentication, API keys, etc.)

3. **Set up the database**:
   ```bash
   # Generate Prisma client
   npm run db:generate
   
   # Push schema to database
   npm run db:push
   
   # (Optional) Create test user
   npm run test:user
   ```

4. **Start development servers**:
   ```bash
   # Terminal 1: Web application
   npm run dev
   
   # Terminal 2: Desktop application (optional)
   cd desktop && npm run dev
   
   # Terminal 3: Blender MCP bridge (when testing orchestration)
   uvx blender-mcp
   ```

5. **Verify setup**:
   - Open http://localhost:3000 in your browser
   - Sign in with test credentials (if created)
   - Test basic functionality

## Making Changes

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feat/` - New features (e.g., `feat/add-export-functionality`)
- `fix/` - Bug fixes (e.g., `fix/authentication-redirect`)
- `docs/` - Documentation updates (e.g., `docs/improve-setup-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-api-handlers`)
- `test/` - Test additions/changes (e.g., `test/add-integration-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

### Commit Messages

Write clear, concise commit messages following these guidelines:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant
- Examples:
  - `feat: add export functionality for project history`
  - `fix: resolve authentication redirect loop (#123)`
  - `docs: update setup instructions for Windows users`

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make your changes** following our coding standards

4. **Run quality checks**:
   ```bash
   npm run lint
   npm run analyze:orchestration  # if changing orchestration logic
   ```

5. **Test your changes**:
   - Run existing tests
   - Add new tests if applicable
   - Test manually with Blender connected
   - Verify no regressions in existing functionality

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

8. **Open a Pull Request**:
   - Use the PR template provided
   - Link related issues
   - Provide clear description of changes
   - Include screenshots for UI changes
   - Request review from maintainers

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated (if applicable)
- [ ] No new warnings or errors
- [ ] Tests added/updated and passing
- [ ] Related issues linked
- [ ] PR description is clear and complete

## Coding Standards

### TypeScript & JavaScript

- Use TypeScript for all new code
- Follow Next.js App Router conventions
- Prefer `async/await` over promise chains
- Use meaningful variable and function names
- Add JSDoc comments for public APIs

### React Components

- Use functional components with hooks
- Keep components focused and single-purpose
- Extract reusable logic into custom hooks
- Use TypeScript interfaces for props

### Styling

- Use Tailwind CSS for styling
- Follow shadcn/ui patterns for components
- Maintain consistent spacing and typography
- Ensure responsive design for all screen sizes

### API Routes

- Validate input data with Zod schemas
- Use proper HTTP status codes
- Handle errors gracefully
- Add authentication where required
- Document API endpoints

### Database

- Use Prisma for all database operations
- Write migrations for schema changes
- Test migrations before committing
- Keep queries efficient and indexed

### Orchestration Logic

- Keep planner logic in `lib/orchestration/planner.ts`
- Executor changes go in `lib/orchestration/executor.ts`
- Add telemetry for debugging (`logs/orchestration.ndjson`)
- Document complex orchestration flows
- Surface plan metadata in the UI

## Project Structure

```
ModelForge/
├── app/                    # Next.js app directory
│   ├── (auth)/            # Authentication routes
│   ├── api/               # API routes
│   ├── dashboard/         # Dashboard pages
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── landing/          # Landing page sections
│   ├── dashboard/        # Dashboard components
│   └── auth/             # Auth forms
├── lib/                   # Shared libraries
│   ├── orchestration/    # AI orchestration logic
│   ├── mcp/              # MCP client
│   ├── auth.ts           # NextAuth config
│   ├── db.ts             # Prisma client
│   └── utils.ts          # Utilities
├── prisma/               # Database schema
├── desktop/              # Electron application
├── public/               # Static assets
├── scripts/              # Build and utility scripts
├── .github/              # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/   # Issue templates
│   ├── workflows/        # CI/CD workflows
│   └── *.yml             # GitHub configurations
└── docs/                 # Documentation (if needed)
```

## Testing Guidelines

### Manual Testing

- Test with Blender MCP server running
- Verify authentication flows
- Check responsive design on multiple devices
- Test error handling and edge cases
- Validate orchestration with real Blender scenes

### Integration Testing

- Test at least one complete workflow with Blender
- Verify MCP command execution
- Check database operations
- Validate API endpoints

### Before Submitting

- Verify no console errors or warnings
- Test on multiple browsers (Chrome, Firefox, Safari)
- Ensure all existing tests pass
- Check performance impact

## Reporting Issues

Use the appropriate issue template:

- **Bug Report**: For reproducible problems
- **Feature Request**: For new feature suggestions
- **Improvement Request**: For enhancements to existing features

Include in your issue:

- Clear, descriptive title
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (OS, browser, Blender version)
- Relevant logs or screenshots
- Error messages (if any)

## Feature Requests

When proposing new features:

1. Check existing issues to avoid duplicates
2. Use the Feature Request template
3. Explain the problem it solves
4. Describe your proposed solution
5. Consider implementation complexity
6. Discuss potential alternatives

## Getting Help

- Check the [README](README.md) for setup and usage
- Review existing [Issues](https://github.com/Ker102/ModelForge/issues)
- Join [Discussions](https://github.com/Ker102/ModelForge/discussions)
- Read the [orchestration documentation](gemini-blender-orchestration.md)

## Recognition

Contributors will be:

- Listed in release notes
- Credited in the project
- Mentioned in related issues/PRs

## Questions?

If you have questions about contributing:

- Open a discussion in GitHub Discussions
- Comment on related issues
- Reach out to maintainers

---

Thank you for contributing to ModelForge! Your efforts help make AI-powered 3D creation accessible to everyone. 🙌
