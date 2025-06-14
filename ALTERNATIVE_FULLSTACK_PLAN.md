# Alternative Full-Stack Implementation Plan

## Issue Identified
The recommended fsai tool requires an OpenAI API key to generate the application code. Without this key, we need an alternative approach.

## Alternative Approaches

### Option 1: Manual Next.js Scaffolding
We can manually create a Next.js application with the required features:

```bash
# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest devprompt-studio --typescript --tailwind --app --use-npm

# Add essential dependencies
cd devprompt-studio
npm install prisma @prisma/client
npm install next-auth @auth/prisma-adapter
npm install socket.io socket.io-client
npm install @tanstack/react-query
npm install framer-motion
npm install lucide-react
npm install -D @types/node
```

### Option 2: Use Wasp Framework
Wasp provides AI-powered app generation through their web interface:
1. Visit https://usemage.ai/
2. Describe the application requirements
3. Download generated code
4. Customize for Tenxsom integration

### Option 3: T3 Stack
Use the T3 stack (Next.js, TypeScript, tRPC, Prisma, Tailwind) as a foundation:
```bash
npm create t3-app@latest devprompt-studio -- --noGit --tailwind --trpc --nextAuth --prisma --appRouter --dbProvider postgresql
```

### Option 4: Create Custom Template
Build our own template repository based on the existing UI work:
1. Use the crystalline UI components already created
2. Add Next.js API routes manually
3. Integrate with Tenxsom AI backend
4. Add authentication and database layer

## Recommended Approach: Option 3 + Custom Integration

### Why T3 Stack?
- Production-ready foundation
- All required technologies included
- Well-documented patterns
- Active community support
- Easy to extend with Tenxsom-specific features

### Implementation Steps

1. **Create T3 Application**
   ```bash
   cd ~/prostudio
   npm create t3-app@latest devprompt-studio
   ```

2. **Port Existing UI Components**
   - Copy crystalline CSS from devprompt_ui/styles.css
   - Convert HTML to React components
   - Integrate drag-and-drop functionality

3. **Create API Integration Layer**
   ```typescript
   // src/server/api/routers/tenxsom.ts
   export const tenxsomRouter = createTRPCRouter({
     createJob: protectedProcedure
       .input(z.object({
         type: z.enum(['video', 'image', 'audio', 'text']),
         prompt: z.string(),
         options: z.record(z.any())
       }))
       .mutation(async ({ input, ctx }) => {
         // Call Tenxsom AI backend
         const response = await fetch(`${env.TENXSOM_URL}/api/job`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(input)
         });
         return response.json();
       })
   });
   ```

4. **Add WebSocket Support**
   ```typescript
   // src/server/websocket.ts
   import { Server } from 'socket.io';
   
   export function createWebSocketServer(httpServer: any) {
     const io = new Server(httpServer, {
       cors: { origin: '*' }
     });
     
     io.on('connection', (socket) => {
       socket.on('subscribe-job', (jobId) => {
         socket.join(`job:${jobId}`);
       });
     });
     
     return io;
   }
   ```

5. **Implement Job Queue**
   ```typescript
   // src/server/queue/index.ts
   import Bull from 'bull';
   
   export const contentQueue = new Bull('content-generation', {
     redis: process.env.REDIS_URL
   });
   
   contentQueue.process(async (job) => {
     const { type, prompt, options } = job.data;
     // Process with Tenxsom AI
   });
   ```

## Immediate Next Steps

1. Create T3 application
2. Set up development environment
3. Port existing UI components
4. Create basic API structure
5. Test integration points

This approach gives us full control while leveraging battle-tested patterns and avoiding the need for proprietary AI services.