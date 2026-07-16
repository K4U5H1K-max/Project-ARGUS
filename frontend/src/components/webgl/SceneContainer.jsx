import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Environment } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { useStore } from '../../store/useStore'
import FactoryModel from './FactoryModel'
import Lighting from './Lighting'
import CameraRig from './CameraRig'

export default function SceneContainer() {
  const groupRef = useRef()
  const progress = useStore((state) => state.progress)

  useFrame((state) => {
    if (groupRef.current) {
      // Subtle cinematic rotation parallax
      const targetX = (state.pointer.x * Math.PI) / 60;
      const targetY = (state.pointer.y * Math.PI) / 60;
      
      groupRef.current.rotation.y += (targetX - groupRef.current.rotation.y) * 0.02;
      groupRef.current.rotation.x += (-targetY - groupRef.current.rotation.x) * 0.02;
    }
  })

  // Cinematic fog logic (Dark and moody)
  const fogColor = progress > 0.5 ? '#060B12' : '#040506'
  const fogDensity = progress > 0.85 ? 0.01 : 0.025

  return (
    <>
      <fog attach="fog" args={[fogColor, 10, 45]} />
      
      <CameraRig />
      <Lighting />
      
      <group ref={groupRef}>
        <FactoryModel />
      </group>

      <EffectComposer disableNormalPass multisampling={4}>
        <Bloom 
          luminanceThreshold={0.5} 
          luminanceSmoothing={0.9} 
          intensity={progress > 0.4 ? 1.8 : 0.8} 
          mipmapBlur 
        />
        <Vignette eskil={false} offset={0.1} darkness={1.2} />
      </EffectComposer>
    </>
  )
}
