import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

const AIOrb = ({ pipelineStage }) => {
  const sphereRef = useRef();

  // Determine target distortion and speed based on pipeline stage
  const targetState = useMemo(() => {
    switch (pipelineStage) {
      case 'thinking': return { distort: 0.6, speed: 4, scale: 2.7, color: '#9B72CB' };
      case 'speaking': return { distort: 0.5, speed: 6, scale: 2.8, color: '#4285F4' };
      case 'analyzing': return { distort: 0.7, speed: 5, scale: 2.6, color: '#D96570' };
      case 'transcribing': return { distort: 0.4, speed: 3, scale: 2.5, color: '#fff' };
      case 'separating': return { distort: 0.5, speed: 2, scale: 2.5, color: '#A0A0AB' };
      default: return { distort: 0.3, speed: 1.5, scale: 2.5, color: '#0A0A0E' }; // complete/idle
    }
  }, [pipelineStage]);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    if (sphereRef.current) {
      // Rotate
      sphereRef.current.rotation.x = time * (targetState.speed * 0.1);
      sphereRef.current.rotation.y = time * (targetState.speed * 0.15);
      
      // Smoothly interpolate current material values toward targets
      const material = sphereRef.current.material;
      material.distort = THREE.MathUtils.lerp(material.distort, targetState.distort + Math.sin(time * 2) * 0.1, 0.05);
      material.speed = THREE.MathUtils.lerp(material.speed, targetState.speed, 0.05);
      
      // Interpolate scale
      const currentScale = sphereRef.current.scale.x;
      const nextScale = THREE.MathUtils.lerp(currentScale, targetState.scale, 0.05);
      sphereRef.current.scale.set(nextScale, nextScale, nextScale);

      // Interpolate color
      const targetColor = new THREE.Color(targetState.color);
      material.color.lerp(targetColor, 0.05);
    }
  });

  return (
    <group>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} color="#4285F4" />
      <directionalLight position={[-10, -10, -5]} intensity={1} color="#9B72CB" />
      <directionalLight position={[0, 0, 10]} intensity={0.5} color="#D96570" />
      
      <Sphere ref={sphereRef} args={[1, 100, 100]} scale={2.5}>
        <MeshDistortMaterial
          color="#0A0A0E"
          attach="material"
          distort={0.4}
          speed={2}
          roughness={0.2}
          metalness={0.8}
          envMapIntensity={1}
          clearcoat={1}
          clearcoatRoughness={0.1}
          emissive="#2A2A3E"
          emissiveIntensity={0.2}
        />
      </Sphere>
    </group>
  );
};

export default AIOrb;
