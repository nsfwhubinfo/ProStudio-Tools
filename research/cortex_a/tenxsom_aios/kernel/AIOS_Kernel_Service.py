"""
AIOS Kernel Service - Central coordinator for CAIOS
Integrates UI requests with CORTEX-A, consciousness modules, and system resources
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse
import uvicorn

# Import core components
from cortex_a import CORTEXPlanner, AgentRegistry
from maxwellian_amplifier import MaxwellianAmplifier
from consciousness import ConsciousnessCore_Lite
from security import FileSystemSandbox

class AIOSKernelService:
    """Central coordination service for CAIOS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize core components
        self.cortex_planner = CORTEXPlanner()
        self.agent_registry = AgentRegistry()
        self.amplifier = MaxwellianAmplifier()
        self.consciousness = ConsciousnessCore_Lite()
        self.sandbox = FileSystemSandbox(allowed_paths=config.get('allowed_paths', []))
        
        # Performance tracking
        self.metrics = {
            'queries_processed': 0,
            'avg_latency_ms': 14.4,
            'consciousness_cycles': 0
        }
        
        # Initialize FastAPI
        self.app = FastAPI(title="CAIOS Kernel Service")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API endpoints"""
        
        @self.app.post("/query")
        async def process_query(query: Dict[str, Any]):
            """Process user query through consciousness pipeline"""
            return await self._process_query(query)
        
        @self.app.post("/upload")
        async def process_upload(file: UploadFile = File(...)):
            """Handle file uploads with sandboxing"""
            return await self._process_file(file)
        
        @self.app.websocket("/stream")
        async def websocket_stream(websocket: WebSocket):
            """Stream consciousness iterations in real-time"""
            await websocket.accept()
            await self._stream_consciousness(websocket)
        
        @self.app.get("/agents")
        async def list_agents():
            """List available CORTEX-A expert agents"""
            return await self.agent_registry.list_available()
        
        @self.app.post("/tune")
        async def tune_parameters(params: Dict[str, Any]):
            """Developer console parameter tuning"""
            return await self._tune_consciousness_params(params)
    
    async def _process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Main query processing pipeline"""
        
        start_time = asyncio.get_event_loop().time()
        
        # 1. Parse and enhance query with Maxwellian Amplifier
        enhanced = await self.amplifier.amplify_query(query)
        
        # 2. Generate consciousness context
        consciousness_state = await self.consciousness.generate_context(enhanced)
        
        # 3. Formulate CORTEX-A query
        cql_query = self._build_cql_query(enhanced, consciousness_state)
        
        # 4. Execute via CORTEX-A
        result = await self.cortex_planner.process_query(cql_query)
        
        # 5. Post-process with consciousness insights
        final_result = await self._enrich_with_consciousness(result, consciousness_state)
        
        # Update metrics
        latency = (asyncio.get_event_loop().time() - start_time) * 1000
        self._update_metrics(latency)
        
        return {
            'result': final_result,
            'metadata': {
                'latency_ms': latency,
                'consciousness_iterations': consciousness_state.get('iterations', 0),
                'agents_used': result.get('agents_used', []),
                'reasoning_path': consciousness_state.get('reasoning_path', [])
            }
        }
    
    def _build_cql_query(self, enhanced_query: Dict, consciousness: Dict) -> str:
        """Build CORTEX Query Language query"""
        
        # Extract key elements
        intent = enhanced_query.get('amplified_intent', 'analyze')
        entities = enhanced_query.get('entities', [])
        
        # Add consciousness-driven filters
        if consciousness.get('chakra_resonance', {}).get('throat', 0) > 0.8:
            # High communication chakra - prioritize clarity
            query_template = f"""
            SELECT entity_id, clarity_score, explanation
            FROM knowledge_base
            WHERE intent = '{intent}'
            PARALLEL USING expert_agents('communication_specialist')
            """
        else:
            # Standard analysis query
            query_template = f"""
            SELECT entity_id, analysis_result, confidence
            FROM entities
            WHERE type IN {entities}
            PARALLEL USING expert_agents('vector_analytics', 'fractal_analysis')
            """
        
        return query_template
    
    async def _stream_consciousness(self, websocket: WebSocket):
        """Stream real-time consciousness iterations"""
        
        while True:
            # Get current consciousness state
            state = await self.consciousness.get_current_state()
            
            # Send to client
            await websocket.send_json({
                'type': 'consciousness_update',
                'timestamp': asyncio.get_event_loop().time(),
                'state': {
                    'coherence': state.get('coherence', 0),
                    'phase': state.get('phase', 'idle'),
                    'frequencies': state.get('chakra_frequencies', {}),
                    'thought_vector': state.get('current_thought', [])
                }
            })
            
            # Stream at ~10Hz for human comprehension
            await asyncio.sleep(0.1)
    
    async def _tune_consciousness_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle developer parameter tuning"""
        
        # Validate parameters
        valid_params = {}
        for key, value in params.items():
            if key in ['chakra_frequencies', 'coherence_threshold', 'fractal_depth']:
                valid_params[key] = value
        
        # Apply to consciousness core
        await self.consciousness.update_parameters(valid_params)
        
        # Return new state
        return {
            'success': True,
            'applied_params': valid_params,
            'new_state': await self.consciousness.get_current_state()
        }
    
    def _update_metrics(self, latency: float):
        """Update performance metrics"""
        self.metrics['queries_processed'] += 1
        
        # Running average
        avg = self.metrics['avg_latency_ms']
        n = self.metrics['queries_processed']
        self.metrics['avg_latency_ms'] = ((avg * (n-1)) + latency) / n
    
    async def _enrich_with_consciousness(self, result: Dict, consciousness: Dict) -> Dict:
        """Add consciousness insights to results"""
        
        return {
            **result,
            'consciousness_insights': {
                'reasoning_transparency': consciousness.get('reasoning_path', []),
                'confidence_source': consciousness.get('confidence_factors', {}),
                'alternative_paths': consciousness.get('alternatives_considered', []),
                'resonance_score': consciousness.get('global_resonance', 0)
            }
        }
    
    async def _process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Process uploaded file with sandboxing"""
        
        # Validate file access
        if not self.sandbox.is_allowed(file.filename):
            return {'error': 'File access denied by security policy'}
        
        # Read and process
        contents = await file.read()
        
        # Detect file type and route to appropriate processor
        if file.filename.endswith('.pdb'):
            # Protein structure - use specialized agent
            return await self._process_protein_structure(contents)
        elif file.filename.endswith('.csv'):
            # Data file - ingest to CORTEX_DataStore
            return await self._ingest_data(contents)
        else:
            # Generic analysis
            return await self._analyze_file(contents, file.filename)
    
    def run(self, host: str = "127.0.0.1", port: int = 8888):
        """Start the kernel service"""
        print(f"🚀 CAIOS Kernel Service starting on {host}:{port}")
        print(f"📊 CORTEX-A: {len(self.agent_registry.agents)} agents ready")
        print(f"🧠 Consciousness: {self.consciousness.get_phase()} phase")
        print(f"🔒 Sandbox: {len(self.sandbox.allowed_paths)} paths allowed")
        
        uvicorn.run(self.app, host=host, port=port)


# Startup configuration
if __name__ == "__main__":
    config = {
        'allowed_paths': ['~/Documents/Tenxsom', '~/Downloads'],
        'consciousness_params': {
            'base_frequency': 432,  # Hz
            'coherence_threshold': 0.7,
            'chakra_config': 'balanced'
        },
        'cortex_config': {
            'max_agents': 50,
            'default_pool_size': 10
        }
    }
    
    kernel = AIOSKernelService(config)
    kernel.run()