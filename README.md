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
    <img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind,nodejs,supabase,electron,python,blender" />
  </a>
</p>
<p align="center">
  <b>Next.js 15 • TypeScript • Tailwind • Supabase • LangChain • Electron • Blender</b>
</p>

<br>

[Features](#-features) • [Agent Tools](#-agent-tools) • [Quick Start](#-quick-start) • [Addon Detection](#-dynamic-addon-detection) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

ModelForge is a comprehensive platform that brings next-gen AI capabilities to Blender through an intelligent agent, a RAG pipeline, and seamless addon integration.

### 🤖 LangChain v1 Agent
- **ReAct Loop**: Built on LangChain 1.x `createAgent` + LangGraph with hallucinated tool-call recovery
- **22 Native Tools**: Direct Blender manipulation without writing Python (transforms, modifiers, parenting, export, and more)
- **Middleware Stack**: Viewport screenshots after code execution, RAG context injection
- **Session Persistence**: `MemorySaver` with `thread_id` keyed to project ID

### 🧠 Dynamic Addon Detection
- **Auto-Discovery**: Agent calls `list_installed_addons` to introspect enabled Blender addons at session start
- **Addon Registry**: 11 known addon profiles (Node Wrangler, Rigify, LoopTools, Bool Tool, etc.)
- **Prompt Injection**: System prompt is dynamically extended with addon-specific operators and usage tips
- **Zero Configuration**: Install an addon → the agent adapts automatically

### 📚 Hybrid RAG Pipeline
- **Context-Aware Generation**: Leverages **113+ professional Blender scripts** for accurate code generation
- **Semantic Search**: Uses Together.ai M2-BERT embeddings for high-quality retrieval
- **CRAG Architecture**: Corrective RAG with quality grading and fallback strategies
- **Knowledge Base**: Covers modeling, rigging, shading, geometry nodes, animation, and lighting

### 🌐 Web Dashboard
- **Supabase Auth**: Secure authentication with Google and GitHub OAuth
- **Dual Modes**: Autopilot (conversational) and Studio (tool-card grid with icon sidebar)
- **Asset Integration**: Toggleable PolyHaven, Hyper3D Rodin, and Sketchfab pipelines
- **Curated Addons Page**: `/addons` route with AI Compatible badges and addon categories

### 🔌 Blender MCP Bridge
- **Socket Bridge**: Executes generated Python directly in Blender via TCP
- **Bidirectional**: Commands sent, results returned as JSON
- **Viewport Capture**: Base64-encoded screenshots for visual feedback loops

---

## 🛠️ Agent Tools

The ModelForge agent has **22 native tools** that it can call directly — no Python code required:

| Category | Tools |
|---|---|
| **Scene Analysis** | `get_scene_info`, `get_object_info`, `get_all_object_info`, `get_viewport_screenshot` |
| **Code Execution** | `execute_code`, `list_materials` |
| **Object Management** | `delete_object`, `rename_object`, `duplicate_object`, `join_objects` |
| **Transforms** | `set_object_transform`, `apply_transforms` |
| **Modifiers** | `add_modifier`, `apply_modifier`, `shade_smooth` |
| **Hierarchy** | `parent_set`, `parent_clear` |
| **Organization** | `set_origin`, `move_to_collection`, `set_visibility` |
| **Export** | `export_object` (GLB, GLTF, FBX, OBJ, STL) |
| **Detection** | `list_installed_addons` |

Plus **6 integration tools** when enabled: PolyHaven (3), Sketchfab (2), Hyper3D Rodin (3).

---

## 🧩 Dynamic Addon Detection

ModelForge is the first AI agent that **auto-adapts to your installed Blender addons**.

```
Session Start
  └→ Executor calls list_installed_addons via MCP
      └→ Blender introspects addon_utils.modules()
          └→ Returns enabled addon metadata
              └→ Matched against Addon Registry (11 profiles)
                  └→ System prompt extended with addon operators
                      └→ Agent knows how to use your addons via execute_code
```

**Currently recognized addons:**

| Addon | Category | What the Agent Gains |
|---|---|---|
| Node Wrangler | Shading | PBR texture auto-connect |
| Rigify | Rigging | Meta-rig to full rig generation |
| LoopTools | Mesh | Relax, circle, bridge operations |
| Bool Tool | Object | Quick boolean unions/differences |
| Images as Planes | Import | Import reference images |
| Extra Mesh Objects | Add Mesh | Procedural gears, gems, stars |
| Extra Curve Objects | Add Curve | Spirals, torus knots |
| F2 | Mesh | Extended face-filling |
| 3D-Print Toolbox | Mesh | Print quality checks |
| Animation Nodes | Animation | Procedural node trees |
| BlenderKit | Import | Asset library downloads |

---

## 🏗️ Technology Stack

<table>
<tr>
<td><b>Frontend</b></td>
<td>
<br>
<img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind" />
<br><br>
<b>Next.js 15 • React 19 • TypeScript 5.6 • Tailwind CSS</b>
<br><br>
</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>
<br>
<img src="https://skillicons.dev/icons?i=nodejs,supabase" />
<br><br>
<b>Node.js 24+ • Supabase (Auth + Postgres) • Stripe</b>
<br><br>
</td>
</tr>
<tr>
<td><b>AI & Desktop</b></td>
<td>
<br>
<img src="https://skillicons.dev/icons?i=gcp,python,electron,blender" />
<br><br>
<b>Gemini 2.5 Pro • LangChain v1 • LangGraph • Electron • Blender Python API</b>
<br><br>
</td>
</tr>
</table>

## 📋 Quick Start

### Prerequisites

- Node.js 18+ (24+ recommended)
- Supabase project (or local instance)
- Blender 4.0+ (5.0 compatible)
- Python 3.10+

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
   Configure `.env` with your Supabase URL/keys, Gemini API key, and Together.ai API key (for RAG).

4. **Start development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

5. **Connect Blender**
   - Install the ModelForge addon in Blender (`public/downloads/modelforge-addon.py`)
   - Click "Start Server" in Blender's sidebar panel
   - The agent connects automatically via TCP socket

## 🔄 Roadmap

- [x] LangChain v1 agent with ReAct loop
- [x] 22 native Blender tools
- [x] Dynamic addon detection + registry
- [x] Curated Addons page (`/addons`)
- [x] Hybrid RAG Pipeline (113+ scripts)
- [x] Supabase Auth (Google + GitHub OAuth)
- [x] Stripe subscription integration
- [x] Viewport screenshot analysis
- [x] Electron desktop shell
- [ ] Manual verification of all tool categories
- [ ] Production desktop packaging
- [ ] Dynamic addon operator discovery (auto-generate tools from unknown addons)
- [ ] Community addon marketplace page

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the [LICENSE](LICENSE) file.

---

<div align="center">

Built with ❤️ by the ModelForge team

[Website](#) • [Documentation](README.md) • [Addons](/addons)

</div>
