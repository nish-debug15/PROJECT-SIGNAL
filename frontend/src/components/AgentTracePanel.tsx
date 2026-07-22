'use client';

import React, { useEffect, useState, useRef } from 'react';

type TraceState = 'active' | 'approve' | 'reject' | 'retry' | 'default';

interface TraceEntry {
  id: string;
  agent: string;
  timestamp: string;
  content: string;
  state: TraceState;
}

export default function AgentTracePanel() {
  const [traceStream, setTraceStream] = useState<TraceEntry[]>([]);
  const [runMode, setRunMode] = useState<'LIVE' | 'SIMULATED' | null>(null);
  const streamEndRef = useRef<HTMLDivElement>(null);
  const queueRef = useRef<TraceEntry[]>([]);
  const isProcessingRef = useRef(false);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traceStream]);

  useEffect(() => {
    // Determine WebSocket URL based on env (Vercel) or fallback to localhost
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/logs';
    const ws = new WebSocket(wsUrl);

    const processQueue = async () => {
      if (isProcessingRef.current) return;
      isProcessingRef.current = true;

      while (queueRef.current.length > 0) {
        const entry = queueRef.current.shift()!;
        
        setTraceStream((prev) => [...prev, entry]);
        
        // Let it breathe on important events to ensure the UI doesn't rush past the demo beat
        if (entry.state === 'reject') {
          await new Promise(resolve => setTimeout(resolve, 4000));
        } else if (entry.state === 'retry') {
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else if (entry.state === 'approve') {
          await new Promise(resolve => setTimeout(resolve, 2000));
        } else {
          // Standard artificial delay for MockLLM rapid fire events
          await new Promise(resolve => setTimeout(resolve, 800));
        }
      }

      isProcessingRef.current = false;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        let state: TraceState = 'default';
        let content = `${data.action}`;
        if (data.data) {
           content += `\n${data.data}`;
        }

        // Mode detection
        if (data.action.includes('Mode') && data.data === 'LIVE') {
            setRunMode(prev => prev === 'SIMULATED' ? 'SIMULATED' : 'LIVE');
        } else if (data.action.includes('Mode') && data.data.includes('SIMULATED')) {
            setRunMode('SIMULATED');
        }
        
        if (data.action === 'Started Incident Response') {
            state = 'active';
        } else if (data.agent === 'Verifier' && data.action === 'Decision: REJECT') {
            state = 'reject';
        } else if (data.agent === 'Verifier' && data.action === 'Decision: APPROVE') {
            state = 'approve';
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

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="trace-panel">
      <div className="trace-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Live Agent Trace</span>
        {runMode && (
          <span className={`run-mode-badge ${runMode === 'LIVE' ? 'badge-live' : 'badge-simulated'}`} 
                style={{ fontSize: '0.7em', padding: '2px 8px', borderRadius: '4px', background: runMode === 'LIVE' ? '#0f4c2e' : '#6b4c12', color: runMode === 'LIVE' ? '#4ade80' : '#facc15', border: `1px solid ${runMode === 'LIVE' ? '#4ade80' : '#facc15'}` }}>
            MODE: {runMode}
          </span>
        )}
      </div>
      <div className="trace-stream mono">
        {traceStream.length === 0 && (
          <div className="trace-entry state-default">
            <div className="trace-content" style={{ opacity: 0.5, fontStyle: 'italic' }}>
              Waiting for incoming agent trace stream...
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
            {entry.state !== 'default' && entry.state !== 'active' && (
              <span className={`trace-status-badge badge-${entry.state}`}>
                {entry.state.toUpperCase()}
              </span>
            )}
            {entry.state === 'active' && (
              <span className={`trace-status-badge badge-${entry.state}`}>
                ACTIVE
              </span>
            )}
          </div>
        ))}
        <div ref={streamEndRef} />
      </div>
    </div>
  );
}
