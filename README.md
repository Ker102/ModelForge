<div align="center">

# 🔨 ModelForge

**AI-Powered Blender Assistant**

<p align="center">
  Transform your 3D workflow with AI-powered Blender automation.<br>
  Create, modify, and enhance your Blender projects through natural conversation.
</p>

<!-- Project Status Badges -->
<a href="https://github.com/Ker102/ModelForge/releases">
  <img src="https://img.shields.io/github/v/release/Ker102/ModelForge?style=for-the-badge&color=2563EB" alt="GitHub Release">
</a>
<a href="LICENSE">
  <img src="https://img.shields.io/github/license/Ker102/ModelForge?style=for-the-badge&color=4ade80" alt="License">
</a>
<a href="https://nextjs.org/">
  <img src="https://img.shields.io/badge/Next.js_16-HDR-black?style=for-the-badge&logo=next.js" alt="Next.js">
</a>
<a href="https://www.typescriptlang.org/">
  <img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
</a>
<a href="https://www.postgresql.org/">
  <img src="https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
</a>

<br>

<!-- Social/Community Badges -->
<a href="https://github.com/Ker102/ModelForge/issues">
  <img src="https://img.shields.io/github/issues/Ker102/ModelForge?style=for-the-badge&color=EF4444" alt="Issues">
</a>
<a href="https://github.com/Ker102/ModelForge/pulls">
  <img src="https://img.shields.io/github/issues-pr/Ker102/ModelForge?style=for-the-badge&color=F59E0B" alt="Pull Requests">
</a>
<a href="https://github.com/Ker102/ModelForge/stargazers">
  <img src="https://img.shields.io/github/stars/Ker102/ModelForge?style=for-the-badge&color=FBBF24" alt="Stars">
</a>

<br><br>

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing) • [Support](#-support)

</div>

---

## 🚀 Features

ModelForge is a comprehensive platform that brings next-gen AI capabilities to Blender through integrated components:

### 🎨 AI-Orchestrated Scene Builder
- **Gemini 3 Pro Orchestration**: Advanced ReAct-style planner with per-step validation
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

<img src="https://img.shields.io/badge/Next.js_16-HDR-black?style=for-the-badge&logo=next.js" alt="Next.js">
<img src="https://img.shields.io/badge/React_19-HDR-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
<img src="https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">

</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>

<img src="https://img.shields.io/badge/Node.js-24+-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js">
<img src="https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
<img src="https://img.shields.io/badge/Prisma-5.20-2D3748?style=for-the-badge&logo=prisma&logoColor=white" alt="Prisma">
<img src="https://img.shields.io/badge/Neon-Serverless-00E599?style=for-the-badge&logo=postgresql&logoColor=white" alt="Neon">

</td>
</tr>
<tr>
<td><b>AI & RAG</b></td>
<td>

<img src="https://img.shields.io/badge/Gemini_3_Pro-Preview-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini 3 Pro">
<img src="https://img.shields.io/badge/LangChain-JS-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
<img src="https://img.shields.io/badge/Together.ai-Embeddings-000000?style=for-the-badge" alt="Together.ai">
<img src="https://img.shields.io/badge/pgvector-Vector_DB-336791?style=for-the-badge" alt="pgvector">

</td>
</tr>
<tr>
<td><b>Desktop</b></td>
<td>

<img src="https://img.shields.io/badge/Electron-Latest-47848F?style=for-the-badge&logo=electron&logoColor=white" alt="Electron">

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
