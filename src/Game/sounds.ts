let context: AudioContext | null = null;

function getContext(): AudioContext | null {
  try {
    context ??= new AudioContext();
    if (context.state === 'suspended') void context.resume();
    return context;
  } catch {
    return null;
  }
}

function tone(frequency: number, duration: number, volume: number, type: OscillatorType = 'sine', delay = 0) {
  const ctx = getContext();
  if (!ctx) return;
  const start = ctx.currentTime + delay;
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, start);
  gain.gain.setValueAtTime(0.0001, start);
  gain.gain.exponentialRampToValueAtTime(volume, start + 0.012);
  gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
  oscillator.connect(gain).connect(ctx.destination);
  oscillator.start(start);
  oscillator.stop(start + duration + 0.03);
}

export function playTap(enabled: boolean) {
  if (!enabled) return;
  const ctx = getContext();
  if (!ctx) return;
  const start = ctx.currentTime;
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();
  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(520, start);
  oscillator.frequency.exponentialRampToValueAtTime(410, start + 0.08);
  gain.gain.setValueAtTime(0.0001, start);
  gain.gain.exponentialRampToValueAtTime(0.1, start + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.08);
  oscillator.connect(gain).connect(ctx.destination);
  oscillator.start(start);
  oscillator.stop(start + 0.1);
}

export function playComplete(enabled: boolean) {
  if (!enabled) return;
  tone(620, 0.07, 0.08, 'triangle');
  tone(780, 0.07, 0.08, 'triangle', 0.115);
}

export function playAllReady(enabled: boolean) {
  if (!enabled) return;
  tone(520, 0.11, 0.09, 'triangle');
  tone(660, 0.11, 0.09, 'triangle', 0.075);
  tone(830, 0.14, 0.1, 'triangle', 0.15);
}

export function playFinish(enabled: boolean) {
  if (!enabled) return;
  tone(660, 0.38, 0.08, 'sine');
  tone(830, 0.38, 0.07, 'triangle', 0.035);
  tone(990, 0.38, 0.06, 'sine', 0.07);
}
