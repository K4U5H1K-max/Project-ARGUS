import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useStore } from '../../store/useStore'
import * as THREE from 'three'

export default function Lighting() {
  const progress = useStore((state) => state.progress)
  
  const ambientRef = useRef()
  const mainLightRef = useRef()
  const rimLightRef = useRef()
  const dangerLightRef = useRef()
  const twinLightRef = useRef()

  useFrame(() => {
    if (!ambientRef.current) return;
    
    let ambient = 0.2
    let main = 0
    let rim = 1.0 // Constant cinematic rim lighting
    let danger = 0
    let twin = 0

    if (progress > 0.08) {
      // Warm industrial lights (Scene 2+)
      main = Math.min(1.5, (progress - 0.08) * 20)
    }

    if (progress > 0.43 && progress < 0.55) {
      // Danger anomaly (Scene 6)
      const peak = 0.47
      danger = Math.max(0, 1 - Math.abs(progress - peak) * 10) * 8.0
    }

    if (progress > 0.55) {
      // Twin takeover (Scene 8+)
      const p = Math.min(1, (progress - 0.55) * 10)
      twin = p * 4.0
      main = main * (1 - p) // fade out warm light
    }

    if (progress > 0.85) {
      // Final dissolve (Scene 11)
      const p = Math.min(1, (progress - 0.85) * 10)
      ambient = 0.5 * p // increase ambient slightly for particles
      twin = twin * (1 - p * 0.5) 
    }

    // Damped interpolations for extreme smoothness
    ambientRef.current.intensity = THREE.MathUtils.lerp(ambientRef.current.intensity, ambient, 0.05)
    mainLightRef.current.intensity = THREE.MathUtils.lerp(mainLightRef.current.intensity, main, 0.05)
    rimLightRef.current.intensity = THREE.MathUtils.lerp(rimLightRef.current.intensity, rim, 0.05)
    dangerLightRef.current.intensity = THREE.MathUtils.lerp(dangerLightRef.current.intensity, danger, 0.1)
    twinLightRef.current.intensity = THREE.MathUtils.lerp(twinLightRef.current.intensity, twin, 0.05)
  })

  return (
    <>
      <ambientLight ref={ambientRef} intensity={0.2} color="#ffffff" />
      
      <directionalLight 
        ref={mainLightRef} 
        position={[10, 20, 10]} 
        color="#F5F2EA"
        intensity={0} 
        castShadow 
      />

      <directionalLight 
        ref={rimLightRef} 
        position={[-15, 5, -15]} 
        color="#3a5b82"
        intensity={1} 
      />

      <pointLight ref={dangerLightRef} position={[4, 2, 4]} color="#FF4A4A" intensity={0} distance={15} />
      
      <pointLight ref={twinLightRef} position={[0, 10, 0]} color="#5DAEFF" intensity={0} distance={40} />
    </>
  )
}
