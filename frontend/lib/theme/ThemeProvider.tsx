"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";

import type { ThemeMode } from "@/types";

const STORAGE_KEY = "argus-theme";

interface ThemeContextValue {
  mode: ThemeMode;
  resolvedTheme: "light" | "dark";
  setMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function readStoredMode(): ThemeMode {
  if (typeof window === "undefined") return "system";
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
}

function resolveTheme(mode: ThemeMode): "light" | "dark" {
  return mode === "system" ? getSystemTheme() : mode;
}

function applyTheme(resolved: "light" | "dark") {
  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(resolved);
  root.style.colorScheme = resolved;
}

function subscribe(onStoreChange: () => void) {
  const onStorage = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY || e.key === null) onStoreChange();
  };
  window.addEventListener("storage", onStorage);

  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  mq.addEventListener("change", onStoreChange);

  return () => {
    window.removeEventListener("storage", onStorage);
    mq.removeEventListener("change", onStoreChange);
  };
}

function getModeSnapshot(): ThemeMode {
  return readStoredMode();
}

function getModeServerSnapshot(): ThemeMode {
  return "system";
}

function getResolvedSnapshot(): "light" | "dark" {
  return resolveTheme(readStoredMode());
}

function getResolvedServerSnapshot(): "light" | "dark" {
  return "dark";
}

function notifyThemeListeners() {
  window.dispatchEvent(new StorageEvent("storage", { key: STORAGE_KEY }));
}

interface ThemeProviderProps {
  children: React.ReactNode;
}

/**
 * Hydration-safe theme via useSyncExternalStore.
 * Server + first client paint use dark; client then reads localStorage.
 */
export function ThemeProvider({ children }: ThemeProviderProps) {
  const mode = useSyncExternalStore(
    subscribe,
    getModeSnapshot,
    getModeServerSnapshot,
  );
  const resolvedTheme = useSyncExternalStore(
    subscribe,
    getResolvedSnapshot,
    getResolvedServerSnapshot,
  );

  const setMode = useCallback((next: ThemeMode) => {
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(resolveTheme(next));
    notifyThemeListeners();
  }, []);

  const toggleTheme = useCallback(() => {
    const current = resolveTheme(readStoredMode());
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
    notifyThemeListeners();
  }, []);

  const value = useMemo(
    () => ({ mode, resolvedTheme, setMode, toggleTheme }),
    [mode, resolvedTheme, setMode, toggleTheme],
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return ctx;
}
