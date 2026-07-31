import React from "react";

const EVENT_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  "Overtake": { icon: "↑", color: "text-green-400", bg: "bg-green-400/10 border-green-400/20" },
  "Pit Stop": { icon: "🔧", color: "text-sky-400", bg: "bg-sky-400/10 border-sky-400/20" },
  "Pit Stop Error": { icon: "⚠️", color: "text-orange-400", bg: "bg-orange-400/10 border-orange-400/20" },
  "DNF": { icon: "✕", color: "text-red-500", bg: "bg-red-500/10 border-red-500/20" },
  "Safety Car": { icon: "SC", color: "text-yellow-400", bg: "bg-yellow-400/10 border-yellow-400/20" },
  "Weather": { icon: "🌤", color: "text-cyan-400", bg: "bg-cyan-400/10 border-cyan-400/20" },
  "Blue Flag": { icon: "🏴", color: "text-blue-400", bg: "bg-blue-400/10 border-blue-400/20" },
  "Team Order": { icon: "📡", color: "text-purple-400", bg: "bg-purple-400/10 border-purple-400/20" },
};

export default function EventFeed({ events, currentLap }: { events: any[]; currentLap: number }) {
  if (!events) return null;

  const visibleEvents = events
    .filter((e) => e.lap <= currentLap)
    .sort((a, b) => b.lap - a.lap || events.indexOf(b) - events.indexOf(a));

  const currentLapEvents = visibleEvents.filter((e) => e.lap === currentLap);
  const pastEvents = visibleEvents.filter((e) => e.lap < currentLap);

  return (
    <div className="flex flex-col gap-2">
      {/* Current lap events (highlighted) */}
      {currentLapEvents.map((event, i) => {
        const config = EVENT_CONFIG[event.type] || { icon: "ℹ", color: "text-neutral-400", bg: "bg-neutral-800/50 border-neutral-700/50" };
        return (
          <div key={`current-${i}`} className={`flex gap-3 items-start p-3 rounded-lg border animate-fade-in ${config.bg}`}>
            <div className="flex flex-col items-center min-w-[2.5rem]">
              <div className="text-[9px] font-bold text-neutral-500 uppercase tracking-[0.15em]">Lap</div>
              <div className="text-base font-[family-name:var(--font-mono)] font-bold text-neutral-200 tabular-nums">{event.lap}</div>
            </div>
            <div className={`text-sm mt-1 ${config.color}`}>{config.icon}</div>
            <div className="flex-1 min-w-0 mt-0.5">
              <div className={`text-[10px] font-bold uppercase tracking-[0.15em] mb-0.5 ${config.color}`}>{event.type}</div>
              <div className="text-xs text-neutral-300 leading-relaxed">{event.message}</div>
            </div>
          </div>
        );
      })}

      {/* Separator */}
      {currentLapEvents.length > 0 && pastEvents.length > 0 && (
        <div className="border-t border-neutral-800/50 my-1"></div>
      )}

      {/* Past events (dimmer) */}
      {pastEvents.map((event, i) => {
        const config = EVENT_CONFIG[event.type] || { icon: "ℹ", color: "text-neutral-400", bg: "bg-neutral-800/50 border-neutral-700/50" };
        return (
          <div key={`past-${i}`} className="flex gap-3 items-start p-2.5 rounded-lg opacity-50 hover:opacity-80 transition-opacity">
            <div className="flex flex-col items-center min-w-[2.5rem]">
              <div className="text-[9px] font-bold text-neutral-600 uppercase tracking-[0.15em]">Lap</div>
              <div className="text-sm font-[family-name:var(--font-mono)] font-bold text-neutral-500 tabular-nums">{event.lap}</div>
            </div>
            <div className={`text-xs mt-1 ${config.color} opacity-60`}>{config.icon}</div>
            <div className="flex-1 min-w-0 mt-0.5">
              <div className="text-[9px] font-bold uppercase tracking-[0.15em] text-neutral-600 mb-0.5">{event.type}</div>
              <div className="text-xs text-neutral-500 leading-relaxed">{event.message}</div>
            </div>
          </div>
        );
      })}

      {visibleEvents.length === 0 && (
        <div className="text-center py-16">
          <div className="text-3xl mb-3 opacity-20">🏁</div>
          <div className="text-neutral-700 text-xs uppercase tracking-[0.2em] font-bold">
            Waiting for lights out...
          </div>
        </div>
      )}
    </div>
  );
}
