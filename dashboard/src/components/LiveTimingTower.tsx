import React from "react";

const TEAM_COLORS: Record<string, string> = {
  "Oracle Red Bull Racing": "var(--team-red-bull)",
  "Scuderia Ferrari HP": "var(--team-ferrari)",
  "McLaren Formula 1": "var(--team-mclaren)",
  "McLaren Formula 1 ": "var(--team-mclaren)",
  "Mercedes-AMG Petronas F1": "var(--team-mercedes)",
  "Mercedes-AMG Petronas F1 ": "var(--team-mercedes)",
  "Aston Martin Aramco F1": "var(--team-aston-martin)",
  "Aston Martin Aramco F1 ": "var(--team-aston-martin)",
  "BWT Alpine F1": "var(--team-alpine)",
  "BWT Alpine F1 ": "var(--team-alpine)",
  "MoneyGram Haas F1": "var(--team-haas)",
  "MoneyGram Haas F1 ": "var(--team-haas)",
  "Visa Cash App Racing Bulls F1": "var(--team-rb)",
  "Visa Cash App Racing Bulls F1 ": "var(--team-rb)",
  "Williams Racing": "var(--team-williams)",
  "Stake F1 Kick Sauber": "var(--team-sauber)",
};

const TIRE_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  soft: { bg: "bg-red-500", text: "text-white", label: "S" },
  medium: { bg: "bg-yellow-400", text: "text-black", label: "M" },
  hard: { bg: "bg-white", text: "text-black", label: "H" },
  intermediate: { bg: "bg-green-500", text: "text-white", label: "I" },
  wet: { bg: "bg-blue-500", text: "text-white", label: "W" },
};

const formatGap = (gap: number, position: number) => {
  if (gap === -1) return <span className="text-red-500 font-bold">OUT</span>;
  if (position === 1) return <span className="text-neutral-500 text-xs">LEADER</span>;
  if (gap < 60) return <span>+{gap.toFixed(3)}</span>;
  const mins = Math.floor(gap / 60);
  const secs = (gap % 60).toFixed(1);
  return <span>+{mins}:{secs.padStart(4, '0')}</span>;
};

const getLastName = (fullName: string) => {
  const parts = fullName.trim().split(" ");
  return parts[parts.length - 1].toUpperCase();
};

const getFirstInitial = (fullName: string) => {
  return fullName.trim().charAt(0) + ".";
};

interface LiveTimingTowerProps {
  lapData: any[] | null;
  previousLapData: any[] | null;
  isGrid: boolean;
}

export default function LiveTimingTower({ lapData, previousLapData, isGrid }: LiveTimingTowerProps) {
  if (!lapData) return null;

  const previousPositionMap: Record<string, number> = {};
  if (previousLapData) {
    previousLapData.forEach((e: any) => {
      previousPositionMap[e.driver] = e.position;
    });
  }

  return (
    <div className="flex flex-col">
      {lapData.map((entry, index) => {
        const teamColor = TEAM_COLORS[entry.team] || "#666";
        const tire = TIRE_CONFIG[entry.tire] || TIRE_CONFIG.medium;
        const prevPos = previousPositionMap[entry.driver];
        const posChange = prevPos !== undefined ? prevPos - entry.position : 0;

        let posChangeClass = "";
        if (posChange > 0) posChangeClass = "animate-pos-up";
        if (posChange < 0) posChangeClass = "animate-pos-down";

        return (
          <div
            key={entry.driver}
            className={`flex justify-between items-center px-4 py-2 border-b border-neutral-800/30 hover:bg-neutral-800/30 transition-colors ${entry.dnf ? 'opacity-40' : ''} ${posChangeClass}`}
          >
            <div className="flex items-center gap-3">
              {/* Position number */}
              <div className="w-7 text-center font-[family-name:var(--font-mono)] font-bold text-sm tabular-nums text-neutral-400">
                {entry.position}
              </div>

              {/* Team color bar */}
              <div
                className="w-1 h-9 rounded-full"
                style={{ backgroundColor: teamColor }}
              />

              {/* Driver name + position delta */}
              <div className="flex items-center gap-2">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-neutral-500 text-xs">{getFirstInitial(entry.driver)}</span>
                    <span className="font-bold tracking-wide text-sm">{getLastName(entry.driver)}</span>
                  </div>
                  <div className="text-[10px] text-neutral-600 truncate max-w-[140px]">{entry.team}</div>
                </div>

                {/* Position change badge */}
                {!isGrid && posChange !== 0 && (
                  <span className={`text-[10px] font-bold px-1 py-0.5 rounded ${posChange > 0 ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'}`}>
                    {posChange > 0 ? `▲${posChange}` : `▼${Math.abs(posChange)}`}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-5">
              {/* Gap */}
              {!isGrid && (
                <div className="font-[family-name:var(--font-mono)] text-xs w-24 text-right tabular-nums text-neutral-300">
                  {formatGap(entry.gap, entry.position)}
                </div>
              )}

              {/* Tire compound */}
              {!isGrid && entry.tire && (
                <div className="flex items-center gap-1">
                  <div className={`w-6 h-6 rounded-full ${tire.bg} ${tire.text} text-[10px] font-black flex items-center justify-center`}>
                    {tire.label}
                  </div>
                  {entry.tire_laps !== undefined && (
                    <span className="text-[10px] text-neutral-600 font-[family-name:var(--font-mono)] w-4">{entry.tire_laps}</span>
                  )}
                </div>
              )}

              {/* Pit count */}
              {!isGrid && (
                <div className="font-[family-name:var(--font-mono)] text-xs w-6 text-center text-neutral-500">
                  {entry.pits || 0}
                </div>
              )}

              {/* Grid indicator */}
              {isGrid && (
                <div className="text-neutral-700 text-[10px] tracking-[0.15em] font-bold uppercase">P{entry.position}</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
