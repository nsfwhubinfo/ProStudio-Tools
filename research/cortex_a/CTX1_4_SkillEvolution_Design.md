# Agent Skill Evolution & Internal Upwork Catalog
## Milestone CTX.1.4

### Executive Summary

This milestone implements the agent skill evolution system and internal marketplace ("Internal Upwork") for CORTEX-A. Agents progress from undergraduate to executive levels based on performance, while the marketplace enables dynamic agent discovery and instantiation based on specialized expertise.

---

## Table of Contents
1. [Skill Evolution Architecture](#skill-evolution-architecture)
2. [Temporal Holographic Markdown](#temporal-holographic-markdown)
3. [Internal Upwork Marketplace](#internal-upwork-marketplace)
4. [Webhook Dispatcher System](#webhook-dispatcher-system)
5. [Implementation Specifications](#implementation-specifications)

---

## Skill Evolution Architecture

### Agent Skill Levels

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class SkillLevel(Enum):
    UNDERGRADUATE = "undergraduate"  # New agent, learning basics
    GRADUATE = "graduate"           # Competent, reliable performance
    PROFESSIONAL = "professional"   # Expert in domain, consistent excellence
    EXECUTIVE = "executive"         # Strategic thinking, cross-domain synthesis

@dataclass
class SkillProfile:
    """Complete skill profile for an agent"""
    current_level: SkillLevel
    experience_points: int
    success_rate: float
    specializations: List[str]
    knowledge_artifacts: Dict[str, float]  # artifact_id -> mastery_level
    evolution_history: List[Dict]
    mentorship_given: int
    mentorship_received: int
```

### Evolution Mechanics

```python
class SkillEvolutionEngine:
    """Manages agent skill progression and knowledge accumulation"""
    
    # Evolution thresholds
    EVOLUTION_CRITERIA = {
        SkillLevel.UNDERGRADUATE: {
            'min_tasks': 10,
            'min_success_rate': 0.8,
            'min_experience': 100
        },
        SkillLevel.GRADUATE: {
            'min_tasks': 50,
            'min_success_rate': 0.9,
            'min_experience': 1000,
            'required_specializations': 2
        },
        SkillLevel.PROFESSIONAL: {
            'min_tasks': 200,
            'min_success_rate': 0.95,
            'min_experience': 5000,
            'required_specializations': 3,
            'mentorship_given': 5
        }
    }
    
    def evaluate_evolution(self, agent: ComputeAgent) -> Optional[SkillLevel]:
        """Determine if agent qualifies for promotion"""
        current_level = agent.skill_profile.current_level
        next_level = self._get_next_level(current_level)
        
        if not next_level:
            return None
            
        criteria = self.EVOLUTION_CRITERIA[current_level]
        
        # Check all criteria
        if (agent.tasks_completed >= criteria['min_tasks'] and
            agent.skill_profile.success_rate >= criteria['min_success_rate'] and
            agent.skill_profile.experience_points >= criteria['min_experience']):
            
            # Additional checks for higher levels
            if 'required_specializations' in criteria:
                if len(agent.skill_profile.specializations) < criteria['required_specializations']:
                    return None
                    
            if 'mentorship_given' in criteria:
                if agent.skill_profile.mentorship_given < criteria['mentorship_given']:
                    return None
                    
            return next_level
            
        return None
```

### Knowledge Accumulation

```python
class KnowledgeAccumulator:
    """Tracks and manages agent knowledge growth"""
    
    def __init__(self, datastore: CORTEXDataStore):
        self.datastore = datastore
        self.knowledge_graph = {}
        
    async def record_learning(self, 
                            agent_id: str,
                            task: CortexTask,
                            outcome: TaskOutcome):
        """Record what an agent learned from a task"""
        
        # Extract knowledge artifacts
        artifacts = self._extract_knowledge_artifacts(task, outcome)
        
        # Store in DataStore
        knowledge_data = {
            'agent_id': agent_id,
            'task_id': task.id,
            'timestamp': time.time(),
            'artifacts': artifacts,
            'quality_score': outcome.quality_score,
            'patterns_discovered': outcome.patterns
        }
        
        await self.datastore.ingest({
            'knowledge_artifacts': [knowledge_data]
        })
        
        # Update agent's knowledge profile
        await self._update_agent_knowledge(agent_id, artifacts)
    
    def _extract_knowledge_artifacts(self, task, outcome):
        """Extract reusable knowledge from task execution"""
        artifacts = []
        
        # Pattern recognition artifacts
        if outcome.patterns:
            artifacts.extend([
                {
                    'type': 'pattern',
                    'content': pattern,
                    'confidence': confidence
                }
                for pattern, confidence in outcome.patterns.items()
            ])
        
        # Optimization discoveries
        if outcome.optimizations:
            artifacts.extend([
                {
                    'type': 'optimization',
                    'technique': opt['technique'],
                    'improvement': opt['improvement']
                }
                for opt in outcome.optimizations
            ])
        
        return artifacts
```

---

## Temporal Holographic Markdown

### Knowledge Representation Format

```markdown
# Agent Knowledge Template: Fractal Analysis Expert
## Metadata
- **Expertise**: fractal_analysis
- **Level**: professional
- **Last Updated**: {{timestamp}}
- **Version**: 2.3.1

## Core Knowledge
### Fractal Dimension Calculation
```python
def calculate_fractal_dimension(data_points):
    # Box-counting method
    scales = np.logspace(-3, 0, 20)
    counts = []
    
    for scale in scales:
        # Count boxes at this scale
        count = count_boxes(data_points, scale)
        counts.append(count)
    
    # Linear regression in log-log space
    coeffs = np.polyfit(np.log(scales), np.log(counts), 1)
    return -coeffs[0]  # Negative slope is fractal dimension
```

### Pattern Recognition Strategies
1. **Multi-scale Analysis**
   - Examine patterns at 5+ scales
   - Look for scale invariance
   - Identity breaking points

2. **Lacunarity Detection**
   - Measure "gappiness" in patterns
   - High lacunarity → heterogeneous
   - Low lacunarity → homogeneous

## Learned Optimizations
### From Task #4521 (CSS-Fractal Correlation)
- **Discovery**: CSS coherence inversely correlates with fractal dimension
- **Application**: Pre-filter by coherence for 3x speedup
- **Confidence**: 0.94

### From Task #5102 (Large-scale Analysis)
- **Discovery**: Hierarchical decomposition effective for D > 1.8
- **Application**: Switch algorithms based on estimated dimension
- **Confidence**: 0.87

## Cross-Domain Insights
### CSS Field Interactions
- Fractal dimension peaks correlate with CSS instability
- Use CSS distance as heuristic for fractal complexity

### FMO Pattern Correlations
- Entity relationships follow power-law distribution
- Fractal signature predicts relationship density

## Evolution History
- 2024-01-15: Promoted to Professional
- 2024-01-20: Discovered CSS-fractal correlation
- 2024-01-25: Mentored 3 undergraduate agents
```

### Knowledge Template Engine

```python
class TemporalHolographicMarkdown:
    """Manages agent knowledge templates with temporal versioning"""
    
    def __init__(self, datastore: CORTEXDataStore):
        self.datastore = datastore
        self.template_cache = {}
        self.jinja_env = Environment(loader=FileSystemLoader('templates'))
        
    async def load_knowledge_template(self, 
                                    agent: ComputeAgent) -> Dict:
        """Load and instantiate knowledge template for agent"""
        
        # Get base template for expertise
        base_template = await self._get_base_template(agent.expertise)
        
        # Get agent's personal knowledge
        personal_knowledge = await self._get_agent_knowledge(agent.id)
        
        # Merge and render
        context = {
            'base_knowledge': base_template,
            'personal_knowledge': personal_knowledge,
            'timestamp': datetime.now().isoformat(),
            'agent': agent
        }
        
        rendered = self.jinja_env.from_string(base_template).render(**context)
        
        # Parse into structured format
        return self._parse_knowledge_markdown(rendered)
    
    async def save_knowledge_snapshot(self, 
                                    agent: ComputeAgent,
                                    reason: str):
        """Save temporal snapshot of agent's knowledge"""
        
        snapshot = {
            'agent_id': agent.id,
            'timestamp': time.time(),
            'skill_level': agent.skill_profile.current_level.value,
            'knowledge_template': await self.render_current_knowledge(agent),
            'reason': reason,
            'metrics': {
                'tasks_completed': agent.tasks_completed,
                'success_rate': agent.skill_profile.success_rate,
                'specializations': agent.skill_profile.specializations
            }
        }
        
        await self.datastore.ingest({
            'knowledge_snapshots': [snapshot]
        })
```

---

## Internal Upwork Marketplace

### Marketplace Architecture

```python
class AgentMarketplace:
    """Internal Upwork for CORTEX-A agents"""
    
    def __init__(self, 
                 registry: AgentRegistry,
                 datastore: CORTEXDataStore):
        self.registry = registry
        self.datastore = datastore
        self.listings = {}
        self.reputation_system = ReputationSystem()
        
    async def post_requirement(self, 
                             requirement: AgentRequirement) -> str:
        """Post a requirement for specialized agent expertise"""
        
        listing_id = f"req_{uuid.uuid4().hex[:8]}"
        
        listing = {
            'id': listing_id,
            'posted_at': time.time(),
            'requirement': requirement,
            'status': 'open',
            'bids': [],
            'selected_agent': None
        }
        
        self.listings[listing_id] = listing
        
        # Notify eligible agents
        await self._notify_eligible_agents(requirement)
        
        return listing_id
    
    async def submit_bid(self, 
                        listing_id: str,
                        agent_id: str,
                        bid: AgentBid):
        """Agent submits bid for a requirement"""
        
        listing = self.listings.get(listing_id)
        if not listing or listing['status'] != 'open':
            raise ValueError("Invalid or closed listing")
        
        # Enhance bid with reputation
        bid.reputation_score = await self.reputation_system.get_score(agent_id)
        bid.past_performance = await self._get_agent_track_record(
            agent_id, 
            listing['requirement'].expertise_needed
        )
        
        listing['bids'].append({
            'agent_id': agent_id,
            'bid': bid,
            'timestamp': time.time()
        })
    
    async def select_agent(self, 
                          listing_id: str,
                          selection_criteria: SelectionCriteria) -> str:
        """Select best agent based on criteria"""
        
        listing = self.listings[listing_id]
        bids = listing['bids']
        
        if not bids:
            # No bids - instantiate new agent
            return await self._instantiate_new_agent(listing['requirement'])
        
        # Score all bids
        scored_bids = []
        for bid_entry in bids:
            score = self._score_bid(
                bid_entry['bid'],
                selection_criteria,
                listing['requirement']
            )
            scored_bids.append((score, bid_entry['agent_id']))
        
        # Select highest scorer
        scored_bids.sort(reverse=True)
        selected_agent_id = scored_bids[0][1]
        
        listing['selected_agent'] = selected_agent_id
        listing['status'] = 'assigned'
        
        return selected_agent_id
```

### Agent Capability Catalog

```python
@dataclass
class AgentCapability:
    """Defines a specific capability an agent offers"""
    name: str
    description: str
    expertise_type: ExpertiseType
    required_skill_level: SkillLevel
    performance_metrics: Dict[str, float]
    example_queries: List[str]
    prerequisites: List[str]

class CapabilityCatalog:
    """Searchable catalog of agent capabilities"""
    
    def __init__(self, datastore: CORTEXDataStore):
        self.datastore = datastore
        self.capability_index = {}
        self._build_capability_index()
    
    async def register_capability(self, 
                                agent_id: str,
                                capability: AgentCapability):
        """Register new capability in catalog"""
        
        # Validate agent meets requirements
        agent = await self._get_agent(agent_id)
        if agent.skill_profile.current_level.value < capability.required_skill_level.value:
            raise ValueError("Agent skill level insufficient")
        
        # Store in catalog
        catalog_entry = {
            'agent_id': agent_id,
            'capability': capability,
            'registered_at': time.time(),
            'availability': 'available'
        }
        
        await self.datastore.ingest({
            'capability_catalog': [catalog_entry]
        })
        
        # Update index
        self._index_capability(agent_id, capability)
    
    async def search_capabilities(self, 
                                query: str,
                                filters: Dict = None) -> List[Dict]:
        """Search for agents with specific capabilities"""
        
        # Parse query for intent
        parsed_query = self._parse_capability_query(query)
        
        # Search index
        matches = []
        for capability_key, agents in self.capability_index.items():
            if self._matches_query(capability_key, parsed_query):
                for agent_id in agents:
                    agent_info = await self._get_agent_listing(agent_id)
                    matches.append(agent_info)
        
        # Apply filters
        if filters:
            matches = self._apply_filters(matches, filters)
        
        # Rank by relevance and reputation
        return self._rank_results(matches, parsed_query)
```

### Dynamic Agent Instantiation

```python
class DynamicAgentFactory:
    """Creates agents on-demand based on requirements"""
    
    def __init__(self, 
                 marketplace: AgentMarketplace,
                 knowledge_engine: TemporalHolographicMarkdown):
        self.marketplace = marketplace
        self.knowledge_engine = knowledge_engine
        self.template_library = {}
        
    async def create_agent_for_requirement(self, 
                                         requirement: AgentRequirement) -> ComputeAgent:
        """Create new agent tailored to specific requirement"""
        
        # Find best template
        template = await self._find_best_template(requirement)
        
        if not template:
            # Create from scratch
            template = await self._synthesize_template(requirement)
        
        # Instantiate agent
        agent = ComputeAgent(
            expertise=requirement.expertise_needed,
            skill_level=SkillLevel.UNDERGRADUATE
        )
        
        # Load knowledge
        knowledge = await self.knowledge_engine.instantiate_template(
            template,
            requirement.context
        )
        agent.load_knowledge(knowledge)
        
        # Set initial capabilities
        for capability in requirement.required_capabilities:
            agent.add_capability(capability)
        
        # Register in marketplace
        await self.marketplace.registry.register_agent(agent)
        
        return agent
    
    async def _synthesize_template(self, requirement: AgentRequirement) -> Dict:
        """Synthesize new knowledge template from existing agents"""
        
        # Find similar successful agents
        similar_agents = await self._find_similar_agents(requirement)
        
        if not similar_agents:
            return self._create_minimal_template(requirement)
        
        # Extract common patterns
        knowledge_patterns = []
        for agent in similar_agents:
            patterns = await self.knowledge_engine.extract_patterns(agent)
            knowledge_patterns.extend(patterns)
        
        # Synthesize new template
        synthesized = {
            'expertise': requirement.expertise_needed,
            'base_knowledge': self._merge_patterns(knowledge_patterns),
            'required_skills': requirement.required_capabilities,
            'optimization_hints': self._extract_optimizations(similar_agents)
        }
        
        return synthesized
```

---

## Webhook Dispatcher System

### FMO Pattern Webhooks

```python
class WebhookDispatcher:
    """Dispatches agents based on FMO pattern detection"""
    
    def __init__(self, 
                 planner: CORTEXPlanner,
                 marketplace: AgentMarketplace):
        self.planner = planner
        self.marketplace = marketplace
        self.webhooks = {}
        self.pattern_subscriptions = defaultdict(list)
        
    def register_webhook(self, 
                        pattern: FMOPattern,
                        action: WebhookAction):
        """Register webhook for FMO pattern"""
        
        webhook_id = f"webhook_{uuid.uuid4().hex[:8]}"
        
        webhook = {
            'id': webhook_id,
            'pattern': pattern,
            'action': action,
            'created_at': time.time(),
            'triggers': 0
        }
        
        self.webhooks[webhook_id] = webhook
        self.pattern_subscriptions[pattern.signature].append(webhook_id)
        
        return webhook_id
    
    async def on_fmo_event(self, event: FMOEvent):
        """Handle FMO pattern detection"""
        
        # Check all matching patterns
        for pattern_sig in event.matching_patterns:
            webhook_ids = self.pattern_subscriptions.get(pattern_sig, [])
            
            for webhook_id in webhook_ids:
                webhook = self.webhooks[webhook_id]
                
                # Check if pattern fully matches
                if self._pattern_matches(event, webhook['pattern']):
                    await self._trigger_webhook(webhook, event)
    
    async def _trigger_webhook(self, webhook: Dict, event: FMOEvent):
        """Execute webhook action"""
        
        action = webhook['action']
        
        if action.type == 'spawn_agent':
            # Create agent requirement from pattern
            requirement = self._create_requirement_from_pattern(
                event.pattern,
                action.agent_specs
            )
            
            # Post to marketplace
            listing_id = await self.marketplace.post_requirement(requirement)
            
            # Auto-select if specified
            if action.auto_select:
                agent_id = await self.marketplace.select_agent(
                    listing_id,
                    action.selection_criteria
                )
                
                # Submit task to CORTEX-A
                task = self._create_task_from_event(event, action.task_template)
                await self.planner.submit_task(task, preferred_agent=agent_id)
        
        elif action.type == 'broadcast_alert':
            # Notify all agents with matching expertise
            await self._broadcast_to_agents(
                action.expertise_filter,
                event
            )
        
        webhook['triggers'] += 1
```

### Pattern-Based Agent Activation

```python
class PatternActivationEngine:
    """Activates dormant agents based on pattern detection"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.activation_rules = {}
        
    def define_activation_rule(self,
                             rule_name: str,
                             pattern_condition: Callable,
                             agent_filter: Callable):
        """Define rule for pattern-based activation"""
        
        self.activation_rules[rule_name] = {
            'condition': pattern_condition,
            'filter': agent_filter,
            'activations': 0
        }
    
    async def evaluate_activation(self, event: FMOEvent):
        """Check if any agents should be activated"""
        
        for rule_name, rule in self.activation_rules.items():
            if rule['condition'](event):
                # Find matching dormant agents
                dormant_agents = await self.registry.get_dormant_agents()
                matching = [a for a in dormant_agents if rule['filter'](a)]
                
                # Activate agents
                for agent in matching:
                    await self._activate_agent(agent, event, rule_name)
                
                rule['activations'] += len(matching)
    
    async def _activate_agent(self, agent: ComputeAgent, event: FMOEvent, rule: str):
        """Activate dormant agent with context"""
        
        # Load relevant knowledge
        context_knowledge = await self._load_context_knowledge(event)
        agent.inject_knowledge(context_knowledge)
        
        # Update status
        agent.status = AgentStatus.ACTIVE
        agent.activation_context = {
            'triggered_by': rule,
            'event': event,
            'timestamp': time.time()
        }
        
        # Notify planner
        await self.registry.notify_agent_available(agent)
```

---

## Implementation Specifications

### Core Classes Integration

```python
class SkillEvolutionSystem:
    """Complete skill evolution and marketplace system"""
    
    def __init__(self, 
                 planner: CORTEXPlanner,
                 datastore: CORTEXDataStore,
                 registry: AgentRegistry):
        # Core components
        self.planner = planner
        self.datastore = datastore
        self.registry = registry
        
        # Evolution components
        self.evolution_engine = SkillEvolutionEngine()
        self.knowledge_accumulator = KnowledgeAccumulator(datastore)
        self.knowledge_engine = TemporalHolographicMarkdown(datastore)
        
        # Marketplace components
        self.marketplace = AgentMarketplace(registry, datastore)
        self.capability_catalog = CapabilityCatalog(datastore)
        self.agent_factory = DynamicAgentFactory(self.marketplace, self.knowledge_engine)
        
        # Webhook system
        self.webhook_dispatcher = WebhookDispatcher(planner, self.marketplace)
        self.pattern_activation = PatternActivationEngine(registry)
        
        # Start background tasks
        self._start_evolution_monitor()
        self._start_marketplace_matcher()
        
    async def process_task_completion(self, 
                                    agent: ComputeAgent,
                                    task: CortexTask,
                                    outcome: TaskOutcome):
        """Process completed task for skill evolution"""
        
        # Record learning
        await self.knowledge_accumulator.record_learning(
            agent.id,
            task,
            outcome
        )
        
        # Update agent metrics
        agent.update_performance_metrics(outcome)
        
        # Check for evolution
        new_level = self.evolution_engine.evaluate_evolution(agent)
        if new_level:
            await self._promote_agent(agent, new_level)
        
        # Update marketplace reputation
        await self.marketplace.reputation_system.update_score(
            agent.id,
            task,
            outcome
        )
    
    async def _promote_agent(self, agent: ComputeAgent, new_level: SkillLevel):
        """Promote agent to new skill level"""
        
        # Save knowledge snapshot
        await self.knowledge_engine.save_knowledge_snapshot(
            agent,
            f"Promotion to {new_level.value}"
        )
        
        # Update profile
        agent.skill_profile.current_level = new_level
        agent.skill_profile.evolution_history.append({
            'from_level': agent.skill_profile.current_level.value,
            'to_level': new_level.value,
            'timestamp': time.time(),
            'metrics': {
                'tasks': agent.tasks_completed,
                'success_rate': agent.skill_profile.success_rate
            }
        })
        
        # Unlock new capabilities
        new_capabilities = self._get_capabilities_for_level(new_level)
        for capability in new_capabilities:
            await self.capability_catalog.register_capability(
                agent.id,
                capability
            )
        
        # Notify marketplace
        await self.marketplace.announce_promotion(agent)
```

### Performance Optimizations

```python
class EvolutionOptimizer:
    """Optimizes skill evolution and marketplace operations"""
    
    def __init__(self, system: SkillEvolutionSystem):
        self.system = system
        
    async def batch_evolution_check(self, agent_ids: List[str]):
        """Batch check multiple agents for evolution"""
        
        # Parallel evaluation
        evolution_tasks = [
            self._check_agent_evolution(agent_id)
            for agent_id in agent_ids
        ]
        
        results = await asyncio.gather(*evolution_tasks)
        
        # Batch promotions
        promotions = [(agent_id, new_level) 
                      for agent_id, new_level in results 
                      if new_level is not None]
        
        if promotions:
            await self._batch_promote(promotions)
    
    async def optimize_marketplace_matching(self):
        """Optimize agent-requirement matching"""
        
        # Pre-compute capability embeddings
        await self._compute_capability_embeddings()
        
        # Build KD-tree for fast nearest neighbor search
        self.capability_tree = self._build_capability_tree()
        
        # Cache frequent queries
        self.query_cache = LRUCache(maxsize=1000)
```

---

## Conclusion

The Agent Skill Evolution and Internal Upwork Catalog completes the CORTEX-A system by providing:

1. **Skill Progression**: Agents evolve from undergraduate to executive level
2. **Knowledge Management**: Temporal holographic markdown captures and versions agent knowledge
3. **Internal Marketplace**: Dynamic discovery and instantiation of specialized agents
4. **Pattern-Based Activation**: Webhook system responds to FMO patterns

This creates a self-improving ecosystem where agents continuously learn, share knowledge, and can be summoned on-demand for specialized tasks - truly realizing the vision of an "Internal Upwork for Agents" within Tenxsom AI.

---

*Design Document Version: 1.0*  
*Milestone: CTX.1.4*  
*Status: Ready for Implementation*