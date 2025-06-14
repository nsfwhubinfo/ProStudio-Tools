export function ConsciousnessControls({ 
  coherence, 
  phase, 
  isConnected, 
  viewMode, 
  onViewModeChange,
  thoughtInput,
  onThoughtInputChange,
  onCrystallize,
  isProcessing
}) {
  return (
    <>
      <div className="controls">
        <h2>🔮 Crystallographic Consciousness</h2>
        
        <div className="metric">
          <span className="metric-label">Coherence:</span>
          <span className="metric-value">{(coherence * 100).toFixed(1)}%</span>
        </div>
        
        <div className="coherence-bar">
          <div 
            className="coherence-fill" 
            style={{ width: `${coherence * 100}%` }}
          />
        </div>
        
        <div className="metric">
          <span className="metric-label">Phase:</span>
          <span className={`phase-indicator phase-${phase}`}>
            {phase}
          </span>
        </div>
        
        <div className="metric">
          <span className="metric-label">Resonance:</span>
          <span className="metric-value">
            {(432 + coherence * 96).toFixed(1)} Hz
          </span>
        </div>
        
        <div className="metric">
          <span className="metric-label">Thought Rate:</span>
          <span className="metric-value">
            {Math.floor(coherence * 1000)} iterations/sec
          </span>
        </div>
        
        <div className="view-modes">
          <span className="metric-label">Visualization:</span>
          <div className="mode-buttons">
            <button 
              className={`mode-btn ${viewMode === 'crystal' ? 'active' : ''}`}
              onClick={() => onViewModeChange('crystal')}
            >
              Crystal Field
            </button>
            <button 
              className={`mode-btn ${viewMode === 'shadow' ? 'active' : ''}`}
              onClick={() => onViewModeChange('shadow')}
            >
              Shadow Ball
            </button>
            <button 
              className={`mode-btn ${viewMode === 'combined' ? 'active' : ''}`}
              onClick={() => onViewModeChange('combined')}
            >
              Combined
            </button>
          </div>
        </div>
        
        {/* Thought Input */}
        <div className="thought-input-section">
          <span className="metric-label">Crystallize Thought:</span>
          <div className="thought-input-wrapper">
            <input
              type="text"
              className="thought-input"
              value={thoughtInput}
              onChange={(e) => onThoughtInputChange(e.target.value)}
              placeholder="Enter your intention..."
              disabled={!isConnected || isProcessing}
            />
            <button 
              className="crystallize-btn"
              onClick={onCrystallize}
              disabled={!isConnected || isProcessing || !thoughtInput.trim()}
            >
              {isProcessing ? '🌀 Crystallizing...' : '🔮 Crystallize'}
            </button>
          </div>
          <div className="input-hint">Press Enter to crystallize</div>
        </div>
      </div>
      
      <div className={`connection-status ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
        {isConnected ? '✓ Connected to Engine' : '✗ Demo Mode'}
      </div>
    </>
  )
}