import { create } from 'zustand';

export const useStore = create((set) => ({
  progress: 0,
  setProgress: (p) => set({ progress: p }),
  activeScene: 0,
  setActiveScene: (s) => set({ activeScene: s }),
  isLoaded: false,
  setLoaded: (l) => set({ isLoaded: l }),
  view: 'briefing', // 'briefing' | 'dashboard'
  setView: (v) => set({ view: v }),
  
  // Dashboard views navigation
  activeTab: 'overview', // 'overview' | 'twin' | 'sensors' | 'predictions' | 'timeline' | 'heatmap'
  setActiveTab: (t) => set({ activeTab: t }),
  
  // Digital Twin click Raycasting
  selectedEquipment: null, // { name, status, temp, pressure, vibration, risk, lastInspection }
  setSelectedEquipment: (e) => set({ selectedEquipment: e }),
}));
