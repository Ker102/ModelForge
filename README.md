<div align="center">

# 🔨 ModelForge

**AI-Powered Blender Assistant**

<p align="center">
  Transform your 3D workflow with AI-powered Blender automation.<br>
  Create, modify, and enhance your Blender projects through natural conversation.
</p>

<!-- Tech Stack Header -->
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind,nodejs,prisma,postgres,electron,python,blender" />
  </a>
</p>
<p align="center">
  <b>Next.js 16 • TypeScript • Tailwind • Node.js • Prisma • Postgres • Electron • Blender</b>
</p>

<br>

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
<br>
<img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind" />
<br><br>
<b>Next.js 16 • React 19 • TypeScript 5.6 • Tailwind CSS</b>
<br><br>
</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>
<br>
<img src="https://skillicons.dev/icons?i=nodejs,prisma,postgres" />
<br><br>
<b>Node.js 24+ • Prisma 5.20 • PostgreSQL 14+ (Neon)</b>
<br><br>
</td>
</tr>
<tr>
<td><b>AI & Desktop</b></td>
<td>
<br>
<img src="https://skillicons.dev/icons?i=gcp,python,electron,blender" />
<br><br>
<b>Gemini 3 Pro • LangChain • Electron • Blender API</b>
<br><br>
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
