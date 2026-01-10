
"use client";

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage, useGLTF } from '@react-three/drei';

interface ModelViewerProps {
    url: string;
}

function Model({ url }: { url: string }) {
    const { scene } = useGLTF(url);
    return <primitive object={scene} />;
}

export function ModelViewer({ url }: ModelViewerProps) {
    if (!url) return null;

    return (
        <div className="w-full h-96 bg-gray-900 rounded-lg overflow-hidden relative">
            <Canvas shadows dpr={[1, 2]} camera={{ fov: 50 }}>
                <Suspense fallback={null}>
                    <Stage environment="city" intensity={0.6}>
                        <Model url={url} />
                    </Stage>
                </Suspense>
                <OrbitControls autoRotate />
            </Canvas>
            <div className="absolute bottom-4 right-4 text-xs text-white/50 pointer-events-none">
                Powered by @react-three/fiber
            </div>
        </div>
    );
}
