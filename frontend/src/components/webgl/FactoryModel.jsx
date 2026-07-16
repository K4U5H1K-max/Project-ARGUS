import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import { useStore } from '../../store/useStore'
import * as THREE from 'three'

export default function FactoryModel() {
  const progress = useStore((state) => state.progress)
  const view = useStore((state) => state.view)
  const activeTab = useStore((state) => state.activeTab)
  const setSelectedEquipment = useStore((state) => state.setSelectedEquipment)
  
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
      if (view === 'dashboard') {
        opacity = 1
      } else if (progress > 0.84) {
        opacity = Math.max(0, 1 - (progress - 0.84) * 8)
      }
      
      solidGroupRef.current.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = true
          child.material.opacity = opacity
          
          // Add a subtle upward float during dissolve
          if (view !== 'dashboard' && progress > 0.84) {
             child.position.y += 0.02 * (1 - opacity)
          } else {
             // Reset y if user scrolls up or switches views
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

  // Pre-calculated machinery node positions
  const nodes = useMemo(() => {
    return [...Array(12)].map((_, i) => {
      const angle = (i / 12) * Math.PI * 2;
      const radius = i % 2 === 0 ? 8 : 6;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const height = i % 2 === 0 ? 4 : 6;
      return { x, z, height, index: i }
    })
  }, [])

  return (
    <group position={[0, -2, 0]}>
      {/* Solid Geometry Group */}
      <group ref={solidGroupRef}>
        {/* Base Platform */}
        <mesh position={[0, -0.5, 0]} receiveShadow material={materials.solidDark}>
          <cylinderGeometry args={[14, 14, 1, 64]} />
        </mesh>
        
        {/* Inner Core */}
        <mesh 
          position={[0, 3, 0]} 
          castShadow 
          receiveShadow 
          material={materials.solid}
          onClick={(e) => {
            if (view === 'dashboard') {
              e.stopPropagation()
              setSelectedEquipment({
                name: 'Central Catalyst Column (Core-01)',
                status: 'NOMINAL',
                temp: '342°C',
                pressure: '14.2 bar',
                vibration: '2.4 mm/s',
                lastInspection: '2026-07-10',
                risk: '0.1%',
                predictedFailure: 'None (Nominal behavior calculated)',
                rul: '18,400 Operating Hours (92.5%)',
                recommendedAction: 'Schedule routine valve seals maintenance check on Q3 cycle.'
              })
            }
          }}
        >
          <cylinderGeometry args={[2.5, 2.5, 8, 32]} />
          
          {/* Floating HUD status indicator above Central Catalyst Column */}
          {view === 'dashboard' && activeTab === 'twin' && (
            <Html position={[0, 4.5, 0]} distanceFactor={15}>
              <div className="html-hud-indicator">
                <div style={{ fontWeight: 'bold', color: 'var(--accent-ai)' }}>CORE-01 [NOMINAL]</div>
                <div>Temp: 342.1°C</div>
                <div>Pres: 14.2 bar</div>
              </div>
            </Html>
          )}
        </mesh>
        
        {/* Piping and Rings */}
        <mesh position={[0, 1, 0]} rotation={[Math.PI / 2, 0, 0]} material={materials.solidDark}>
          <torusGeometry args={[5, 0.3, 16, 100]} />
        </mesh>
        <mesh position={[0, 4, 0]} rotation={[Math.PI / 2, 0, 0]} material={materials.solidDark}>
          <torusGeometry args={[4, 0.2, 16, 100]} />
        </mesh>

        {/* Machinery Nodes */}
        {nodes.map((node) => {
          const { x, z, height, index } = node
          return (
            <group 
              key={index} 
              position={[x, height/2, z]}
              onClick={(e) => {
                if (view === 'dashboard') {
                  e.stopPropagation()
                  setSelectedEquipment({
                    name: `Pumping Station Node (Node-${index + 1})`,
                    status: index === 5 ? 'WARNING' : 'NOMINAL',
                    temp: index === 5 ? '88°C' : '45°C',
                    pressure: index === 5 ? '4.8 bar' : '2.1 bar',
                    vibration: index === 5 ? '7.8 mm/s' : '1.8 mm/s',
                    lastInspection: '2026-06-22',
                    risk: index === 5 ? '14.2%' : '0.4%',
                    predictedFailure: index === 5 ? 'Vibration displacement misalignment' : 'None',
                    rul: index === 5 ? '4,200 Operating Hours (68.1%)' : '24,000 Operating Hours (98.9%)',
                    recommendedAction: index === 5 ? 'Calibrate pump shaft alignment and grease motor bearing housings.' : 'Routine observation on next shift.'
                  })
                }
              }}
            >
              <mesh castShadow receiveShadow material={materials.solid}>
                <boxGeometry args={[1.5, height, 1.5]} />
              </mesh>
              {/* Top sensor nodes */}
              <mesh position={[0, height/2 + 0.5, 0]} material={materials.solidDark}>
                <cylinderGeometry args={[0.5, 0.5, 1, 16]} />
              </mesh>

              {/* Float indicators above Node-06 (warning node) and Node-01 (nominal) */}
              {view === 'dashboard' && activeTab === 'twin' && index === 5 && (
                <Html position={[0, height/2 + 1.2, 0]} distanceFactor={15}>
                  <div className="html-hud-indicator warning">
                    <div style={{ fontWeight: 'bold', color: 'var(--accent-warning)' }}>NODE-06 [WARNING]</div>
                    <div>Vibr: 7.8 mm/s</div>
                    <div>Temp: 88.2°C</div>
                  </div>
                </Html>
              )}
              {view === 'dashboard' && activeTab === 'twin' && index === 0 && (
                <Html position={[0, height/2 + 1.2, 0]} distanceFactor={15}>
                  <div className="html-hud-indicator">
                    <div style={{ fontWeight: 'bold', color: 'var(--accent-success)' }}>NODE-01 [NOMINAL]</div>
                    <div>Vibr: 1.8 mm/s</div>
                    <div>Temp: 45.1°C</div>
                  </div>
                </Html>
              )}
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
  const view = useStore((state) => state.view)
  const activeTab = useStore((state) => state.activeTab)
  const setSelectedEquipment = useStore((state) => state.setSelectedEquipment)
  
  useFrame((state) => {
    if (ref.current) {
      let intensity = 0;
      if (view === 'dashboard') {
        // Slow flashing danger light in dashboard
        const time = state.clock.getElapsedTime()
        intensity = 0.5 + Math.sin(time * 4) * 0.5
      } else if (progress > 0.4 && progress < 0.6) {
        const peak = 0.47
        const p = Math.max(0, 1 - Math.abs(progress - peak) * 7);
        intensity = p * 4;
      }
      ref.current.material.emissiveIntensity = intensity;
    }
  })

  return (
    <mesh 
      ref={ref} 
      position={position} 
      material={materials.danger}
      onClick={(e) => {
        if (view === 'dashboard') {
          e.stopPropagation()
          setSelectedEquipment({
            name: 'Thermal Reactor Vessel (Tank-04)',
            status: 'CRITICAL',
            temp: '142.4°C',
            pressure: '24.8 bar',
            vibration: '11.4 mm/s',
            lastInspection: '2026-07-15',
            risk: '94.2%',
            predictedFailure: 'Thermal runaway leading to core structural rupture',
            rul: '180 Operating Hours (2.1%)',
            recommendedAction: 'Emergency bypass: Trigger auxiliary cooling valves in Zone C and depressurize catalyst core.'
          })
        }
      }}
    >
      <sphereGeometry args={[1.2, 32, 32]} />

      {/* Floating HUD status indicator above Reactor Tank-04 */}
      {view === 'dashboard' && activeTab === 'twin' && (
        <Html position={[0, 1.8, 0]} distanceFactor={15}>
          <div className="html-hud-indicator danger">
            <div style={{ fontWeight: 'bold', color: 'var(--accent-danger)' }}>TANK-04 [CRITICAL]</div>
            <div>Temp: 142.4°C</div>
            <div>Pres: 24.8 bar</div>
          </div>
        </Html>
      )}
    </mesh>
  )
}

function DigitalTwinOverlay({ progress }) {
  const groupRef = useRef()
  const view = useStore((state) => state.view)
  
  useFrame(() => {
    if (groupRef.current) {
      let opacity = 0;
      if (view === 'dashboard') {
        opacity = 1.0;
      } else {
        if (progress >= 0.26) {
          opacity = Math.min(1, (progress - 0.26) * 10);
        }
        if (progress > 0.85) {
          opacity *= Math.max(0, 1 - (progress - 0.85) * 8);
        }
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
  const view = useStore((state) => state.view)
  
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
      if (view === 'dashboard') {
        opacity = 0;
      } else if (progress > 0.84) {
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
