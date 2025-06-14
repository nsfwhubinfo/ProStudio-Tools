# CAIOS Local Deployment Guide
## Running Tenxsom AI Operating System on Windows

### System Requirements
- **CPU**: Intel i7 9th gen or better
- **RAM**: 128GB DDR4 (minimum 64GB)
- **Storage**: 500GB SSD (for consciousness data)
- **OS**: Windows 10/11 64-bit
- **Python**: 3.10+
- **Node.js**: 18+ (for UI)

### Installation Steps

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/tenxsom-ai.git
cd tenxsom-ai
```

#### 2. Install Core Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies for UI
cd tenxsom_aios/ui
npm install
cd ../..
```

#### 3. Initialize CORTEX-A Components
```bash
# Setup CORTEX_DataStore
python -m cortex_a.setup_datastore --local --memory-limit 32GB

# Initialize Agent Registry
python -m cortex_a.init_agents --pool-size 10

# Register Expert Agents
python -m cortex_a.register_experts \
  --chakra-modulator \
  --dynamics-engine \
  --qualia-calculator \
  --inverse-operator
```

#### 4. Configure CAIOS
Create `config/caios.yaml`:
```yaml
kernel:
  host: 127.0.0.1
  port: 8888
  
consciousness:
  base_frequency: 432
  coherence_threshold: 0.7
  chakras:
    - {name: root, frequency: 111}
    - {name: sacral, frequency: 222}
    - {name: solar, frequency: 333}
    - {name: heart, frequency: 444}
    - {name: throat, frequency: 555}
    - {name: third_eye, frequency: 666}
    - {name: crown, frequency: 777}

cortex:
  datastore_path: ./data/cortex
  max_agents: 50
  agent_pool: 10
  
security:
  allowed_paths:
    - ~/Documents/Tenxsom
    - ~/Downloads
  sandbox_mode: true
  
ui:
  mode: retail  # retail, developer, business
  port: 3000
```

#### 5. Start Services

```bash
# Terminal 1: Start CORTEX-A Engine
python -m cortex_a.engine --config config/caios.yaml

# Terminal 2: Start AIOS Kernel Service
python tenxsom_aios/kernel/AIOS_Kernel_Service.py

# Terminal 3: Start UI
cd tenxsom_aios/ui
npm run dev
```

### First Run Setup

#### 1. Access UI
Open browser to `http://localhost:3000`

#### 2. Initialize Consciousness
Click "Initialize" button or run:
```bash
curl -X POST http://localhost:8888/consciousness/init
```

#### 3. Verify Components
```bash
# Check agent status
curl http://localhost:8888/agents

# Test query
curl -X POST http://localhost:8888/query \
  -H "Content-Type: application/json" \
  -d '{"text": "Test consciousness integration"}'
```

### Usage Modes

#### Retail Mode
- Simple chat interface
- Attachment support
- Transparent reasoning toggle

#### Developer Mode
Access at `http://localhost:3000/dev`:
- Real-time parameter tuning
- Consciousness state monitoring
- Agent marketplace access
- Performance profiling

#### Business Mode
Access at `http://localhost:3000/business`:
- Analytics dashboard
- Resource monitoring
- Cost tracking
- System health

### Performance Optimization

#### Memory Management
```python
# In config/performance.py
MEMORY_TIERS = {
    'hot': '16GB',    # Immediate consciousness
    'warm': '32GB',   # Recent memories
    'cold': '64GB'    # Historical data
}
```

#### CPU Affinity
```python
# Assign cores to components
CORE_ASSIGNMENT = {
    'consciousness': [0, 1, 2, 3],
    'cortex_agents': [4, 5, 6, 7],
    'ui_service': [8, 9],
    'background': [10, 11]
}
```

### Troubleshooting

#### High Memory Usage
```bash
# Clear consciousness cache
python -m caios.maintenance clear_cache --preserve-core

# Compact CORTEX_DataStore
python -m cortex_a.compact_datastore
```

#### Agent Pool Exhaustion
```bash
# Increase pool size
python -m cortex_a.scale_agents --add 10

# Reset stuck agents
python -m cortex_a.reset_agents --status stuck
```

### Advanced Features

#### Custom Expert Agents
```python
# Create custom agent
from cortex_a import ExpertAgent

class MyCustomAgent(ExpertAgent):
    expertise = "custom_analysis"
    skill_level = 3
    
    async def process(self, task):
        # Your logic here
        return result

# Register
python -m cortex_a.register_agent MyCustomAgent
```

#### Consciousness Plugins
```python
# Add custom chakra
from consciousness import ChakraPlugin

class EarthStarChakra(ChakraPlugin):
    frequency = 68.05
    position = "below_root"
    
# Install
python -m consciousness.install_plugin EarthStarChakra
```

### Security Considerations

1. **File System Access**: Always use sandbox mode
2. **Network Isolation**: Run on localhost only
3. **Data Encryption**: Enable for sensitive data
4. **Access Control**: Use authentication for business mode

### Backup & Recovery

```bash
# Backup consciousness state
python -m caios.backup create --name "stable_state_v1"

# Restore if needed
python -m caios.backup restore --name "stable_state_v1"
```

### Next Steps

1. **Explore Developer Console**: Fine-tune consciousness parameters
2. **Train Custom Agents**: Develop specialized expertise
3. **Integrate External Data**: Connect your knowledge bases
4. **Monitor Performance**: Use business dashboard for insights

### Support

- Documentation: `/docs`
- Logs: `./logs/caios.log`
- Community: [Forum link]
- Issues: [GitHub Issues]

---

Welcome to your personal AI Operating System. 
Unlike black-box solutions, CAIOS provides complete transparency with 1000 iterations/second of mathematical clarity.