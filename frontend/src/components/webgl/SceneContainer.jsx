import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { useStore } from '../../store/useStore'
import FactoryModel from './FactoryModel'
import Lighting from './Lighting'
import CameraRig from './CameraRig'
import * as THREE from 'three'

export default function SceneContainer() {
  const groupRef = useRef()
  const progress = useStore((state) => state.progress)
  const view = useStore((state) => state.view)
  const activeTab = useStore((state) => state.activeTab)

  useFrame((state) => {
    if (groupRef.current) {
      // Disable mouse-pointer parallax when manually orbiting in dashboard view
      if (view === 'dashboard' && activeTab === 'twin') {
        groupRef.current.rotation.x = THREE.MathUtils.lerp(groupRef.current.rotation.x, 0, 0.05)
        groupRef.current.rotation.y = THREE.MathUtils.lerp(groupRef.current.rotation.y, 0, 0.05)
        return
      }

      // Subtle cinematic rotation parallax
      const targetX = (state.pointer.x * Math.PI) / 60;
      const targetY = (state.pointer.y * Math.PI) / 60;
      
      groupRef.current.rotation.y += (targetX - groupRef.current.rotation.y) * 0.02;
      groupRef.current.rotation.x += (-targetY - groupRef.current.rotation.x) * 0.02;
    }
  })

  // Cinematic fog logic (Dark and moody)
  const fogColor = view === 'dashboard' ? '#0A0B0D' : (progress > 0.5 ? '#060B12' : '#040506')

  return (
    <>
      <fog attach="fog" args={[fogColor, 10, 45]} />
      
      <CameraRig />
      <Lighting />
      
      <group ref={groupRef}>
        <FactoryModel />
      </group>

      {/* Render OrbitControls only when inspecting the 3D twin inside Mission Control */}
      {view === 'dashboard' && activeTab === 'twin' && (
        <OrbitControls 
          enableDamping 
          dampingFactor={0.05} 
          minDistance={8} 
          maxDistance={35} 
          maxPolarAngle={Math.PI / 2 - 0.05} /* Prevent camera going below platform base */
        />
      )}

      <EffectComposer disableNormalPass multisampling={4}>
        <Bloom 
          luminanceThreshold={0.5} 
          luminanceSmoothing={0.9} 
          intensity={view === 'dashboard' ? 1.2 : (progress > 0.4 ? 1.8 : 0.8)} 
          mipmapBlur 
        />
        <Vignette eskil={false} offset={0.1} darkness={1.2} />
      </EffectComposer>
    </>
  )
}
