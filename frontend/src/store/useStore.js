import { create } from 'zustand';

export const useStore = create((set) => ({
  progress: 0,
  setProgress: (p) => set({ progress: p }),
  activeScene: 0,
  setActiveScene: (s) => set({ activeScene: s }),
  isLoaded: false,
  setLoaded: (l) => set({ isLoaded: l })
}));
