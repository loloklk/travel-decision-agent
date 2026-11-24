import { createContext, useContext, ReactNode } from "react";
import type en from "./en";
import zh from "./zh";

export type MessageKeys = keyof typeof en;
interface I18nContextValue {
  lang: "zh" | "en";
  t: (key: MessageKeys) => string;
}
const I18nContext = createContext<I18nContextValue>(null!);
const chineseLocale: I18nContextValue = {
  lang: "zh",
  t: (key) => zh[key] ?? key,
};
export function I18nProvider({ children }: { children: ReactNode }) {
  return <I18nContext.Provider value={chineseLocale}>{children}</I18nContext.Provider>;
}
export function useT() {
  return useContext(I18nContext);
}
