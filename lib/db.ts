import { PrismaClient } from '@prisma/client'

// Serverless-optimized Prisma client configuration
// Works with Neon, Supabase, and other serverless PostgreSQL providers

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

const prismaClientOptions = {
  log: process.env.NODE_ENV === 'development'
    ? ['query', 'error', 'warn'] as const
    : ['error'] as const,
  // Recommended for serverless: reduce connection timeout
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
}

export const prisma =
  globalForPrisma.prisma ?? new PrismaClient(prismaClientOptions)

// Prevent multiple instances in development (hot reload)
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

// Graceful shutdown for serverless environments
async function disconnectOnExit() {
  await prisma.$disconnect()
}

// Handle process termination
if (typeof process !== 'undefined') {
  process.on('beforeExit', disconnectOnExit)
}
