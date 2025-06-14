# Full-Stack AI Implementation Plan for Tenxsom AI

## Executive Summary

This plan outlines the transition from incremental UI development to a holistic, AI-generated full-stack application that serves as the primary interface for the Tenxsom AI fabric. We'll leverage open-source AI code generation tools to create a production-ready application scaffold, then integrate it with the existing Tenxsom AI backend.

## Tool Selection Analysis

Based on the research and Tenxsom AI's requirements, here's our evaluation:

### 1. **full-stack-ai (fsai) - RECOMMENDED** ✅

**Why this is our choice:**
- **Full code ownership**: Generates complete Next.js codebase we can modify
- **Modern stack**: Next.js 14, TypeScript, Tailwind, Prisma
- **API-first**: Easy to replace backend with Tenxsom AI calls
- **Local deployment**: Runs entirely on our infrastructure
- **Comprehensive features**: Auth, payments, CRUD APIs out-of-box

**Command to generate our base:**
```bash
npx fsai gen "Build a multi-modal AI content studio called DevPrompt that allows users to create videos, images, audio, and text content using AI. Include workflow builder, real-time progress tracking, user authentication with GitHub, and API endpoints for all content generation tools. Use Postgres for data storage and include dark/light mode."
```

### 2. **Wasp (with MAGE)** - Alternative

**Pros:**
- Web-based interface (easier for non-CLI users)
- Strong community (10k+ GitHub stars)
- Good for rapid prototyping

**Cons:**
- Less flexibility than fsai
- Opinionated framework might conflict with Tenxsom architecture

### 3. **app.build** - Reference Only

**Use case:**
- Study for AI agent implementation patterns
- Not suitable as primary tool (too Postgres-specific)

## Implementation Plan

### Phase 1: Generate Base Application (Week 1)

#### Step 1.1: Environment Setup
```bash
# Install prerequisites
npm install -g fsai
export OPENAI_API_KEY="your-key-here"

# Create project directory
mkdir ~/prostudio/devprompt-fullstack
cd ~/prostudio/devprompt-fullstack
```

#### Step 1.2: Generate Application
```bash
# Generate comprehensive prompt incorporating Tenxsom AI requirements
cat > app-prompt.txt << 'EOF'
Build a production-ready AI content creation platform called DevPrompt Studio with these features:

Frontend:
- Modern, glassmorphic UI with crystalline design elements
- Drag-and-drop workflow builder for connecting AI tools
- Real-time progress indicators for long-running tasks
- Multi-modal chat interface supporting text, image, video, audio
- Dashboard showing project history and analytics
- WebSocket support for live updates

Backend:
- RESTful API with OpenAPI documentation
- WebSocket server for real-time updates
- Job queue system for async content generation
- File upload/download with S3-compatible storage
- Comprehensive error handling and logging

Authentication:
- GitHub OAuth for developers
- Google OAuth for general users
- API key management for programmatic access

Database:
- User profiles and preferences
- Content generation history
- Workflow templates
- Usage analytics and quotas

API Endpoints:
- POST /api/content/generate - Start content generation
- GET /api/content/{id}/status - Check generation status
- GET /api/content/{id}/result - Download result
- POST /api/workflow/create - Save workflow
- GET /api/workflow/list - List user workflows
- POST /api/workflow/{id}/execute - Run saved workflow

Include TypeScript, Tailwind CSS, shadcn/ui components, and Postgres with Prisma.
EOF

# Generate the application
npx fsai gen "$(cat app-prompt.txt)"
```

#### Step 1.3: Initial Setup & Verification
```bash
# Install dependencies
npm install

# Setup database
npm run db:setup

# Start development server
npm run dev
```

### Phase 2: Integration with Tenxsom AI (Week 2)

#### Step 2.1: Create API Gateway Layer

Create `/api/tenxsom/gateway.ts`:
```typescript
import { AIOS_KERNEL_URL } from '@/config';

export class TenxsomGateway {
  async createContentJob(params: {
    type: 'video' | 'image' | 'audio' | 'text';
    prompt: string;
    options: Record<string, any>;
  }) {
    const response = await fetch(`${AIOS_KERNEL_URL}/api/cortex/job`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow: params.type,
        prompt: params.prompt,
        priority: 1.0, // User-initiated = high priority
        metadata: params.options
      })
    });
    return response.json();
  }

  async getJobStatus(jobId: string) {
    const response = await fetch(`${AIOS_KERNEL_URL}/api/cortex/job/${jobId}`);
    return response.json();
  }
}
```

#### Step 2.2: Replace Mock Implementations

Update content generation endpoints to use Tenxsom AI:
```typescript
// /api/content/generate/route.ts
import { TenxsomGateway } from '@/lib/tenxsom/gateway';

export async function POST(request: Request) {
  const gateway = new TenxsomGateway();
  const { type, prompt, options } = await request.json();
  
  // Create job in Tenxsom AI fabric
  const job = await gateway.createContentJob({ type, prompt, options });
  
  // Store job reference in our DB
  await prisma.contentJob.create({
    data: {
      id: job.id,
      userId: session.user.id,
      type,
      prompt,
      status: 'processing',
      tenxsomJobId: job.tenxsomId
    }
  });
  
  return Response.json({ jobId: job.id });
}
```

#### Step 2.3: WebSocket Integration for Real-time Updates

```typescript
// /lib/websocket/tenxsom-sync.ts
export class TenxsomWebSocketSync {
  constructor(private io: Server) {
    this.connectToTenxsom();
  }

  private connectToTenxsom() {
    const ws = new WebSocket(`${AIOS_KERNEL_WS_URL}/events`);
    
    ws.on('message', (data) => {
      const event = JSON.parse(data);
      
      if (event.type === 'job.progress') {
        // Forward to connected clients
        this.io.to(`job:${event.jobId}`).emit('progress', {
          progress: event.progress,
          stage: event.stage,
          preview: event.preview
        });
      }
    });
  }
}
```

### Phase 3: Production Hardening (Week 3)

#### Step 3.1: Error Handling & Resilience

```typescript
// /lib/tenxsom/resilient-gateway.ts
export class ResilientTenxsomGateway extends TenxsomGateway {
  async createContentJobWithRetry(params: any, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await this.createContentJob(params);
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        
        // Log to FractalAwareCMS
        await this.logFailure(error, params, i + 1);
        
        // Exponential backoff
        await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
      }
    }
  }
}
```

#### Step 3.2: Resource Management

```typescript
// /lib/resource-manager.ts
export class ResourceManager {
  private currentUsage = { vram: 0, ram: 0, jobs: 0 };
  
  async canAcceptJob(estimatedResources: ResourceEstimate): boolean {
    const available = await this.getAvailableResources();
    
    return (
      available.vram >= estimatedResources.vram &&
      available.ram >= estimatedResources.ram &&
      this.currentUsage.jobs < MAX_CONCURRENT_JOBS
    );
  }
  
  async allocateResources(jobId: string, resources: ResourceEstimate) {
    this.currentUsage.vram += resources.vram;
    this.currentUsage.ram += resources.ram;
    this.currentUsage.jobs += 1;
    
    // Register cleanup on job completion
    this.registerCleanup(jobId, resources);
  }
}
```

### Phase 4: Autonomous Pipeline Integration (Week 4)

#### Step 4.1: Google Trends Scanner

```typescript
// /lib/autonomous/trend-scanner.ts
export class TrendScanner {
  async scan(): Promise<TrendData[]> {
    const trends = await googleTrends.dailyTrends({ geo: 'US' });
    
    return trends.map(trend => ({
      topic: trend.title,
      velocity: this.calculateVelocity(trend),
      novelty: this.calculateNovelty(trend),
      relevance: this.calculateRelevance(trend)
    }));
  }
  
  async submitToResonanceArbiter(trends: TrendData[]) {
    const resonantTrends = trends.filter(t => 
      t.novelty > 0.9 && t.relevance > 0.7
    );
    
    for (const trend of resonantTrends) {
      await this.createAutonomousJob(trend);
    }
  }
}
```

#### Step 4.2: Priority Queue Implementation

```typescript
// /lib/queue/priority-queue.ts
export class MaxwellianPriorityQueue {
  async enqueue(job: Job) {
    const priority = job.source === 'user' ? 1.0 : 0.2;
    
    await prisma.jobQueue.create({
      data: {
        ...job,
        priority,
        amplifiedProbability: this.calculateAmplification(priority)
      }
    });
  }
  
  async dequeue(): Promise<Job | null> {
    // Use Maxwellian selection logic
    const jobs = await prisma.jobQueue.findMany({
      where: { status: 'pending' },
      orderBy: { amplifiedProbability: 'desc' }
    });
    
    if (jobs.length === 0) return null;
    
    // Probabilistic selection with heavy bias toward high priority
    const selected = this.maxwellianSelect(jobs);
    
    await prisma.jobQueue.update({
      where: { id: selected.id },
      data: { status: 'processing' }
    });
    
    return selected;
  }
}
```

## Migration Strategy

### From Current State to Full-Stack AI

1. **Preserve Existing Work**
   - Move current UI components to `/legacy` for reference
   - Extract reusable crystalline CSS animations
   - Document custom interactions for recreation

2. **Incremental Migration**
   - Week 1: Generate and customize base application
   - Week 2: Connect authentication and basic APIs
   - Week 3: Integrate ProStudio tools one by one
   - Week 4: Enable autonomous features

3. **Testing Strategy**
   - Unit tests for each Tenxsom gateway method
   - Integration tests for full workflows
   - Load tests for resource management
   - E2E tests for critical user paths

## Success Metrics

1. **Functional Completion**
   - [ ] All ProStudio tools integrated
   - [ ] Real-time progress tracking working
   - [ ] Autonomous pipeline operational
   - [ ] User priority system active

2. **Performance Targets**
   - API response time < 200ms
   - WebSocket latency < 50ms
   - Video generation start < 5s
   - Resource allocation < 1s

3. **Reliability Goals**
   - 99.9% uptime for API
   - Graceful degradation on tool failure
   - Zero data loss on crashes
   - Automatic recovery from errors

## Next Immediate Steps

1. **Install fsai**: `npm install -g fsai`
2. **Set OpenAI API key**: Required for AI generation
3. **Generate base app**: Run the fsai command with our prompt
4. **Review generated code**: Understand the structure
5. **Plan integration points**: Map Tenxsom APIs to generated endpoints

This approach gives us a production-ready foundation in days rather than months, allowing us to focus on the unique value of Tenxsom AI rather than boilerplate code.