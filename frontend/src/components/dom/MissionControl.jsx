import React, { useEffect, useState, useRef, useMemo } from 'react'
import { useStore } from '../../store/useStore'
import { 
  Shield,
  Clock, 
  Compass, 
  Database, 
  Thermometer, 
  Layers, 
  ChevronLeft, 
  ChevronRight
} from 'lucide-react'

// Mock sensors database
const SENSORS_DB = [
  { id: 'SNSR-T104', location: 'Zone C - Tank-04', type: 'Thermal', val: 142.4, unit: '°C', status: 'CRITICAL', health: 91, trend: 'UP' },
  { id: 'SNSR-P104', location: 'Zone C - Tank-04', type: 'Pressure', val: 24.8, unit: 'bar', status: 'CRITICAL', health: 94, trend: 'STABLE' },
  { id: 'SNSR-V120', location: 'Zone B - Rig-12', type: 'Vibration', val: 7.8, unit: 'mm/s', status: 'WARNING', health: 82, trend: 'UP' },
  { id: 'SNSR-T202', location: 'Zone B - Rig-12', type: 'Thermal', val: 88.2, unit: '°C', status: 'WARNING', health: 85, trend: 'STABLE' },
  { id: 'SNSR-G301', location: 'Zone A - Catalyst', type: 'Gas Lvl', val: 12.4, unit: 'ppm', status: 'NOMINAL', health: 99, trend: 'DOWN' },
  { id: 'SNSR-C01A', location: 'Zone A - Catalyst', type: 'Pressure', val: 14.2, unit: 'bar', status: 'NOMINAL', health: 99, trend: 'STABLE' },
  { id: 'SNSR-T01A', location: 'Zone A - Catalyst', type: 'Thermal', val: 342.1, unit: '°C', status: 'NOMINAL', health: 98, trend: 'UP' },
  { id: 'SNSR-V01B', location: 'Zone B - Shaft', type: 'Vibration', val: 1.8, unit: 'mm/s', status: 'NOMINAL', health: 99, trend: 'STABLE' },
  { id: 'SNSR-E404', location: 'Zone D - Elec Sub', type: 'Current', val: 412.5, unit: 'A', status: 'NOMINAL', health: 97, trend: 'STABLE' },
  { id: 'SNSR-T404', location: 'Zone D - Elec Sub', type: 'Thermal', val: 38.6, unit: '°C', status: 'NOMINAL', health: 99, trend: 'DOWN' }
]

// Mock Assets hierarchy databases
const ASSETS_HIERARCHY = {
  tanks: [
    { id: 'TANK-01', name: 'Feedstock Storage (Tank-01)', status: 'NOMINAL', temp: '24.1°C', pressure: '1.0 bar', vibration: '0.2 mm/s', health: 99, rul: '45,000 Hours (99%)', risk: '0.1%', last: '2026-07-02', fail: 'None', action: 'Routine scheduled check next quarter.' },
    { id: 'TANK-02', name: 'Catalyst Pre-Heater (Tank-02)', status: 'NOMINAL', temp: '110.5°C', pressure: '4.2 bar', vibration: '1.1 mm/s', health: 98, rul: '32,000 Hours (95%)', risk: '0.2%', last: '2026-07-05', fail: 'None', action: 'Routine cleaning on next turnaround.' },
    { id: 'TANK-03', name: 'Quench Separator (Tank-03)', status: 'NOMINAL', temp: '42.8°C', pressure: '2.1 bar', vibration: '0.8 mm/s', health: 99, rul: '38,000 Hours (97%)', risk: '0.1%', last: '2026-07-08', fail: 'None', action: 'Monitor level control valve performance.' },
    { id: 'TANK-04', name: 'Thermal Reactor Vessel (Tank-04)', status: 'CRITICAL', temp: '142.4°C', pressure: '24.8 bar', vibration: '11.4 mm/s', health: 21, rul: '180 Hours (2.1%)', risk: '94.2%', last: '2026-07-15', fail: 'Thermal runaway leading to core structural rupture', action: 'Emergency bypass: Trigger auxiliary cooling valves in Zone C and depressurize catalyst core.' }
  ],
  pumps: [
    { id: 'PUMP-01', name: 'Catalyst Feed Pump (Pump-01)', status: 'NOMINAL', temp: '38.2°C', pressure: '6.2 bar', vibration: '1.2 mm/s', health: 99, rul: '28,000 Hours (98%)', risk: '0.1%', last: '2026-06-15', fail: 'None', action: 'Inspect seal oil pot level.' },
    { id: 'PUMP-02', name: 'Recycle Gas Compressor (Pump-02)', status: 'NOMINAL', temp: '55.1°C', pressure: '12.8 bar', vibration: '2.4 mm/s', health: 97, rul: '18,500 Hours (91%)', risk: '0.3%', last: '2026-06-20', fail: 'None', action: 'Log motor windings insulation resistance.' },
    { id: 'PUMP-03', name: 'Cooling Water Circulator (Pump-03)', status: 'NOMINAL', temp: '32.4°C', pressure: '3.5 bar', vibration: '1.4 mm/s', health: 99, rul: '22,000 Hours (97%)', risk: '0.1%', last: '2026-06-25', fail: 'None', action: 'Check discharge strainer differential pressure.' },
    { id: 'PUMP-06', name: 'Rig-12 Hydraulic Pump (Pump-06)', status: 'WARNING', temp: '88.2°C', pressure: '4.8 bar', vibration: '7.8 mm/s', health: 68, rul: '4,200 Hours (68.1%)', risk: '14.2%', last: '2026-06-22', fail: 'Vibration displacement misalignment', action: 'Calibrate pump shaft alignment and grease motor bearing housings.' }
  ],
  pipelines: [
    { id: 'PIPE-A', name: 'Main Catalyst Inlet Pipe-A', status: 'NOMINAL', temp: '342.1°C', pressure: '14.2 bar', vibration: '2.4 mm/s', health: 98, rul: '18,400 Hours', risk: '0.1%', last: '2026-07-10', fail: 'None', action: 'Schedule ultrasonic thickness testing.' },
    { id: 'PIPE-B', name: 'Zone B Compressors Header Line-B', status: 'NOMINAL', temp: '45.1°C', pressure: '2.1 bar', vibration: '1.8 mm/s', health: 99, rul: '24,000 Hours', risk: '0.4%', last: '2026-06-22', fail: 'None', action: 'Check hanger support springs deflection.' }
  ],
  valves: [
    { id: 'VALVE-01', name: 'Emergency Depressurization Valve-01', status: 'NOMINAL', temp: '38.2°C', pressure: '14.2 bar', vibration: '0.1 mm/s', health: 99, rul: '50,000 Hours', risk: '0.1%', last: '2026-07-10', fail: 'None', action: 'Stroke-test valve during next maintenance shut-down.' },
    { id: 'VALVE-12', name: 'Aux Cooling Bypass Valve-12', status: 'WARNING', temp: '82.5°C', pressure: '4.8 bar', vibration: '3.1 mm/s', health: 74, rul: '8,400 Hours', risk: '8.4%', last: '2026-07-12', fail: 'Actuator diaphragm minor leakage', action: 'Replace valve actuator diaphragm at next opportunity.' }
  ]
}

const TIMELINE_EVENTS = [
  // Upcoming Predicted Events
  { id: 101, time: '08:45 (Predicted)', category: 'predicted', title: 'Electrical Substation over-load', zone: 'Zone D - Substation 4', conf: '99.2%', risk: 'WARNING', text: 'Bypass auxiliary load transformers and inspect breaker coils.', action: 'Deploy maintenance crew for load shedding sequence.', timeToInc: '14 Hours' },
  { id: 102, time: '08:35 (Predicted)', category: 'predicted', title: 'Cooling fluid filter clog', zone: 'Zone B - Node-06 Compressor', conf: '88.4%', risk: 'WARNING', text: 'Calibrate pump shaft alignment and clear fluid strainer.', action: 'Activate filter backwash valves remotely.', timeToInc: '3.5 Hours' },
  
  // Past Events (Stabilization lifecycle)
  { id: 1, time: '08:24', category: 'past', title: 'Reactor stabilized', zone: 'Zone C - Tank-04', conf: '100%', risk: 'NOMINAL', text: 'Core temperature cooled below 120°C. Pressure returned to 14.2 bar.', action: 'Coolant circulation active. Safety risk coefficient dropped to 0.1%. Hot work permit paused.', timeToInc: 'N/A' },
  { id: 2, time: '08:22', category: 'past', title: 'Supervisor Alert Sent', zone: 'Zone C - Tank-04', conf: '100%', risk: 'WARNING', text: 'Smart wearables notified. Safety operators dispatched to Zone C.', action: 'Supervisor smart-watch bands vibrated with action checklist: Verify Valve C3 override.', timeToInc: 'N/A' },
  { id: 3, time: '08:21', category: 'past', title: 'Mitigation Recommended', zone: 'Zone C - Tank-04', conf: '99.5%', risk: 'NOMINAL', text: 'AI executes cooling valve bypass and depressurization sequence.', action: 'Rerouting flow loops to Zone C auxiliary heat exchangers. Depressurization valve #C3 triggered.', timeToInc: 'N/A' },
  { id: 4, time: '08:20', category: 'past', title: 'Prediction Engine Activated', zone: 'Zone C - Tank-04', conf: '94.2%', risk: 'CRITICAL', text: 'Vessel structural limits forecasted at 180 min useful life.', action: 'Thermodynamic modeling predicts reactor rupture if temperature continues to climb past 155°C.', timeToInc: 'N/A' },
  { id: 5, time: '08:19', category: 'past', title: 'Compound Risk Correlated', zone: 'Zone C - Tank-04', conf: '94.2%', risk: 'CRITICAL', text: 'AI Risk Engine matches temperature spike with active Permit #804.', action: 'Coincidence of high heat, pressure, and hot work activity in Zone C raises risk index to 94.2%.', timeToInc: 'N/A' },
  { id: 6, time: '08:17', category: 'past', title: 'Gas concentration rising', zone: 'Zone A - Catalyst', conf: '100%', risk: 'WARNING', text: 'Gas sensors detect minor trace leakage near Catalyst conduit.', action: 'Trace concentrations of toxic catalyst vapors logged at 12.4 ppm. Smart bands warn adjacent personnel.', timeToInc: 'N/A' },
  { id: 7, time: '08:15', category: 'past', title: 'Pressure increase confirmed', zone: 'Zone C - Tank-04', conf: '100%', risk: 'CRITICAL', text: 'Pressure sensors in Tank-04 confirm rise to 24.8 bar.', action: 'Expansion chamber relief valves failed to actuate automatically. Safety override engaged.', timeToInc: 'N/A' },
  { id: 8, time: '08:13', category: 'past', title: 'Temperature anomaly detected', zone: 'Zone C - Tank-04', conf: '100%', risk: 'CRITICAL', text: 'Sensor SNSR-T104 in Zone C registered 142.4°C (Limit: 130°C).', action: 'Primary Reactor core heating coils experienced unexpected resistance spike. Diagnostic logs dispatched.', timeToInc: 'N/A' }
]

export default function MissionControl() {
  const setView = useStore((state) => state.setView)
  const setProgressState = useStore((state) => state.setProgress)
  const activeTab = useStore((state) => state.activeTab)
  const setActiveTab = useStore((state) => state.setActiveTab)
  const selectedEquipment = useStore((state) => state.selectedEquipment)
  const setSelectedEquipment = useStore((state) => state.setSelectedEquipment)

  // Real-time ticking indicators
  const [liveTime, setLiveTime] = useState(new Date())
  const [eventsProcessed, setEventsProcessed] = useState(1847204)
  const [riskScore, setRiskScore] = useState(1.41)
  const [sensors, setSensors] = useState(SENSORS_DB)
  const [search, setSearch] = useState('')
  const [sortCol, setSortCol] = useState(null)
  const [sortAsc, setSortAsc] = useState(true)
  const [statusFilter, setStatusFilter] = useState('ALL')

  // Heatmap settings
  const [heatmapMetric, setHeatmapMetric] = useState('temp')
  const [heatmapRefresh, setHeatmapRefresh] = useState(true)

  // Timeline filters
  const [timelineFilter, setTimelineFilter] = useState('ALL') // 'ALL' | 'CRITICAL' | 'WARNING' | 'NOMINAL'
  const [hoveredTimelineId, setHoveredTimelineId] = useState(null)

  // Asset sync logs (Digital Twin)
  const [syncLogs, setSyncLogs] = useState([
    { id: 1, text: '[SYNC] SCADA core telemetry stream synchronized in 4ms.', type: 'info' },
    { id: 2, text: '[AI] Remaining Useful Life (RUL) calculated for Tank-04: 180 operating hours remaining.', type: 'ai' },
    { id: 3, text: '[SENSOR] Thermal sensor SNSR-T104 value registered: 142.4°C.', type: 'warning' },
    { id: 4, text: '[OPERATOR] Operator acknowledged Tank-04 alert state.', type: 'success' }
  ])

  // Copilot assistant panel states
  const [copilotCollapsed, setCopilotCollapsed] = useState(true)
  const [chatMessages, setChatMessages] = useState([
    { text: 'ARGUS AI Copilot initialized. Select a safety query below or prompt details.', type: 'ai' }
  ])
  const [isTyping, setIsTyping] = useState(false)
  const chatEndRef = useRef(null)

  // Active alerts list state (interactive)
  const [alerts, setAlerts] = useState([
    { id: 1, title: 'Thermal Deviation in Zone C', desc: 'Vessel Tank-04 thermal readings outside standard nominal range (exceeded +12°C). AI Rerouted.', status: 'CRITICAL', ack: false },
    { id: 2, title: 'Proximity Warning in Zone B', desc: 'Personnel wearing smart band #124 detected within 1.5m zone of active mechanical rig #12.', status: 'WARNING', ack: false },
    { id: 3, title: 'Permit-to-Work Incongruity Checked', desc: 'Hot work permit identified in Zone A alongside trace carbon sensors check.', status: 'INFO', ack: false }
  ])

  // Live ticking values simulating telemetry sync
  useEffect(() => {
    const timer = setInterval(() => {
      setLiveTime(new Date())
      setEventsProcessed(prev => prev + Math.floor(Math.random() * 4) + 1)
      setRiskScore(prev => +(prev + (Math.random() * 0.04 - 0.02)).toFixed(2))
      
      // Fluctuated sensor readings
      setSensors(prev => prev.map(sensor => {
        if (Math.random() > 0.6) {
          const delta = (Math.random() * 0.4 - 0.2)
          return {
            ...sensor,
            val: +(sensor.val + delta).toFixed(1),
            lastUpdated: new Date().toLocaleTimeString()
          }
        }
        return sensor
      }))

      // Rotate sync logs inside digital twin bottom log console
      if (Math.random() > 0.7) {
        const mockMsgs = [
          { text: `[SYNC] Database synced. Active plant telemetry streams nominal.`, type: 'info' },
          { text: `[AI] Recalculating threat metrics: Compound risk coefficient is stable.`, type: 'ai' },
          { text: `[SENSOR] Proximity coordinates updated for smart band #124 in Sector B.`, type: 'info' },
          { text: `[OPERATOR] System health checklist verification checked nominal.`, type: 'success' },
          { text: `[SENSOR] Pressure valve valve-12 output registered: 4.8 bar.`, type: 'warning' }
        ]
        const choice = mockMsgs[Math.floor(Math.random() * mockMsgs.length)]
        setSyncLogs(prev => [
          ...prev.slice(1),
          { id: Date.now(), text: choice.text, type: choice.type }
        ])
      }
    }, 2500)
    
    return () => clearInterval(timer)
  }, [])

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [chatMessages, isTyping])

  // Reset progress and return back to the scrollytelling path
  const handleReturnToBriefing = () => {
    window.scrollTo(0, 0)
    setProgressState(0)
    setView('briefing')
  }

  // Acknowledge alert click handler
  const handleAcknowledgeAlert = (id) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, ack: true } : a))
  }

  // Sorting helper for sensor table
  const handleSort = (col) => {
    const isAsc = sortCol === col ? !sortAsc : true
    setSortCol(col)
    setSortAsc(isAsc)
    
    const sorted = [...sensors].sort((a, b) => {
      const valA = a[col]
      const valB = b[col]
      if (typeof valA === 'number') {
        return isAsc ? valA - valB : valB - valA
      }
      return isAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA))
    })
    setSensors(sorted)
  }

  // Filtered sensors dataset
  const filteredSensors = useMemo(() => {
    return sensors.filter(s => {
      const matchSearch = s.id.toLowerCase().includes(search.toLowerCase()) || 
                          s.location.toLowerCase().includes(search.toLowerCase()) ||
                          s.type.toLowerCase().includes(search.toLowerCase())
      const matchStatus = statusFilter === 'ALL' ? true : s.status === statusFilter
      return matchSearch && matchStatus
    })
  }, [sensors, search, statusFilter])

  // Filtered Timeline events (Past & Predicted)
  const filteredTimelineEvents = useMemo(() => {
    return TIMELINE_EVENTS.filter(e => {
      if (timelineFilter === 'ALL') return true
      if (timelineFilter === 'CRITICAL') return e.risk === 'CRITICAL'
      if (timelineFilter === 'WARNING') return e.risk === 'WARNING'
      if (timelineFilter === 'NOMINAL') return e.risk === 'NOMINAL'
      return true
    })
  }, [timelineFilter])

  // Heatmap parameters mapping based on metric
  const heatmapData = useMemo(() => {
    switch (heatmapMetric) {
      case 'gas':
        return {
          title: 'Catalyst Gas Concentration (ppm)',
          scale: '0 - 100 ppm',
          avg: '14.8 ppm',
          highestZone: 'Sector A: Reaction Catalyst (12.4 ppm)',
          zones: [
            { id: 'A', name: 'Sector A: Reaction Catalyst', color: '#F59E0B', val: '12.4 ppm', desc: 'Organic solvents' },
            { id: 'B', name: 'Sector B: Compressors Rig', color: '#10B981', val: '2.1 ppm', desc: 'Nominal baseline' },
            { id: 'C', name: 'Sector C: Reactor Tank core', color: '#007CFF', val: '0.4 ppm', desc: 'Purged' },
            { id: 'D', name: 'Sector D: Electrical station', color: '#007CFF', val: '0.1 ppm', desc: 'Secure' }
          ],
          hotspots: [
            { loc: 'Zone A - Pipe joint #3', val: '24.1 ppm', conf: '94%', response: 'Deploy sensor technician to examine structural gaskets.' },
            { loc: 'Zone B - Compressor exhaust', val: '12.8 ppm', conf: '81%', response: 'Routine ventilation sweep scheduled.' }
          ]
        }
      case 'press':
        return {
          title: 'Hydraulic System Pressure (bar)',
          scale: '0 - 50 bar',
          avg: '11.3 bar',
          highestZone: 'Sector C: Reactor Tank core (24.8 bar)',
          zones: [
            { id: 'A', name: 'Sector A: Reaction Catalyst', color: '#F59E0B', val: '14.2 bar', desc: 'Standard operating' },
            { id: 'B', name: 'Sector B: Compressors Rig', color: '#007CFF', val: '2.1 bar', desc: 'Standby' },
            { id: 'C', name: 'Sector C: Reactor Tank core', color: '#EF4444', val: '24.8 bar', desc: 'Over-pressure threshold' },
            { id: 'D', name: 'Sector D: Electrical station', color: '#007CFF', val: '0.0 bar', desc: 'Atmospheric' }
          ],
          hotspots: [
            { loc: 'Zone C - Tank-04 Core Valve', val: '24.8 bar', conf: '99%', response: 'Emergency bypass: Trigger auxiliary cooling valves.' },
            { loc: 'Zone A - Catalyst Pump Core', val: '14.2 bar', conf: '89%', response: 'Observe outlet pressure differential indicator.' }
          ]
        }
      case 'stress':
        return {
          title: 'Structural Strain Coefficients (μm/m)',
          scale: '0 - 1000 μm/m',
          avg: '124 μm/m',
          highestZone: 'Sector B: Compressors Rig (320 μm/m)',
          zones: [
            { id: 'A', name: 'Sector A: Reaction Catalyst', color: '#10B981', val: '45 μm/m', desc: 'Rigid platform' },
            { id: 'B', name: 'Sector B: Compressors Rig', color: '#F59E0B', val: '320 μm/m', desc: 'Vibratory load shift' },
            { id: 'C', name: 'Sector C: Reactor Tank core', color: '#10B981', val: '112 μm/m', desc: 'Symmetrical expand' },
            { id: 'D', name: 'Sector D: Electrical station', color: '#10B981', val: '12 μm/m', desc: 'Zero drift' }
          ],
          hotspots: [
            { loc: 'Zone B - Compressor Rig Shaft', val: '320 μm/m', conf: '88%', response: 'Calibrate pump shaft alignment and grease motor housing.' },
            { loc: 'Zone C - Vessel foundation ring', val: '112 μm/m', conf: '74%', response: 'Monitor strain gauge readings on next shift.' }
          ]
        }
      case 'occup':
        return {
          title: 'Personnel Location Occupancy Density',
          scale: '0 - 10 Personnel',
          avg: '4 Active smartbands',
          highestZone: 'Sector D: Electrical Substation (3 smartbands)',
          zones: [
            { id: 'A', name: 'Sector A: Reaction Catalyst', color: '#10B981', val: '0 smartbands', desc: 'Cleared zone' },
            { id: 'B', name: 'Sector B: Compressors Rig', color: '#F59E0B', val: '1 smartband', desc: 'Maintenance' },
            { id: 'C', name: 'Sector C: Reactor Tank core', color: '#007CFF', val: '0 smartbands', desc: 'Bypassed' },
            { id: 'D', name: 'Sector D: Electrical station', color: '#EF4444', val: '3 smartbands', desc: 'Shift rotation' }
          ],
          hotspots: [
            { loc: 'Zone D - Electrical Substation Room', val: '3 Smartbands', conf: '100%', response: 'Log crew names: R. Madhu, K. Kaushik, S. Nair.' },
            { loc: 'Zone B - Rig-12 Platform Gantry', val: '1 Smartband', conf: '99%', response: 'Confirm Hot Work Permit pt-804 verification.' }
          ]
        }
      case 'temp':
      default:
        return {
          title: 'Thermal Core Readings (°C)',
          scale: '0 - 400°C',
          avg: '68.4°C',
          highestZone: 'Sector C: Reactor Tank core (142.4°C)',
          zones: [
            { id: 'A', name: 'Sector A: Reaction Catalyst', color: '#10B981', val: '42°C', desc: 'Ambient cooling active' },
            { id: 'B', name: 'Sector B: Compressors Rig', color: '#F59E0B', val: '88°C', desc: 'Compressor node warning' },
            { id: 'C', name: 'Sector C: Reactor Tank core', color: '#EF4444', val: '142°C', desc: 'Vessel anomaly spike' },
            { id: 'D', name: 'Sector D: Electrical station', color: '#007CFF', val: '38°C', desc: 'Cabinet nominal' }
          ],
          hotspots: [
            { loc: 'Zone C - Tank-04 Reactor Vessel', val: '142.4°C', conf: '94%', response: 'Depressurize and activate Zone C aux cooling bypass valves.' },
            { loc: 'Zone B - Compressor Rig Node-06', val: '88.2°C', conf: '88%', response: 'Calibrate pump shaft alignment and grease motor housing.' }
          ]
        }
    }
  }, [heatmapMetric])

  // Copilot preset question click handler
  const handleCopilotQuestion = (question, answer) => {
    if (isTyping) return
    setChatMessages(prev => [...prev, { text: question, type: 'user' }])
    setIsTyping(true)

    setTimeout(() => {
      setIsTyping(false)
      setChatMessages(prev => [...prev, { text: answer, type: 'ai' }])
    }, 1200)
  }

  // Camera mock operations console triggers (Digital Twin Workspace HUD)
  const handleCameraOp = (op) => {
    const timestamp = new Date().toLocaleTimeString()
    setSyncLogs(prev => [
      ...prev.slice(1),
      { id: Date.now(), text: `[OPERATOR] Camera operation executed: ${op} at ${timestamp}`, type: 'success' }
    ])
  }

  return (
    <div className="dashboard-screen">
      <div className="crt-overlay" />

      {/* ====================================================================
         TOP NAVIGATION BAR
         ==================================================================== */}
      <header className="dashboard-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '2.5rem' }}>
          <div className="hud-logo">
            ARGUS <span className="hud-logo-sub">MC_OS_V1.9</span>
          </div>

          <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center', borderLeft: '1px solid var(--border-color)', paddingLeft: '2rem' }}>
            <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
              <span className="text-secondary">FACILITY:</span> CO-LOC_04
            </div>
            <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
              <span className="text-secondary">SHIFT:</span> B (06:00 - 14:00)
            </div>
            <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
              <span className="text-secondary">SHIELD:</span> <span className="text-ai" style={{ fontWeight: 600 }}>ACTIVE</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderRight: '1px solid var(--border-color)', paddingRight: '1.5rem' }}>
            <span className="telemetry-pulse-dot" style={{ backgroundColor: 'var(--accent-success)', boxShadow: '0 0 6px var(--accent-success)' }} />
            <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>SYS_OS: NOMINAL</span>
          </div>
          
          <div style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
            {liveTime.toLocaleTimeString()} UTC
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', pointerEvents: 'auto' }}>
            <button className="btn-industrial" style={{ padding: '0.4rem 0.8rem', fontSize: '0.7rem' }} onClick={handleReturnToBriefing}>
              Return to Briefing
            </button>
          </div>
        </div>
      </header>

      {/* ====================================================================
         MAIN COMMAND CENTER CONTENT
         ==================================================================== */}
      <div className="dashboard-layout" style={{ gap: '1.5rem' }}>
        
        {/* LEFT NAVIGATION SIDEBAR */}
        <aside className="dashboard-sidebar-panel" style={{ width: '220px' }}>
          <div className="hud-widget" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem', background: 'rgba(12, 14, 18, 0.85)' }}>
            <div>
              <div className="hud-widget-title">NAVIGATION CORE</div>
              <ul className="sidebar-nav-list">
                {[
                  { id: 'overview', label: 'Overview', icon: <Compass size={14} /> },
                  { id: 'twin', label: 'Digital Twin', icon: <Layers size={14} /> },
                  { id: 'sensors', label: 'Sensor Network', icon: <Database size={14} /> },
                  { id: 'predictions', label: 'AI Predictions', icon: <Shield size={14} /> },
                  { id: 'timeline', label: 'Risk Timeline', icon: <Clock size={14} /> },
                  { id: 'heatmap', label: 'Thermal Heatmap', icon: <Thermometer size={14} /> }
                ].map((item) => (
                  <li key={item.id} className="sidebar-nav-item">
                    <button 
                      className={`sidebar-nav-btn ${activeTab === item.id ? 'active' : ''}`}
                      onClick={() => {
                        setActiveTab(item.id)
                        setSelectedEquipment(null) // clear selected mesh details
                      }}
                    >
                      {item.icon}
                      <span>{item.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ marginTop: 'auto' }}>
              <div className="hud-widget-title">OS METADATA</div>
              <div className="telemetry-row">
                <span className="telemetry-label">Events</span>
                <span className="telemetry-value">{eventsProcessed.toLocaleString()}</span>
              </div>
              <div className="telemetry-row">
                <span className="telemetry-label">OS_V</span>
                <span className="telemetry-value">1.9.2</span>
              </div>
              <div className="telemetry-row">
                <span className="telemetry-label">Sec_L</span>
                <span className="telemetry-value text-success">HIGH</span>
              </div>
            </div>
          </div>
        </aside>

        {/* CENTER COLUMN WORKSPACE */}
        <main className="dashboard-main-view" style={{ flex: 1 }}>
          
          {/* TAB PANEL 1: OVERVIEW DASHBOARD */}
          {activeTab === 'overview' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto' }}>
              <div className="overview-grid">
                <div className="hud-widget">
                  <div className="hud-widget-title">TOTAL INGESTED SENSORS</div>
                  <div className="info-card-value text-primary">14,957</div>
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-success)' }}>● 14,802 SENSOR STR. NOMINAL</div>
                </div>
                <div className="hud-widget">
                  <div className="hud-widget-title">OFFLINE CHANNELS</div>
                  <div className="info-card-value text-danger">00</div>
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>ALL SCADA STREAMS DETECTED</div>
                </div>
                <div className="hud-widget">
                  <div className="hud-widget-title">PREDICTION ACCURACY</div>
                  <div className="info-card-value text-ai">99.24%</div>
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>EVALUATING 1,402 COGNITIVE VECTOR PATHS</div>
                </div>
                <div className="hud-widget">
                  <div className="hud-widget-title">FACILITY RISK INDEX</div>
                  <div className="info-card-value text-warning">{riskScore}%</div>
                  <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-success)' }}>OSHA STANDARDS COMPLIANT</div>
                </div>
              </div>

              <div className="industrial-card" style={{ flex: 1 }}>
                <div className="hud-widget-title" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
                  <span>AI RISK INTELLIGENCE STATUS REPORT</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Real-time Digital Twin Synchronization</h3>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '1.5rem' }}>
                      ARGUS continuously integrates SCADA values, smart wearables, and computer vision streams, matching them against active maintenance logs. 
                      Click the **Digital Twin** tab in the navigation menu to unlock interactive orbit inspect tools and query individual parts.
                    </p>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <button className="btn-industrial" onClick={() => setActiveTab('twin')}>Inspect Twin</button>
                      <button className="btn-industrial" onClick={() => setActiveTab('sensors')}>Live Grid</button>
                    </div>
                  </div>
                  <div className="hud-widget" style={{ background: 'rgba(0,0,0,0.1)' }}>
                    <div className="hud-widget-title">OSHA ZERO HARM COMPLIANCE</div>
                    <div className="telemetry-row"><span className="telemetry-label">Conformity Index</span><span className="telemetry-value">99.98%</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Active Permits</span><span className="telemetry-value">14 Node-Permits</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Incidents Today</span><span className="telemetry-value text-success">0</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Mitigation Status</span><span className="telemetry-value text-success">AUTOMATED</span></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB PANEL 2: DIGITAL TWIN INTEGRATED INSPECTION WORKSPACE */}
          {activeTab === 'twin' && (
            <div className="twin-workspace-container">
              
              {/* Left Side Hierarchy Explorer */}
              <div className="hud-widget twin-left-panel">
                <div style={{ flex: 1 }}>
                  <div className="hud-widget-title" style={{ marginBottom: '0.75rem' }}>Hierarchy Explorer</div>
                  
                  {/* Tanks group */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.35rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.2rem' }}>TANKS</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {ASSETS_HIERARCHY.tanks.map(t => (
                        <button 
                          key={t.id} 
                          className={`sidebar-nav-btn ${selectedEquipment?.name.includes(t.id) ? 'active' : ''}`}
                          style={{ padding: '0.35rem 0.5rem', fontSize: '0.7rem' }}
                          onClick={() => setSelectedEquipment(t)}
                        >
                          <span className={t.status === 'CRITICAL' ? 'text-danger' : 'text-primary'}>■</span> {t.id}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Pumps group */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.35rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.2rem' }}>PUMPS</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {ASSETS_HIERARCHY.pumps.map(p => (
                        <button 
                          key={p.id} 
                          className={`sidebar-nav-btn ${selectedEquipment?.name.includes(p.id) ? 'active' : ''}`}
                          style={{ padding: '0.35rem 0.5rem', fontSize: '0.7rem' }}
                          onClick={() => setSelectedEquipment(p)}
                        >
                          <span className={p.status === 'WARNING' ? 'text-warning' : 'text-primary'}>■</span> {p.id}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Pipelines group */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.35rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.2rem' }}>PIPELINES</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {ASSETS_HIERARCHY.pipelines.map(l => (
                        <button 
                          key={l.id} 
                          className={`sidebar-nav-btn ${selectedEquipment?.name.includes(l.id) ? 'active' : ''}`}
                          style={{ padding: '0.35rem 0.5rem', fontSize: '0.7rem' }}
                          onClick={() => setSelectedEquipment(l)}
                        >
                          <span>■</span> {l.id}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Valves group */}
                  <div>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.35rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.2rem' }}>VALVES</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {ASSETS_HIERARCHY.valves.map(v => (
                        <button 
                          key={v.id} 
                          className={`sidebar-nav-btn ${selectedEquipment?.name.includes(v.id) ? 'active' : ''}`}
                          style={{ padding: '0.35rem 0.5rem', fontSize: '0.7rem' }}
                          onClick={() => setSelectedEquipment(v)}
                        >
                          <span className={v.status === 'WARNING' ? 'text-warning' : 'text-primary'}>■</span> {v.id}
                        </button>
                      ))}
                    </div>
                  </div>

                </div>
              </div>

              {/* Center Viewport Placeholder area */}
              <div className="twin-center-viewport">
                
                <div className="twin-viewport-placeholder">
                  {/* Subtle scan grid lines showing in placeholder layout */}
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundImage: 'radial-gradient(rgba(0,124,255,0.02) 1.5px, transparent 1.5px)', backgroundSize: '16px 16px', pointerEvents: 'none' }} />
                  
                  {/* Instructions badge */}
                  <div style={{ textAlign: 'center', zIndex: 1, pointerEvents: 'none', background: 'rgba(8, 9, 11, 0.85)', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '2px', maxWidth: '340px' }}>
                    <div className="text-ai" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.1em' }}>3D INTERACTION CORE ACTIVE</div>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.5rem', lineHeight: '1.4' }}>
                      The background Canvas is active. Drag mouse outside overlays to rotate, scroll to zoom, or click components directly on the 3D model.
                    </p>
                  </div>

                  {/* Camera Controls HUD Overlay */}
                  <div className="twin-camera-controls-hud">
                    <button className="btn-industrial" style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem' }} onClick={() => handleCameraOp('Zoom In')}>Zoom +</button>
                    <button className="btn-industrial" style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem' }} onClick={() => handleCameraOp('Zoom Out')}>Zoom -</button>
                    <button className="btn-industrial" style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem' }} onClick={() => handleCameraOp('Orbit Left')}>Rotate L</button>
                    <button className="btn-industrial" style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem' }} onClick={() => handleCameraOp('Orbit Right')}>Rotate R</button>
                    <button className="btn-industrial" style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem', borderColor: 'var(--accent-ai)' }} onClick={() => handleCameraOp('Camera Reset')}>Reset Camera</button>
                  </div>
                </div>

                {/* Bottom Event Log */}
                <div className="twin-bottom-log">
                  <div className="hud-widget-title" style={{ paddingBottom: '0.2rem', marginBottom: '0.4rem', fontSize: '0.65rem', border: 'none' }}>
                    <span>Active Synchronization Logs</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                    {syncLogs.map((log) => (
                      <div key={log.id} style={{ color: log.type === 'warning' ? 'var(--accent-warning)' : log.type === 'ai' ? 'var(--accent-ai)' : log.type === 'success' ? 'var(--accent-success)' : 'var(--text-secondary)' }}>
                        {log.text}
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* Right Side Asset details Inspector */}
              <div className="hud-widget twin-right-inspector">
                <div className="hud-widget-title" style={{ paddingBottom: '0.4rem', marginBottom: '0.6rem' }}>
                  <span>Asset Inspector</span>
                </div>

                {!selectedEquipment ? (
                  <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '1rem' }}>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', lineHeight: '1.4' }}>
                      SELECT ANY ASSET FROM THE LEFT HIERARCHY TREE OR CLICK THE 3D MODEL DIRECTLY TO COMMENCE TELEMETRY AUDIT.
                    </p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.75rem' }}>
                    <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                      <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>ASSET CLASS</div>
                      <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.15rem' }}>{selectedEquipment.name}</h4>
                    </div>

                    <div className="telemetry-row"><span className="telemetry-label">Asset ID</span><span className="telemetry-value" style={{ fontFamily: 'var(--font-mono)' }}>{selectedEquipment.id}</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Health status</span><span className={`telemetry-value ${selectedEquipment.status === 'CRITICAL' ? 'text-danger' : selectedEquipment.status === 'WARNING' ? 'text-warning' : 'text-success'}`} style={{ fontWeight: 600 }}>{selectedEquipment.health}% ({selectedEquipment.status})</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Temperature</span><span className="telemetry-value">{selectedEquipment.temp}</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Pressure</span><span className="telemetry-value">{selectedEquipment.pressure}</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Vibration</span><span className="telemetry-value">{selectedEquipment.vibration}</span></div>

                    <div style={{ borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                      <div className="telemetry-row"><span className="telemetry-label">Maintenance status</span><span className="telemetry-value">{selectedEquipment.status === 'CRITICAL' ? 'OVERDUE' : 'NOMINAL'}</span></div>
                      <div className="telemetry-row"><span className="telemetry-label">Remaining Life</span><span className="telemetry-value text-success" style={{ fontWeight: 600 }}>{selectedEquipment.rul}</span></div>
                      <div className="telemetry-row"><span className="telemetry-label">Risk index</span><span className={`telemetry-value ${selectedEquipment.status === 'CRITICAL' ? 'text-danger' : 'text-primary'}`} style={{ fontWeight: 600 }}>{selectedEquipment.risk}</span></div>
                      <div className="telemetry-row"><span className="telemetry-label">Last Inspection</span><span className="telemetry-value">{selectedEquipment.last}</span></div>
                    </div>

                    <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                      <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>PREDICTED ANOMALY ANALYSIS:</div>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-primary)', marginTop: '0.15rem', lineHeight: '1.3' }}>
                        {selectedEquipment.fail}
                      </p>
                    </div>

                    <div style={{ borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                      <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>RECOMMENDED MITIGATION PATHS:</div>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.15rem', lineHeight: '1.4' }}>
                        {selectedEquipment.recommendedAction}
                      </p>
                    </div>

                    <button className="btn-industrial" style={{ marginTop: '0.5rem', width: '100%', fontSize: '0.7rem', padding: '0.4rem' }} onClick={() => setSelectedEquipment(null)}>
                      Deselect Asset
                    </button>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* TAB PANEL 3: LIVE SENSOR GRID TABLE */}
          {activeTab === 'sensors' && (
            <div className="industrial-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', gap: '1rem', flexWrap: 'wrap' }}>
                <div className="hud-widget-title" style={{ width: 'auto', border: 'none', margin: 0, padding: 0 }}>
                  <span>SCADA TELEMETRY NETWORK STREAM</span>
                </div>
                
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  {/* Status Filter */}
                  <select 
                    className="sensors-table-search" 
                    style={{ width: '150px' }}
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="ALL">ALL STATUSES</option>
                    <option value="NOMINAL">NOMINAL</option>
                    <option value="WARNING">WARNING</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                  
                  {/* Search bar */}
                  <input 
                    type="text" 
                    placeholder="Search sensor or location..." 
                    className="sensors-table-search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              </div>

              <div className="sensors-table-container" style={{ flex: 1 }}>
                <table className="sensors-table">
                  <thead>
                    <tr>
                      <th style={{ cursor: 'pointer' }} onClick={() => handleSort('id')}>Sensor ID {sortCol === 'id' && (sortAsc ? '▲' : '▼')}</th>
                      <th style={{ cursor: 'pointer' }} onClick={() => handleSort('location')}>Location {sortCol === 'location' && (sortAsc ? '▲' : '▼')}</th>
                      <th style={{ cursor: 'pointer' }} onClick={() => handleSort('type')}>Type {sortCol === 'type' && (sortAsc ? '▲' : '▼')}</th>
                      <th style={{ cursor: 'pointer' }} onClick={() => handleSort('val')}>Telemetry Reading {sortCol === 'val' && (sortAsc ? '▲' : '▼')}</th>
                      <th>Trend</th>
                      <th style={{ cursor: 'pointer' }} onClick={() => handleSort('health')}>Health {sortCol === 'health' && (sortAsc ? '▲' : '▼')}</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSensors.map((s) => (
                      <tr key={s.id}>
                        <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{s.id}</td>
                        <td>{s.location}</td>
                        <td className="text-secondary">{s.type}</td>
                        <td>{s.val} {s.unit}</td>
                        <td className={s.trend === 'UP' ? 'text-danger' : s.trend === 'DOWN' ? 'text-success' : 'text-secondary'}>
                          {s.trend}
                        </td>
                        <td>{s.health}%</td>
                        <td>
                          <span className={`badge-status ${s.status === 'CRITICAL' ? 'danger' : s.status === 'WARNING' ? 'warning' : ''}`} style={{ fontSize: '0.6rem', padding: '0.15rem 0.4rem' }}>
                            {s.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB PANEL 4: AI PREDICTION LIST */}
          {activeTab === 'predictions' && (
            <div className="industrial-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
              <div className="hud-widget-title" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>
                <span>AI PREDICTIVE ANALYTICS RUNTIME</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {[
                  { name: 'Electrical Failure Vector (Substation-D4)', conf: '99.2%', sev: 'WARNING', action: 'Bypass auxiliary load transformers and inspect breaker coils.', time: '14 Hours' },
                  { name: 'Overheating Risk Envelope (Node-06 Station)', conf: '88.4%', sev: 'WARNING', action: 'Calibrate pump shaft alignment and grease motor bearing housings.', time: '3.5 Hours' },
                  { name: 'Vessel Valve Degradation (Tank-04 Core)', conf: '94.2%', sev: 'CRITICAL', action: 'Emergency bypass: Trigger auxiliary cooling valves in Zone C and depressurize core.', time: 'Immediate' },
                  { name: 'Carbon Gas Leak probability (Shaft Catalyst)', conf: '14.5%', sev: 'NOMINAL', action: 'Routine sensor replacement on shift change.', time: '18 Days' }
                ].map((p, index) => (
                  <div key={index} className="hud-widget" style={{ borderLeft: `3px solid ${p.sev === 'CRITICAL' ? 'var(--accent-danger)' : p.sev === 'WARNING' ? 'var(--accent-warning)' : 'var(--border-color)'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{p.name}</span>
                      <span className={`badge-status ${p.sev === 'CRITICAL' ? 'danger' : p.sev === 'WARNING' ? 'warning' : ''}`} style={{ padding: '0.2rem 0.5rem', fontSize: '0.65rem' }}>
                        {p.sev}
                      </span>
                    </div>
                    <div className="telemetry-row"><span className="telemetry-label">Algorithm Confidence</span><span className="telemetry-value">{p.conf}</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Estimated Time To Incident</span><span className="telemetry-value text-warning">{p.time}</span></div>
                    <div className="telemetry-row"><span className="telemetry-label">Mitigation Workflow</span><span className="telemetry-value" style={{ color: 'var(--text-primary)' }}>{p.action}</span></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB PANEL 5: RISK CHRONOLOGICAL TIMELINE (PAST vs PREDICTED EVENTS) */}
          {activeTab === 'timeline' && (
            <div className="industrial-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', gap: '1rem', flexWrap: 'wrap' }}>
                <div className="hud-widget-title" style={{ width: 'auto', border: 'none', margin: 0, padding: 0 }}>
                  <span>RISK TIMELINE EVENT JOURNAL</span>
                </div>
                
                {/* Timeline Filters */}
                <div style={{ display: 'flex', gap: '0.5rem', pointerEvents: 'auto' }}>
                  {[
                    { id: 'ALL', label: 'ALL EVENTS' },
                    { id: 'CRITICAL', label: 'CRITICAL' },
                    { id: 'WARNING', label: 'WARNINGS' },
                    { id: 'NOMINAL', label: 'NOMINAL' }
                  ].map(f => (
                    <button 
                      key={f.id} 
                      className="btn-industrial"
                      style={{ padding: '0.35rem 0.65rem', fontSize: '0.65rem', borderColor: timelineFilter === f.id ? 'var(--border-active)' : 'var(--border-color)', background: timelineFilter === f.id ? 'rgba(0,124,255,0.08)' : 'var(--surface-color)' }}
                      onClick={() => setTimelineFilter(f.id)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Scrolling events timeline */}
              <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.25rem' }}>
                
                {/* UPCOMING PREDICTED EVENTS SECTION */}
                {filteredTimelineEvents.some(e => e.category === 'predicted') && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-ai)', fontWeight: 600, letterSpacing: '0.1em', marginBottom: '0.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.25rem' }}>
                      &gt;&gt; UPCOMING PREDICTED EVENTS
                    </div>
                    <div className="timeline-flow">
                      {filteredTimelineEvents.filter(e => e.category === 'predicted').map((event) => (
                        <div 
                          key={event.id} 
                          className="timeline-node ai"
                          onMouseEnter={() => setHoveredTimelineId(event.id)}
                          onMouseLeave={() => setHoveredTimelineId(null)}
                        >
                          <div className="timeline-dot" />
                          <div 
                            className="hud-widget" 
                            style={{ 
                              padding: '0.8rem 1.2rem', 
                              cursor: 'pointer', 
                              borderColor: hoveredTimelineId === event.id ? 'var(--border-active)' : 'var(--border-color)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-ai)' }}>{event.title}</span>
                              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--accent-ai)' }}>{event.time}</span>
                            </div>
                            <div style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                              ZONE: {event.zone} | CONFIDENCE: {event.conf}
                            </div>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-primary)', lineHeight: '1.4' }}>
                              {event.text}
                            </p>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.4rem', borderTop: '1px dashed var(--border-color)', paddingTop: '0.4rem' }}>
                              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Recommended Action:</span> {event.action}
                            </div>
                            <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-warning)', marginTop: '0.25rem' }}>
                              ESTIMATED TIME UNTIL INCIDENT: {event.timeToInc}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* CURRENT SYSTEM TIME DIVIDER */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '1.5rem 0', fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--text-disabled)' }}>
                  <hr style={{ flex: 1, borderColor: 'var(--border-color)', borderStyle: 'dashed' }} />
                  <span>CURRENT TIME TIMEPOINT: {liveTime.toLocaleTimeString()} UTC</span>
                  <hr style={{ flex: 1, borderColor: 'var(--border-color)', borderStyle: 'dashed' }} />
                </div>

                {/* PAST COMPLETED EVENTS SECTION */}
                {filteredTimelineEvents.some(e => e.category === 'past') && (
                  <div>
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.1em', marginBottom: '0.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.25rem' }}>
                      &gt;&gt; PAST EVENTS JOURNAL
                    </div>
                    <div className="timeline-flow">
                      {filteredTimelineEvents.filter(e => e.category === 'past').map((event) => (
                        <div 
                          key={event.id} 
                          className={`timeline-node ${event.status}`}
                          onMouseEnter={() => setHoveredTimelineId(event.id)}
                          onMouseLeave={() => setHoveredTimelineId(null)}
                        >
                          <div className="timeline-dot" />
                          <div 
                            className="hud-widget" 
                            style={{ 
                              padding: '0.8rem 1.2rem', 
                              cursor: 'pointer', 
                              borderColor: hoveredTimelineId === event.id ? 'var(--border-active)' : 'var(--border-color)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{event.title}</span>
                              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{event.time}</span>
                            </div>
                            <div style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                              ZONE: {event.zone} | RISK RATING: <span className={event.risk === 'CRITICAL' ? 'text-danger' : event.risk === 'WARNING' ? 'text-warning' : 'text-success'} style={{ fontWeight: 600 }}>{event.risk}</span>
                            </div>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-primary)', lineHeight: '1.4' }}>
                              {event.text}
                            </p>
                            
                            {hoveredTimelineId === event.id && (
                              <div className="timeline-hover-details">
                                <div><span style={{ color: 'var(--text-primary)' }}>&gt; METRIC DETAIL:</span> {event.action}</div>
                                <div><span style={{ color: 'var(--text-primary)' }}>&gt; PROTOCOL FLAG:</span> PTW-SEC_LEVEL_3</div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            </div>
          )}

          {/* TAB PANEL 6: FACILITY THERMAL HEATMAP */}
          {activeTab === 'heatmap' && (
            <div className="heatmap-dashboard-container">
              
              {/* Left filter control sidebar */}
              <div className="hud-widget heatmap-filter-panel">
                <div style={{ flex: 1 }}>
                  <div className="hud-widget-title" style={{ marginBottom: '0.75rem' }}>Filter Parameters</div>
                  
                  {/* Facility dropdown */}
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>FACILITY</label>
                    <select className="sensors-table-search" style={{ width: '100%' }}>
                      <option>CO-LOC_04 (Steel Core)</option>
                      <option>CO-LOC_05 (Oil & Gas Ref)</option>
                    </select>
                  </div>

                  {/* Building selector */}
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>BUILDING</label>
                    <select className="sensors-table-search" style={{ width: '100%' }}>
                      <option>Building A - Core Catalyst</option>
                      <option>Building B - Compressor Unit</option>
                    </select>
                  </div>

                  {/* Zone filters checkbox */}
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>ACTIVE ZONES</label>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Sector A: Catalyst</label>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Sector B: Compressor</label>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Sector C: Reactor Core</label>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Sector D: Electrical</label>
                    </div>
                  </div>

                  {/* Equipment Type checkbox */}
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>EQUIPMENT TYPE</label>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Reactor Vessels</label>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> Pumps & Motors</label>
                      <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}><input type="checkbox" defaultChecked /> SCADA Transmitters</label>
                    </div>
                  </div>

                  {/* Temperature Threshold slider */}
                  <div>
                    <label style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>TEMP THRESHOLD (0 - 200°C)</label>
                    <input type="range" min="0" max="200" defaultValue="100" style={{ width: '100%', accentColor: 'var(--accent-ai)' }} />
                  </div>

                </div>
              </div>

              {/* Center Map/SVG area */}
              <div className="heatmap-center-workspace">
                
                {/* Top Controls bar */}
                <div className="hud-widget" style={{ padding: '0.5rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {/* Metric Selectors */}
                  <div style={{ display: 'flex', gap: '0.35rem' }}>
                    {[
                      { id: 'temp', label: 'Temp' },
                      { id: 'gas', label: 'Gas' },
                      { id: 'press', label: 'Press' },
                      { id: 'stress', label: 'Stress' },
                      { id: 'occup', label: 'Occupancy' }
                    ].map(m => (
                      <button 
                        key={m.id} 
                        className="btn-industrial"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.65rem', borderColor: heatmapMetric === m.id ? 'var(--border-active)' : 'var(--border-color)', background: heatmapMetric === m.id ? 'rgba(0,124,255,0.08)' : 'var(--surface-color)' }}
                        onClick={() => setHeatmapMetric(m.id)}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn-industrial" style={{ padding: '0.3rem 0.6rem', fontSize: '0.65rem', borderColor: heatmapRefresh ? 'var(--border-active)' : 'var(--border-color)', background: heatmapRefresh ? 'rgba(0,124,255,0.08)' : 'var(--surface-color)' }} onClick={() => setHeatmapRefresh(!heatmapRefresh)}>
                      Auto Refresh: {heatmapRefresh ? 'ON' : 'OFF'}
                    </button>
                    <button className="btn-industrial" style={{ padding: '0.3rem 0.6rem', fontSize: '0.65rem' }} onClick={() => alert('Snapshot captured: CO-LOC_04_thermal.png')}>Snapshot</button>
                    <button className="btn-industrial" style={{ padding: '0.3rem 0.6rem', fontSize: '0.65rem' }} onClick={() => alert('Exporting telemetry spreadsheet logs...')}>Export</button>
                  </div>
                  
                  {/* Historical Comparison toggle */}
                  <button className="btn-industrial" style={{ padding: '0.3rem 0.6rem', fontSize: '0.65rem' }} onClick={() => alert('Historical comparison window loading...')}>Historical Compare</button>
                </div>

                {/* SVG Visualizer */}
                <div className="heatmap-svg-container">
                  <svg width="100%" height="100%" viewBox="0 0 400 240">
                    <defs>
                      <radialGradient id="heat-A" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#10B981" stopOpacity="0.7"/>
                        <stop offset="60%" stopColor="#10B981" stopOpacity="0.2"/>
                        <stop offset="100%" stopColor="#10B981" stopOpacity="0"/>
                      </radialGradient>
                      <radialGradient id="heat-B" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.75"/>
                        <stop offset="60%" stopColor="#F59E0B" stopOpacity="0.25"/>
                        <stop offset="100%" stopColor="#F59E0B" stopOpacity="0"/>
                      </radialGradient>
                      <radialGradient id="heat-C" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#EF4444" stopOpacity="0.8"/>
                        <stop offset="70%" stopColor="#EF4444" stopOpacity="0.3"/>
                        <stop offset="100%" stopColor="#EF4444" stopOpacity="0"/>
                      </radialGradient>
                      <radialGradient id="heat-D" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#007CFF" stopOpacity="0.6"/>
                        <stop offset="60%" stopColor="#007CFF" stopOpacity="0.15"/>
                        <stop offset="100%" stopColor="#007CFF" stopOpacity="0"/>
                      </radialGradient>
                    </defs>

                    <rect x="15" y="15" width="370" height="210" fill="none" stroke="#242930" strokeWidth="1" strokeDasharray="3 3" />
                    
                    <line x1="200" y1="15" x2="200" y2="225" stroke="#242930" strokeWidth="1.5" />
                    <line x1="15" y1="120" x2="385" y2="120" stroke="#242930" strokeWidth="1.5" />

                    <text x="30" y="35" fill="var(--text-secondary)" fontSize="8" fontFamily="var(--font-mono)">SECTOR A: CATALYST</text>
                    <text x="215" y="35" fill="var(--text-secondary)" fontSize="8" fontFamily="var(--font-mono)">SECTOR B: COMPRESSORS</text>
                    <text x="30" y="140" fill="var(--text-secondary)" fontSize="8" fontFamily="var(--font-mono)">SECTOR C: REACTOR CORE</text>
                    <text x="215" y="140" fill="var(--text-secondary)" fontSize="8" fontFamily="var(--font-mono)">SECTOR D: ELECTRICAL</text>

                    <circle cx="100" cy="70" r="50" fill={heatmapMetric === 'gas' ? 'url(#heat-B)' : 'url(#heat-A)'} className="heatmap-pulse" />
                    <circle cx="300" cy="70" r="55" fill={heatmapMetric === 'occup' ? 'url(#heat-A)' : (heatmapMetric === 'stress' ? 'url(#heat-B)' : 'url(#heat-B)')} className="heatmap-pulse" style={{ animationDelay: '0.8s' }} />
                    <circle cx="100" cy="170" r="60" fill={heatmapMetric === 'gas' || heatmapMetric === 'occup' ? 'url(#heat-D)' : 'url(#heat-C)'} className="heatmap-pulse" style={{ animationDelay: '1.6s' }} />
                    <circle cx="300" cy="170" r="45" fill={heatmapMetric === 'occup' ? 'url(#heat-C)' : 'url(#heat-D)'} className="heatmap-pulse" style={{ animationDelay: '2.4s' }} />
                  </svg>
                  
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', background: 'linear-gradient(to bottom, transparent, rgba(0, 124, 255, 0.03) 50%, transparent)', animation: 'radar-sweep 6s linear infinite' }} />
                </div>

                {/* Bottom Hotspots table list */}
                <div className="heatmap-bottom-table-container">
                  <table className="sensors-table">
                    <thead>
                      <tr>
                        <th>Location Coordinates</th>
                        <th>Measured Metric Value</th>
                        <th>AI Confidence</th>
                        <th>Suggested Preventative Response</th>
                      </tr>
                    </thead>
                    <tbody>
                      {heatmapData.hotspots.map((h, idx) => (
                        <tr key={idx}>
                          <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{h.loc}</td>
                          <td className="text-warning">{h.val}</td>
                          <td>{h.conf}</td>
                          <td>{h.response}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

              </div>

              {/* Right Side Stats sidebar */}
              <div className="hud-widget twin-right-inspector">
                <div className="hud-widget-title" style={{ paddingBottom: '0.4rem', marginBottom: '0.6rem' }}>
                  <span>Live Statistics</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', fontSize: '0.75rem' }}>
                  <div className="hud-widget" style={{ padding: '0.6rem', background: 'rgba(0,0,0,0.1)' }}>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>MAX CORE TEMP</div>
                    <div className="text-danger" style={{ fontSize: '1.25rem', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>142.4°C</div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-secondary)' }}>Registered in Sector C</div>
                  </div>

                  <div className="hud-widget" style={{ padding: '0.6rem', background: 'rgba(0,0,0,0.1)' }}>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>MIN TEMP</div>
                    <div className="text-success" style={{ fontSize: '1.25rem', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>38.6°C</div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-secondary)' }}>Registered in Sector D</div>
                  </div>

                  <div className="hud-widget" style={{ padding: '0.6rem', background: 'rgba(0,0,0,0.1)' }}>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>AVERAGE VALUE</div>
                    <div className="text-ai" style={{ fontSize: '1.25rem', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{heatmapData.avg}</div>
                    <div style={{ fontSize: '0.6rem', color: 'var(--text-secondary)' }}>Across all reporting sensors</div>
                  </div>

                  <div className="telemetry-row"><span className="telemetry-label">Active Hotspots</span><span className="telemetry-value text-warning" style={{ fontWeight: 600 }}>2 Zones</span></div>
                  <div className="telemetry-row"><span className="telemetry-label">Sensors Synced</span><span className="telemetry-value">14,957 / 14,957</span></div>

                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', marginTop: 'auto' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                      <span>Cold</span>
                      <span>Normal</span>
                      <span>Warning</span>
                      <span>Critical</span>
                    </div>
                    <div style={{ height: '8px', borderRadius: '4px', background: 'linear-gradient(to right, #007CFF, #10B981, #F59E0B, #EF4444)', width: '100%' }} />
                    <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginTop: '0.5rem', textAlign: 'center' }}>
                      SCALE RANGE: {heatmapData.scale}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          )}

        </main>

        {/* ====================================================================
           RIGHT SIDEBAR (LIVE ALERTS OR DIGITAL TWIN EQUIPMENT INSPECTOR)
           ==================================================================== */}
        <aside className="dashboard-sidebar-panel" style={{ width: '280px' }}>
          
          {/* DIGITAL TWIN INSPECTOR DETAILS PANEL - FLAGSHIP VIEW OVERLAY */}
          {activeTab === 'twin' && selectedEquipment ? (
            <div className="hud-widget" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', background: 'rgba(12, 14, 18, 0.85)', borderColor: selectedEquipment.status === 'CRITICAL' ? 'var(--accent-danger)' : selectedEquipment.status === 'WARNING' ? 'var(--accent-warning)' : 'var(--border-color)' }}>
              <div className="hud-widget-title" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.4rem', marginBottom: '0.25rem' }}>
                <span>EQUIPMENT INSPECTOR</span>
                <span className={`badge-status ${selectedEquipment.status === 'CRITICAL' ? 'danger' : selectedEquipment.status === 'WARNING' ? 'warning' : ''}`} style={{ fontSize: '0.55rem', padding: '0.1rem 0.35rem' }}>
                  {selectedEquipment.status}
                </span>
              </div>
              
              <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>UNIT CLASSIFICATION:</div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.15rem' }}>{selectedEquipment.name}</h4>
              </div>

              <div>
                <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>ACTIVE SCADA SENSORS:</div>
                <div className="telemetry-row"><span className="telemetry-label">Thermal Reactor</span><span className="telemetry-value">{selectedEquipment.temp}</span></div>
                <div className="telemetry-row"><span className="telemetry-label">Conduit Pressure</span><span className="telemetry-value">{selectedEquipment.pressure}</span></div>
                <div className="telemetry-row"><span className="telemetry-label">Vibration index</span><span className="telemetry-value">{selectedEquipment.vibration}</span></div>
              </div>

              <div style={{ borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem' }}>
                <div className="telemetry-row"><span className="telemetry-label">Last Inspection</span><span className="telemetry-value">{selectedEquipment.lastInspection}</span></div>
                <div className="telemetry-row"><span className="telemetry-label">Next Inspection</span><span className="telemetry-value">2026-08-15</span></div>
                <div className="telemetry-row"><span className="telemetry-label">RUL estimate</span><span className="telemetry-value text-success" style={{ fontWeight: 600 }}>{selectedEquipment.rul}</span></div>
              </div>

              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>PREDICTED ANOMALY PATH:</div>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-primary)', marginTop: '0.15rem', lineHeight: '1.3' }}>
                  {selectedEquipment.fail}
                </p>
              </div>

              <div style={{ borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                <div style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>RECOMMENDED WORKFLOWS:</div>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.15rem', lineHeight: '1.4' }}>
                  {selectedEquipment.recommendedAction}
                </p>
              </div>

              <button className="btn-industrial" style={{ marginTop: 'auto', width: '100%', fontSize: '0.7rem', padding: '0.5rem' }} onClick={() => setSelectedEquipment(null)}>
                Close Inspector
              </button>
            </div>
          ) : (
            // Default Alerts Sidebar View (Overview/Sensors/Predictions/Timeline/Heatmap)
            <>
              {/* Live Alerts */}
              <div className="hud-widget" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div className="hud-widget-title" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                  <span>ACTIVE WARNING ALERTS ({alerts.filter(a => !a.ack).length})</span>
                </div>
                
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.25rem' }}>
                  {alerts.map((alert) => (
                    <div key={alert.id} className={`dashboard-alert-item ${alert.ack ? 'acknowledged' : ''}`} style={{ flexDirection: 'column', gap: '0.4rem', alignItems: 'flex-start', padding: '0.6rem 0.8rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                        <span className={`badge-status ${alert.status === 'CRITICAL' ? 'danger' : alert.status === 'WARNING' ? 'warning' : ''}`} style={{ fontSize: '0.6rem', padding: '0.1rem 0.35rem' }}>
                          {alert.status}
                        </span>
                        <button 
                          style={{ background: 'none', border: 'none', color: alert.ack ? 'var(--text-disabled)' : 'var(--accent-ai)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.65rem' }}
                          disabled={alert.ack}
                          onClick={() => handleAcknowledgeAlert(alert.id)}
                        >
                          {alert.ack ? 'ACKNOWLEDGED' : '[ACK]'}
                        </button>
                      </div>
                      <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: alert.ack ? 'var(--text-secondary)' : 'var(--text-primary)' }}>{alert.title}</h4>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', lineHeight: '1.3' }}>{alert.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Recommendations */}
              <div className="hud-widget">
                <div className="hud-widget-title">AI RECOMMENDATIONS</div>
                <div style={{ fontSize: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                  <div style={{ borderLeft: '2px solid var(--accent-ai)', paddingLeft: '0.5rem' }}>
                    <span className="text-primary" style={{ fontWeight: 600 }}>Coolant Injection:</span> Activate Zone C aux reservoir lines.
                  </div>
                  <div style={{ borderLeft: '2px solid var(--accent-warning)', paddingLeft: '0.5rem' }}>
                    <span className="text-primary" style={{ fontWeight: 600 }}>Hot Work Permits:</span> Pause permit #804 pending gas ventilation.
                  </div>
                </div>
              </div>
            </>
          )}

        </aside>

        {/* ====================================================================
           COLLAPSIBLE AI COPILOT ASSISTANT (SLIDES FROM RIGHT EDGE)
           ==================================================================== */}
        <div className={`copilot-panel ${copilotCollapsed ? 'collapsed' : ''}`}>
          {/* Toggle trigger button */}
          <button className="copilot-toggle-btn" onClick={() => setCopilotCollapsed(!copilotCollapsed)}>
            {copilotCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>
          
          <div className="hud-widget-title" style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', margin: 0 }}>
            <span>ARGUS SAFETY COPILOT</span>
            <span className="telemetry-pulse-dot" style={{ backgroundColor: 'var(--accent-ai)' }} />
          </div>

          {/* Chat Messages scroll area */}
          <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
            {chatMessages.map((msg, index) => (
              <div key={index} className={`chat-bubble ${msg.type}`}>
                {msg.text}
              </div>
            ))}
            {isTyping && (
              <div className="chat-bubble ai" style={{ fontStyle: 'italic', color: 'var(--text-disabled)' }}>
                ARGUS AI is typing safety analysis...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Copilot Presets Quick Queries */}
          <div style={{ padding: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.4rem', background: 'rgba(0,0,0,0.15)' }}>
            <span style={{ fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>SELECT QUICK QUERY DIRECTIVE:</span>
            {[
              { 
                q: 'Why is Tank-04 high risk?', 
                a: 'Thermal Reactor Tank-04 risk is evaluated at 94.2% due to a compound variance: vessel thermal readings exceeded nominal thresholds (+12.4°C) while an active Hot Work permit was logged in the same coordinate zone. Core pressure rerouted.'
              },
              { 
                q: 'Show active alarms.', 
                a: 'Current alerts index includes: 1 Critical Alert (Zone C Reactor Thermal Spikes), 1 Warning Alert (Zone B Shaft Proximity sensor bounds).' 
              },
              { 
                q: 'Predict next failure.', 
                a: 'Correlating 1,402 simulations: structural fatigue on Core-01 catalysts shaft has risen 0.4% over 48 hours. Preventive lubrication scheduled for Shift change.' 
              }
            ].map((p, idx) => (
              <button 
                key={idx} 
                className="btn-industrial" 
                style={{ padding: '0.4rem 0.6rem', fontSize: '0.7rem', textAlign: 'left', justifyContent: 'flex-start' }}
                onClick={() => handleCopilotQuestion(p.q, p.a)}
              >
                &gt; {p.q}
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
