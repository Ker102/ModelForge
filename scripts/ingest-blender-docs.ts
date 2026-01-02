/**
 * Ingestion Script for Blender Documentation and Scripts
 * 
 * Reads Python scripts from data/blender-scripts/, extracts metadata,
 * generates embeddings, and stores them in the Neon pgvector store.
 */

import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { addDocuments, deleteBySource } from '../lib/ai/vectorstore';

// Load environment variables from .env
dotenv.config();

const SCRIPTS_DIR = path.join(process.cwd(), 'data', 'blender-scripts');
const SOURCE_TAG = 'blender-scripts';

async function ingest() {
    console.log(`🚀 Starting ingestion from ${SCRIPTS_DIR}...`);

    try {
        // 1. Clear existing documents from this source to avoid duplicates
        console.log(`🧹 Clearing existing documents for source: ${SOURCE_TAG}...`);
        await deleteBySource(SOURCE_TAG);

        const files = fs.readdirSync(SCRIPTS_DIR).filter(f => f.endsWith('.py'));
        const documents = [];

        for (const file of files) {
            const filePath = path.join(SCRIPTS_DIR, file);
            const content = fs.readFileSync(filePath, 'utf-8');

            // Extraction of metadata from the docstring
            // Expecting format: """ { "json": "metadata" } """ at the start of the file
            const docstringMatch = content.match(/^"""([\s\S]*?)"""/);
            let metadata = { filename: file };
            let cleanContent = content;

            if (docstringMatch) {
                try {
                    const extractedJson = JSON.parse(docstringMatch[1].trim());
                    metadata = { ...metadata, ...extractedJson };
                    // Optionally remove the docstring from content to keep it clean, 
                    // or keep it for context. We'll keep it for now.
                } catch (e) {
                    console.warn(`⚠️ Could not parse metadata in ${file}: ${e.message}`);
                }
            }

            documents.push({
                content: content,
                metadata: metadata,
                source: SOURCE_TAG
            });
            console.log(`📄 Prepared: ${file} (${metadata.title || 'Untitled'})`);
        }

        if (documents.length === 0) {
            console.log('🛑 No documents found to ingest.');
            return;
        }

        // 2. Add to vector store (handles embedding generation via Together.ai)
        console.log(`📤 Ingesting ${documents.length} documents...`);
        const ids = await addDocuments(documents);

        console.log(`✅ Successfully ingested ${ids.length} documents.`);
    } catch (error: any) {
        console.error('❌ Ingestion failed:');
        const errorData = {
            message: error.message,
            code: error.code,
            meta: error.meta,
            stack: error.stack,
            error: error
        };
        fs.writeFileSync('debug_error.json', JSON.stringify(errorData, null, 2));
        console.log('📝 Error details written to debug_error.json');
    }
}

ingest().catch(console.error);
