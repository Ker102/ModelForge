/**
 * Monitoring Module — Public API
 * 
 * Usage:
 *   import { createMonitoringSession } from "@/lib/monitoring"
 *   const monitor = createMonitoringSession("request-id")
 *   monitor.info("executor", "Step 1 executing", { action: "create_mesh" })
 */

export {
    createMonitoringSession,
    MonitoringSession,
    type LogEntry,
    type LogLevel,
    type LogNamespace,
    type SessionSummary,
    type NeuralCostEntry,
    type TimerEntry,
} from "./logger"
