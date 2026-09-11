"use client";

import React, { useState, useEffect } from "react";

interface DriverResult {
  driver: string;
  team: string;
  position: number;
  gap: number;
  tire?: string;
  tire_laps?: number;
  pits?: number;
  dnf?: boolean;
  dnf_reason?: string;
  time?: number;
}

interface RaceFinishModalProps {
  isOpen: boolean;
  onClose: () => void;
  standings: DriverResult[];
  circuitName: string;
  totalLaps: number;
}

const POINTS_SYSTEM = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1];

const TEAM_COLORS: Record<string, string> = {
  "Oracle Red Bull Racing": "#3671C6",
  "Scuderia Ferrari HP": "#E8002D",
  "Scuderia Ferrari": "#E8002D",
  "McLaren Formula 1": "#FF8000",
  "McLaren Formula 1 Team": "#FF8000",
  "Mercedes-AMG Petronas F1": "#27F4D2",
  "Mercedes-AMG Petronas F1 Team": "#27F4D2",
  "Aston Martin Aramco F1": "#229971",
  "Aston Martin Aramco F1 Team": "#229971",
  "BWT Alpine F1": "#FF87BC",
  "BWT Alpine F1 Team": "#FF87BC",
  "MoneyGram Haas F1": "#B6BABD",
  "MoneyGram Haas F1 Team": "#B6BABD",
  "Visa Cash App Racing Bulls F1": "#6692FF",
  "RB Formula One Team": "#6692FF",
  "Williams Racing": "#64C4FF",
  "Stake F1 Kick Sauber": "#52E252",
  "Kick Sauber": "#52E252",
};

const TIRE_BADGES: Record<string, { bg: string; text: string; label: string }> = {
  soft: { bg: "bg-red-500", text: "text-white", label: "S" },
  medium: { bg: "bg-yellow-400", text: "text-black", label: "M" },
  hard: { bg: "bg-white", text: "text-black", label: "H" },
  intermediate: { bg: "bg-emerald-500", text: "text-white", label: "I" },
  wet: { bg: "bg-blue-500", text: "text-white", label: "W" },
};

export default function RaceFinishModal({
  isOpen,
  onClose,
  standings,
  circuitName,
  totalLaps,
}: RaceFinishModalProps) {
  const [showFullField, setShowFullField] = useState<boolean>(false);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !standings || standings.length === 0) return null;

  const p1 = standings[0];
  const p2 = standings[1];
  const p3 = standings[2];

  const top10 = standings.slice(0, 10);
  const displayedStandings = showFullField ? standings : top10;

  // Format total seconds into H:MM:SS.sss or MM:SS.sss
  const formatTime = (totalSeconds?: number): string => {
    if (!totalSeconds || isNaN(totalSeconds)) return "-";
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = (totalSeconds % 60).toFixed(3);
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, "0")}:${seconds.padStart(6, "0")}`;
    }
    return `${minutes}:${seconds.padStart(6, "0")}`;
  };

  // Downloadable CSV generator
  const handleDownloadCsv = () => {
    const cleanCircuit = circuitName ? circuitName.trim().replace(/\s+/g, "_") : "Grand_Prix";
    const filename = `F1_${cleanCircuit}_Results.csv`;

    const headers = [
      "Position",
      "Driver",
      "Team",
      "Status",
      "Time(s)",
      "Gap",
      "Points",
      "Tyre",
      "Tyre Laps",
      "Pit Stops",
    ];

    const rows = standings.map((d, index) => {
      const pos = d.position || index + 1;
      const pts = d.dnf || pos > 10 ? 0 : POINTS_SYSTEM[pos - 1] || 0;
      const status = d.dnf ? (d.dnf_reason || "DNF") : "Finished";
      const timeVal = d.time ? Number(d.time).toFixed(3) : "";
      const gapVal = d.dnf
        ? "DNF"
        : pos === 1
        ? "LEADER"
        : d.gap !== -1 && d.gap !== undefined
        ? `+${Number(d.gap).toFixed(3)}s`
        : "";

      return [
        pos,
        `"${(d.driver || "").replace(/"/g, '""')}"`,
        `"${(d.team || "").replace(/"/g, '""')}"`,
        `"${status.replace(/"/g, '""')}"`,
        timeVal,
        `"${gapVal}"`,
        pts,
        `"${(d.tire || "").toUpperCase()}"`,
        d.tire_laps || 0,
        d.pits || 0,
      ].join(",");
    });

    const csvString = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto animate-fade-in">
      {/* Modal Container */}
      <div
        className="relative w-full max-w-4xl bg-neutral-950 border border-white/10 rounded-2xl shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col my-auto max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Glowing Header Strip */}
        <div className="h-1.5 w-full bg-gradient-to-r from-yellow-500 via-amber-400 to-yellow-500 shadow-[0_0_15px_rgba(234,179,8,0.5)]" />

        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-white/10 bg-neutral-900/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏁</span>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-black uppercase tracking-[0.25em] text-yellow-400 bg-yellow-500/10 px-2 py-0.5 rounded border border-yellow-500/20">
                  Official Race Classification
                </span>
                <span className="text-xs text-neutral-400 font-mono">
                  &bull; {totalLaps} Laps Completed
                </span>
              </div>
              <h2 className="text-lg sm:text-xl font-black uppercase text-white tracking-wide mt-0.5">
                {circuitName || "Grand Prix"}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Download CSV Button */}
            <button
              onClick={handleDownloadCsv}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-mono font-bold text-xs tracking-wider transition-all shadow-lg hover:shadow-red-600/30 cursor-pointer"
              title="Download results as CSV"
            >
              <span>📥</span>
              <span className="hidden sm:inline">Download CSV</span>
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white flex items-center justify-center transition-colors text-sm font-bold border border-white/5 cursor-pointer"
              title="Close modal (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body: Scrollable */}
        <div className="p-4 sm:p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
          {/* ── 3-Tier Podium Ceremony ── */}
          {p1 && (
            <div className="grid grid-cols-3 gap-2 sm:gap-4 items-end pt-2 pb-1">
              {/* P2 - Silver */}
              {p2 && (
                <div className="p-3 sm:p-4 rounded-xl border border-neutral-700 bg-gradient-to-t from-neutral-900/90 to-neutral-800/40 text-center flex flex-col items-center shadow-lg relative">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-neutral-300 text-neutral-950 font-black text-base sm:text-lg flex items-center justify-center shadow-md mb-2 border-2 border-white">
                    🥈
                  </div>
                  <span className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-neutral-400">
                    P2 &bull; 2nd Place
                  </span>
                  <div className="font-black text-white text-xs sm:text-sm mt-1 truncate max-w-full">
                    {p2.driver}
                  </div>
                  <div
                    className="text-[10px] sm:text-[11px] font-medium truncate max-w-full mt-0.5"
                    style={{ color: TEAM_COLORS[p2.team] || "#aaa" }}
                  >
                    {p2.team}
                  </div>
                  <div className="mt-2 text-[10px] sm:text-xs font-mono font-bold text-neutral-300">
                    +{p2.gap ? Number(p2.gap).toFixed(3) : "0.000"}s
                  </div>
                  <span className="mt-2 px-2 py-0.5 rounded-full bg-neutral-400/20 text-neutral-200 border border-neutral-400/30 text-[10px] font-mono font-black">
                    +18 PTS
                  </span>
                </div>
              )}

              {/* P1 - Gold (Winner) */}
              <div className="p-4 sm:p-5 rounded-xl border-2 border-yellow-500/70 bg-gradient-to-t from-yellow-950/40 via-neutral-900/90 to-neutral-800/60 text-center flex flex-col items-center shadow-[0_0_25px_rgba(234,179,8,0.25)] relative scale-105 z-10">
                <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-yellow-500 text-neutral-950 font-black text-xl sm:text-2xl flex items-center justify-center shadow-[0_0_15px_rgba(234,179,8,0.6)] mb-2 border-2 border-yellow-200 animate-pulse">
                  🏆
                </div>
                <span className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-yellow-400">
                  P1 &bull; Winner
                </span>
                <div className="font-black text-white text-sm sm:text-base mt-1 truncate max-w-full">
                  {p1.driver}
                </div>
                <div
                  className="text-[10px] sm:text-xs font-bold truncate max-w-full mt-0.5"
                  style={{ color: TEAM_COLORS[p1.team] || "#eab308" }}
                >
                  {p1.team}
                </div>
                <div className="mt-2 text-[10px] sm:text-xs font-mono font-bold text-yellow-300">
                  {formatTime(p1.time)}
                </div>
                <span className="mt-2 px-2.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/50 text-[11px] font-mono font-black shadow-sm">
                  +25 PTS
                </span>
              </div>

              {/* P3 - Bronze */}
              {p3 && (
                <div className="p-3 sm:p-4 rounded-xl border border-amber-700/60 bg-gradient-to-t from-neutral-900/90 to-neutral-800/40 text-center flex flex-col items-center shadow-lg relative">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-amber-700 text-white font-black text-base sm:text-lg flex items-center justify-center shadow-md mb-2 border-2 border-amber-500">
                    🥉
                  </div>
                  <span className="text-[10px] sm:text-xs font-black uppercase tracking-widest text-amber-500">
                    P3 &bull; 3rd Place
                  </span>
                  <div className="font-black text-white text-xs sm:text-sm mt-1 truncate max-w-full">
                    {p3.driver}
                  </div>
                  <div
                    className="text-[10px] sm:text-[11px] font-medium truncate max-w-full mt-0.5"
                    style={{ color: TEAM_COLORS[p3.team] || "#aaa" }}
                  >
                    {p3.team}
                  </div>
                  <div className="mt-2 text-[10px] sm:text-xs font-mono font-bold text-neutral-300">
                    +{p3.gap ? Number(p3.gap).toFixed(3) : "0.000"}s
                  </div>
                  <span className="mt-2 px-2 py-0.5 rounded-full bg-amber-600/20 text-amber-300 border border-amber-600/30 text-[10px] font-mono font-black">
                    +15 PTS
                  </span>
                </div>
              )}
            </div>
          )}

          {/* ── Points Classification Table (P1-P10) ── */}
          <div className="border border-white/10 rounded-xl overflow-hidden bg-neutral-900/40">
            <div className="px-4 py-2.5 bg-neutral-900/80 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-white">
                  {showFullField ? "Full Race Classification" : "Top 10 Points Scorers (P1–P10)"}
                </span>
                <span className="text-[10px] font-mono text-neutral-400">
                  ({displayedStandings.length} Drivers)
                </span>
              </div>

              {standings.length > 10 && (
                <button
                  onClick={() => setShowFullField(!showFullField)}
                  className="text-xs text-red-400 hover:text-red-300 font-mono font-bold transition-colors cursor-pointer"
                >
                  {showFullField ? "▲ Show Top 10 Only" : "▼ Show Full Field (P11–P20 & DNFs)"}
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-white/10 bg-black/40 text-[10px] uppercase tracking-wider text-neutral-400">
                    <th className="py-2.5 px-3">POS</th>
                    <th className="py-2.5 px-3">DRIVER</th>
                    <th className="py-2.5 px-3 hidden sm:table-cell">TEAM</th>
                    <th className="py-2.5 px-3 text-right">TIME / GAP</th>
                    <th className="py-2.5 px-3 text-center">TYRE</th>
                    <th className="py-2.5 px-3 text-center">PITS</th>
                    <th className="py-2.5 px-3 text-right">POINTS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {displayedStandings.map((driver, index) => {
                    const pos = driver.position || index + 1;
                    const pts = driver.dnf || pos > 10 ? 0 : POINTS_SYSTEM[pos - 1] || 0;
                    const isTop10 = pos <= 10 && !driver.dnf;
                    const tyreBadge = TIRE_BADGES[(driver.tire || "").toLowerCase()] || TIRE_BADGES.medium;

                    return (
                      <tr
                        key={driver.driver + index}
                        className={`hover:bg-white/[0.03] transition-colors ${
                          pos === 1
                            ? "bg-yellow-500/5 font-semibold"
                            : pos === 2
                            ? "bg-neutral-400/5"
                            : pos === 3
                            ? "bg-amber-600/5"
                            : ""
                        }`}
                      >
                        {/* Position */}
                        <td className="py-2.5 px-3">
                          <span
                            className={`inline-flex items-center justify-center w-6 h-6 rounded text-[11px] font-black ${
                              pos === 1
                                ? "bg-yellow-500 text-black shadow-sm"
                                : pos === 2
                                ? "bg-neutral-300 text-black"
                                : pos === 3
                                ? "bg-amber-700 text-white"
                                : isTop10
                                ? "bg-white/10 text-white"
                                : "text-neutral-500"
                            }`}
                          >
                            {pos}
                          </span>
                        </td>

                        {/* Driver */}
                        <td className="py-2.5 px-3 font-bold text-white">
                          <div className="flex items-center gap-2">
                            <span
                              className="w-1 h-3.5 rounded-full"
                              style={{ backgroundColor: TEAM_COLORS[driver.team] || "#888" }}
                            />
                            <span>{driver.driver}</span>
                            {driver.dnf && (
                              <span className="text-[10px] font-black px-1.5 py-0.2 rounded bg-red-600/20 text-red-400 border border-red-500/30">
                                DNF
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Team */}
                        <td className="py-2.5 px-3 text-neutral-400 hidden sm:table-cell">
                          {driver.team}
                        </td>

                        {/* Time / Gap */}
                        <td className="py-2.5 px-3 text-right font-mono">
                          {driver.dnf ? (
                            <span className="text-red-400 text-[11px] font-medium">
                              {driver.dnf_reason || "Retired"}
                            </span>
                          ) : pos === 1 ? (
                            <span className="text-yellow-400 font-bold">
                              {formatTime(driver.time)}
                            </span>
                          ) : (
                            <span className="text-neutral-300">
                              +{driver.gap ? Number(driver.gap).toFixed(3) : "0.000"}s
                            </span>
                          )}
                        </td>

                        {/* Tyre */}
                        <td className="py-2.5 px-3 text-center">
                          <span
                            className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-black ${tyreBadge.bg} ${tyreBadge.text}`}
                            title={`${driver.tire || "Medium"} compound (${driver.tire_laps || 0} laps)`}
                          >
                            {tyreBadge.label}
                          </span>
                        </td>

                        {/* Pit Stops */}
                        <td className="py-2.5 px-3 text-center text-neutral-300">
                          {driver.pits || 0}
                        </td>

                        {/* Points */}
                        <td className="py-2.5 px-3 text-right">
                          {pts > 0 ? (
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-[11px] font-black font-mono ${
                                pos === 1
                                  ? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/40"
                                  : pos === 2
                                  ? "bg-neutral-300/20 text-neutral-200 border border-neutral-300/40"
                                  : pos === 3
                                  ? "bg-amber-600/20 text-amber-300 border border-amber-600/40"
                                  : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              }`}
                            >
                              +{pts} PTS
                            </span>
                          ) : (
                            <span className="text-neutral-600 text-[11px] font-mono">0 PTS</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-white/10 bg-neutral-900/60 flex items-center justify-between text-xs font-mono text-neutral-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Official FIA F1 Points System &bull; 25-18-15-12-10-8-6-4-2-1</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadCsv}
              className="text-neutral-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer font-bold"
            >
              <span>📥</span>
              <span>Export CSV</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-white font-bold transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
