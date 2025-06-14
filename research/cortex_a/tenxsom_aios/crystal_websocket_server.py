#!/usr/bin/env python3
"""
Crystal WebSocket Server - Streams real crystallization data to browser
"""

import asyncio
import websockets
import json
import numpy as np
from datetime import datetime
import sys
sys.path.append('/home/golde/prostudio/research/cortex_a/tenxsom_aios')

try:
    from crystallographic_thought_engine import (
        CrystallographicThought,
        CrystallographicConsciousnessEngine
    )
    ENGINE_AVAILABLE = True
except ImportError:
    print("Warning: Crystallographic engine not available, using demo mode")
    ENGINE_AVAILABLE = False


class CrystalWebSocketServer:
    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
        self.engine = CrystallographicConsciousnessEngine() if ENGINE_AVAILABLE else None
        
    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def send_to_all(self, message):
        """Send message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.send(json.dumps({
                'type': 'connection',
                'status': 'connected',
                'engine': ENGINE_AVAILABLE,
                'timestamp': datetime.now().isoformat()
            }))
            
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'crystallize':
                    intention = data.get('intention', 'explore consciousness')
                    await self.crystallize_thought(intention, websocket)
                    
                elif data['type'] == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def crystallize_thought(self, intention, websocket):
        """Stream crystallization process to client"""
        print(f"Crystallizing thought: '{intention}'")
        
        if ENGINE_AVAILABLE and self.engine:
            # Use real engine
            thought = CrystallographicThought(intention)
            
            async for state in thought.crystallize(self.engine.consciousness_state):
                # Convert numpy arrays to lists for JSON
                field_data = state['formation'].pattern
                
                # Downsample if needed (for performance)
                if field_data.shape[0] > 64:
                    step = field_data.shape[0] // 64
                    field_data = field_data[::step, ::step]
                
                update = {
                    'type': 'crystal_update',
                    'iteration': state['iteration'],
                    'coherence': float(state['coherence']),
                    'phase': state['phase'],
                    'field': field_data.flatten().tolist(),
                    'shape': field_data.shape,
                    'timestamp': datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(update))
                
                # Small delay to not overwhelm client
                await asyncio.sleep(0.05)
                
                # Stop if crystallized
                if state['coherence'] > 0.9:
                    break
                    
        else:
            # Demo mode - generate synthetic data
            for i in range(100):
                coherence = i / 100.0
                
                # Generate demo field
                size = 64
                x = np.linspace(-1, 1, size)
                y = np.linspace(-1, 1, size)
                X, Y = np.meshgrid(x, y)
                
                # Create pattern that becomes more coherent
                noise = np.random.randn(size, size) * (1 - coherence)
                pattern = np.sin(X * 10 * coherence) * np.cos(Y * 10 * coherence)
                field = pattern * coherence + noise
                
                # Determine phase
                if coherence < 0.2:
                    phase = 'chaos'
                elif coherence < 0.5:
                    phase = 'emergence'
                elif coherence < 0.8:
                    phase = 'structuring'
                else:
                    phase = 'crystallized'
                
                update = {
                    'type': 'crystal_update',
                    'iteration': i,
                    'coherence': coherence,
                    'phase': phase,
                    'field': field.flatten().tolist(),
                    'shape': [size, size],
                    'timestamp': datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(update))
                await asyncio.sleep(0.1)
        
        # Send completion
        await websocket.send(json.dumps({
            'type': 'crystal_complete',
            'intention': intention,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def start(self):
        """Start the WebSocket server"""
        print(f"Starting Crystal WebSocket Server on port {self.port}...")
        print(f"Engine available: {ENGINE_AVAILABLE}")
        
        async with websockets.serve(self.handle_client, 'localhost', self.port):
            print(f"Server running at ws://localhost:{self.port}")
            print("Waiting for connections...")
            await asyncio.Future()  # Run forever


if __name__ == '__main__':
    server = CrystalWebSocketServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nServer stopped.")