export type ThemeMode = "light" | "dark" | "system";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

export type SignalLevel = "info" | "warning" | "critical" | "safe";

export interface NavItem {
  label: string;
  href: string;
}
