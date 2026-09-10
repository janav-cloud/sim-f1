"use client";

import React, { useState } from "react";

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

const KNOWN_CODES: Record<string, string> = {
  "Max Verstappen": "VER",
  "Sergio Perez": "PER",
  "Charles Leclerc": "LEC",
  "Carlos Sainz": "SAI",
  "Lando Norris": "NOR",
  "Oscar Piastri": "PIA",
  "Lewis Hamilton": "HAM",
  "George Russell": "RUS",
  "Fernando Alonso": "ALO",
  "Lance Stroll": "STR",
  "Pierre Gasly": "GAS",
  "Esteban Ocon": "OCO",
  "Alexander Albon": "ALB",
  "Franco Colapinto": "COL",
  "Logan Sargeant": "SAR",
  "Yuki Tsunoda": "TSU",
  "Liam Lawson": "LAW",
  "Daniel Ricciardo": "RIC",
  "Valtteri Bottas": "BOT",
  "Zhou Guanyu": "ZHO",
  "Nico Hulkenberg": "HUL",
  "Kevin Magnussen": "MAG",
  "Oliver Bearman": "BEA",
};

const TIRE_CONFIG: Record<string, { bg: string; text: string; label: string; border: string }> = {
  soft: { bg: "bg-red-500", text: "text-white", label: "S", border: "border-red-400" },
  medium: { bg: "bg-yellow-400", text: "text-black", label: "M", border: "border-yellow-300" },
  hard: { bg: "bg-white", text: "text-black", label: "H", border: "border-neutral-200" },
  intermediate: { bg: "bg-emerald-500", text: "text-white", label: "I", border: "border-emerald-400" },
  wet: { bg: "bg-blue-500", text: "text-white", label: "W", border: "border-blue-400" },
};

const getTeamColor = (teamName: string): string => {
  if (TEAM_COLORS[teamName]) return TEAM_COLORS[teamName];
  for (const [key, color] of Object.entries(TEAM_COLORS)) {
    if (teamName.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(teamName.toLowerCase())) {
      return color;
    }
  }
  return "#737373";
};

const getDriverCode = (fullName: string): string => {
  if (KNOWN_CODES[fullName]) return KNOWN_CODES[fullName];
  const parts = fullName.trim().split(" ");
  const lastName = parts[parts.length - 1];
  return lastName.slice(0, 3).toUpperCase();
};

const getLastName = (fullName: string) => {
  const parts = fullName.trim().split(" ");
  return parts[parts.length - 1].toUpperCase();
};

const getFirstInitial = (fullName: string) => {
  return fullName.trim().charAt(0) + ".";
};

const formatGapNumber = (gap: number) => {
  if (gap <= 0.0001) return "+0.000";
  if (gap < 60) return `+${gap.toFixed(3)}`;
  const mins = Math.floor(gap / 60);
  const secs = (gap % 60).toFixed(1);
  return `+${mins}:${secs.padStart(4, "0")}`;
};

interface LiveTimingTowerProps {
  lapData: any[] | null;
  previousLapData: any[] | null;
  isGrid: boolean;
  isSafetyCar?: boolean;
  isVSC?: boolean;
  selectedDriver?: string | null;
  onSelectDriver?: (driver: string | null) => void;
}

export default function LiveTimingTower({
  lapData,
  previousLapData,
  isGrid,
  isSafetyCar = false,
  isVSC = false,
  selectedDriver,
  onSelectDriver,
}: LiveTimingTowerProps) {
  const [gapMode, setGapMode] = useState<"leader" | "interval">("interval");

  if (!lapData) return null;

  const previousPositionMap: Record<string, number> = {};
  const previousPitsMap: Record<string, number> = {};

  if (previousLapData) {
    previousLapData.forEach((e: any) => {
      previousPositionMap[e.driver] = e.position;
      previousPitsMap[e.driver] = e.pits || 0;
    });
  }

  return (
    <div className="flex flex-col h-full select-none bg-neutral-950">
      {/* Tower Track Status Header */}
      <div className="px-4 py-2.5 border-b border-white/10 flex items-center justify-between bg-neutral-900/90 backdrop-blur-md">
        <div className="flex items-center gap-2">
          {isSafetyCar ? (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/60 text-amber-300 animate-sc-glow text-[11px] font-black tracking-widest uppercase">
              <span className="animate-flash-flag">⚠️</span>
              <span>SC Active</span>
            </div>
          ) : isVSC ? (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-yellow-500/20 border border-yellow-500/60 text-yellow-300 animate-vsc-glow text-[11px] font-black tracking-widest uppercase">
              <span className="animate-flash-flag">⏱️</span>
              <span>VSC Active</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-400 uppercase tracking-widest">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
              <span>Track Clear</span>
            </div>
          )}
        </div>

        {/* Gap Mode Toggle */}
        {!isGrid && (
          <div className="flex items-center bg-black/50 p-0.5 rounded border border-white/5 text-[9px] font-mono">
            <button
              onClick={() => setGapMode("interval")}
              className={`px-2 py-0.5 rounded transition-all cursor-pointer font-bold uppercase tracking-wider ${
                gapMode === "interval"
                  ? "bg-neutral-700 text-white shadow-xs"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
              title="Interval to car ahead"
            >
              Interval
            </button>
            <button
              onClick={() => setGapMode("leader")}
              className={`px-2 py-0.5 rounded transition-all cursor-pointer font-bold uppercase tracking-wider ${
                gapMode === "leader"
                  ? "bg-neutral-700 text-white shadow-xs"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
              title="Gap to race leader"
            >
              Leader
            </button>
          </div>
        )}
      </div>

      {/* Column Titles */}
      <div className="bg-neutral-900/60 px-4 py-2 text-[9px] uppercase tracking-[0.2em] font-black text-neutral-400 flex justify-between items-center border-b border-white/5">
        <div className="flex items-center gap-4">
          <span className="w-5 text-center">POS</span>
          <span>DRIVER</span>
        </div>
        <div className="flex items-center gap-5 text-right">
          {!isGrid && <span className="w-18">{gapMode === "interval" ? "INTERVAL" : "GAP"}</span>}
          {!isGrid && <span className="w-12 text-center">TYRE</span>}
          {!isGrid && <span className="w-7 text-center">PIT</span>}
          {isGrid && <span className="text-right">GRID</span>}
        </div>
      </div>

      {/* Timing Rows */}
      <div className="divide-y divide-white/5 overflow-y-auto custom-scrollbar flex-1">
        {lapData.map((entry, index) => {
          const teamColor = getTeamColor(entry.team);
          const tire = TIRE_CONFIG[entry.tire] || TIRE_CONFIG.medium;
          const prevPos = previousPositionMap[entry.driver];
          const posChange = prevPos !== undefined ? prevPos - entry.position : 0;
          const prevPits = previousPitsMap[entry.driver] ?? entry.pits;
          const justPitted = !isGrid && entry.pits > prevPits;
          const isSelected = selectedDriver === entry.driver;

          // Compute interval to the running car ahead
          let displayGap: React.ReactNode = null;
          if (entry.dnf || entry.gap === -1) {
            displayGap = <span className="text-red-500 font-bold text-[11px]">OUT</span>;
          } else if (entry.position === 1) {
            displayGap = <span className="text-neutral-400 font-bold text-[10px]">LEADER</span>;
          } else if (gapMode === "leader") {
            displayGap = <span>{formatGapNumber(entry.gap)}</span>;
          } else {
            // Interval mode: calculate difference with the immediately preceding non-DNF car
            let prevRunningCarGap = 0;
            for (let i = index - 1; i >= 0; i--) {
              if (!lapData[i].dnf && lapData[i].gap !== -1) {
                prevRunningCarGap = lapData[i].gap;
                break;
              }
            }
            const interval = Math.max(0, entry.gap - prevRunningCarGap);
            displayGap = <span>{formatGapNumber(interval)}</span>;
          }

          let posChangeClass = "";
          if (posChange > 0) posChangeClass = "animate-pos-up";
          if (posChange < 0) posChangeClass = "animate-pos-down";

          return (
            <div
              key={entry.driver}
              onClick={() => onSelectDriver?.(isSelected ? null : entry.driver)}
              className={`flex justify-between items-center px-4 py-2 transition-all cursor-pointer group ${
                isSelected
                  ? "bg-red-950/40 border-l-4 border-l-red-500"
                  : "hover:bg-neutral-800/40"
              } ${entry.dnf ? "opacity-45 hover:opacity-75" : ""} ${posChangeClass}`}
            >
              {/* Left Column: Position, Team Stripe, Driver Name */}
              <div className="flex items-center gap-2.5 min-w-0">
                {/* Position number */}
                <div
                  className={`w-6 text-center font-[family-name:var(--font-mono)] font-bold text-xs tabular-nums ${
                    entry.position === 1
                      ? "text-yellow-400"
                      : entry.position <= 3
                      ? "text-neutral-200"
                      : "text-neutral-400"
                  }`}
                >
                  {entry.position}
                </div>

                {/* Team Livery Colored Vertical Bar */}
                <div
                  className="w-1 h-8 rounded-full flex-shrink-0 shadow-[0_0_8px_rgba(255,255,255,0.2)]"
                  style={{ backgroundColor: teamColor }}
                />

                {/* Driver Tag & Name */}
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    {/* Official Driver 3-Letter Code */}
                    <span className="font-black text-xs font-[family-name:var(--font-mono)] tracking-wider px-1 py-0.2 rounded bg-black/40 border border-white/10 text-white">
                      {getDriverCode(entry.driver)}
                    </span>

                    <span className="text-neutral-400 text-xs hidden sm:inline">
                      {getFirstInitial(entry.driver)}
                    </span>
                    <span className="font-bold tracking-wide text-xs text-neutral-100 truncate">
                      {getLastName(entry.driver)}
                    </span>

                    {/* Position Delta Badge */}
                    {!isGrid && posChange !== 0 && (
                      <span
                        className={`text-[9px] font-black px-1 rounded flex items-center tabular-nums ${
                          posChange > 0
                            ? "text-emerald-400 bg-emerald-500/20"
                            : "text-red-400 bg-red-500/20"
                        }`}
                      >
                        {posChange > 0 ? `▲${posChange}` : `▼${Math.abs(posChange)}`}
                      </span>
                    )}
                  </div>

                  {/* Team name or DNF Reason */}
                  <div className="text-[10px] text-neutral-400 truncate max-w-[150px]">
                    {entry.dnf ? (
                      <span className="text-red-400 font-medium">
                        {entry.dnf_reason || "Retired"}
                      </span>
                    ) : (
                      entry.team
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Timing, Tyre, Pit */}
              <div className="flex items-center gap-5 flex-shrink-0">
                {/* Gap / Interval */}
                {!isGrid && (
                  <div className="font-[family-name:var(--font-mono)] text-xs w-18 text-right tabular-nums text-neutral-200 font-medium">
                    {displayGap}
                  </div>
                )}

                {/* Tyre Compound Pill */}
                {!isGrid && entry.tire && (
                  <div className="flex items-center gap-1 w-12 justify-center">
                    <div
                      className={`w-5 h-5 rounded-full ${tire.bg} ${tire.text} text-[10px] font-black flex items-center justify-center shadow-xs border ${tire.border}`}
                      title={`${entry.tire.toUpperCase()} tyre`}
                    >
                      {tire.label}
                    </div>
                    {entry.tire_laps !== undefined && (
                      <span
                        className="text-[10px] text-neutral-400 font-[family-name:var(--font-mono)] tabular-nums"
                        title={`${entry.tire_laps} laps on this compound`}
                      >
                        L{entry.tire_laps}
                      </span>
                    )}
                  </div>
                )}

                {/* Pit Stops Count or Pit-in Flash */}
                {!isGrid && (
                  <div className="w-7 text-center">
                    {justPitted ? (
                      <span className="px-1 py-0.5 rounded bg-sky-500 text-black font-black text-[9px] animate-pulse">
                        PIT
                      </span>
                    ) : (
                      <span className="font-[family-name:var(--font-mono)] text-xs text-neutral-400 tabular-nums">
                        {entry.pits || 0}
                      </span>
                    )}
                  </div>
                )}

                {/* Starting Grid Position */}
                {isGrid && (
                  <div className="text-neutral-400 text-xs font-mono font-bold uppercase tracking-wider">
                    P{entry.position}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
