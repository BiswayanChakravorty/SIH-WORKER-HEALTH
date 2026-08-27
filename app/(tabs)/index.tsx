import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { Linking, Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from "react-native";

import { RiskPill } from "@/components/safety-ui";
import { ScreenContainer } from "@/components/screen-container";
import { riskColors, type MetricAssessment } from "@/lib/safety";
import { useSafety } from "@/lib/safety-context";

const icons = {
  heartRateBpm: "favorite" as const,
  respiratoryRateBrpm: "air" as const,
  bodyTemperatureC: "device-thermostat" as const,
  ambientOxygenPercent: "air" as const,
  methanePercent: "local-fire-department" as const,
  carbonMonoxidePpm: "cloud" as const,
};

function ReadingCard({ reading }: { reading: MetricAssessment }) {
  const colors = riskColors[reading.level];
  return (
    <View style={styles.readingCard}>
      <View style={styles.readingHeader}>
        <View style={[styles.sensorIcon, { backgroundColor: colors.background }]}>
          <MaterialIcons name={icons[reading.key]} size={19} color={colors.text} />
        </View>
        <RiskPill level={reading.level} />
      </View>
      <Text style={styles.readingLabel}>{reading.label}</Text>
      <Text style={styles.readingValue}>{reading.valueLabel}</Text>
      <Text style={styles.readingStandard}>Standard: {reading.standard.standard}</Text>
    </View>
  );
}

export default function SimpleWorkerMonitor() {
  const { width } = useWindowDimensions();
  const desktop = width >= 900;
  const { telemetry, evaluation, isGasAlarmDemo, isAlertAcknowledged, startGasAlarmDemo, acknowledgeAlert, resetDemo } = useSafety();
  const health = evaluation.assessments.slice(0, 3);
  const atmosphere = evaluation.assessments.slice(3);
  const active = evaluation.assessments.filter((reading) => reading.level !== "normal");
  const levelColors = riskColors[evaluation.overallLevel];
  const openSource = (url: string) => void Linking.openURL(url);

  return (
    <ScreenContainer edges={["top", "left", "right", "bottom"]}>
      <ScrollView contentContainerStyle={[styles.page, desktop && styles.pageDesktop]} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View style={styles.brand}><View style={styles.logo}><MaterialIcons name="health-and-safety" size={22} color="#FFFFFF" /></View><View><Text style={styles.brandName}>Worker Health Band</Text><Text style={styles.brandTagline}>Simple mine-worker monitoring</Text></View></View>
          <View style={styles.connection}><View style={styles.liveDot} /><Text style={styles.connectionText}>Band {telemetry.bandId} connected</Text></View>
        </View>

        <View style={[styles.statusBanner, { backgroundColor: evaluation.overallLevel === "normal" ? "#0B1F33" : levelColors.background, borderColor: evaluation.overallLevel === "normal" ? "#0B1F33" : levelColors.border }]}>
          <View style={styles.statusLeft}><View style={[styles.statusIcon, { backgroundColor: evaluation.overallLevel === "normal" ? "#173A55" : "#FFFFFF" }]}><MaterialIcons name={evaluation.overallLevel === "normal" ? "verified-user" : "warning"} size={26} color={evaluation.overallLevel === "normal" ? "#5FE0CD" : levelColors.text} /></View><View><Text style={[styles.statusLabel, evaluation.overallLevel !== "normal" && { color: levelColors.text }]}>CURRENT SAFETY STATE</Text><Text style={[styles.statusTitle, evaluation.overallLevel !== "normal" && { color: levelColors.text }]}>{evaluation.overallLabel}</Text><Text style={[styles.statusText, evaluation.overallLevel !== "normal" && { color: levelColors.text }]}>{evaluation.overallLevel === "normal" ? "Latest sensor values are below the displayed hazard thresholds." : "The local band alarm should be active. Follow site emergency procedure."}</Text></View></View>
          <RiskPill level={evaluation.overallLevel} label={isGasAlarmDemo ? "Demo alert" : "Live demo"} />
        </View>

        <View style={[styles.contentGrid, desktop && styles.contentGridDesktop]}>
          <View style={styles.monitorColumn}>
            <Text style={styles.sectionTitle}>Worker monitoring</Text><Text style={styles.sectionSubtitle}>Current vital-sign readings from worker {telemetry.workerId}</Text>
            <View style={styles.cardGrid}>{health.map((reading) => <ReadingCard key={reading.key} reading={reading} />)}</View>
            <Text style={[styles.sectionTitle, styles.gasHeading]}>Gas monitoring</Text><Text style={styles.sectionSubtitle}>Atmosphere values measured by the wristband sensor</Text>
            <View style={styles.cardGrid}>{atmosphere.map((reading) => <ReadingCard key={reading.key} reading={reading} />)}</View>
          </View>

          <View style={styles.trackingColumn}>
            <View style={styles.locationCard}>
              <View style={styles.locationHeader}><View><Text style={styles.sectionTitle}>Worker tracking</Text><Text style={styles.sectionSubtitle}>Last reported band location</Text></View><View style={styles.locationBadge}><MaterialIcons name="my-location" size={16} color="#087D70" /></View></View>
              <View style={styles.locationVisual}><View style={styles.tunnelLine} /><View style={styles.mapPin}><MaterialIcons name="person" size={18} color="#FFFFFF" /></View><Text style={styles.locationLabel}>NORTH DRIFT 04</Text><Text style={styles.locationDistance}>Level −220 m · Checkpoint 7</Text></View>
              <View style={styles.locationFooter}><View><Text style={styles.locationMetaLabel}>WORKER</Text><Text style={styles.locationMetaValue}>{telemetry.workerName}</Text></View><View><Text style={styles.locationMetaLabel}>LAST UPDATE</Text><Text style={styles.locationMetaValue}>Just now</Text></View></View>
            </View>

            <View style={styles.alarmCard}>
              <View style={styles.alarmHeader}><View><Text style={styles.sectionTitle}>Gas alarm</Text><Text style={styles.sectionSubtitle}>Test the website alert workflow</Text></View><MaterialIcons name="campaign" size={22} color="#D92D20" /></View>
              {evaluation.overallLevel === "normal" ? <><Text style={styles.alarmSafe}>No active gas hazard</Text><Pressable accessibilityRole="button" onPress={startGasAlarmDemo} style={({ pressed }) => [styles.testButton, pressed && styles.pressed]}><MaterialIcons name="warning" size={18} color="#FFFFFF" /><Text style={styles.testButtonText}>Run gas alarm test</Text></Pressable></> : <><Text style={styles.alarmDanger}>Unsafe gas condition detected</Text><Text style={styles.alarmInstruction}>Leave the area and follow the site’s emergency plan. Acknowledgement does not resolve the hazard.</Text>{active.map((reading) => <View key={reading.key} style={styles.activeRow}><Text style={styles.activeName}>{reading.label}</Text><Text style={styles.activeValue}>{reading.valueLabel}</Text></View>)}<View style={styles.alarmActions}><Pressable accessibilityRole="button" disabled={isAlertAcknowledged} onPress={acknowledgeAlert} style={({ pressed }) => [styles.ackButton, isAlertAcknowledged && styles.acknowledged, pressed && !isAlertAcknowledged && styles.pressed]}><Text style={[styles.ackButtonText, isAlertAcknowledged && styles.acknowledgedText]}>{isAlertAcknowledged ? "Acknowledged" : "Acknowledge"}</Text></Pressable><Pressable accessibilityRole="button" onPress={resetDemo} style={({ pressed }) => [styles.resetButton, pressed && styles.pressed]}><Text style={styles.resetText}>Reset</Text></Pressable></View></>}
            </View>
          </View>
        </View>

        <View style={styles.tablePanel}>
          <View style={styles.tableTitleRow}><View><Text style={styles.sectionTitle}>Reading / Standard / Status</Text><Text style={styles.sectionSubtitle}>The standards are source-linked and are a reference baseline, not a site approval.</Text></View><MaterialIcons name="fact-check" size={22} color="#087D70" /></View>
          <View style={styles.tableHead}><Text style={[styles.tableHeadText, styles.columnMetric]}>SENSOR</Text><Text style={[styles.tableHeadText, styles.columnReading]}>READING</Text><Text style={[styles.tableHeadText, styles.columnStandard]}>STANDARD</Text><Text style={[styles.tableHeadText, styles.columnStatus]}>STATUS</Text></View>
          {evaluation.assessments.map((reading) => <View key={reading.key} style={styles.tableRow}><Text style={[styles.tableMetric, styles.columnMetric]}>{reading.label}</Text><Text style={[styles.tableReading, styles.columnReading]}>{reading.valueLabel}</Text><Pressable accessibilityRole="link" onPress={() => openSource(reading.standard.sourceUrl)} style={[styles.columnStandard, styles.sourceLink]}><Text style={styles.sourceLinkText}>{reading.standard.standard}</Text><MaterialIcons name="open-in-new" size={12} color="#087D70" /></Pressable><View style={styles.columnStatus}><RiskPill level={reading.level} label={reading.statusLabel} /></View></View>)}
        </View>

        <View style={styles.footer}><MaterialIcons name="info-outline" size={17} color="#6B7E92" /><Text style={styles.footerText}>Demo data only. This website does not replace certified gas monitoring, approved site thresholds, sensor calibration, or emergency procedures.</Text></View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  page: { backgroundColor: "#F5F8FB", padding: 18, paddingBottom: 34, gap: 20, minHeight: "100%" }, pageDesktop: { paddingHorizontal: 44, paddingTop: 30, alignSelf: "center", width: "100%", maxWidth: 1380 }, header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12 }, brand: { flexDirection: "row", alignItems: "center", gap: 10 }, logo: { width: 42, height: 42, borderRadius: 13, backgroundColor: "#087D70", alignItems: "center", justifyContent: "center" }, brandName: { color: "#0B1F33", fontSize: 17, lineHeight: 21, fontWeight: "900" }, brandTagline: { color: "#6C7F92", fontSize: 11, lineHeight: 15 }, connection: { flexDirection: "row", alignItems: "center", gap: 6, backgroundColor: "#FFFFFF", borderColor: "#E0E8EF", borderWidth: 1, paddingHorizontal: 10, paddingVertical: 8, borderRadius: 99 }, liveDot: { width: 7, height: 7, borderRadius: 5, backgroundColor: "#12B6A6" }, connectionText: { color: "#53657A", fontSize: 10, fontWeight: "800" }, statusBanner: { borderWidth: 1, borderRadius: 20, padding: 17, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }, statusLeft: { flexDirection: "row", gap: 11, flex: 1 }, statusIcon: { width: 47, height: 47, borderRadius: 15, alignItems: "center", justifyContent: "center" }, statusLabel: { color: "#9CC8CE", fontSize: 9, lineHeight: 13, fontWeight: "900", letterSpacing: 0.7 }, statusTitle: { color: "#FFFFFF", fontSize: 21, lineHeight: 27, fontWeight: "900" }, statusText: { color: "#C1D0D9", fontSize: 11, lineHeight: 17, maxWidth: 460 }, contentGrid: { gap: 15 }, contentGridDesktop: { flexDirection: "row", alignItems: "flex-start" }, monitorColumn: { flex: 1.55 }, trackingColumn: { flex: 0.95, gap: 15 }, sectionTitle: { color: "#0B1F33", fontSize: 16, lineHeight: 21, fontWeight: "900" }, sectionSubtitle: { color: "#708399", fontSize: 11, lineHeight: 16, marginTop: 2 }, cardGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10, marginTop: 11 }, readingCard: { backgroundColor: "#FFFFFF", borderColor: "#E2EAF0", borderWidth: 1, borderRadius: 17, padding: 13, flexGrow: 1, flexBasis: "30%", minWidth: 148, gap: 3 }, readingHeader: { flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 5 }, sensorIcon: { width: 35, height: 35, borderRadius: 11, alignItems: "center", justifyContent: "center" }, readingLabel: { color: "#5C6D80", fontSize: 11, lineHeight: 15, fontWeight: "700" }, readingValue: { color: "#0B1F33", fontSize: 20, lineHeight: 26, fontWeight: "900", letterSpacing: -0.3 }, readingStandard: { color: "#8592A3", fontSize: 9, lineHeight: 13 }, gasHeading: { marginTop: 20 }, locationCard: { backgroundColor: "#FFFFFF", borderColor: "#E2EAF0", borderWidth: 1, borderRadius: 19, padding: 15, gap: 13 }, locationHeader: { flexDirection: "row", justifyContent: "space-between", gap: 8 }, locationBadge: { width: 34, height: 34, borderRadius: 11, alignItems: "center", justifyContent: "center", backgroundColor: "#E9F9F5" }, locationVisual: { height: 148, borderRadius: 14, backgroundColor: "#E9F1EF", overflow: "hidden", alignItems: "center", justifyContent: "center" }, tunnelLine: { width: "140%", height: 74, borderWidth: 23, borderColor: "#C7D7D4", borderRadius: 80, transform: [{ rotate: "-8deg" }] }, mapPin: { width: 37, height: 37, borderRadius: 19, backgroundColor: "#D92D20", alignItems: "center", justifyContent: "center", position: "absolute", top: 35 }, locationLabel: { color: "#0B1F33", fontSize: 11, letterSpacing: 0.7, fontWeight: "900", position: "absolute", bottom: 31 }, locationDistance: { color: "#607489", fontSize: 10, position: "absolute", bottom: 15 }, locationFooter: { flexDirection: "row", gap: 28 }, locationMetaLabel: { color: "#7A8A9B", fontSize: 9, lineHeight: 12, letterSpacing: 0.5, fontWeight: "900" }, locationMetaValue: { color: "#24394F", fontSize: 11, lineHeight: 16, fontWeight: "800" }, alarmCard: { backgroundColor: "#FFFFFF", borderColor: "#E2EAF0", borderWidth: 1, borderRadius: 19, padding: 15, gap: 11 }, alarmHeader: { flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }, alarmSafe: { color: "#087D70", backgroundColor: "#E9F9F5", borderColor: "#A8E4D9", borderWidth: 1, borderRadius: 11, padding: 10, fontSize: 12, fontWeight: "900" }, testButton: { minHeight: 43, backgroundColor: "#D92D20", borderRadius: 12, alignItems: "center", justifyContent: "center", gap: 7, flexDirection: "row" }, testButtonText: { color: "#FFFFFF", fontSize: 13, fontWeight: "900" }, alarmDanger: { color: "#B42318", backgroundColor: "#FEF0EE", borderColor: "#F7B2AC", borderWidth: 1, borderRadius: 11, padding: 10, fontSize: 12, fontWeight: "900" }, alarmInstruction: { color: "#7A271A", fontSize: 11, lineHeight: 16 }, activeRow: { flexDirection: "row", justifyContent: "space-between", gap: 8, borderTopColor: "#E9EDF1", borderTopWidth: 1, paddingTop: 8 }, activeName: { color: "#53657A", fontSize: 11, fontWeight: "800" }, activeValue: { color: "#B42318", fontSize: 12, fontWeight: "900" }, alarmActions: { flexDirection: "row", gap: 8 }, ackButton: { flex: 1.2, minHeight: 39, borderRadius: 11, backgroundColor: "#D92D20", justifyContent: "center", alignItems: "center" }, ackButtonText: { color: "#FFFFFF", fontSize: 12, fontWeight: "900" }, acknowledged: { backgroundColor: "#E9F9F5", borderColor: "#A8E4D9", borderWidth: 1 }, acknowledgedText: { color: "#087D70" }, resetButton: { flex: 0.8, minHeight: 39, borderRadius: 11, borderColor: "#E1A19B", borderWidth: 1, justifyContent: "center", alignItems: "center" }, resetText: { color: "#B42318", fontSize: 12, fontWeight: "900" }, tablePanel: { backgroundColor: "#FFFFFF", borderColor: "#E2EAF0", borderWidth: 1, borderRadius: 19, padding: 15, gap: 12 }, tableTitleRow: { flexDirection: "row", justifyContent: "space-between", gap: 8 }, tableHead: { flexDirection: "row", backgroundColor: "#F3F7F9", borderRadius: 9, paddingHorizontal: 8, paddingVertical: 8 }, tableHeadText: { color: "#708399", fontSize: 9, lineHeight: 12, letterSpacing: 0.55, fontWeight: "900" }, tableRow: { flexDirection: "row", alignItems: "center", paddingHorizontal: 8, paddingVertical: 10, borderBottomColor: "#E9EDF1", borderBottomWidth: 1 }, columnMetric: { flex: 1.2 }, columnReading: { flex: 0.9 }, columnStandard: { flex: 1.3 }, columnStatus: { flex: 1.15 }, tableMetric: { color: "#24394F", fontSize: 10, lineHeight: 14, fontWeight: "900", paddingRight: 4 }, tableReading: { color: "#0B1F33", fontSize: 10, lineHeight: 14, fontWeight: "900", paddingRight: 4 }, sourceLink: { flexDirection: "row", alignItems: "center", gap: 3, paddingRight: 4 }, sourceLinkText: { color: "#087D70", fontSize: 10, lineHeight: 14, fontWeight: "800", flexShrink: 1 }, footer: { backgroundColor: "#EAF0F4", borderRadius: 13, padding: 12, flexDirection: "row", gap: 8 }, footerText: { flex: 1, color: "#63758A", fontSize: 10, lineHeight: 15 }, pressed: { opacity: 0.72, transform: [{ scale: 0.98 }] },
});
