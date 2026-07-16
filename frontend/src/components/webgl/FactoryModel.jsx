import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { useStore } from '../../store/useStore'
import * as THREE from 'three'

export default function FactoryModel() {
  const progress = useStore((state) => state.progress)
  
  // Materials
  const materials = useMemo(() => {
    return {
      solid: new THREE.MeshStandardMaterial({
        color: '#16181B',
        roughness: 0.3,
        metalness: 0.8,
      }),
      solidDark: new THREE.MeshStandardMaterial({
        color: '#0A0A0C',
        roughness: 0.2,
        metalness: 0.9,
      }),
      danger: new THREE.MeshStandardMaterial({
        color: '#FF4A4A',
        emissive: '#FF4A4A',
        emissiveIntensity: 0,
        roughness: 0.4,
      })
    }
  }, [])

  const solidGroupRef = useRef()

  useFrame(() => {
    // Dissolve logic for Scene 11 (progress > 0.84)
    if (solidGroupRef.current) {
      let opacity = 1
      if (progress > 0.84) {
        opacity = Math.max(0, 1 - (progress - 0.84) * 8)
      }
      
      solidGroupRef.current.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = true
          child.material.opacity = opacity
          
          // Add a subtle upward float during dissolve
          if (progress > 0.84) {
             child.position.y += 0.02 * (1 - opacity)
          } else {
             // Reset y if user scrolls up
             if (child.userData.originalY !== undefined) {
               child.position.y = THREE.MathUtils.lerp(child.position.y, child.userData.originalY, 0.1)
             } else {
               child.userData.originalY = child.position.y
             }
          }
        }
      })
    }
  })

  return (
    <group position={[0, -2, 0]}>
      {/* Solid Geometry Group */}
      <group ref={solidGroupRef}>
        {/* Base Platform */}
        <mesh position={[0, -0.5, 0]} receiveShadow material={materials.solidDark}>
          <cylinderGeometry args={[14, 14, 1, 64]} />
        </mesh>
        
        {/* Inner Core */}
        <mesh position={[0, 3, 0]} castShadow receiveShadow material={materials.solid}>
          <cylinderGeometry args={[2.5, 2.5, 8, 32]} />
        </mesh>
        
        {/* Piping and Rings */}
        <mesh position={[0, 1, 0]} rotation={[Math.PI / 2, 0, 0]} material={materials.solidDark}>
          <torusGeometry args={[5, 0.3, 16, 100]} />
        </mesh>
        <mesh position={[0, 4, 0]} rotation={[Math.PI / 2, 0, 0]} material={materials.solidDark}>
          <torusGeometry args={[4, 0.2, 16, 100]} />
        </mesh>

        {/* Machinery Nodes (Denser than before) */}
        {[...Array(12)].map((_, i) => {
          const angle = (i / 12) * Math.PI * 2;
          const radius = i % 2 === 0 ? 8 : 6;
          const x = Math.cos(angle) * radius;
          const z = Math.sin(angle) * radius;
          const height = i % 2 === 0 ? 4 : 6;
          return (
            <group key={i} position={[x, height/2, z]}>
              <mesh castShadow receiveShadow material={materials.solid}>
                <boxGeometry args={[1.5, height, 1.5]} />
              </mesh>
              {/* Top sensor nodes */}
              <mesh position={[0, height/2 + 0.5, 0]} material={materials.solidDark}>
                <cylinderGeometry args={[0.5, 0.5, 1, 16]} />
              </mesh>
            </group>
          )
        })}

        {/* The Anomaly Node */}
        <AnomalousNode materials={materials} progress={progress} position={[6, 3, 0]} />
      </group>

      {/* Digital Twin Overlays */}
      <DigitalTwinOverlay progress={progress} />
      
      {/* Dissolve Particles (Scene 11) */}
      <DissolveSystem progress={progress} />
    </group>
  )
}

function AnomalousNode({ materials, progress, position }) {
  const ref = useRef()
  
  useFrame(() => {
    if (ref.current) {
      let intensity = 0;
      if (progress > 0.4 && progress < 0.6) {
        const peak = 0.47
        const p = Math.max(0, 1 - Math.abs(progress - peak) * 7);
        intensity = p * 4;
      }
      ref.current.material.emissiveIntensity = intensity;
    }
  })

  return (
    <mesh ref={ref} position={position} material={materials.danger}>
      <sphereGeometry args={[1.2, 32, 32]} />
    </mesh>
  )
}

function DigitalTwinOverlay({ progress }) {
  const groupRef = useRef()
  
  useFrame(() => {
    if (groupRef.current) {
      let opacity = 0;
      if (progress >= 0.26) {
        opacity = Math.min(1, (progress - 0.26) * 10);
      }
      if (progress > 0.85) {
        opacity *= Math.max(0, 1 - (progress - 0.85) * 8);
      }
      
      groupRef.current.traverse(child => {
        if (child.isMesh && child.material) {
          child.material.opacity = opacity * 0.4;
        }
      })
    }
  })

  return (
    <group ref={groupRef}>
      <mesh position={[0, 3, 0]}>
        <cylinderGeometry args={[2.55, 2.55, 8.1, 16]} />
        <meshBasicMaterial color="#5DAEFF" wireframe transparent opacity={0} depthWrite={false} />
      </mesh>
      
      {[...Array(12)].map((_, i) => {
        const angle = (i / 12) * Math.PI * 2;
        const radius = i % 2 === 0 ? 8 : 6;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        const height = i % 2 === 0 ? 4 : 6;
        return (
          <mesh key={i} position={[x, height/2, z]}>
            <boxGeometry args={[1.6, height + 0.1, 1.6]} />
            <meshBasicMaterial color="#5DAEFF" wireframe transparent opacity={0} depthWrite={false} />
          </mesh>
        )
      })}
    </group>
  )
}

function DissolveSystem({ progress }) {
  const pointsRef = useRef()
  
  const particleCount = 3000;
  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3)
    for(let i=0; i<particleCount; i++) {
      const r = Math.random() * 12
      const theta = Math.random() * Math.PI * 2
      pos[i*3] = Math.cos(theta) * r
      pos[i*3+1] = Math.random() * 8
      pos[i*3+2] = Math.sin(theta) * r
    }
    return pos
  }, [])

  useFrame(() => {
    if (pointsRef.current) {
      let opacity = 0;
      if (progress > 0.84) {
        opacity = Math.min(1, (progress - 0.84) * 8);
      }
      pointsRef.current.material.opacity = opacity;
      
      if (opacity > 0) {
        pointsRef.current.rotation.y += 0.002;
        const positions = pointsRef.current.geometry.attributes.position.array;
        for(let i=0; i<particleCount; i++) {
          positions[i*3+1] += 0.015; 
          if (positions[i*3+1] > 20) positions[i*3+1] = 0; 
        }
        pointsRef.current.geometry.attributes.position.needsUpdate = true;
      }
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={particleCount} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} color="#5DAEFF" transparent opacity={0} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </points>
  )
}
