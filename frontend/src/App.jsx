import { useEffect } from 'react'
import Lenis from 'lenis'
import { Canvas } from '@react-three/fiber'
import { useStore } from './store/useStore'
import Overlay from './components/dom/Overlay'
import SceneContainer from './components/webgl/SceneContainer'

export default function App() {
  const setProgress = useStore((state) => state.setProgress)

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.5,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      gestureDirection: 'vertical',
      smooth: true,
      mouseMultiplier: 1,
      smoothTouch: false,
      touchMultiplier: 2,
      infinite: false,
    })

    lenis.on('scroll', (e) => {
      setProgress(e.progress)
    })

    function raf(time) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }

    requestAnimationFrame(raf)

    return () => {
      lenis.destroy()
    }
  }, [setProgress])

  return (
    <>
      <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        <Canvas 
          camera={{ position: [0, 5, 20], fov: 45 }}
          gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
          dpr={[1, 2]}
        >
          <color attach="background" args={['#0F1012']} />
          <SceneContainer />
        </Canvas>
      </div>
      
      {/* Scrollable area to drive progress. 2500vh gives ~80-90 seconds of slow cinematic scrolling */}
      <div style={{ height: '2500vh', position: 'relative', zIndex: 1 }}>
        <Overlay />
      </div>
    </>
  )
}
