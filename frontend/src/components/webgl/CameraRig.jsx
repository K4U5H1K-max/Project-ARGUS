import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useStore } from '../../store/useStore'
import * as THREE from 'three'

export default function CameraRig() {
  const progress = useStore((state) => state.progress)
  const view = useStore((state) => state.view)
  const activeTab = useStore((state) => state.activeTab)
  
  // Damped targets
  const currentPos = useRef(new THREE.Vector3(0, 2, 25))
  const currentLook = useRef(new THREE.Vector3(0, 2, 0))

  useFrame((state) => {
    // If we are actively inspecting the 3D twin inside the dashboard tab,
    // let OrbitControls completely command the camera coordinates.
    if (view === 'dashboard' && activeTab === 'twin') {
      return
    }

    let targetPos = new THREE.Vector3()
    let targetLook = new THREE.Vector3(0, 2, 0)
    
    if (view === 'dashboard') {
      // Slow orbital rotate for active monitoring visual feed in dashboard mode
      const time = state.clock.getElapsedTime() * 0.08
      const radius = 20
      targetPos.set(Math.sin(time) * radius, 8, Math.cos(time) * radius)
      targetLook.set(0, 1.5, 0)
    } else {
      // Continuous 11-chapter cinematic spline equivalent
      if (progress < 0.08) {
        const p = progress / 0.08
        targetPos.set(0, 2, 25 - p * 5)
      } else if (progress < 0.17) {
        const p = (progress - 0.08) / 0.09
        targetPos.set(p * 10, 2 + p * 2, 20 - p * 5)
        targetLook.set(p * 2, 2, 0)
      } else if (progress < 0.25) {
        const p = (progress - 0.17) / 0.08
        targetPos.set(10 - p * 4, 4 - p * 2, 15 - p * 7)
        targetLook.set(2 + p * 2, 2, p * 4)
      } else if (progress < 0.34) {
        const p = (progress - 0.25) / 0.09
        targetPos.set(6 + p * 2, 2 + p * 4, 8)
        targetLook.set(4, 2, 4)
      } else if (progress < 0.42) {
        const p = (progress - 0.34) / 0.08
        targetPos.set(8, 6, 8 - p * 13)
        targetLook.set(4, 2, 4 - p * 4)
      } else if (progress < 0.50) {
        const p = (progress - 0.42) / 0.08
        targetPos.set(8 - p * 3.5, 6 - p * 3.5, -5 + p * 9.5)
        targetLook.set(4, 2, 0 + p * 4)
      } else if (progress < 0.59) {
        const p = (progress - 0.50) / 0.09
        // Smooth S-curve for this pull back
        const sp = p * p * (3 - 2 * p)
        targetPos.set(4.5 + sp * 5.5, 2.5 + sp * 5.5, 4.5 + sp * 5.5)
        targetLook.set(4 - sp * 4, 2, 4 - sp * 4)
      } else if (progress < 0.67) {
        const p = (progress - 0.59) / 0.08
        const sp = p * p * (3 - 2 * p)
        targetPos.set(10 - sp * 25, 8 + sp * 4, 10 - sp * 25)
        targetLook.set(0, 2 - sp * 2, 0)
      } else if (progress < 0.84) {
        const p = (progress - 0.67) / 0.17
        targetPos.set(-15 - p * 3, 12 + p * 3, -15 + p * 5)
        targetLook.set(0, 0, 0)
      } else {
        const p = (progress - 0.84) / 0.16
        targetPos.set(-18 - p * 2, 15 + p * 10, -10 + p * 10)
        targetLook.set(0, 0, 0)
      }
    }

    // Heavy damping for cinematic weight (simulates heavy camera equipment)
    currentPos.current.lerp(targetPos, 0.025)
    currentLook.current.lerp(targetLook, 0.025)

    state.camera.position.copy(currentPos.current)
    state.camera.lookAt(currentLook.current)
    
    // Add subtle cinematic dutch angle during the anomaly/tension phase
    let targetRoll = 0
    if (view !== 'dashboard' && progress > 0.4 && progress < 0.6) {
      const p = Math.max(0, 1 - Math.abs(progress - 0.47) * 7)
      targetRoll = p * 0.05 // max 0.05 radians
    }
    state.camera.rotation.z += (targetRoll - state.camera.rotation.z) * 0.03
  })

  return null
}
