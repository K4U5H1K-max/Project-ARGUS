import React, { useState, useEffect } from 'react'
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
        left: '50%',
        width: '90%',
        maxWidth: '600px', // Restrain slightly for large empty cinematic center space
        transform: `translate(-50%, calc(-50% + ${y}px)) scale(${scale})`,
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
  const setView = useStore((state) => state.setView)
  const [isBooting, setIsBooting] = useState(false)
  const [isScrolling, setIsScrolling] = useState(false)
  const [hudExpanded, setHudExpanded] = useState(false)

  // Scroll detection to fade HUD panels
  useEffect(() => {
    let scrollTimeout;
    const handleScroll = () => {
      setIsScrolling(true)
      clearTimeout(scrollTimeout)
      scrollTimeout = setTimeout(() => {
        setIsScrolling(false)
      }, 300)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', handleScroll)
      clearTimeout(scrollTimeout)
    }
  }, [])

  const handleLaunch = () => {
    setIsBooting(true)
    setTimeout(() => {
      setView('dashboard')
    }, 1500)
  }

  const scrollingClass = isScrolling ? ' scrolling-fade' : '';

  return (
    <div className={`overlay-container-grid ${hudExpanded ? 'hud-drawer-open' : ''}`}>
      
      {/* ====================================================================
         LEFT COLUMN SIDEBAR (LOGO, NETWORK, DATA INGESTION)
         ==================================================================== */}
      <div className={`hud-sidebar left${scrollingClass}`}>
        <div className="hud-logo-wrapper">
          <div className="hud-logo">
            ARGUS <span className="hud-logo-sub">OS_CORE_V1.9</span>
          </div>
        </div>
        
        {/* Connected Network widget */}
        <div className="hud-widget">
          <div className="hud-widget-title">CONNECTED NETWORK</div>
          <div className="telemetry-row">
            <span className="telemetry-label">Active Plants</span>
            <span className="telemetry-value">05 / 05</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">Digital Twin</span>
            <span className="telemetry-value">SYNCED</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">System Health</span>
            <span className="telemetry-value">99.9%</span>
          </div>
        </div>
        
        {/* Data Ingestion widget */}
        <div className="hud-widget">
          <div className="hud-widget-title">DATA INGESTION</div>
          <div className="telemetry-row">
            <span className="telemetry-label">SCADA streams</span>
            <span className="telemetry-value">14,802 / S</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">CCTV analytics</span>
            <span className="telemetry-value">2,481 Cam</span>
          </div>
        </div>
      </div>

      {/* ====================================================================
         CENTER COLUMN (STORIES / STORYTELLING ONLY - PREVENTS SIDEBAR OVERLAPS)
         ==================================================================== */}
      <div className="storytelling-center-column">
        {/* Guided AI Briefing Scenes */}
        
        {/* Stage 1: Industrial Monitoring */}
        <SceneText id="scene-1" start={0} end={8} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--accent-ai)', paddingLeft: '2rem' }}>
            <div className="text-secondary" style={{ marginBottom: '0.5rem' }}>STAGE 01 // OVERVIEW</div>
            <h1 className="heading-giant">Project ARGUS</h1>
            <p className="body-large" style={{ marginTop: '1rem' }}>
              Mission-critical Industrial Safety Intelligence Platform.<br />
              Continuous digital twin risk mitigation for hazardous environments.
            </p>
          </div>
        </SceneText>

        <SceneText id="scene-2" start={9} end={17} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--border-color)', paddingLeft: '2rem' }}>
            <div className="text-secondary" style={{ marginBottom: '0.5rem' }}>STAGE 01 // SENSOR ENVIRONMENT</div>
            <h2 className="heading-large">Industrial Monitoring</h2>
            <p className="body-large" style={{ marginTop: '1.2rem' }}>
              Refineries, chemical yards, and mine shafts operate thousands of physical telemetry sensors,<br />
              continuously producing millions of variables per second.
            </p>
          </div>
        </SceneText>

        {/* Stage 2: Sensor Ingestion / Limits of Old Systems */}
        <SceneText id="scene-3" start={18} end={25} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--accent-danger)', paddingLeft: '2rem' }}>
            <div className="text-danger" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>WARN // SYSTEM LIMITATIONS</div>
            <h2 className="heading-large">The Danger of Isolated Alarms</h2>
            <p className="body-large" style={{ marginTop: '1.2rem' }}>
              Traditional SCADA threshold alarms operate in silos. A single temperature rise or proximity alert<br />
              fails to notify operators of complex, compounding safety risks.
            </p>
          </div>
        </SceneText>

        <SceneText id="scene-4" start={26} end={34} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--accent-ai)', paddingLeft: '2rem' }}>
            <div className="text-ai" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>INIT // SENSOR INGESTION</div>
            <h2 className="heading-large">Sensor Intelligence</h2>
            <p className="body-large" style={{ marginTop: '1.2rem' }}>
              ARGUS unifies telemetry pipelines. We continuously ingest SCADA values, smart wearables,<br />
              CCTV cameras, worker location coordinates, and Permit-to-Work logs.
          </p>
          </div>
        </SceneText>

        <SceneText id="scene-5" start={35} end={42} progress={progress}>
          <div className="industrial-card">
            <div className="text-secondary" style={{ marginBottom: '0.5rem' }}>DIGITAL TWIN PROTOCOL</div>
            <h2 className="heading-medium">Real-Time Core Sync</h2>
            <p className="body-large" style={{ marginTop: '0.75rem', fontSize: '1rem' }}>
              Ingested streams are mapped directly onto the live 3D twin of the facility, aligning telemetry data with structural physical coordinates.
            </p>
          </div>
        </SceneText>

        {/* Stage 3: Compound Risk Correlation */}
        <SceneText id="scene-6" start={43} end={50} progress={progress}>
          <div className="industrial-card" style={{ borderLeft: '4px solid var(--accent-danger)' }}>
            <div className="text-danger" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>EVALUATION // RISK ENVELOPE</div>
            <h2 className="heading-large text-danger" style={{ fontSize: '2.25rem' }}>Compound Risk Correlation</h2>
            <p className="body-large" style={{ marginTop: '0.75rem', fontSize: '1rem', color: 'var(--text-primary)' }}>
              Disasters are rarely caused by single anomalies. ARGUS correlates weak, distributed signals—such as gas accumulation coupled with a Hot Work Permit in the same zone.
            </p>
          </div>
        </SceneText>

        <SceneText id="scene-7" start={51} end={59} progress={progress}>
          <div className="industrial-card" style={{ borderLeft: '4px solid var(--accent-ai)' }}>
            <div className="text-ai" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>AI RISK SHIELD MODELING</div>
            <h2 className="heading-large text-ai" style={{ fontSize: '2.25rem' }}>Weak Signal Correlator</h2>
            <p className="body-large" style={{ marginTop: '0.75rem', fontSize: '1rem', color: 'var(--text-primary)' }}>
              We evaluate worker proximity to degrading machinery, or confined space entry levels during process variance, preventing accidents before critical limits are reached.
            </p>
          </div>
        </SceneText>

        {/* Stage 4: Predictive Intervention */}
        <SceneText id="scene-8" start={60} end={67} progress={progress}>
          <div className="industrial-card" style={{ borderLeft: '4px solid var(--accent-success)' }}>
            <div className="text-success" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>PREDICTIVE INTERVENTION</div>
            <h2 className="heading-large" style={{ fontSize: '2.25rem' }}>AI Risk Shield Engine</h2>
            <p className="body-large text-secondary" style={{ marginTop: '0.75rem', fontSize: '0.95rem' }}>
              The ARGUS Risk Shield runs 1,402 continuous predictive simulations per minute, forecasting risk progression curves to trigger preventative maintenance before alerts fire.
            </p>
          </div>
        </SceneText>

        {/* Stage 5: Autonomous Response */}
        <SceneText id="scene-9" start={68} end={75} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--border-color)', paddingLeft: '2rem' }}>
            <div className="text-secondary" style={{ marginBottom: '0.5rem' }}>MITIGATION DEPLOYMENT</div>
            <h2 className="heading-medium">Coordinated Response</h2>
            <p className="body-large" style={{ marginTop: '1rem', fontSize: '1.1rem' }}>
              Once a compound risk is confirmed, ARGUS alerts safety operators, provides actionable response workflows, routes emergency teams, and logs sensor files for compliance audits.
            </p>
          </div>
        </SceneText>

        {/* Stage 6: Zero Harm Mission */}
        <SceneText id="scene-10" start={76} end={84} progress={progress}>
          <div style={{ borderLeft: '4px solid var(--accent-success)', paddingLeft: '2rem' }}>
            <div className="text-success" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>MISSION OBJECTIVE</div>
            <h2 className="heading-large">Zero Harm Operations</h2>
            <p className="body-large" style={{ marginTop: '1.2rem' }}>
              We believe every worker has the right to return home safely.<br />
              AI-driven predictive intelligence turns safety compliance into guaranteed risk shield prevention.
            </p>
          </div>
        </SceneText>

        {/* Chapter 11: Final Reveal */}
        <SceneText id="scene-11" start={85} end={100} progress={progress}>
          <div className="industrial-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <div className="text-secondary" style={{ marginBottom: '0.25rem' }}>OVERVIEW REPORT // ARGUS OS CORE</div>
              <h2 className="heading-medium" style={{ textTransform: 'uppercase', fontSize: '1.75rem' }}>Security Protocol Active</h2>
            </div>
            <p className="body-large" style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>
              Digital twin is actively syncing with sensor grids. All predictive calculations nominal. Ready for operational supervisor dashboard inspection.
            </p>
            <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
              <div className="badge-status">
                STATUS: ZERO HARM
              </div>
              <button 
                className="btn-industrial"
                disabled={isBooting}
                onClick={handleLaunch}
                style={{ 
                  pointerEvents: 'auto', 
                  minWidth: '220px',
                  borderColor: isBooting ? 'var(--accent-ai)' : 'var(--border-color)',
                  boxShadow: isBooting ? '0 0 15px rgba(0, 124, 255, 0.2)' : 'none'
                }}
              >
                {isBooting ? 'INITIALIZING MISSION CONTROL...' : 'Explore Mission Control'}
              </button>
            </div>
          </div>
        </SceneText>
      </div>

      {/* ====================================================================
         RIGHT COLUMN SIDEBAR (SHIELD MONITORING, AI ENGINE, EVENTS MONITOR)
         ==================================================================== */}
      <div className={`hud-sidebar right${scrollingClass}`}>
        <div className="hud-top-right-wrapper" style={{ width: '100%' }}>
          <div className="hud-widget" style={{ padding: '0.6rem 0.8rem', background: 'rgba(10, 11, 13, 0.45)', border: '1px solid var(--border-color)', width: '100%' }}>
            <div className="hud-widget-title" style={{ border: 'none', padding: 0, margin: 0 }}>
              <span>SHIELD MONITORING</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.25rem' }}>
              <span className="telemetry-pulse-dot" style={{ backgroundColor: 'var(--accent-success)', boxShadow: '0 0 6px var(--accent-success)' }} />
              <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em' }}>AI ENGINE ONLINE</span>
            </div>
          </div>
        </div>
        
        {/* AI Engine Status widget */}
        <div className="hud-widget">
          <div className="hud-widget-title">AI ENGINE STATUS</div>
          <div className="telemetry-row">
            <span className="telemetry-label">Model status</span>
            <span className="telemetry-value text-success" style={{ fontWeight: 600 }}>NOMINAL</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">Prediction Int.</span>
            <span className="telemetry-value">99.2%</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">Sim Rate</span>
            <span className="telemetry-value">1,402 / M</span>
          </div>
        </div>

        {/* Events Monitor widget */}
        <div className="hud-widget">
          <div className="hud-widget-title">EVENTS MONITOR</div>
          <div className="telemetry-row">
            <span className="telemetry-label">Processed Today</span>
            <span className="telemetry-value">1,847,204</span>
          </div>
          <div className="telemetry-row">
            <span className="telemetry-label">Risk anomalies</span>
            <span className="telemetry-value text-warning">01 ACK</span>
          </div>
        </div>
      </div>

      {/* ====================================================================
         MOBILE DRAWER TRIGGER (REPOSITIONS EXISTING SIDEBAR NODES VIA CSS)
         ==================================================================== */}
      <div className="hud-mobile-toggle" onClick={() => setHudExpanded(!hudExpanded)}>
        <span className="telemetry-pulse-dot" style={{ backgroundColor: 'var(--accent-success)' }} />
        <span>{hudExpanded ? 'CLOSE TELEMETRY [TAP]' : 'SYS_STATUS: NOMINAL [TAP FOR TELEMETRY]'}</span>
      </div>

      {/* Global Status HUD Footer */}
      <footer className="hud-footer">
        <div>
          SYS_TIME: {new Date().toISOString().slice(0, 19).replace('T', ' ')} UTC
        </div>
        <div className="hud-status-indicator">
          <span>BRIEFING PROGRESS: {Math.floor(progress * 100)}%</span>
          <span style={{ color: 'var(--border-color)' }}>|</span>
          <span className={progress > 0.6 ? 'text-ai' : 'text-success'}>
            {progress > 0.6 ? 'SHIELD_DEPLOYED' : 'INITIALIZING'}
          </span>
          <span className={`status-dot ${progress > 0.6 ? 'active' : 'nominal'}`} />
        </div>
      </footer>
      
    </div>
  )
}
