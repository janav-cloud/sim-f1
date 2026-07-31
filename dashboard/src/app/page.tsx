"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import LiveTimingTower from "@/components/LiveTimingTower";
import PlaybackControls from "@/components/PlaybackControls";
import EventFeed from "@/components/EventFeed";

export default function Dashboard() {
  const [raceData, setRaceData] = useState<any>(null);
  const [currentLap, setCurrentLap] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadJson = (text: string) => {
    try {
      const json = JSON.parse(text);
      // Normalize: support both old 'laps' key and new 'total_laps' key
      if (!json.total_laps && json.laps) {
        json.total_laps = json.laps;
      }
      setRaceData(json);
      setCurrentLap(0);
      setIsPlaying(false);
    } catch {
      alert("Invalid JSON file.");
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => loadJson(e.target?.result as string);
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => loadJson(ev.target?.result as string);
    reader.readAsText(file);
  };

  const totalLaps = raceData?.total_laps || 0;

  const getCurrentLapData = useCallback(() => {
    if (!raceData || currentLap === 0) return null;
    const lapEntry = raceData.laps_data[currentLap - 1];
    // Support both new format (object with standings) and old format (array)
    if (Array.isArray(lapEntry)) return lapEntry;
    return lapEntry?.standings || [];
  }, [raceData, currentLap]);

  const getPreviousLapData = useCallback(() => {
    if (!raceData || currentLap <= 1) return null;
    const lapEntry = raceData.laps_data[currentLap - 2];
    if (Array.isArray(lapEntry)) return lapEntry;
    return lapEntry?.standings || [];
  }, [raceData, currentLap]);

  const getCurrentWeather = useCallback(() => {
    if (!raceData || currentLap === 0) return raceData?.initial_weather || "Dry";
    const lapEntry = raceData.laps_data[currentLap - 1];
    if (lapEntry && !Array.isArray(lapEntry)) return lapEntry.weather || "Dry";
    return "Dry";
  }, [raceData, currentLap]);

  const isSafetyCar = useCallback(() => {
    if (!raceData || currentLap === 0) return false;
    const lapEntry = raceData.laps_data[currentLap - 1];
    if (lapEntry && !Array.isArray(lapEntry)) return lapEntry.safety_car || false;
    return false;
  }, [raceData, currentLap]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === "Space") { e.preventDefault(); setIsPlaying(p => !p); }
      if (e.code === "ArrowRight") { e.preventDefault(); setCurrentLap(l => Math.min(totalLaps, l + 1)); }
      if (e.code === "ArrowLeft") { e.preventDefault(); setCurrentLap(l => Math.max(0, l - 1)); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [totalLaps]);

  const weatherIcons: Record<string, string> = {
    "Dry": "☀️", "Hot": "🔥", "Cold": "❄️",
    "Light Rain": "🌦️", "Heavy Rain": "🌧️", "Overcast": "☁️"
  };

  if (!raceData) {
    return (
      <div
        className={`min-h-screen bg-neutral-950 flex flex-col items-center justify-center text-white p-8 transition-all ${isDragOver ? 'drag-active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        <div className="max-w-lg w-full">
          <div className="text-center mb-12">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-red-600 to-red-700 rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(220,38,38,0.3)] rotate-3">
              <span className="text-3xl">🏎️</span>
            </div>
            <h1 className="text-4xl font-bold tracking-tight mb-3">F1 Race Replay</h1>
            <p className="text-neutral-500 text-sm max-w-xs mx-auto">Upload a simulation <code className="text-neutral-400 bg-neutral-800 px-1.5 py-0.5 rounded text-xs">replay.json</code> to visualize the race lap by lap.</p>
          </div>

          <label className="cursor-pointer group block">
            <div className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center gap-4 transition-all duration-300 ${isDragOver ? 'border-red-500 bg-red-500/10' : 'border-neutral-800 hover:border-neutral-600 hover:bg-neutral-900/50'}`}>
              <div className="w-12 h-12 rounded-full bg-neutral-800 group-hover:bg-neutral-700 flex items-center justify-center transition-colors">
                <svg className="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
              </div>
              <div className="text-center">
                <span className="text-neutral-300 font-medium block mb-1">Drop file here or click to browse</span>
                <span className="text-neutral-600 text-xs">JSON files only</span>
              </div>
            </div>
            <input ref={fileInputRef} type="file" accept=".json" className="hidden" onChange={handleFileUpload} />
          </label>

          <div className="mt-8 text-center text-neutral-700 text-xs">
            <span>Space: Play/Pause · ← →: Navigate laps</span>
          </div>
        </div>
      </div>
    );
  }

  const currentWeather = getCurrentWeather();
  const scActive = isSafetyCar();

  return (
    <div className="h-screen bg-neutral-950 text-white flex flex-col overflow-hidden">
      {/* Safety Car Banner */}
      {scActive && (
        <div className="bg-yellow-500/90 text-black py-2 px-8 text-center font-bold uppercase tracking-[0.3em] text-sm animate-slide-down animate-pulse-glow flex items-center justify-center gap-3">
          <span className="text-lg">⚠️</span>
          Safety Car Deployed
          <span className="text-lg">⚠️</span>
        </div>
      )}

      {/* Header */}
      <header className="bg-neutral-900/80 backdrop-blur-md border-b border-neutral-800/50 px-8 py-3 flex justify-between items-center z-10 relative">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center shadow-[0_0_12px_rgba(220,38,38,0.3)]">
              <span className="text-sm">🏎️</span>
            </div>
            <div>
              <h1 className="text-sm font-bold uppercase tracking-[0.2em] text-red-500">Live Timing</h1>
              <p className="text-xs text-neutral-500">{raceData.circuit}</p>
            </div>
          </div>
          <div className="h-8 w-px bg-neutral-800"></div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-lg">{weatherIcons[currentWeather] || "☀️"}</span>
            <span className="text-neutral-400 font-medium">{currentWeather}</span>
          </div>
        </div>

        <div className="flex items-center gap-8">
          <div className="text-right">
            <div className="text-[10px] text-neutral-600 uppercase tracking-[0.2em] font-bold">Lap</div>
            <div className="text-xl font-[family-name:var(--font-mono)] font-bold tabular-nums">
              {currentLap === 0 ? (
                <span className="text-neutral-500">GRID</span>
              ) : (
                <>{currentLap}<span className="text-neutral-600 text-base"> / {totalLaps}</span></>
              )}
            </div>
          </div>
          <button
            onClick={() => { setRaceData(null); setCurrentLap(0); setIsPlaying(false); }}
            className="text-neutral-600 hover:text-neutral-300 transition-colors text-xs uppercase tracking-widest font-bold"
          >
            ✕ Close
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left: Timing Tower */}
        <div className="w-[480px] flex-shrink-0 flex flex-col border-r border-neutral-800/50 bg-neutral-950">
          <div className="bg-neutral-900/60 px-4 py-2.5 text-[10px] uppercase tracking-[0.2em] font-bold text-neutral-600 flex justify-between items-center border-b border-neutral-800/50">
            <span>Pos</span>
            <div className="flex gap-6">
              <span className="w-20 text-right">Interval</span>
              <span className="w-8 text-center">Tire</span>
              <span className="w-8 text-center">Pits</span>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <LiveTimingTower
              lapData={currentLap === 0 ? raceData.starting_grid : getCurrentLapData()}
              previousLapData={getPreviousLapData()}
              isGrid={currentLap === 0}
            />
          </div>
        </div>

        {/* Right Panel */}
        <div className="flex-1 flex flex-col bg-neutral-950">
          {/* Playback Controls */}
          <div className="border-b border-neutral-800/50 px-6 py-5">
            <PlaybackControls
              currentLap={currentLap}
              totalLaps={totalLaps}
              isPlaying={isPlaying}
              speed={speed}
              onPlayPause={() => setIsPlaying(!isPlaying)}
              onSeek={(val) => setCurrentLap(val)}
              onSpeedChange={(s) => setSpeed(s)}
            />
          </div>

          {/* Event Feed */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="bg-neutral-900/60 px-6 py-2.5 text-[10px] uppercase tracking-[0.2em] font-bold text-neutral-600 border-b border-neutral-800/50">
              Race Events
            </div>
            <div className="flex-1 px-6 py-4 overflow-y-auto custom-scrollbar">
              <EventFeed events={raceData.events} currentLap={currentLap} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
