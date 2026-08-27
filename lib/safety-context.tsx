import * as Haptics from "expo-haptics";
import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { Platform } from "react-native";
import { GAS_ALARM_DEMO_TELEMETRY, NORMAL_DEMO_TELEMETRY, evaluateTelemetry, type BandTelemetry, type SafetyEvaluation } from "@/lib/safety";

interface SafetyContextValue { telemetry: BandTelemetry; evaluation: SafetyEvaluation; isGasAlarmDemo: boolean; isAlertAcknowledged: boolean; startGasAlarmDemo: () => void; resetDemo: () => void; acknowledgeAlert: () => void; }
const SafetyContext = createContext<SafetyContextValue | undefined>(undefined);

export function SafetyProvider({ children }: { children: ReactNode }) {
  const [isGasAlarmDemo, setIsGasAlarmDemo] = useState(false);
  const [isAlertAcknowledged, setIsAlertAcknowledged] = useState(false);
  const telemetry = isGasAlarmDemo ? GAS_ALARM_DEMO_TELEMETRY : NORMAL_DEMO_TELEMETRY;
  const evaluation = useMemo(() => evaluateTelemetry(telemetry), [telemetry]);
  const value = useMemo<SafetyContextValue>(() => ({ telemetry, evaluation, isGasAlarmDemo, isAlertAcknowledged, startGasAlarmDemo: () => { setIsGasAlarmDemo(true); setIsAlertAcknowledged(false); if (Platform.OS !== "web") void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); }, resetDemo: () => { setIsGasAlarmDemo(false); setIsAlertAcknowledged(false); if (Platform.OS !== "web") void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); }, acknowledgeAlert: () => { setIsAlertAcknowledged(true); if (Platform.OS !== "web") void Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); } }), [evaluation, isAlertAcknowledged, isGasAlarmDemo, telemetry]);
  return <SafetyContext.Provider value={value}>{children}</SafetyContext.Provider>;
}

export function useSafety() { const context = useContext(SafetyContext); if (!context) throw new Error("useSafety must be used within SafetyProvider"); return context; }
