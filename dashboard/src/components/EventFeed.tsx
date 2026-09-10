"use client";

import React, { useState } from "react";

const EVENT_CONFIG: Record<string, { icon: string; color: string; border: string; bg: string; badge: string }> = {
  "Safety Car": {
    icon: "⚠️",
    color: "text-amber-300",
    border: "border-amber-500/40",
    bg: "bg-amber-950/30",
    badge: "bg-amber-500/20 text-amber-300 border-amber-500/40"
  },
  "Virtual Safety Car": {
    icon: "⏱️",
    color: "text-yellow-300",
    border: "border-yellow-500/40",
    bg: "bg-yellow-950/30",
    badge: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40"
  },
  "DNF": {
    icon: "🛑",
    color: "text-red-400",
    border: "border-red-500/40",
    bg: "bg-red-950/30",
    badge: "bg-red-500/20 text-red-300 border-red-500/40"
  },
  "Pit Stop": {
    icon: "🔧",
    color: "text-sky-400",
    border: "border-sky-500/30",
    bg: "bg-sky-950/20",
    badge: "bg-sky-500/20 text-sky-300 border-sky-500/30"
  },
  "Pit Stop Error": {
    icon: "⏱️",
    color: "text-orange-400",
    border: "border-orange-500/40",
    bg: "bg-orange-950/30",
    badge: "bg-orange-500/20 text-orange-300 border-orange-500/40"
  },
  "Overtake": {
    icon: "⚡",
    color: "text-emerald-400",
    border: "border-emerald-500/30",
    bg: "bg-emerald-950/20",
    badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
  },
  "Weather": {
    icon: "🌧️",
    color: "text-cyan-400",
    border: "border-cyan-500/30",
    bg: "bg-cyan-950/20",
    badge: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
  },
  "Team Order": {
    icon: "📻",
    color: "text-purple-400",
    border: "border-purple-500/30",
    bg: "bg-purple-950/20",
    badge: "bg-purple-500/20 text-purple-300 border-purple-500/30"
  },
  "Blue Flag": {
    icon: "🏴",
    color: "text-blue-400",
    border: "border-blue-500/30",
    bg: "bg-blue-950/20",
    badge: "bg-blue-500/20 text-blue-300 border-blue-500/30"
  },
};

type FilterCategory = "all" | "sc" | "dnf" | "pits" | "overtakes";

interface EventFeedProps {
  events: any[];
  currentLap: number;
  isSafetyCar?: boolean;
  isVSC?: boolean;
  onSelectLap?: (lap: number) => void;
}

export default function EventFeed({
  events,
  currentLap,
  isSafetyCar = false,
  isVSC = false,
  onSelectLap,
}: EventFeedProps) {
  const [filter, setFilter] = useState<FilterCategory>("all");

  if (!events || !Array.isArray(events)) return null;

  // Stable sort: current / recent laps first
  const visibleEvents = events
    .map((e, idx) => ({ ...e, _idx: idx }))
    .filter((e) => e.lap <= currentLap)
    .sort((a, b) => b.lap - a.lap || b._idx - a._idx);

  const filteredEvents = visibleEvents.filter((event) => {
    if (filter === "all") return true;
    if (filter === "sc") return event.type === "Safety Car" || event.type === "Virtual Safety Car";
    if (filter === "dnf") return event.type === "DNF";
    if (filter === "pits") return event.type === "Pit Stop" || event.type === "Pit Stop Error";
    if (filter === "overtakes") return event.type === "Overtake";
    return true;
  });

  const currentLapEvents = filteredEvents.filter((e) => e.lap === currentLap);
  const pastEvents = filteredEvents.filter((e) => e.lap < currentLap);

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 flex-wrap pb-1 border-b border-white/5">
        {(
          [
            { id: "all", label: "All Events" },
            { id: "sc", label: "SC & VSC" },
            { id: "dnf", label: "Incidents & DNF" },
            { id: "pits", label: "Pit Stops" },
            { id: "overtakes", label: "Overtakes" },
          ] as const
        ).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer ${
              filter === tab.id
                ? "bg-red-600/90 text-white shadow-[0_0_12px_rgba(225,6,0,0.4)]"
                : "bg-neutral-900/80 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active Track Condition Banner */}
      {currentLap > 0 && (
        <div className="transition-all">
          {isSafetyCar ? (
            <div className="p-3 rounded-lg border border-amber-500/50 bg-amber-500/10 animate-sc-glow flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="text-xl animate-flash-flag">⚠️</span>
                <div>
                  <div className="text-xs font-black uppercase tracking-widest text-amber-400">
                    Safety Car Deployed &bull; Lap {currentLap}
                  </div>
                  <div className="text-[11px] text-amber-300/80">
                    Field clustered behind physical Safety Car &bull; No overtaking permitted
                  </div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-amber-400 text-black font-black text-[10px] tracking-wider">
                SC
              </span>
            </div>
          ) : isVSC ? (
            <div className="p-3 rounded-lg border border-yellow-500/50 bg-yellow-500/10 animate-vsc-glow flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="text-xl animate-flash-flag">⏱️</span>
                <div>
                  <div className="text-xs font-black uppercase tracking-widest text-yellow-400">
                    Virtual Safety Car Active &bull; Lap {currentLap}
                  </div>
                  <div className="text-[11px] text-yellow-300/80">
                    Strict delta speed limits active &bull; Maintain minimum time delta
                  </div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-yellow-400 text-black font-black text-[10px] tracking-wider">
                VSC
              </span>
            </div>
          ) : currentLapEvents.length === 0 ? (
            <div className="py-2.5 px-3 rounded-lg border border-emerald-500/20 bg-emerald-950/20 flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold tracking-wide">
                <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
                <span>Track Clear &bull; Green Flag Racing</span>
              </div>
              <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">
                Lap {currentLap}
              </span>
            </div>
          ) : null}
        </div>
      )}

      {/* Current Lap Events */}
      {currentLapEvents.length > 0 && (
        <div className="flex flex-col gap-2">
          <div className="text-[10px] uppercase tracking-[0.2em] font-black text-neutral-400 flex items-center gap-2">
            <span>Lap {currentLap} Incidents</span>
            <span className="h-px flex-1 bg-neutral-800"></span>
          </div>

          {currentLapEvents.map((event) => {
            const config = EVENT_CONFIG[event.type] || {
              icon: "ℹ️",
              color: "text-neutral-300",
              border: "border-neutral-700/40",
              bg: "bg-neutral-900/60",
              badge: "bg-neutral-800 text-neutral-300 border-neutral-700",
            };

            return (
              <div
                key={`current-${event._idx}`}
                onClick={() => onSelectLap?.(event.lap)}
                className={`flex gap-3 items-start p-3 rounded-lg border ${config.border} ${config.bg} animate-fade-in hover:brightness-110 transition-all cursor-pointer shadow-sm relative group`}
              >
                <div className="flex flex-col items-center justify-center min-w-[2.75rem] py-1 px-1.5 rounded bg-black/40 border border-white/5">
                  <span className="text-[8px] font-black text-neutral-400 uppercase tracking-wider">
                    LAP
                  </span>
                  <span className="text-base font-bold font-[family-name:var(--font-mono)] text-white tabular-nums">
                    {event.lap}
                  </span>
                </div>

                <div className="text-lg select-none pt-0.5">{config.icon}</div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded border ${config.badge}`}
                    >
                      {event.type}
                    </span>
                    <span className="text-[9px] text-neutral-500 font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                      Click to jump
                    </span>
                  </div>
                  <div className="text-xs text-neutral-200 leading-relaxed font-medium">
                    {event.message}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Past Events Divider */}
      {pastEvents.length > 0 && (
        <div className="flex items-center gap-2 pt-1">
          <span className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-500">
            Previous Events ({pastEvents.length})
          </span>
          <div className="flex-1 border-t border-neutral-800/80"></div>
        </div>
      )}

      {/* Past Events List */}
      <div className="flex flex-col gap-2">
        {pastEvents.map((event) => {
          const config = EVENT_CONFIG[event.type] || {
            icon: "ℹ️",
            color: "text-neutral-400",
            border: "border-neutral-800/40",
            bg: "bg-neutral-900/30",
            badge: "bg-neutral-800/50 text-neutral-400 border-neutral-800",
          };

          return (
            <div
              key={`past-${event._idx}`}
              onClick={() => onSelectLap?.(event.lap)}
              className="flex gap-3 items-start p-2.5 rounded-lg border border-white/5 bg-neutral-900/40 hover:bg-neutral-800/60 hover:border-neutral-700 transition-all cursor-pointer group"
            >
              <div className="flex flex-col items-center justify-center min-w-[2.25rem] py-0.5 px-1 rounded bg-black/40 border border-white/5">
                <span className="text-[8px] font-bold text-neutral-500 uppercase tracking-wider">
                  L{event.lap}
                </span>
              </div>

              <div className="text-sm select-none opacity-80 pt-0.5">{config.icon}</div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span
                    className={`text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded border ${config.badge}`}
                  >
                    {event.type}
                  </span>
                  <span className="text-[9px] text-neutral-500 font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                    Jump to Lap {event.lap}
                  </span>
                </div>
                <div className="text-xs text-neutral-300 leading-normal">{event.message}</div>
              </div>
            </div>
          );
        })}
      </div>

      {visibleEvents.length === 0 && (
        <div className="text-center py-16 flex flex-col items-center justify-center">
          <div className="text-3xl mb-3 opacity-30">🏁</div>
          <div className="text-neutral-500 text-xs uppercase tracking-[0.2em] font-bold">
            Waiting for Lights Out...
          </div>
          <div className="text-neutral-600 text-[11px] mt-1">
            Advance laps to watch on-track incidents unfold
          </div>
        </div>
      )}
    </div>
  );
}
