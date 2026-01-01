import { createBlenderAgent } from "../lib/ai/agents"
import { embeddings } from "../lib/ai/embeddings"
import { vectorStore } from "../lib/ai/vectorstore"

async function testAIStack() {
    console.log("🧪 Starting AI Stack Verification...")

    // 1. Test Embeddings (Together.ai)
    console.log("\n1. Testing Together.ai Embeddings...")
    try {
        const text = "ModelForge is an AI-powered Blender assistant."
        const vector = await embeddings.embedQuery(text)
        console.log(`✅ Embedding generated successfully. Vector length: ${vector.length}`)
        if (vector.length !== 768) {
            console.warn("⚠️ Warning: Expected 768 dimensions (M2-BERT), got " + vector.length)
        }
    } catch (error) {
        console.error("❌ Embedding test failed:", error)
    }

    // 2. Test Vector Store (Neon pgvector)
    console.log("\n2. Testing Neon Vector Store...")
    try {
        // Basic connectivity check (search for something unlikely match)
        const results = await vectorStore.similaritySearch("test query", 1)
        console.log(`✅ Vector store search completed. Found ${results.length} results.`)
    } catch (error) {
        console.error("❌ Vector store test failed:", error)
    }

    // 3. Test Agent Planning (LangChain + Gemini 3 Pro)
    console.log("\n3. Testing BlenderAgent Planning...")
    const agent = createBlenderAgent({ useRAG: false }) // Disable RAG to isolate LLM test
    try {
        const plan = await agent.plan("Add a red cube at the center")
        console.log("✅ Plan generated successfully:")
        console.log(`- Steps: ${plan.steps.length}`)
        console.log(`- Summary: ${plan.plan_summary}`)
        console.log(`- First Action: ${plan.steps[0]?.action}`)
    } catch (error) {
        console.error("❌ Agent planning failed:", error)
    }

    console.log("\n🏁 Verification Complete.")
}

testAIStack().catch(console.error)
