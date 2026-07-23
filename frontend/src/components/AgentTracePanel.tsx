'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';

type TraceState = 'active' | 'approve' | 'reject' | 'retry' | 'default';

interface TraceEntry {
  id: string;
  agent: string;
  timestamp: string;
  content: string;
  state: TraceState;
}

interface AgentTracePanelProps {
  runCounter: number;
  onApproved?: () => void;
}

export default function AgentTracePanel({ runCounter, onApproved }: AgentTracePanelProps) {
  const [traceStream, setTraceStream] = useState<TraceEntry[]>([]);
  const [runMode, setRunMode] = useState<'LIVE' | 'SIMULATED' | null>(null);
  const streamEndRef = useRef<HTMLDivElement>(null);
  const queueRef = useRef<TraceEntry[]>([]);
  const isProcessingRef = useRef(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clear trace when a new run is triggered
  useEffect(() => {
    if (runCounter > 0) {
      setTraceStream([]);
      setRunMode(null);
      queueRef.current = [];
      isProcessingRef.current = false;
    }
  }, [runCounter]);

  // Auto-scroll to bottom
  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traceStream]);

  const connectWebSocket = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/logs';

    // Avoid duplicate connections
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    const processQueue = async () => {
      if (isProcessingRef.current) return;
      isProcessingRef.current = true;

      while (queueRef.current.length > 0) {
        const entry = queueRef.current.shift()!;

        setTraceStream((prev) => [...prev, entry]);

        // Pacing delays for presentation readability
        if (entry.state === 'reject') {
          await new Promise(resolve => setTimeout(resolve, 4000));
        } else if (entry.state === 'retry') {
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else if (entry.state === 'approve') {
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else {
          await new Promise(resolve => setTimeout(resolve, 800));
        }
      }

      isProcessingRef.current = false;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Mode detection — update badge but don't render as a trace entry
        if (data.action && data.action.includes('Mode')) {
          if (data.data === 'LIVE') {
            setRunMode(prev => prev === 'SIMULATED' ? 'SIMULATED' : 'LIVE');
          } else if (data.data && data.data.includes('SIMULATED')) {
            setRunMode('SIMULATED');
          }
          return; // Don't add mode events to the visible stream
        }

        // Filter out internal error noise from the trace
        if (data.action && data.action.includes('Error') && data.agent === 'System') {
          return;
        }

        let state: TraceState = 'default';
        let content = `${data.action}`;
        if (data.data) {
          content += `\n${data.data}`;
        }

        if (data.action === 'Started Incident Response') {
          state = 'active';
        } else if (data.agent === 'Verifier' && data.action === 'Decision: REJECT') {
          state = 'reject';
        } else if (data.agent === 'Verifier' && data.action === 'Decision: APPROVE') {
          state = 'approve';
          onApproved?.();
        } else if (data.agent === 'System' && data.action === 'Retry Triggered') {
          state = 'retry';
        }

        const newEntry: TraceEntry = {
          id: Math.random().toString(36).substring(7),
          agent: data.agent.toUpperCase(),
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
          content: content,
          state: state
        };

        queueRef.current.push(newEntry);
        processQueue();
      } catch (err) {
        console.error("Failed to parse ws message", err);
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
      // Reconnect after 3 seconds
      reconnectTimerRef.current = setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connectWebSocket]);

  return (
    <div className="trace-panel">
      <div className="trace-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Live Agent Trace</span>
        {runMode && (
          <span
            className="run-mode-badge"
            style={{
              fontSize: '0.7em',
              padding: '2px 8px',
              borderRadius: '4px',
              background: runMode === 'LIVE' ? '#0f4c2e' : '#6b4c12',
              color: runMode === 'LIVE' ? '#4ade80' : '#facc15',
              border: `1px solid ${runMode === 'LIVE' ? '#4ade80' : '#facc15'}`,
            }}
          >
            {runMode === 'LIVE' ? '● LIVE' : '◌ SIMULATED'}
          </span>
        )}
      </div>
      <div className="trace-stream mono">
        {traceStream.length === 0 && (
          <div className="trace-entry state-default">
            <div className="trace-content" style={{ opacity: 0.5, fontStyle: 'italic' }}>
              Select an incident scenario to begin agent trace...
            </div>
          </div>
        )}
        {traceStream.map((entry) => (
          <div key={entry.id} className={`trace-entry state-${entry.state}`}>
            <div className="trace-entry-header">
              <span className="trace-agent-name">{entry.agent}</span>
              <span className="trace-timestamp">{entry.timestamp}</span>
            </div>
            <div className="trace-content" style={{ whiteSpace: 'pre-wrap' }}>
              {entry.content}
            </div>
            {(entry.state === 'reject' || entry.state === 'approve' || entry.state === 'retry' || entry.state === 'active') && (
              <span className={`trace-status-badge badge-${entry.state}`}>
                {entry.state === 'active' ? 'ACTIVE' : entry.state.toUpperCase()}
              </span>
            )}
          </div>
        ))}
        <div ref={streamEndRef} />
      </div>
    </div>
  );
}
