<div align="center">

# 🔨 ModelForge

**AI-Powered Blender Assistant**

Transform your 3D workflow with AI-powered Blender automation. Create, modify, and enhance your Blender projects through natural conversation.

[![GitHub release](https://img.shields.io/github/v/release/Ker102/ModelForge?include_prereleases&style=flat-square)](https://github.com/Ker102/ModelForge/releases)
[![License](https://img.shields.io/github/license/Ker102/ModelForge?style=flat-square)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
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

ModelForge is a comprehensive platform that brings AI capabilities to Blender through integrated components:

### 🎨 AI-Orchestrated Scene Builder
- **Gemini 2.0 Orchestration**: ReAct-style planner with per-step validation
- **Smart Material Application**: Automatic material assignment and validation
- **Scene Auditing**: Ensures lighting, camera, and base materials exist with auto-correction

### 📚 Hybrid RAG Pipeline
- **Context-Aware Generation**: Leverages **113+ professional Blender scripts** for accurate code generation
- **Semantic Search**: Uses Together.ai M2-BERT embeddings for high-quality retrieval
- **Knowledge Base**: Covers modeling, rigging, shading, geometry nodes, and animation

### 🌐 Web Dashboard
- **User Authentication**: Secure NextAuth.js v5 with Google OAuth
- **Project Management**: Track multiple Blender projects
- **Asset Integration**: Toggles for Poly Haven, Hyper3D Rodin, and Sketchfab

### 🔌 Blender MCP Server Integration
- **Socket Bridge**: Executes generated Python directly in Blender
- **Real-time Communication**: Live feedback from Blender operations
- **External Integration**: Compatible with [blender-mcp](https://github.com/ahujasid/blender-mcp)

## 🛠️ Technology Stack

<table>
<tr>
<td><b>Frontend</b></td>
<td>

![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css)

</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>

![Node.js](https://img.shields.io/badge/Node.js-24+-339933?style=flat-square&logo=node.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql)
![Prisma](https://img.shields.io/badge/Prisma-5.20-2D3748?style=flat-square&logo=prisma)
![Neon](https://img.shields.io/badge/Neon-Serverless-00E599?style=flat-square&logo=postgresql)

</td>
</tr>
<tr>
<td><b>AI & RAG</b></td>
<td>

![Google Gemini](https://img.shields.io/badge/Gemini_2.x-Flash/Pro-4285F4?style=flat-square&logo=google)
![LangChain](https://img.shields.io/badge/LangChain-JS-1C3C3C?style=flat-square&logo=langchain)
![Together.ai](https://img.shields.io/badge/Together.ai-Embeddings-000000?style=flat-square)
![pgvector](https://img.shields.io/badge/pgvector-Vector_DB-336791?style=flat-square)

</td>
</tr>
<tr>
<td><b>Desktop</b></td>
<td>

![Electron](https://img.shields.io/badge/Electron-latest-47848F?style=flat-square&logo=electron)

</td>
</tr>
</table>

## 📋 Quick Start

### Prerequisites

- Node.js 18+ (24+ recommended)
- PostgreSQL 14+ with `vector` extension (or Neon)
- Blender 3.0+
- Python 3.10+
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
   Configure `.env` with your Database URL, NextAuth secret, Gemini API key, and Together.ai API key (for RAG).

4. **Initialize Database**
   ```bash
   npm run db:generate
   npm run db:push
   ```

5. **Ingest RAG Knowledge** (Optional but recommended)
   ```bash
   npm run ingest:blender
   ```

6. **Start development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📊 Database Schema

Main tables:
- **users**: Accounts and auth
- **projects**: Blender projects
- **conversations**: Chat history
- **document_embeddings**: RAG knowledge base (pgvector)
- **project_snapshots**: Scene state

## 🔄 Roadmap

- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] **Hybrid RAG Pipeline** (Neon + Together.ai)
- [x] **Expanded Script Library** (113+ scripts)
- [ ] Conversation memory with vector embeddings
- [ ] Viewport screenshot analysis
- [ ] Production desktop app packaging

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the [LICENSE](LICENSE) file.

---

<div align="center">

Built with ❤️ by the ModelForge community

[Website](#) • [Documentation](README.md) • [Discord](#) • [Twitter](#)

</div>
