'use client';

import React from 'react';

type TraceState = 'active' | 'approve' | 'reject' | 'retry' | 'default';

interface TraceEntry {
  id: string;
  agent: string;
  timestamp: string;
  content: string;
  state: TraceState;
}

const mockTraceStream: TraceEntry[] = [
  {
    id: '1',
    agent: 'SYSTEM',
    timestamp: '19:30:05',
    content: 'INCIDENT INJECTED: Koramangala waterlogging critical at Koramangala Water Tank Junction (J-KRM-01).',
    state: 'active'
  },
  {
    id: '2',
    agent: 'COORDINATOR',
    timestamp: '19:30:06',
    content: 'Delegating to RerouteAgent and SignalTimingAgent...',
    state: 'default'
  },
  {
    id: '3',
    agent: 'REROUTE_AGENT',
    timestamp: '19:30:12',
    content: 'PROPOSED: Divert Route 201R and 340 away from Koramangala. Alternative route via Silk Board Junction (J-SB-01) to bypass waterlogged area.',
    state: 'default'
  },
  {
    id: '4',
    agent: 'SIGNAL_TIMING_AGENT',
    timestamp: '19:30:14',
    content: 'PROPOSED: J-KRM-01 adjustments:\n- ST Bed Road: Green 10s (was 20s)\n- 80ft Road North/South: Green 35s (was 30s)',
    state: 'default'
  },
  {
    id: '5',
    agent: 'COORDINATOR',
    timestamp: '19:30:18',
    content: 'Synthesized preliminary plan. Awaiting verification.',
    state: 'default'
  },
  {
    id: '6',
    agent: 'VERIFIER',
    timestamp: '19:30:25',
    content: 'DECISION: REJECT\nREASON: The proposed plan suggests rerouting traffic via Silk Board, which is currently experiencing critical congestion. This would exacerbate existing traffic problems at Silk Board.\nCONSTRAINT: Avoid rerouting traffic through Silk Board Junction when its congestion level is critical.',
    state: 'reject'
  },
  {
    id: '7',
    agent: 'COORDINATOR',
    timestamp: '19:30:26',
    content: 'Plan rejected by verifier. Re-triggering generation with new constraints.',
    state: 'retry'
  },
  {
    id: '8',
    agent: 'REROUTE_AGENT',
    timestamp: '19:30:35',
    content: 'REVISED: Suspend Route 201R/340 through Koramangala. Direct commuters to board 500D from Indiranagar. Explicitly bypass Silk Board (J-SB-01).',
    state: 'default'
  },
  {
    id: '9',
    agent: 'VERIFIER',
    timestamp: '19:30:42',
    content: 'DECISION: APPROVE\nREASON: Plan successfully addresses waterlogging by reducing J-KRM-01 inflow. Rerouting avoids critically congested Silk Board Junction.',
    state: 'approve'
  }
];

export default function AgentTracePanel() {
  return (
    <div className="trace-panel">
      <div className="trace-header">
        Live Agent Trace
      </div>
      <div className="trace-stream mono">
        {mockTraceStream.map((entry) => (
          <div key={entry.id} className={`trace-entry state-${entry.state}`}>
            <div className="trace-entry-header">
              <span className="trace-agent-name">{entry.agent}</span>
              <span className="trace-timestamp">{entry.timestamp}</span>
            </div>
            <div className="trace-content">
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
      </div>
    </div>
  );
}
