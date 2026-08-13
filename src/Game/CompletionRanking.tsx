import { useCallback, useEffect, useRef, useState } from 'react';
import { getTelegramId, isInAigramNow, openAigramProfile } from '../shared/runtime/bridge';
import { useGameEvent } from '../shared/runtime/useGameEvent';
import { useGameScore, type LeaderboardEntry } from '../shared/leaderboard/useGameScore';
import './CompletionRanking.less';

const SCORE_CEILING_CENTISECONDS = 10_000_000;
const COMPLETION_COUPON_SCORE_FLOOR = 10;
const ALTERU_APP_URL = 'https://alteru.app/';

export function durationToRankScore(durationMs: number): number {
  const centiseconds = Math.max(1, Math.round(durationMs / 10));
  return Math.max(COMPLETION_COUPON_SCORE_FLOOR, SCORE_CEILING_CENTISECONDS - centiseconds);
}

export function rankScoreToDuration(score: number): number {
  return Math.max(0, (SCORE_CEILING_CENTISECONDS - score) * 10);
}

export function formatCompletionTime(durationMs: number): string {
  const tenths = Math.max(0, Math.round(durationMs / 100));
  const minutes = Math.floor(tenths / 600);
  const seconds = Math.floor((tenths % 600) / 10);
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${tenths % 10}`;
}

interface RankingCopy {
  title: string;
  leaders: string;
  me: string;
  empty: string;
  loading: string;
  openInAlterU: string;
  getAlterU: string;
  close: string;
}

interface Config {
  gameName: string;
  posterUrl: string;
  copy: RankingCopy;
}

export interface CompletionRankingState {
  completionMs: number | null;
  champion: LeaderboardEntry | null;
  rows: LeaderboardEntry[];
  loading: boolean;
  isOpen: boolean;
  copy: RankingCopy;
  gameName: string;
  startRun: () => void;
  finishRun: () => number | null;
  resetRun: () => void;
  openLeaderboard: () => void;
  closeLeaderboard: () => void;
  fetchLeaderboard: () => Promise<void>;
}

export function useCompletionRanking({ gameName, posterUrl, copy }: Config): CompletionRankingState {
  const { submitScore, fetchLeaderboard: fetchRankRows } = useGameScore();
  const { trigger } = useGameEvent();
  const [completionMs, setCompletionMs] = useState<number | null>(null);
  const [champion, setChampion] = useState<LeaderboardEntry | null>(null);
  const [rows, setRows] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const runStartedAtRef = useRef<number | null>(null);
  const runIdRef = useRef(0);
  const rowsRef = useRef<LeaderboardEntry[]>([]);
  const preRunBestRef = useRef(0);

  const applyRows = useCallback((nextRows: LeaderboardEntry[]) => {
    rowsRef.current = nextRows;
    setRows(nextRows);
    setChampion(nextRows[0] ?? null);
  }, []);

  const fetchLeaderboard = useCallback(async () => {
    setLoading(true);
    try {
      applyRows(await fetchRankRows());
    } finally {
      setLoading(false);
    }
  }, [applyRows, fetchRankRows]);

  useEffect(() => {
    if (isInAigramNow()) fetchLeaderboard().catch(() => {});
  }, [fetchLeaderboard]);

  const startRun = useCallback(() => {
    if (runStartedAtRef.current != null) return;
    runIdRef.current += 1;
    const runId = runIdRef.current;
    runStartedAtRef.current = performance.now();
    setCompletionMs(null);
    const myId = getTelegramId();
    const me = myId ? rowsRef.current.find((row) => String(row.user_id) === String(myId)) : null;
    preRunBestRef.current = me?.score ?? 0;
    if (isInAigramNow()) {
      fetchRankRows().then((fresh) => {
        applyRows(fresh);
        if (runIdRef.current !== runId || runStartedAtRef.current == null) return;
        const liveId = getTelegramId();
        const liveMe = liveId ? fresh.find((row) => String(row.user_id) === String(liveId)) : null;
        preRunBestRef.current = liveMe?.score ?? 0;
      }).catch(() => {});
    }
  }, [applyRows, fetchRankRows]);

  const finishRun = useCallback(() => {
    const startedAt = runStartedAtRef.current;
    if (startedAt == null) return null;
    runStartedAtRef.current = null;
    const elapsedMs = Math.max(10, Math.round(performance.now() - startedAt));
    const score = durationToRankScore(elapsedMs);
    setCompletionMs(elapsedMs);

    submitScore(score).then(async () => {
      if (!isInAigramNow() || score <= preRunBestRef.current) return;
      try {
        const fresh = await fetchRankRows();
        applyRows(fresh);
        const myId = getTelegramId();
        if (!myId) return;
        const beaten = fresh
          .filter((row) => String(row.user_id) !== String(myId))
          .filter((row) => row.score < score && row.score > preRunBestRef.current)
          .sort((a, b) => b.score - a.score)[0];
        if (!beaten) return;
        trigger('score_beat', {
          actions: [{
            type: 'notify',
            target_user_id: String(beaten.user_id),
            image: {
              ref_url: posterUrl,
              prompt: `Colorful UMe Family completion scene from ${gameName}.`,
            },
            message: {
              template: `{sender_name} beat your completion time with ${formatCompletionTime(elapsedMs)} on ${gameName}.`,
              variables: ['sender_name'],
            },
          }],
        });
      } catch {
        // Ranking refresh and social notification never block the result screen.
      }
    }).catch(() => {});
    return elapsedMs;
  }, [applyRows, fetchRankRows, gameName, posterUrl, submitScore, trigger]);

  const resetRun = useCallback(() => {
    runIdRef.current += 1;
    runStartedAtRef.current = null;
    setCompletionMs(null);
  }, []);

  const openLeaderboard = useCallback(() => {
    setIsOpen(true);
    if (isInAigramNow()) fetchLeaderboard().catch(() => {});
  }, [fetchLeaderboard]);

  return {
    completionMs,
    champion,
    rows,
    loading,
    isOpen,
    copy,
    gameName,
    startRun,
    finishRun,
    resetRun,
    openLeaderboard,
    closeLeaderboard: () => setIsOpen(false),
    fetchLeaderboard,
  };
}

function TrophyIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4h8v3c0 4-1.8 6-4 6S8 11 8 7V4Z" /><path d="M8 6H5v1c0 2.2 1.2 3.5 3.6 3.8M16 6h3v1c0 2.2-1.2 3.5-3.6 3.8M12 13v4m-4 3h8m-6-3h4" /></svg>;
}

function CloseIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg>;
}

function Avatar({ entry }: { entry: LeaderboardEntry }) {
  return <span className="completion-rank__avatar" aria-hidden="true">
    {entry.avatar_url ? <img src={entry.avatar_url} alt="" draggable={false} /> : entry.name.charAt(0).toUpperCase()}
  </span>;
}

export function CompletionChampion({ ranking }: { ranking: CompletionRankingState }) {
  return <button type="button" className="completion-champion" onPointerDown={ranking.openLeaderboard} aria-label={ranking.copy.leaders}>
    <TrophyIcon />
    {ranking.champion ? <>
      <Avatar entry={ranking.champion} />
      <span>{formatCompletionTime(rankScoreToDuration(ranking.champion.score))}</span>
    </> : <span>{ranking.copy.leaders}</span>}
  </button>;
}

export function CompletionLeaderboard({ ranking }: { ranking: CompletionRankingState }) {
  if (!ranking.isOpen) return null;
  const inAlterU = isInAigramNow();
  return <div className="completion-rank" onPointerDown={(event) => { if (event.target === event.currentTarget) ranking.closeLeaderboard(); }}>
    <section className="completion-rank__panel" role="dialog" aria-modal="true" aria-label={ranking.copy.title}>
      <header>
        <TrophyIcon />
        <div><strong>{ranking.copy.title}</strong><span>{ranking.gameName}</span></div>
        <button type="button" onPointerDown={ranking.closeLeaderboard} aria-label={ranking.copy.close}><CloseIcon /></button>
      </header>
      {!inAlterU ? <div className="completion-rank__state">
        <p>{ranking.copy.openInAlterU}</p>
        <a href={ALTERU_APP_URL} target="_blank" rel="noopener noreferrer">{ranking.copy.getAlterU}</a>
      </div> : <div className="completion-rank__list">
        {ranking.loading && <div className="completion-rank__state" role="status"><i className="completion-rank__spinner" /><p>{ranking.copy.loading}</p></div>}
        {!ranking.loading && ranking.rows.length === 0 && <div className="completion-rank__state"><p>{ranking.copy.empty}</p></div>}
        {!ranking.loading && ranking.rows.map((entry, index) => {
          const content = <>
            <b>{index + 1}</b><Avatar entry={entry} /><span>{entry.name}{entry.isMe && <small>{ranking.copy.me}</small>}</span>
            <strong>{formatCompletionTime(rankScoreToDuration(entry.score))}</strong>
          </>;
          return entry.isMe ? <div className="completion-rank__row is-me" key={entry.user_id}>{content}</div> :
            <button type="button" className="completion-rank__row" key={entry.user_id} onClick={() => openAigramProfile(entry.user_id)}>{content}</button>;
        })}
      </div>}
    </section>
  </div>;
}
