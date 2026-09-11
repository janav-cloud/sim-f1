"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import LiveTimingTower from "@/components/LiveTimingTower";
import PlaybackControls from "@/components/PlaybackControls";
import EventFeed from "@/components/EventFeed";
import RaceFinishModal from "@/components/RaceFinishModal";

export default function Dashboard() {
  const [raceData, setRaceData] = useState<any>(null);
  const [currentLap, setCurrentLap] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [selectedDriver, setSelectedDriver] = useState<string | null>(null);
  const [dismissedIncidentLaps, setDismissedIncidentLaps] = useState<Set<number>>(new Set());
  const [showFinishModal, setShowFinishModal] = useState<boolean>(false);
  const [hasAutoOpenedFinishModal, setHasAutoOpenedFinishModal] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadJson = (text: string) => {
    try {
      const json = JSON.parse(text);
      // Support both old 'laps' key and standard 'total_laps' key
      if (!json.total_laps && json.laps) {
        json.total_laps = json.laps;
      }
      setRaceData(json);
      setCurrentLap(0);
      setIsPlaying(false);
      setSelectedDriver(null);
      setDismissedIncidentLaps(new Set());
      setShowFinishModal(false);
      setHasAutoOpenedFinishModal(false);
    } catch {
      alert("Invalid JSON file. Please provide a valid F1 simulation replay JSON.");
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

  // Resiliently compute all SC, VSC, DNF, and weather incident laps
  const { scLapSet, vscLapSet, dnfLapSet, weatherChangeLapSet, incidentLapList } = useMemo(() => {
    if (!raceData) {
      return {
        scLapSet: new Set<number>(),
        vscLapSet: new Set<number>(),
        dnfLapSet: new Set<number>(),
        weatherChangeLapSet: new Set<number>(),
        incidentLapList: [] as number[],
      };
    }

    const sc = new Set<number>();
    const vsc = new Set<number>();
    const dnfs = new Set<number>();
    const weather = new Set<number>();
    const incidents = new Set<number>();

    // 1. Scan laps_data directly
    if (Array.isArray(raceData.laps_data)) {
      raceData.laps_data.forEach((entry: any, idx: number) => {
        const lapNum = entry.lap || idx + 1;
        if (entry.vsc) {
          vsc.add(lapNum);
          incidents.add(lapNum);
        } else if (entry.safety_car) {
          sc.add(lapNum);
          incidents.add(lapNum);
        }
      });
    }

    // 2. Scan events to ensure any SC/VSC periods logged in events are captured even if missing in laps_data
    if (Array.isArray(raceData.events)) {
      let activeSCStart: number | null = null;
      let activeVSCStart: number | null = null;

      raceData.events.forEach((ev: any) => {
        const lap = ev.lap;
        if (ev.type === "DNF") {
          dnfs.add(lap);
          incidents.add(lap);
        } else if (ev.type === "Weather") {
          weather.add(lap);
        } else if (ev.type === "Safety Car") {
          incidents.add(lap);
          const msg = (ev.message || "").toLowerCase();
          if (msg.includes("in this lap") || msg.includes("ending") || msg.includes("resume")) {
            if (activeSCStart !== null) {
              for (let l = activeSCStart; l <= lap; l++) sc.add(l);
              activeSCStart = null;
            } else {
              sc.add(lap);
            }
          } else {
            activeSCStart = lap;
            sc.add(lap);
          }
        } else if (ev.type === "Virtual Safety Car") {
          incidents.add(lap);
          const msg = (ev.message || "").toLowerCase();
          if (msg.includes("ending") || msg.includes("green") || msg.includes("clear")) {
            if (activeVSCStart !== null) {
              for (let l = activeVSCStart; l <= lap; l++) vsc.add(l);
              activeVSCStart = null;
            } else {
              vsc.add(lap);
            }
          } else {
            activeVSCStart = lap;
            vsc.add(lap);
          }
        }
      });

      if (activeSCStart !== null) {
        for (let l = activeSCStart; l <= Math.min(activeSCStart + 3, raceData.total_laps); l++) sc.add(l);
      }
      if (activeVSCStart !== null) {
        for (let l = activeVSCStart; l <= Math.min(activeVSCStart + 2, raceData.total_laps); l++) vsc.add(l);
      }
    }

    return {
      scLapSet: sc,
      vscLapSet: vsc,
      dnfLapSet: dnfs,
      weatherChangeLapSet: weather,
      incidentLapList: Array.from(incidents).sort((a, b) => a - b),
    };
  }, [raceData]);

  const getCurrentLapData = useCallback(() => {
    if (!raceData || currentLap === 0) return null;
    const lapEntry = raceData.laps_data[currentLap - 1];
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

  // SC & VSC status checks
  const isVSCActive = useMemo(() => {
    if (!raceData || currentLap === 0) return false;
    const lapEntry = raceData.laps_data?.[currentLap - 1];
    if (lapEntry && !Array.isArray(lapEntry) && lapEntry.vsc === true) return true;
    return vscLapSet.has(currentLap);
  }, [raceData, currentLap, vscLapSet]);

  const isSafetyCarActive = useMemo(() => {
    if (!raceData || currentLap === 0 || isVSCActive) return false;
    const lapEntry = raceData.laps_data?.[currentLap - 1];
    if (lapEntry && !Array.isArray(lapEntry) && lapEntry.safety_car === true && !lapEntry.vsc) {
      return true;
    }
    return scLapSet.has(currentLap);
  }, [raceData, currentLap, isVSCActive, scLapSet]);

  // Active Incidents on current lap for PopUp banner
  const currentLapIncidents = useMemo(() => {
    if (!raceData?.events || currentLap === 0) return [];
    return raceData.events.filter(
      (e: any) =>
        e.lap === currentLap &&
        (e.type === "Safety Car" ||
          e.type === "Virtual Safety Car" ||
          e.type === "DNF" ||
          e.type === "Pit Stop Error")
    );
  }, [raceData, currentLap]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        setIsPlaying((p) => !p);
      }
      if (e.code === "ArrowRight") {
        e.preventDefault();
        setCurrentLap((l) => Math.min(totalLaps, l + 1));
      }
      if (e.code === "ArrowLeft") {
        e.preventDefault();
        setCurrentLap((l) => Math.max(0, l - 1));
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [totalLaps]);

  const weatherIcons: Record<string, string> = {
    Dry: "☀️",
    Hot: "🔥",
    Cold: "❄️",
    "Light Rain": "🌦️",
    "Heavy Rain": "🌧️",
    Overcast: "☁️",
  };

  // Selected driver telemetry computation
  const currentStandings = currentLap === 0 ? raceData?.starting_grid : getCurrentLapData();
  const selectedDriverData = useMemo(() => {
    if (!selectedDriver || !currentStandings) return null;
    return currentStandings.find((d: any) => d.driver === selectedDriver) || null;
  }, [selectedDriver, currentStandings]);

  // Teammate lookup
  const teammateData = useMemo(() => {
    if (!selectedDriverData || !currentStandings) return null;
    return (
      currentStandings.find(
        (d: any) => d.team === selectedDriverData.team && d.driver !== selectedDriverData.driver
      ) || null
    );
  }, [selectedDriverData, currentStandings]);

  // Running vs DNF counts
  const runningCount = currentStandings
    ? currentStandings.filter((d: any) => !d.dnf).length
    : 0;
  const dnfCount = currentStandings ? currentStandings.length - runningCount : 0;

  // Closest DRS on-track battle
  const closestBattle = useMemo(() => {
    if (!currentStandings || currentStandings.length < 2 || currentLap === 0) return null;
    const running = currentStandings.filter((d: any) => !d.dnf && d.gap !== -1);
    let minGap = 999;
    let battlePair: { leader: any; chaser: any; gap: number } | null = null;

    for (let i = 1; i < running.length; i++) {
      const gapDiff = running[i].gap - running[i - 1].gap;
      if (gapDiff > 0 && gapDiff < minGap) {
        minGap = gapDiff;
        battlePair = { leader: running[i - 1], chaser: running[i], gap: minGap };
      }
    }
    return battlePair && battlePair.gap < 1.2 ? battlePair : null;
  }, [currentStandings, currentLap]);

  // Real simulation telemetry: Grid tyre compound distribution
  const tyreDistribution = useMemo(() => {
    if (!currentStandings) return { soft: 0, medium: 0, hard: 0, intermediate: 0, wet: 0 };
    const counts = { soft: 0, medium: 0, hard: 0, intermediate: 0, wet: 0 };
    currentStandings.forEach((d: any) => {
      if (d.dnf) return;
      const compound = (d.tire || "").toLowerCase();
      if (compound.includes("soft")) counts.soft++;
      else if (compound.includes("hard")) counts.hard++;
      else if (compound.includes("inter")) counts.intermediate++;
      else if (compound.includes("wet")) counts.wet++;
      else counts.medium++;
    });
    return counts;
  }, [currentStandings]);

  // Real simulation telemetry: Pack spread (gap to last running car)
  const packSpread = useMemo(() => {
    if (!currentStandings || currentLap === 0) return 0;
    const running = currentStandings.filter((d: any) => !d.dnf && d.gap >= 0);
    if (running.length < 2) return 0;
    return running[running.length - 1].gap;
  }, [currentStandings, currentLap]);

  // Real simulation telemetry: Total pit stops completed across the grid
  const totalGridPitStops = useMemo(() => {
    if (!currentStandings) return 0;
    return currentStandings.reduce((sum: number, d: any) => sum + (d.pits || 0), 0);
  }, [currentStandings]);

  // Chequered flag at finish
  const isFinished = currentLap === totalLaps && totalLaps > 0;

  // Auto-open finish modal when chequered flag is reached
  useEffect(() => {
    if (isFinished) {
      if (!hasAutoOpenedFinishModal) {
        setShowFinishModal(true);
        setHasAutoOpenedFinishModal(true);
      }
    } else {
      setHasAutoOpenedFinishModal(false);
    }
  }, [isFinished, hasAutoOpenedFinishModal]);

  // ── Upload Screen (When no data loaded) ──
  if (!raceData) {
    return (
      <div
        className={`min-h-screen bg-neutral-950 flex flex-col justify-between text-white px-6 sm:px-12 md:px-16 lg:px-24 py-6 md:py-8 relative overflow-hidden select-none ${
          isDragOver ? "drag-active" : ""
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        {/* Cinematic Background MP4 Video with Gradient Overlays */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <video
            autoPlay
            loop
            muted
            playsInline
            ref={(el) => {
              if (el) {
                el.muted = true;
                el.play().catch(() => {});
              }
            }}
            className="w-full h-full object-cover object-center scale-105"
          >
            <source src="/assets/f1.mp4" type="video/mp4" />
          </video>
          {/* Multi-layered cinematic gradient: Darker on left for high legibility, transparent on right for full video view */}
          <div className="absolute inset-0 bg-gradient-to-r from-neutral-950/95 via-neutral-950/80 md:via-neutral-950/65 to-black/25" />
          <div className="absolute inset-0 bg-gradient-to-t from-neutral-950/90 via-transparent to-neutral-950/60" />
        </div>

        {/* Top Header on Landing */}
        <header className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/assets/formula1.png"
              alt="Formula 1"
              className="h-9 md:h-11 w-auto object-contain drop-shadow-[0_0_20px_rgba(225,6,0,0.6)]"
            />
            <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-white/10">
              <span className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444] animate-pulse"></span>
              <span className="text-[11px] font-mono tracking-widest uppercase text-neutral-300 font-bold">
                Simulation Telemetry
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 bg-neutral-900/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>SYSTEM READY</span>
          </div>
        </header>

        {/* Main Left-Aligned Hero Section */}
        <div className="max-w-xl w-full relative z-10 my-auto text-left py-8">
          <div className="mb-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-600/20 border border-red-500/40 text-red-400 text-xs font-mono font-bold uppercase tracking-widest mb-4 backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444] animate-ping"></span>
              F1 Simulation Replay
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white uppercase italic leading-[1.05] drop-shadow-lg">
              RACE REPLAY
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-red-400 to-amber-300">
                CENTER
              </span>
            </h1>

            <p className="text-neutral-300 text-xs sm:text-sm mt-3 max-w-lg leading-relaxed font-sans drop-shadow">
              Visualize race simulations with live timing towers, real-time Safety Car deployments,
              dynamic battle radars, and interactive incident feeds.
            </p>
          </div>

          {/* Upload Drop Zone (Glassmorphic, Left-Aligned) */}
          <label className="cursor-pointer group block">
            <div
              className={`border-2 border-dashed rounded-2xl p-6 sm:p-7 flex items-center gap-5 transition-all duration-300 bg-neutral-900/60 backdrop-blur-xl shadow-2xl ${
                isDragOver
                  ? "border-red-500 bg-red-500/20 scale-[1.02]"
                  : "border-white/15 hover:border-red-500/70 hover:bg-neutral-900/80"
              }`}
            >
              <div className="w-14 h-14 rounded-2xl bg-neutral-800/80 group-hover:bg-red-600/30 group-hover:border-red-500/50 border border-white/10 flex-shrink-0 flex items-center justify-center transition-all shadow-inner">
                <svg
                  className="w-7 h-7 text-neutral-300 group-hover:text-red-400 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
              </div>

              <div className="flex-1">
                <span className="text-white font-bold block text-sm sm:text-base">
                  Drop simulation <code className="text-red-400 bg-black/60 px-1.5 py-0.5 rounded text-xs font-mono font-bold">replay.json</code> here
                </span>
                <span className="text-neutral-400 text-xs block mt-1">
                  or click to select replay file from your computer
                </span>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              className="hidden"
              onChange={handleFileUpload}
            />
          </label>

          {/* Feature Badges */}
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="p-3 rounded-xl border border-white/10 bg-neutral-900/50 backdrop-blur-md text-[11px]">
              <div className="font-bold text-neutral-200 mb-0.5 flex items-center gap-1.5">
                <span>⚠️</span> SC & VSC Tracking
              </div>
              <div className="text-neutral-400 text-[10px]">
                Full safety car and virtual safety car period detection
              </div>
            </div>

            <div className="p-3 rounded-xl border border-white/10 bg-neutral-900/50 backdrop-blur-md text-[11px]">
              <div className="font-bold text-neutral-200 mb-0.5 flex items-center gap-1.5">
                <span>⏱️</span> Live Timing & Gaps
              </div>
              <div className="text-neutral-400 text-[10px]">
                Leader gap vs interval toggle & tyre telemetry
              </div>
            </div>
          </div>

          <div className="mt-4 text-neutral-400 text-xs font-mono flex items-center gap-2">
            <span>Controls: Space to Play/Pause &bull; ← / → to Navigate Laps</span>
          </div>
        </div>

        {/* Upload Screen Footer */}
        <footer className="relative z-10 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-neutral-400 py-3 border-t border-white/10 gap-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
            <span>Formula 1 Telemetry Analysis</span>
          </div>
          <div className="text-neutral-300 font-semibold">
            Made with 🏎️ by Janav Dua
          </div>
        </footer>
      </div>
    );
  }

  const currentWeather = getCurrentWeather();

  return (
    <div className="h-screen bg-neutral-950 text-white flex flex-col overflow-hidden select-none">
      {/* Dynamic Top Status Glow Accent */}
      <div
        className={`h-1 w-full transition-colors duration-300 ${isSafetyCarActive
            ? "bg-amber-400 animate-flash-flag shadow-[0_0_15px_#f59e0b]"
            : isVSCActive
              ? "bg-yellow-400 animate-flash-flag shadow-[0_0_15px_#eab308]"
              : isFinished
                ? "bg-gradient-to-r from-neutral-200 via-neutral-900 to-neutral-200"
                : "bg-red-600 shadow-[0_0_10px_#e10600]"
          }`}
      />

      {/* Broadcast Header with F1 Logo */}
      <header className="bg-neutral-900/90 backdrop-blur-md border-b border-white/10 px-6 py-2 flex justify-between items-center z-20 relative">
        {/* Left: Official F1 Logo & Circuit Title */}
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-3">
            <img
              src="/assets/formula1.png"
              alt="Formula 1 Logo"
              className="h-6 w-auto object-contain drop-shadow-[0_0_10px_rgba(225,6,0,0.5)]"
            />

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-black uppercase tracking-wider text-white">
                  {raceData.circuit || "Grand Prix"}
                </h1>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-white/10 text-neutral-300">
                  {totalLaps} LAPS
                </span>
              </div>
              <p className="text-[10px] text-neutral-400 font-mono">
                Monte Carlo Simulation Replay
              </p>
            </div>
          </div>

          <div className="h-7 w-px bg-neutral-800 hidden md:block"></div>

          {/* Weather Widget */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-md bg-black/40 border border-white/5 text-xs">
            <span className="text-base">{weatherIcons[currentWeather] || "☀️"}</span>
            <span className="text-neutral-300 font-medium">{currentWeather}</span>
          </div>
        </div>

        {/* Center: Track Status Pill */}
        <div className="flex items-center">
          {isSafetyCarActive ? (
            <div className="px-4 py-1 rounded-full bg-amber-400 text-black font-black uppercase tracking-[0.2em] text-xs flex items-center gap-2 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.6)]">
              <span className="text-sm animate-flash-flag">⚠️</span>
              <span>Safety Car Deployed</span>
              <span className="text-sm animate-flash-flag">⚠️</span>
            </div>
          ) : isVSCActive ? (
            <div className="px-4 py-1 rounded-full bg-yellow-400 text-black font-black uppercase tracking-[0.2em] text-xs flex items-center gap-2 animate-pulse shadow-[0_0_15px_rgba(234,179,8,0.6)]">
              <span className="text-sm animate-flash-flag">⏱️</span>
              <span>Virtual Safety Car Active</span>
              <span className="text-sm animate-flash-flag">⏱️</span>
            </div>
          ) : isFinished ? (
            <button
              onClick={() => setShowFinishModal(true)}
              className="px-4 py-1 rounded-full bg-neutral-100 hover:bg-yellow-400 text-black font-black uppercase tracking-[0.2em] text-xs flex items-center gap-2 shadow-md transition-all cursor-pointer"
              title="Click to view Official Race Classification"
            >
              <span>🏁</span>
              <span>Chequered Flag &bull; View Results</span>
              <span>🏆</span>
            </button>
          ) : currentLap === 0 ? (
            <div className="px-3 py-1 rounded-full bg-neutral-800 text-neutral-300 font-mono font-bold uppercase tracking-wider text-xs border border-white/5">
              Starting Grid
            </div>
          ) : (
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-widest px-3 py-1 rounded-full bg-emerald-950/30 border border-emerald-500/30">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
              <span>Track Clear</span>
            </div>
          )}
        </div>

        {/* Right: Lap Counter & Session Controls */}
        <div className="flex items-center gap-6">
          {/* Running vs DNF Pill */}
          <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono text-neutral-400">
            <span className="text-emerald-400 font-bold">{runningCount} Running</span>
            {dnfCount > 0 && <span className="text-red-400">&bull; {dnfCount} DNF</span>}
          </div>

          {/* Lap Counter */}
          <div className="text-right">
            <div className="text-[9px] text-neutral-400 uppercase tracking-[0.2em] font-black">
              LAP
            </div>
            <div className="text-xl font-[family-name:var(--font-mono)] font-black tabular-nums text-white leading-none">
              {currentLap === 0 ? (
                <span className="text-neutral-400">GRID</span>
              ) : (
                <>
                  {currentLap}
                  <span className="text-neutral-500 text-sm font-normal"> / {totalLaps}</span>
                </>
              )}
            </div>
          </div>

          {/* Close File Button */}
          <button
            onClick={() => {
              setRaceData(null);
              setCurrentLap(0);
              setIsPlaying(false);
              setSelectedDriver(null);
            }}
            className="text-neutral-400 hover:text-white px-2.5 py-1 rounded border border-white/5 hover:bg-neutral-800 transition-all text-xs font-mono font-bold cursor-pointer"
            title="Load another replay file"
          >
            ✕ Close
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Column: Official F1 Timing Tower */}
        <div className="w-[490px] flex-shrink-0 flex flex-col border-r border-white/10 bg-neutral-950">
          <LiveTimingTower
            lapData={currentLap === 0 ? raceData.starting_grid : getCurrentLapData()}
            previousLapData={getPreviousLapData()}
            isGrid={currentLap === 0}
            isSafetyCar={isSafetyCarActive}
            isVSC={isVSCActive}
            selectedDriver={selectedDriver}
            onSelectDriver={(d) => setSelectedDriver(d)}
          />
        </div>

        {/* Right Column: Controls, Telemetry HUD, Incident Alerts, and Event Feed */}
        <div className="flex-1 flex flex-col bg-neutral-950 overflow-hidden">
          {/* Playback Controls & Multi-Track Scrubber */}
          <div className="border-b border-white/10 px-6 pt-15 pb-6 bg-neutral-900/40 backdrop-blur-sm">
            <PlaybackControls
              currentLap={currentLap}
              totalLaps={totalLaps}
              isPlaying={isPlaying}
              speed={speed}
              onPlayPause={() => setIsPlaying(!isPlaying)}
              onSeek={(val) => setCurrentLap(val)}
              onSpeedChange={(s) => setSpeed(s)}
              events={raceData.events}
              safetyCarLaps={Array.from(scLapSet)}
              vscLaps={Array.from(vscLapSet)}
              dnfLaps={Array.from(dnfLapSet)}
              weatherChangeLaps={Array.from(weatherChangeLapSet)}
              incidentLaps={incidentLapList}
            />
          </div>

          {/* F1 PopUp Incident Banner (Appears when an incident occurs on this lap) */}
          {currentLapIncidents.length > 0 && !dismissedIncidentLaps.has(currentLap) && (
            <div className="mx-6 mt-3 p-3.5 rounded-xl border animate-slide-down flex items-center justify-between shadow-2xl relative overflow-hidden bg-gradient-to-r from-amber-950/90 via-neutral-900/95 to-neutral-950/95 border-amber-500/60 shadow-[0_0_25px_rgba(245,158,11,0.25)]">
              <div className="flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-amber-500 text-black font-black flex items-center justify-center text-lg animate-flash-flag shadow-md">
                  ⚠️
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] px-1.5 py-0.5 rounded bg-amber-500 text-black">
                      {currentLapIncidents[0].type}
                    </span>
                    <span className="text-[11px] font-mono text-neutral-400">
                      RACE CONTROL NOTIFICATION &bull; LAP {currentLap}
                    </span>
                  </div>
                  <div className="text-xs font-bold text-white mt-1">
                    {currentLapIncidents[0].message}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setDismissedIncidentLaps((prev) => new Set(prev).add(currentLap))}
                className="text-neutral-400 hover:text-white px-2.5 py-1 rounded bg-black/40 hover:bg-black/60 text-xs font-mono border border-white/5 cursor-pointer"
                title="Dismiss incident popup"
              >
                ✕ Dismiss
              </button>
            </div>
          )}

          {/* Telemetry Bar: DRS Battle Tracker & Track Conditions Radar */}
          <div className="mx-6 mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Closest Battle Card */}
            <div className="p-3 rounded-lg border border-white/5 bg-neutral-900/40 backdrop-blur-sm flex items-center justify-between">
              <div>
                <div className="text-[9px] uppercase font-black tracking-wider text-neutral-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></span>
                  Closest On-Track Battle
                </div>
                <div className="text-xs font-bold text-neutral-100 mt-0.5">
                  {closestBattle ? (
                    <>
                      <span>{closestBattle.chaser.driver.split(" ").pop()}</span>
                      <span className="text-red-400 mx-1">⚔️</span>
                      <span>{closestBattle.leader.driver.split(" ").pop()}</span>
                      <span className="text-emerald-400 font-mono text-[11px] ml-1.5">
                        +{closestBattle.gap.toFixed(3)}s
                      </span>
                    </>
                  ) : (
                    <span className="text-neutral-400 text-[11px]">Field spread &gt; 1.2s</span>
                  )}
                </div>
              </div>
              <span
                className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${closestBattle && !isSafetyCarActive && !isVSCActive
                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-drs"
                    : "bg-neutral-800 text-neutral-400 border-neutral-700"
                  }`}
              >
                {isSafetyCarActive || isVSCActive ? "DRS DISABLED" : "DRS ACTIVE"}
              </span>
            </div>

            {/* Real Telemetry: Grid Tyre Compounds & Pack Spread */}
            <div className="p-3 rounded-lg border border-white/5 bg-neutral-900/40 backdrop-blur-sm flex items-center justify-between">
              <div>
                <div className="text-[9px] uppercase font-black tracking-wider text-neutral-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  Grid Tyres & Pack Spread
                </div>
                <div className="text-xs font-mono font-bold text-neutral-200 mt-0.5 flex items-center gap-2">
                  <div className="flex items-center gap-1.5">
                    {tyreDistribution.soft > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-red-400">
                        <span className="w-2 h-2 rounded-full bg-red-500 inline-block"></span>
                        {tyreDistribution.soft}S
                      </span>
                    )}
                    {tyreDistribution.medium > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-yellow-400">
                        <span className="w-2 h-2 rounded-full bg-yellow-400 inline-block"></span>
                        {tyreDistribution.medium}M
                      </span>
                    )}
                    {tyreDistribution.hard > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-neutral-300">
                        <span className="w-2 h-2 rounded-full bg-neutral-300 inline-block"></span>
                        {tyreDistribution.hard}H
                      </span>
                    )}
                    {tyreDistribution.intermediate > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
                        {tyreDistribution.intermediate}I
                      </span>
                    )}
                    {tyreDistribution.wet > 0 && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-blue-400">
                        <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
                        {tyreDistribution.wet}W
                      </span>
                    )}
                  </div>
                  <span className="text-neutral-500">&bull;</span>
                  <span className="text-neutral-300 text-[11px]">
                    Spread: {packSpread > 0 ? `+${packSpread.toFixed(1)}s` : "0.0s"}
                  </span>
                </div>
              </div>
              <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-white/5 text-neutral-300 border border-white/5 font-bold">
                {totalGridPitStops} {totalGridPitStops === 1 ? "Pit Stop" : "Pit Stops"}
              </span>
            </div>
          </div>

          {/* Race Finish Celebration Podium (When Chequered Flag is Reached) */}
          {isFinished && currentStandings && currentStandings.length >= 3 && (
            <div className="mx-6 mt-3 p-4 rounded-xl border border-yellow-500/40 bg-gradient-to-r from-yellow-950/30 via-neutral-900/60 to-yellow-950/30 animate-fade-in flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-yellow-500 text-black font-black flex items-center justify-center text-xl shadow-[0_0_20px_rgba(234,179,8,0.5)]">
                  🏆
                </div>
                <div>
                  <div className="text-[10px] uppercase font-black tracking-[0.2em] text-yellow-400">
                    Grand Prix Winner
                  </div>
                  <div className="text-base font-black text-white">
                    {currentStandings[0]?.driver}
                  </div>
                  <div className="text-xs text-neutral-400">{currentStandings[0]?.team}</div>
                </div>
              </div>

              {/* Podium P2 & P3 */}
              <div className="flex items-center gap-6 text-xs">
                <div className="text-right">
                  <span className="text-[10px] font-black text-neutral-400 uppercase">P2 &bull; 🥈</span>
                  <div className="font-bold text-neutral-200">{currentStandings[1]?.driver}</div>
                  <div className="text-[10px] font-mono text-neutral-400">+{currentStandings[1]?.gap?.toFixed(3)}s</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-black text-neutral-400 uppercase">P3 &bull; 🥉</span>
                  <div className="font-bold text-neutral-200">{currentStandings[2]?.driver}</div>
                  <div className="text-[10px] font-mono text-neutral-400">+{currentStandings[2]?.gap?.toFixed(3)}s</div>
                </div>

                {/* View Official Results Dialog Button */}
                <button
                  onClick={() => setShowFinishModal(true)}
                  className="px-3.5 py-2 rounded-lg bg-yellow-500 hover:bg-yellow-400 text-black font-mono font-black text-xs uppercase tracking-wider transition-all shadow-lg hover:shadow-yellow-500/30 cursor-pointer flex items-center gap-1.5 ml-2"
                  title="View full P1-P10 points classification and podium"
                >
                  <span>🏆</span>
                  <span className="hidden sm:inline">Official</span> Results
                </button>
              </div>
            </div>
          )}

          {/* Driver Cockpit Telemetry HUD (When a driver is clicked) */}
          {selectedDriverData && (
            <div className="mx-6 mt-3 p-3.5 rounded-xl border border-red-500/40 bg-neutral-900/80 backdrop-blur-md animate-fade-in shadow-xl">
              <div className="flex items-center justify-between mb-2.5 border-b border-white/5 pb-2">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-red-600 text-white font-mono font-black text-xs">
                    P{selectedDriverData.position}
                  </span>
                  <div>
                    <h3 className="text-sm font-black uppercase tracking-wide text-white">
                      {selectedDriverData.driver}
                    </h3>
                    <span className="text-[11px] text-neutral-400">{selectedDriverData.team}</span>
                  </div>
                </div>

                {/* Cockpit Shift Lights Simulation */}
                <div className="hidden sm:flex items-center gap-1 bg-black/50 px-2.5 py-1 rounded-full border border-white/10">
                  <span className="w-2 h-2 rounded-full shift-light-green"></span>
                  <span className="w-2 h-2 rounded-full shift-light-green"></span>
                  <span className="w-2 h-2 rounded-full shift-light-green"></span>
                  <span className="w-2 h-2 rounded-full shift-light-red"></span>
                  <span className="w-2 h-2 rounded-full shift-light-red"></span>
                  <span className="w-2 h-2 rounded-full shift-light-blue animate-pulse"></span>
                  <span className="text-[10px] font-mono text-neutral-300 ml-1 font-bold">11,800 RPM</span>
                </div>

                <button
                  onClick={() => setSelectedDriver(null)}
                  className="text-neutral-400 hover:text-white text-xs font-mono px-2 py-0.5 rounded hover:bg-neutral-800 transition-colors cursor-pointer"
                >
                  ✕ Close
                </button>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                <div className="p-2.5 rounded bg-black/40 border border-white/5">
                  <div className="text-[9px] font-black uppercase tracking-wider text-neutral-400">
                    Gap to Leader
                  </div>
                  <div className="text-sm font-mono font-bold text-neutral-100 mt-0.5">
                    {selectedDriverData.position === 1
                      ? "LEADER"
                      : selectedDriverData.dnf
                        ? "RETIRED"
                        : `+${selectedDriverData.gap?.toFixed(3)}s`}
                  </div>
                </div>

                <div className="p-2.5 rounded bg-black/40 border border-white/5">
                  <div className="text-[9px] font-black uppercase tracking-wider text-neutral-400">
                    Current Tyre
                  </div>
                  <div className="text-sm font-mono font-bold text-neutral-100 mt-0.5 capitalize">
                    {selectedDriverData.tire || "Medium"}{" "}
                    <span className="text-neutral-400 text-xs">
                      ({selectedDriverData.tire_laps || 0} laps)
                    </span>
                  </div>
                </div>

                <div className="p-2.5 rounded bg-black/40 border border-white/5">
                  <div className="text-[9px] font-black uppercase tracking-wider text-neutral-400">
                    Pit Stops
                  </div>
                  <div className="text-sm font-mono font-bold text-neutral-100 mt-0.5">
                    {selectedDriverData.pits || 0} Stops
                  </div>
                </div>

                <div className="p-2.5 rounded bg-black/40 border border-white/5">
                  <div className="text-[9px] font-black uppercase tracking-wider text-neutral-400">
                    Teammate Delta
                  </div>
                  <div className="text-sm font-mono font-bold text-neutral-100 mt-0.5">
                    {teammateData
                      ? teammateData.position < selectedDriverData.position
                        ? `Behind by ${(selectedDriverData.gap - teammateData.gap).toFixed(3)}s`
                        : `Ahead by ${(teammateData.gap - selectedDriverData.gap).toFixed(3)}s`
                      : "N/A"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Event Feed Section */}
          <div className="flex-1 flex flex-col overflow-hidden mt-2">
            <div className="px-6 py-2 border-b border-white/5 flex justify-between items-center bg-neutral-900/30">
              <span className="text-[10px] uppercase tracking-[0.2em] font-black text-neutral-400">
                Live Incident & Race Event Feed
              </span>
              <span className="text-[10px] text-neutral-500 font-mono">
                Showing up to Lap {currentLap}
              </span>
            </div>

            <div className="flex-1 px-6 py-2.5 overflow-y-auto custom-scrollbar">
              <EventFeed
                events={raceData.events}
                currentLap={currentLap}
                isSafetyCar={isSafetyCarActive}
                isVSC={isVSCActive}
                onSelectLap={(lap) => setCurrentLap(lap)}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Broadcast Dashboard Footer */}
      <footer className="bg-neutral-900/90 backdrop-blur-md border-t border-white/10 px-6 py-2 flex items-center justify-between text-xs font-mono text-neutral-400 z-20">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
          <span>F1 Live Timing System &bull; {raceData.circuit}</span>
        </div>

        <div className="text-neutral-300 font-semibold flex items-center gap-1.5">
          <span>Made with 🏎️ by Janav Dua</span>
        </div>

        <div className="text-neutral-500">
          Lap {currentLap} / {totalLaps}
        </div>
      </footer>

      {/* Race Finish Official Results Dialog (Podium, P1-P10 Points & CSV Export) */}
      <RaceFinishModal
        isOpen={showFinishModal}
        onClose={() => setShowFinishModal(false)}
        standings={currentStandings || []}
        circuitName={raceData?.circuit || "Grand Prix"}
        totalLaps={totalLaps}
      />
    </div>
  );
}

