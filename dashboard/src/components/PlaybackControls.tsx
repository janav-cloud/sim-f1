import React, { useEffect } from "react";

interface PlaybackControlsProps {
  currentLap: number;
  totalLaps: number;
  isPlaying: boolean;
  speed: number;
  onPlayPause: () => void;
  onSeek: (lap: number) => void;
  onSpeedChange: (speed: number) => void;
}

const SPEEDS = [0.5, 1, 2, 4];

export default function PlaybackControls({
  currentLap, totalLaps, isPlaying, speed,
  onPlayPause, onSeek, onSpeedChange
}: PlaybackControlsProps) {
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

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Progress bar */}
      <div className="relative">
        <div className="h-1 bg-neutral-800 rounded-full overflow-hidden mb-1">
          <div
            className="h-full bg-gradient-to-r from-red-600 to-red-500 rounded-full transition-all duration-300 ease-linear"
            style={{ width: `${progress}%` }}
          />
        </div>
        <input
          type="range"
          min="0"
          max={totalLaps}
          value={currentLap}
          onChange={(e) => onSeek(parseInt(e.target.value))}
          className="absolute inset-0 w-full opacity-0 cursor-pointer h-6 -top-2"
        />
        <div className="flex justify-between text-[10px] text-neutral-700 font-[family-name:var(--font-mono)] tabular-nums">
          <span>Lap 0</span>
          <span>Lap {totalLaps}</span>
        </div>
      </div>

      {/* Controls row */}
      <div className="flex items-center justify-between">
        {/* Speed selector */}
        <div className="flex items-center gap-1">
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`px-2.5 py-1 rounded-md text-xs font-bold transition-all ${
                speed === s
                  ? 'bg-red-600 text-white shadow-[0_0_10px_rgba(220,38,38,0.3)]'
                  : 'bg-neutral-800 text-neutral-500 hover:text-neutral-300 hover:bg-neutral-700'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>

        {/* Transport controls */}
        <div className="flex items-center gap-2">
          {/* Skip to start */}
          <button
            onClick={() => onSeek(0)}
            className="p-2 rounded-lg text-neutral-500 hover:text-white hover:bg-neutral-800 transition-all"
            title="Go to grid"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z" /></svg>
          </button>

          {/* Previous lap */}
          <button
            onClick={() => onSeek(Math.max(0, currentLap - 1))}
            className="p-2 rounded-lg text-neutral-500 hover:text-white hover:bg-neutral-800 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
          </button>

          {/* Play/Pause */}
          <button
            onClick={onPlayPause}
            className="w-12 h-12 rounded-full bg-red-600 hover:bg-red-500 text-white transition-all flex items-center justify-center shadow-[0_0_20px_rgba(220,38,38,0.25)] hover:shadow-[0_0_25px_rgba(220,38,38,0.4)]"
          >
            {isPlaying ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6zm8 0h4v16h-4z" /></svg>
            ) : (
              <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
            )}
          </button>

          {/* Next lap */}
          <button
            onClick={() => onSeek(Math.min(totalLaps, currentLap + 1))}
            className="p-2 rounded-lg text-neutral-500 hover:text-white hover:bg-neutral-800 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" /></svg>
          </button>

          {/* Skip to end */}
          <button
            onClick={() => onSeek(totalLaps)}
            className="p-2 rounded-lg text-neutral-500 hover:text-white hover:bg-neutral-800 transition-all"
            title="Go to finish"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" /></svg>
          </button>
        </div>

        {/* Keyboard hint */}
        <div className="flex items-center gap-2 text-[10px] text-neutral-700">
          <kbd className="px-1.5 py-0.5 bg-neutral-800 rounded text-neutral-500 font-[family-name:var(--font-mono)]">Space</kbd>
          <kbd className="px-1.5 py-0.5 bg-neutral-800 rounded text-neutral-500 font-[family-name:var(--font-mono)]">← →</kbd>
        </div>
      </div>
    </div>
  );
}
