import { Tabs } from "expo-router";
import { Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { HapticTab } from "@/components/haptic-tab";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";

export default function TabLayout() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPadding = Platform.OS === "web" ? 12 : Math.max(insets.bottom, 8);

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#087D70",
        tabBarInactiveTintColor: "#7B8798",
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: { paddingTop: 8, paddingBottom: bottomPadding, height: Platform.OS === "web" ? 0 : 58 + bottomPadding, display: Platform.OS === "web" ? "none" : "flex", backgroundColor: colors.background, borderTopColor: "#E7ECF1", borderTopWidth: 1 },
        tabBarLabelStyle: { fontSize: 10, fontWeight: "700" },
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home", tabBarIcon: ({ color }) => <IconSymbol size={24} name="house.fill" color={color} /> }} />
      <Tabs.Screen name="readings" options={{ title: "Readings", tabBarIcon: ({ color }) => <IconSymbol size={24} name="waveform.path.ecg" color={color} /> }} />
      <Tabs.Screen name="alerts" options={{ title: "Alerts", tabBarIcon: ({ color }) => <IconSymbol size={24} name="exclamationmark.triangle.fill" color={color} /> }} />
      <Tabs.Screen name="standards" options={{ title: "Standards", tabBarIcon: ({ color }) => <IconSymbol size={24} name="book.closed.fill" color={color} /> }} />
    </Tabs>
  );
}
