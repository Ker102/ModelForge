// ── Features Section — Visual, not generic ──────────────────────

const features = [
  {
    title: "Talk to Your Scene",
    description:
      "Describe what you want in plain English. ModelForge translates your words into precise Blender Python — no coding, no menus, no manual work.",
    visual: "chat",
  },
  {
    title: "AI That Sees Your Viewport",
    description:
      "After every operation, the AI captures your viewport and checks the result. If something looks off, it self-corrects automatically.",
    visual: "eye",
  },
  {
    title: "134 Expert Scripts as Memory",
    description:
      "A curated library of professional Blender scripts — rigging, topology, animation, PBR materials — indexed by RAG so the AI always writes correct code.",
    visual: "brain",
  },
  {
    title: "Neural 3D Generation",
    description:
      "Generate meshes from text or images using Hunyuan3D and TRELLIS 2. ModelForge imports, cleans, and rigs the result — all in one pipeline.",
    visual: "neural",
  },
  {
    title: "Live Blender Bridge",
    description:
      "Execute Python directly inside Blender through MCP. No copy-paste, no file exports — real-time scene manipulation from your browser.",
    visual: "bridge",
  },
  {
    title: "Studio Workflow Mode",
    description:
      "Pick your tools, queue steps, and control each stage. The guided workflow lets you mix procedural, neural, and manual operations with full visibility.",
    visual: "workflow",
  },
]

// ── Visual Illustrations (Mini SVG scenes) ──────────────────────

function FeatureVisual({ type }: { type: string }) {
  const visualMap: Record<string, React.ReactNode> = {
    chat: (
      <div className="relative w-full h-full flex items-end justify-center pb-6">
        {/* Chat bubbles */}
        <div className="absolute left-4 top-6 rounded-2xl rounded-bl-sm px-3 py-2 text-[10px] font-medium max-w-[60%]"
          style={{ backgroundColor: "hsl(var(--forge-surface-dim))", color: "hsl(var(--forge-text-muted))" }}>
          Create a medieval castle with stone towers
        </div>
        <div className="absolute right-4 top-[52px] rounded-2xl rounded-br-sm px-3 py-2 text-[10px] font-medium max-w-[65%]"
          style={{ backgroundColor: "hsl(var(--forge-accent))", color: "white" }}>
          Building castle: base walls, 4 towers, keep, gate...
        </div>
        {/* Code snippet */}
        <div className="rounded-lg px-3 py-2 text-[9px] font-mono max-w-[80%]"
          style={{ backgroundColor: "hsl(222 47% 8%)", color: "hsl(168 75% 65%)" }}>
          bpy.ops.mesh.primitive_cylinder_add(radius=2)
        </div>
      </div>
    ),
    eye: (
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Eye icon */}
        <div className="relative">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <ellipse cx="32" cy="32" rx="28" ry="18" stroke="hsl(var(--forge-accent))" strokeWidth="2" fill="none" />
            <circle cx="32" cy="32" r="10" stroke="hsl(var(--forge-accent))" strokeWidth="2" fill="hsl(var(--forge-accent-subtle))" />
            <circle cx="32" cy="32" r="4" fill="hsl(var(--forge-accent))" />
          </svg>
          {/* Scanning lines */}
          <div className="absolute -top-2 -left-4 w-[88px] h-[2px] rounded-full opacity-40"
            style={{ background: "linear-gradient(90deg, transparent, hsl(var(--forge-accent)), transparent)" }} />
          <div className="absolute -bottom-2 -left-4 w-[88px] h-[2px] rounded-full opacity-40"
            style={{ background: "linear-gradient(90deg, transparent, hsl(var(--forge-accent)), transparent)" }} />
        </div>
        <div className="absolute bottom-4 right-4 rounded-md px-2 py-1 text-[9px] font-medium"
          style={{ backgroundColor: "hsl(var(--forge-accent))", color: "white" }}>
          ✓ Scene verified
        </div>
      </div>
    ),
    brain: (
      <div className="relative w-full h-full flex items-center justify-center gap-3">
        {/* Script pills */}
        <div className="flex flex-col gap-1.5 items-end">
          {["rigging.py", "pbr_loader.py", "retopo.py"].map((s) => (
            <div key={s} className="rounded-md px-2 py-1 text-[8px] font-mono"
              style={{ backgroundColor: "hsl(var(--forge-surface-dim))", color: "hsl(var(--forge-text-muted))", border: "1px solid hsl(var(--forge-border))" }}>
              {s}
            </div>
          ))}
        </div>
        {/* Arrow */}
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--forge-accent))" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12h14m-7-7 7 7-7 7" />
        </svg>
        {/* RAG result */}
        <div className="rounded-lg px-3 py-2"
          style={{ backgroundColor: "hsl(var(--forge-accent-subtle))", border: "1px solid hsl(var(--forge-accent-muted))" }}>
          <div className="text-[9px] font-semibold mb-1" style={{ color: "hsl(var(--forge-accent))" }}>RAG Match</div>
          <div className="text-[8px]" style={{ color: "hsl(var(--forge-text-muted))" }}>Relevance: 0.94</div>
          <div className="text-[8px]" style={{ color: "hsl(var(--forge-text-muted))" }}>134 scripts indexed</div>
        </div>
      </div>
    ),
    neural: (
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Text prompt → mesh pipeline */}
        <div className="flex items-center gap-2">
          <div className="rounded-lg px-2.5 py-1.5 text-[9px]"
            style={{ backgroundColor: "hsl(var(--forge-surface-dim))", border: "1px solid hsl(var(--forge-border))", color: "hsl(var(--forge-text-muted))" }}>
            &quot;A dragon&quot;
          </div>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--forge-accent))" strokeWidth="2"><path d="M5 12h14m-7-7 7 7-7 7" /></svg>
          <div className="w-14 h-14 rounded-xl flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, hsl(var(--forge-accent-muted)), hsl(var(--forge-accent-subtle)))" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--forge-accent))" strokeWidth="1.5">
              <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
              <path d="M12 12l8-4.5M12 12v9M12 12L4 7.5" />
            </svg>
          </div>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--forge-accent))" strokeWidth="2"><path d="M5 12h14m-7-7 7 7-7 7" /></svg>
          <div className="rounded-lg px-2.5 py-1.5 text-[9px] font-medium"
            style={{ backgroundColor: "hsl(var(--forge-accent))", color: "white" }}>
            .glb
          </div>
        </div>
        {/* Provider badges */}
        <div className="absolute bottom-3 flex gap-2">
          <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ backgroundColor: "hsl(var(--forge-accent-subtle))", color: "hsl(var(--forge-accent))" }}>Hunyuan3D</span>
          <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ backgroundColor: "hsl(var(--forge-accent-subtle))", color: "hsl(var(--forge-accent))" }}>TRELLIS 2</span>
        </div>
      </div>
    ),
    bridge: (
      <div className="relative w-full h-full flex items-center justify-center gap-4">
        {/* Browser */}
        <div className="rounded-lg border p-2" style={{ borderColor: "hsl(var(--forge-border))" }}>
          <div className="w-12 h-8 rounded flex items-center justify-center" style={{ backgroundColor: "hsl(var(--forge-surface-dim))" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--forge-accent))" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18" /></svg>
          </div>
          <div className="text-[7px] text-center mt-1" style={{ color: "hsl(var(--forge-text-subtle))" }}>Browser</div>
        </div>
        {/* Connection line */}
        <div className="flex flex-col items-center gap-1">
          <div className="w-12 h-[2px] rounded-full" style={{ background: "linear-gradient(90deg, hsl(var(--forge-accent)), hsl(var(--forge-accent-muted)))" }} />
          <span className="text-[7px] font-medium" style={{ color: "hsl(var(--forge-accent))" }}>MCP</span>
          <div className="w-12 h-[2px] rounded-full" style={{ background: "linear-gradient(90deg, hsl(var(--forge-accent-muted)), hsl(var(--forge-accent)))" }} />
        </div>
        {/* Blender */}
        <div className="rounded-lg border p-2" style={{ borderColor: "hsl(var(--forge-border))" }}>
          <div className="w-12 h-8 rounded flex items-center justify-center" style={{ backgroundColor: "hsl(222 47% 8%)" }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="hsl(168 75% 65%)" strokeWidth="1.5">
              <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
            </svg>
          </div>
          <div className="text-[7px] text-center mt-1" style={{ color: "hsl(var(--forge-text-subtle))" }}>Blender</div>
        </div>
      </div>
    ),
    workflow: (
      <div className="relative w-full h-full flex items-center justify-center px-4">
        {/* Workflow steps with icons */}
        <div className="flex items-center gap-2 w-full justify-center">
          {[
            { label: "Generate", done: true, icon: "M12 15a3 3 0 100-6 3 3 0 000 6zM19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" },
            { label: "Clean", done: true, icon: "M12 19l7-7 3 3-7 7-3-3zM18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" },
            { label: "Rig", active: true, icon: "M18 20V6M14 20V4M10 20V8M6 20v-6" },
            { label: "Export", pending: true, icon: "M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" },
          ].map((step, i) => (
            <div key={step.label} className="flex items-center gap-2">
              <div className="flex flex-col items-center gap-1.5">
                {/* Icon above */}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke={step.done || step.active ? "hsl(var(--forge-accent))" : "hsl(var(--forge-text-subtle))"}
                  strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d={step.icon} />
                </svg>
                {/* Step pill with optional glow */}
                <div className="relative">
                  {step.active && (
                    <div className="absolute -inset-2 rounded-full opacity-30"
                      style={{ background: "radial-gradient(circle, hsl(var(--forge-accent)), transparent 70%)", filter: "blur(6px)" }} />
                  )}
                  <div
                    className="relative rounded-full px-3 py-1.5 text-[9px] font-semibold whitespace-nowrap"
                    style={{
                      backgroundColor: step.done ? "hsl(var(--forge-accent))" : step.active ? "white" : "hsl(var(--forge-surface-dim))",
                      color: step.done ? "white" : step.active ? "hsl(var(--forge-accent))" : "hsl(var(--forge-text-subtle))",
                      border: step.active ? "1.5px solid hsl(var(--forge-accent))" : step.pending ? "1px solid hsl(var(--forge-border))" : "none",
                    }}
                  >
                    {step.done && "✓ "}{step.label}
                  </div>
                </div>
              </div>
              {i < 3 && (
                <div className="w-4 h-[1.5px] mb-1 shrink-0" style={{ backgroundColor: step.done ? "hsl(var(--forge-accent))" : "hsl(var(--forge-border))" }} />
              )}
            </div>
          ))}
        </div>
      </div>
    ),
  }

  return (
    <div
      className="w-full h-36 rounded-xl overflow-hidden relative"
      style={{
        backgroundColor: "hsl(var(--forge-surface-dim))",
        border: "1px solid hsl(var(--forge-border))",
      }}
    >
      {visualMap[type] ?? null}
    </div>
  )
}

// ── Feature Card ────────────────────────────────────────────────

function FeatureCard({
  title,
  description,
  visual,
}: {
  title: string
  description: string
  visual: string
}) {
  return (
    <div
      className="rounded-2xl border transition-all duration-200 hover:shadow-lg overflow-hidden group"
      style={{
        borderColor: "hsl(var(--forge-border))",
        backgroundColor: "white",
      }}
    >
      <FeatureVisual type={visual} />
      <div className="p-5">
        <h3
          className="text-base font-semibold mb-2"
          style={{ color: "hsl(var(--forge-text))" }}
        >
          {title}
        </h3>
        <p
          className="text-sm leading-relaxed"
          style={{ color: "hsl(var(--forge-text-muted))" }}
        >
          {description}
        </p>
      </div>
    </div>
  )
}

// ── Main Section ────────────────────────────────────────────────

export function Features() {
  return (
    <section
      id="features"
      className="py-20 md:py-28"
      style={{ backgroundColor: "hsl(var(--forge-surface-dim))" }}
    >
      <div className="container mx-auto max-w-6xl">
        <div className="text-center space-y-4 mb-16">
          <div
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium"
            style={{
              backgroundColor: "hsl(var(--forge-accent-subtle))",
              color: "hsl(var(--forge-accent))",
            }}
          >
            Features
          </div>
          <h2
            className="text-3xl md:text-5xl font-bold tracking-tight"
            style={{ color: "hsl(var(--forge-text))" }}
          >
            Everything You Need to Create
          </h2>
          <p
            className="text-lg max-w-2xl mx-auto"
            style={{ color: "hsl(var(--forge-text-muted))" }}
          >
            From natural language to finished 3D model — ModelForge handles the entire pipeline.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature) => (
            <FeatureCard
              key={feature.title}
              title={feature.title}
              description={feature.description}
              visual={feature.visual}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
