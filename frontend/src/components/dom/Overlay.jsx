import React from 'react'
import { useStore } from '../../store/useStore'

// Cinematic easing functions
const easeInOutSine = (x) => -(Math.cos(Math.PI * x) - 1) / 2;
const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);

function SceneText({ children, start, end, id, progress }) {
  const s = start / 100
  const e = end / 100
  
  let opacity = 0
  let y = 40
  let blur = 20
  let scale = 0.95

  if (progress >= s && progress <= e) {
    const peak = (s + e) / 2
    const range = e - s
    
    if (progress < peak) {
      // Fade in
      const p = (progress - s) / (range / 2)
      const eased = easeOutCubic(p)
      opacity = eased
      y = 40 * (1 - eased)
      blur = 20 * (1 - eased)
      scale = 0.95 + (0.05 * eased)
    } else {
      // Fade out
      const p = (progress - peak) / (range / 2)
      const eased = easeInOutSine(p)
      opacity = 1 - eased
      y = -40 * eased
      blur = 20 * eased
      scale = 1 + (0.05 * eased)
    }
  }

  // Optimize rendering
  if (opacity <= 0.01 && progress > 0.01) return null

  // Hold first frame
  if (s === 0 && progress < 0.01) { opacity = 1; y = 0; blur = 0; scale = 1; }
  // Hold last frame
  if (e === 1 && progress > 0.99) { opacity = 1; y = 0; blur = 0; scale = 1; }

  return (
    <div 
      id={id}
      style={{
        position: 'absolute',
        top: '50%',
        left: '10%',
        width: '80%',
        transform: `translateY(calc(-50% + ${y}px)) scale(${scale})`,
        opacity: opacity,
        filter: `blur(${blur}px)`,
        willChange: 'opacity, transform, filter',
      }}
    >
      {children}
    </div>
  )
}

export default function Overlay() {
  const progress = useStore((state) => state.progress)

  return (
    <div className="overlay-container" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 10 }}>
      {/* Global Header */}
      <header style={{ position: 'absolute', top: '2.5rem', left: '3rem' }}>
        <div style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '0.2em' }} className="text-secondary">ARGUS</div>
      </header>

      {/* Global Status HUD */}
      <div style={{ position: 'absolute', bottom: '2.5rem', left: '3rem', fontSize: '0.85rem', letterSpacing: '0.1em', opacity: 0.5, fontFamily: 'monospace' }}>
        SYS_STATUS: {Math.floor(progress * 100)}% // {progress > 0.6 ? 'TWIN_ACTIVE' : 'NOMINAL'}
      </div>

      {/* Chapter 1: Intro */}
      <SceneText id="scene-1" start={0} end={8} progress={progress}>
        <h1 className="heading-giant">ARGUS</h1>
        <p className="body-large" style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>AI Powered Risk Guardian<br/>for Unified Safety</p>
      </SceneText>

      {/* Chapter 2: The Problem */}
      <SceneText id="scene-2" start={9} end={17} progress={progress}>
        <h2 className="heading-large">Every shift begins<br/>with trust.</h2>
      </SceneText>

      {/* Chapter 3: Failure */}
      <SceneText id="scene-3" start={18} end={25} progress={progress}>
        <h2 className="heading-large">Hidden risks rarely<br/>announce themselves.</h2>
      </SceneText>

      {/* Chapter 4: Twin Creation */}
      <SceneText id="scene-4" start={26} end={34} progress={progress}>
        <h2 className="heading-large">To prevent failure,<br/>we must map everything.</h2>
        <p className="body-large text-ai" style={{ marginTop: '1rem' }}>Initiating Digital Twin Protocol</p>
      </SceneText>

      {/* Chapter 5: Live Monitoring */}
      <SceneText id="scene-5" start={35} end={42} progress={progress}>
        <h2 className="heading-medium">Real-time Sensor Network</h2>
        <p className="body-large" style={{ marginTop: '1rem' }}>CCTV Intelligence & Telemetry Sync</p>
      </SceneText>

      {/* Chapter 6: Hidden Risk */}
      <SceneText id="scene-6" start={43} end={50} progress={progress}>
        <h2 className="heading-large text-danger">Anomaly Detected.</h2>
        <p className="body-large" style={{ marginTop: '1rem' }}>Thermal variance outside operational envelope.</p>
      </SceneText>

      {/* Chapter 7: Prediction Engine */}
      <SceneText id="scene-7" start={51} end={59} progress={progress}>
        <h2 className="heading-large text-ai">Prediction changes<br/>everything.</h2>
        <p className="body-large" style={{ marginTop: '1rem' }}>Simulating 1,402 failure vectors.</p>
      </SceneText>

      {/* Chapter 8: AI Intervention */}
      <SceneText id="scene-8" start={60} end={67} progress={progress}>
        <h2 className="heading-large">Emergency Response<br/>Automated.</h2>
        <p className="body-large text-success" style={{ marginTop: '1rem' }}>Routing safe operational path.</p>
      </SceneText>

      {/* Chapter 9: Key Features */}
      <SceneText id="scene-9" start={68} end={75} progress={progress}>
        <h2 className="heading-medium">Continuous Intelligence</h2>
        <p className="body-large" style={{ marginTop: '1rem' }}>Worker Safety • Machine Health • Heatmap Analytics</p>
      </SceneText>

      {/* Chapter 10: Impact */}
      <SceneText id="scene-10" start={76} end={84} progress={progress}>
        <h2 className="heading-large">Every worker deserves<br/>to return home.</h2>
      </SceneText>

      {/* Chapter 11: Final Reveal */}
      <SceneText id="scene-11" start={85} end={100} progress={progress}>
        <h2 className="heading-giant">ARGUS</h2>
        <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <div style={{ padding: '0.5rem 1rem', border: '1px solid var(--accent-success)', color: 'var(--accent-success)', borderRadius: '4px', letterSpacing: '0.1em', fontSize: '0.9rem' }}>
            STATUS: ZERO HARM
          </div>
          <button style={{ 
            pointerEvents: 'auto', 
            padding: '1rem 2rem', 
            background: 'var(--text-primary)', 
            color: 'var(--bg-color)', 
            border: 'none', 
            borderRadius: '4px', 
            fontSize: '1rem', 
            fontWeight: 600, 
            cursor: 'pointer',
            transition: 'opacity 0.3s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
          onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
          >
            Explore Mission Control
          </button>
        </div>
      </SceneText>
    </div>
  )
}
