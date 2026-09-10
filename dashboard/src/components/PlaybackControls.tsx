"use client";

import React, { useEffect, useState, useRef, useMemo } from "react";

interface PlaybackControlsProps {
  currentLap: number;
  totalLaps: number;
  isPlaying: boolean;
  speed: number;
  onPlayPause: () => void;
  onSeek: (lap: number) => void;
  onSpeedChange: (speed: number) => void;
  events?: any[];
  safetyCarLaps?: number[];
  vscLaps?: number[];
  dnfLaps?: number[];
  weatherChangeLaps?: number[];
  incidentLaps?: number[];
}

const SPEEDS = [0.5, 1, 2, 4, 8];

export default function PlaybackControls({
  currentLap,
  totalLaps,
  isPlaying,
  speed,
  onPlayPause,
  onSeek,
  onSpeedChange,
  events = [],
  safetyCarLaps = [],
  vscLaps = [],
  dnfLaps = [],
  weatherChangeLaps = [],
  incidentLaps = [],
}: PlaybackControlsProps) {
  const [hoverLap, setHoverLap] = useState<number | null>(null);
  const [hoverPos, setHoverPos] = useState<number>(0);
  const scrubberRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && currentLap < totalLaps) {
      interval = setInterval(() => {
        onSeek(currentLap + 1);
      }, 1000 / speed);
    } else if (currentLap >= totalLaps && isPlaying) {
      onPlayPause();
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentLap, totalLaps, speed, onSeek, onPlayPause]);

  const progress = totalLaps > 0 ? (currentLap / totalLaps) * 100 : 0;

  // Map each lap to incident details
  const lapIncidentMap = useMemo(() => {
    const map: Record<number, string[]> = {};
    if (Array.isArray(events)) {
      events.forEach((ev: any) => {
        if (!map[ev.lap]) map[ev.lap] = [];
        if (ev.type === "Safety Car" || ev.type === "Virtual Safety Car" || ev.type === "DNF" || ev.type === "Weather") {
          map[ev.lap].push(`${ev.type}: ${ev.message}`);
        }
      });
    }
    return map;
  }, [events]);

  // Find next / prev incidents
  const sortedIncidents = Array.from(new Set(incidentLaps)).sort((a, b) => a - b);
  const prevIncident = sortedIncidents.slice().reverse().find((lap) => lap < currentLap);
  const nextIncident = sortedIncidents.find((lap) => lap > currentLap);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!scrubberRef.current || totalLaps === 0) return;
    const rect = scrubberRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const pct = x / rect.width;
    const targetLap = Math.round(pct * totalLaps);
    setHoverLap(targetLap);
    setHoverPos(x);
  };

  const handleMouseLeave = () => {
    setHoverLap(null);
  };

  // Convert SC and VSC laps into contiguous segments for smooth timeline display
  const getSegments = (laps: number[]) => {
    if (!laps || laps.length === 0 || totalLaps === 0) return [];
    const sorted = Array.from(new Set(laps)).sort((a, b) => a - b);
    const segments: { start: number; end: number }[] = [];
    let start = sorted[0];
    let prev = sorted[0];

    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i] === prev + 1) {
        prev = sorted[i];
      } else {
        segments.push({ start, end: prev });
        start = sorted[i];
        prev = sorted[i];
      }
    }
    segments.push({ start, end: prev });
    return segments;
  };

  const scSegments = getSegments(safetyCarLaps);
  const vscSegments = getSegments(vscLaps);

  // Clamped position for hover tooltip to prevent overflow on container boundaries
  const containerWidth = scrubberRef.current?.clientWidth || 500;
  const clampedHoverLeft = Math.max(75, Math.min(hoverPos, containerWidth - 75));

  return (
    <div className="flex flex-col gap-3.5 w-full select-none">
      {/* Interactive Multi-Track Timeline */}
      <div
        ref={scrubberRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="relative pt-2 pb-1 cursor-pointer group"
      >
        {/* Track container */}
        <div className="relative h-2.5 bg-neutral-900 rounded-full border border-white/5 overflow-hidden">
          {/* Safety Car Regions (Yellow bands) */}
          {scSegments.map((seg, idx) => {
            const left = ((seg.start - 0.5) / totalLaps) * 100;
            const width = Math.max(1, ((seg.end - seg.start + 1) / totalLaps) * 100);
            return (
              <div
                key={`sc-${idx}`}
                className="absolute top-0 bottom-0 bg-amber-400/50 hover:bg-amber-400/80 transition-colors z-0"
                style={{ left: `${Math.max(0, left)}%`, width: `${width}%` }}
                title={`Safety Car: Laps ${seg.start}-${seg.end}`}
              />
            );
          })}

          {/* VSC Regions (Amber bands) */}
          {vscSegments.map((seg, idx) => {
            const left = ((seg.start - 0.5) / totalLaps) * 100;
            const width = Math.max(1, ((seg.end - seg.start + 1) / totalLaps) * 100);
            return (
              <div
                key={`vsc-${idx}`}
                className="absolute top-0 bottom-0 bg-yellow-400/40 hover:bg-yellow-400/70 transition-colors z-0"
                style={{ left: `${Math.max(0, left)}%`, width: `${width}%` }}
                title={`VSC: Laps ${seg.start}-${seg.end}`}
              />
            );
          })}

          {/* DNF Markers (Red ticks) */}
          {dnfLaps.map((lap, idx) => {
            const left = (lap / totalLaps) * 100;
            return (
              <div
                key={`dnf-${idx}`}
                className="absolute top-0 bottom-0 w-1 bg-red-500 z-10"
                style={{ left: `${left}%` }}
                title={`Incident / DNF on Lap ${lap}`}
              />
            );
          })}

          {/* Weather Change Markers (Cyan ticks) */}
          {weatherChangeLaps.map((lap, idx) => {
            const left = (lap / totalLaps) * 100;
            return (
              <div
                key={`weather-${idx}`}
                className="absolute top-0 bottom-0 w-1 bg-cyan-400 z-10"
                style={{ left: `${left}%` }}
                title={`Weather shift on Lap ${lap}`}
              />
            );
          })}

          {/* Playback progress fill */}
          <div
            className="h-full bg-gradient-to-r from-red-700 via-red-600 to-red-500 rounded-full transition-all duration-150 ease-out relative z-20 pointer-events-none"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
          </div>
        </div>

        {/* Range Slider for drag control */}
        <input
          type="range"
          min="0"
          max={totalLaps}
          value={currentLap}
          onChange={(e) => onSeek(parseInt(e.target.value))}
          className="absolute inset-0 w-full opacity-0 cursor-pointer h-7 -top-0.5 z-30"
          aria-label="Race Lap Timeline Scrubber"
        />

        {/* Hover Incident & Lap PopUp Tooltip */}
        {hoverLap !== null && (
          <div
            className="absolute -top-11 pointer-events-none transform -translate-x-1/2 bg-neutral-950/95 border border-neutral-700/80 px-3 py-1.5 rounded-lg text-[11px] font-mono text-neutral-200 shadow-[0_4px_20px_rgba(0,0,0,0.8)] z-50 whitespace-nowrap flex items-center gap-2 animate-fade-in backdrop-blur-md"
            style={{ left: `${clampedHoverLeft}px` }}
          >
            <span className="font-bold text-white bg-red-600/30 text-red-400 px-1.5 py-0.5 rounded border border-red-500/30 text-[10px]">
              LAP {hoverLap}
            </span>

            {lapIncidentMap[hoverLap] && lapIncidentMap[hoverLap].length > 0 ? (
              <span className="font-medium text-amber-300 max-w-[280px] truncate">
                {lapIncidentMap[hoverLap][0]}
              </span>
            ) : safetyCarLaps.includes(hoverLap) ? (
              <span className="text-amber-400 font-bold flex items-center gap-1">
                ⚠️ Safety Car Active
              </span>
            ) : vscLaps.includes(hoverLap) ? (
              <span className="text-yellow-400 font-bold flex items-center gap-1">
                ⏱️ Virtual Safety Car
              </span>
            ) : dnfLaps.includes(hoverLap) ? (
              <span className="text-red-400 font-bold flex items-center gap-1">
                🛑 Incident / Retirement
              </span>
            ) : (
              <span className="text-neutral-400 text-[10px]">Green Flag Racing</span>
            )}
          </div>
        )}

        {/* Timeline Legend / Key Info */}
        <div className="flex justify-between items-center text-[10px] text-neutral-500 font-[family-name:var(--font-mono)] mt-2 px-0.5">
          <div className="flex items-center gap-3">
            <span className="font-bold text-neutral-400">GRID (L0)</span>
            <div className="flex items-center gap-2">
              {scSegments.length > 0 && (
                <span className="inline-flex items-center gap-1 text-[9px] text-amber-400 font-bold">
                  <span className="w-2 h-2 rounded-xs bg-amber-400/80"></span> SC ({safetyCarLaps.length} Laps)
                </span>
              )}
              {vscSegments.length > 0 && (
                <span className="inline-flex items-center gap-1 text-[9px] text-yellow-400 font-bold">
                  <span className="w-2 h-2 rounded-xs bg-yellow-400/80"></span> VSC ({vscLaps.length} Laps)
                </span>
              )}
            </div>
          </div>

          {/* Prominent Current Lap Badge */}
          <div className="px-3 py-0.5 rounded-full bg-red-600/20 border border-red-500/40 text-white font-bold tracking-wider text-[11px] font-mono flex items-center gap-1.5 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            <span>LAP {currentLap} / {totalLaps}</span>
            <span className="text-neutral-400 text-[10px]">({Math.round(progress)}%)</span>
          </div>

          <span className="font-bold text-neutral-400">FINISH (L{totalLaps})</span>
        </div>
      </div>

      {/* Control Buttons & Speeds */}
      <div className="flex items-center justify-between gap-4">
        {/* Playback Speed selector */}
        <div className="flex items-center gap-1 bg-black/40 p-1 rounded-lg border border-white/5">
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold transition-all cursor-pointer ${
                speed === s
                  ? "bg-red-600 text-white shadow-[0_0_10px_rgba(225,6,0,0.4)]"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/80"
              }`}
            >
              {s}x
            </button>
          ))}
        </div>

        {/* Transport Controls */}
        <div className="flex items-center gap-1.5">
          {/* Skip to Grid */}
          <button
            onClick={() => onSeek(0)}
            className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800/80 transition-all cursor-pointer border border-transparent hover:border-white/10"
            title="Jump to Grid (Lap 0)"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" />
            </svg>
          </button>

          {/* Quick -5 Laps */}
          <button
            onClick={() => onSeek(Math.max(0, currentLap - 5))}
            className="px-2 py-1 rounded-md text-[10px] font-mono font-bold text-neutral-400 hover:text-white bg-neutral-900 border border-white/5 hover:bg-neutral-800 transition-all cursor-pointer"
            title="Jump back 5 laps"
          >
            -5
          </button>

          {/* Jump to Previous Incident */}
          {sortedIncidents.length > 0 && (
            <button
              onClick={() => prevIncident !== undefined && onSeek(prevIncident)}
              disabled={prevIncident === undefined}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
                prevIncident !== undefined
                  ? "text-amber-300 border-amber-500/30 bg-amber-950/20 hover:bg-amber-900/30 hover:border-amber-400"
                  : "text-neutral-600 border-transparent cursor-not-allowed"
              }`}
              title={prevIncident !== undefined ? `Jump to previous incident on Lap ${prevIncident}` : "No earlier incidents"}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
              <span className="text-[10px] uppercase font-bold tracking-wider">Prev Incident</span>
            </button>
          )}

          {/* Step Back 1 Lap */}
          <button
            onClick={() => onSeek(Math.max(0, currentLap - 1))}
            className="p-2 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800 transition-all cursor-pointer border border-white/5"
            title="Step Back 1 Lap (←)"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Big Play / Pause Button */}
          <button
            onClick={onPlayPause}
            className="w-11 h-11 rounded-full bg-gradient-to-br from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white transition-all flex items-center justify-center shadow-[0_0_20px_rgba(225,6,0,0.4)] hover:shadow-[0_0_25px_rgba(225,6,0,0.6)] cursor-pointer active:scale-95"
            title={isPlaying ? "Pause (Space)" : "Play Replay (Space)"}
          >
            {isPlaying ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6zm8 0h4v16h-4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          {/* Step Forward 1 Lap */}
          <button
            onClick={() => onSeek(Math.min(totalLaps, currentLap + 1))}
            className="p-2 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800 transition-all cursor-pointer border border-white/5"
            title="Step Forward 1 Lap (→)"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Jump to Next Incident */}
          {sortedIncidents.length > 0 && (
            <button
              onClick={() => nextIncident !== undefined && onSeek(nextIncident)}
              disabled={nextIncident === undefined}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
                nextIncident !== undefined
                  ? "text-amber-300 border-amber-500/30 bg-amber-950/20 hover:bg-amber-900/30 hover:border-amber-400"
                  : "text-neutral-600 border-transparent cursor-not-allowed"
              }`}
              title={nextIncident !== undefined ? `Jump to next incident on Lap ${nextIncident}` : "No upcoming incidents"}
            >
              <span className="text-[10px] uppercase font-bold tracking-wider">Next Incident</span>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          )}

          {/* Quick +5 Laps */}
          <button
            onClick={() => onSeek(Math.min(totalLaps, currentLap + 5))}
            className="px-2 py-1 rounded-md text-[10px] font-mono font-bold text-neutral-400 hover:text-white bg-neutral-900 border border-white/5 hover:bg-neutral-800 transition-all cursor-pointer"
            title="Jump forward 5 laps"
          >
            +5
          </button>

          {/* Skip to Finish */}
          <button
            onClick={() => onSeek(totalLaps)}
            className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800/80 transition-all cursor-pointer border border-transparent hover:border-white/10"
            title="Jump to Finish"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
            </svg>
          </button>
        </div>

        {/* Keyboard hints */}
        <div className="hidden lg:flex items-center gap-2 text-[10px] text-neutral-500">
          <kbd className="px-1.5 py-0.5 bg-neutral-900 border border-neutral-700/60 rounded text-neutral-400 font-mono">
            Space
          </kbd>
          <kbd className="px-1.5 py-0.5 bg-neutral-900 border border-neutral-700/60 rounded text-neutral-400 font-mono">
            ← →
          </kbd>
        </div>
      </div>
    </div>
  );
}
