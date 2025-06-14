import React from 'react'
import ReactDOM from 'react-dom/client'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stats } from '@react-three/drei'
import './styles.css'
import { CrystalField } from './components/CrystalField'
import { SpinningShadowBall } from './components/SpinningShadowBall'
import { ParticleField } from './components/ParticleField'
import { ConsciousnessControls } from './components/ConsciousnessControls'
import { useCrystalEngine } from './hooks/useCrystalEngine'

// Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Crystal visualization error:', error, errorInfo)
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ color: 'white', padding: '20px' }}>
          <h2>Something went wrong with the crystal visualization</h2>
          <pre>{this.state.error?.toString()}</pre>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const [viewMode, setViewMode] = React.useState('crystal') // 'crystal', 'shadow', 'combined'
  const [thoughtInput, setThoughtInput] = React.useState('understand consciousness')
  
  // Use real crystal engine connection
  const {
    isConnected,
    crystalData,
    coherence,
    phase,
    isProcessing,
    crystallizeThought
  } = useCrystalEngine()
  
  // Convert crystalData for visualization
  const thoughtData = crystalData

  // Handle keyboard shortcut for crystallization
  React.useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && !isProcessing) {
        crystallizeThought(thoughtInput)
      }
    }
    
    window.addEventListener('keypress', handleKeyPress)
    return () => window.removeEventListener('keypress', handleKeyPress)
  }, [thoughtInput, isProcessing, crystallizeThought])

  return (
    <div className="app">
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 5, 10], fov: 60 }}>
          <ambientLight intensity={0.05} />
          <pointLight position={[10, 10, 10]} intensity={0.3} />
          <pointLight position={[-10, -10, -10]} intensity={0.2} color="#4400ff" />
          
          {/* Particle field for atmosphere */}
          <ParticleField coherence={coherence} phase={phase} />
          
          {/* Main visualization based on view mode */}
          {thoughtData && viewMode === 'crystal' && (
            <CrystalField 
              thoughtData={thoughtData}
              coherence={coherence}
              phase={phase}
            />
          )}
          
          {thoughtData && viewMode === 'shadow' && (
            <SpinningShadowBall
              thoughtData={thoughtData}
              coherence={coherence}
              phase={phase}
            />
          )}
          
          {thoughtData && viewMode === 'combined' && (
            <>
              <group position={[0, -2, 0]}>
                <CrystalField 
                  thoughtData={thoughtData}
                  coherence={coherence}
                  phase={phase}
                />
              </group>
              <group position={[0, 3, 0]} scale={[0.8, 0.8, 0.8]}>
                <SpinningShadowBall
                  thoughtData={thoughtData}
                  coherence={coherence}
                  phase={phase}
                />
              </group>
            </>
          )}
          
          <OrbitControls 
            enableDamping
            dampingFactor={0.05}
            rotateSpeed={0.5}
            autoRotate={coherence > 0.9}
            autoRotateSpeed={0.5}
          />
          <Stats />
          
          <fog attach="fog" args={['#000', 5, 50]} />
          
          {/* Post-processing effects removed temporarily */}
        </Canvas>
      </div>
      
      <ConsciousnessControls 
        coherence={coherence}
        phase={phase}
        isConnected={isConnected}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        thoughtInput={thoughtInput}
        onThoughtInputChange={setThoughtInput}
        onCrystallize={() => crystallizeThought(thoughtInput)}
        isProcessing={isProcessing}
      />
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
)