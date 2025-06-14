import { useState, useEffect, useCallback } from 'react'

export function useCrystalEngine() {
  const [ws, setWs] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [crystalData, setCrystalData] = useState(null)
  const [coherence, setCoherence] = useState(0)
  const [phase, setPhase] = useState('chaos')
  const [isProcessing, setIsProcessing] = useState(false)
  
  // Connect to WebSocket server
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket('ws://localhost:8765')
        
        websocket.onopen = () => {
          console.log('Connected to Crystal Engine!')
          setIsConnected(true)
          setWs(websocket)
        }
        
        websocket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          
          switch (data.type) {
            case 'connection':
              console.log('Engine status:', data)
              break
              
            case 'crystal_update':
              // Convert flat array back to 2D
              const fieldData = new Float32Array(data.field)
              setCrystalData(fieldData)
              setCoherence(data.coherence)
              setPhase(data.phase)
              break
              
            case 'crystal_complete':
              console.log('Crystallization complete!')
              setIsProcessing(false)
              break
          }
        }
        
        websocket.onerror = (error) => {
          console.error('WebSocket error:', error)
        }
        
        websocket.onclose = () => {
          console.log('Disconnected from Crystal Engine')
          setIsConnected(false)
          setWs(null)
          
          // Attempt reconnection after 3 seconds
          setTimeout(connectWebSocket, 3000)
        }
        
      } catch (error) {
        console.error('Failed to connect:', error)
        setTimeout(connectWebSocket, 3000)
      }
    }
    
    connectWebSocket()
    
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])
  
  // Crystallize a thought
  const crystallizeThought = useCallback((intention) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      setIsProcessing(true)
      ws.send(JSON.stringify({
        type: 'crystallize',
        intention: intention
      }))
    } else {
      console.error('Not connected to Crystal Engine')
    }
  }, [ws])
  
  return {
    isConnected,
    crystalData,
    coherence,
    phase,
    isProcessing,
    crystallizeThought
  }
}