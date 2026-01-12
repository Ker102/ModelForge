"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
    children: ReactNode;
    fallbackTitle?: string;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

/**
 * Error Boundary component for catching and handling React errors gracefully.
 * Logs errors to console and provides a user-friendly fallback UI.
 */
export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        // Log error for debugging/telemetry
        console.error("ErrorBoundary caught an error:", error, errorInfo);

        // TODO: Send to error tracking service (e.g., Sentry)
        // if (typeof window !== 'undefined') {
        //     captureException(error, { extra: errorInfo });
        // }
    }

    handleRetry = (): void => {
        this.setState({ hasError: false, error: null });
    };

    render(): ReactNode {
        if (this.state.hasError) {
            return (
                <div className="w-full max-w-2xl mx-auto p-8">
                    <div className="flex flex-col items-center justify-center text-center space-y-4 p-6 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <AlertTriangle className="w-12 h-12 text-red-500" />
                        <h2 className="text-xl font-semibold text-red-500">
                            {this.props.fallbackTitle || "Something went wrong"}
                        </h2>
                        <p className="text-sm text-muted-foreground max-w-md">
                            An unexpected error occurred while rendering this component.
                            Please try again or refresh the page.
                        </p>
                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                onClick={this.handleRetry}
                                className="gap-2"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Try Again
                            </Button>
                            <Button
                                variant="ghost"
                                onClick={() => window.location.reload()}
                            >
                                Refresh Page
                            </Button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
