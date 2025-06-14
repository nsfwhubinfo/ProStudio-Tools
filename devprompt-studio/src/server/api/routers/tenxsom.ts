import { z } from "zod";
import { createTRPCRouter, protectedProcedure, publicProcedure } from "~/server/api/trpc";
import { TRPCError } from "@trpc/server";

// Input schemas
const createJobSchema = z.object({
  type: z.enum(["video", "image", "audio", "text"]),
  prompt: z.string().min(1).max(1000),
  options: z.record(z.any()).optional(),
});

const jobStatusSchema = z.object({
  jobId: z.string(),
});

// Mock Tenxsom backend URL - replace with actual
const TENXSOM_API_URL = process.env.TENXSOM_API_URL || "http://localhost:8000";

export const tenxsomRouter = createTRPCRouter({
  // Create a new content generation job
  createJob: protectedProcedure
    .input(createJobSchema)
    .mutation(async ({ input, ctx }) => {
      try {
        // Call Tenxsom AI backend
        const response = await fetch(`${TENXSOM_API_URL}/api/cortex/job`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${process.env.TENXSOM_API_KEY}`,
          },
          body: JSON.stringify({
            workflow: input.type,
            prompt: input.prompt,
            priority: 1.0, // User-initiated = high priority
            metadata: {
              ...input.options,
              userId: ctx.session.user.id,
            },
          }),
        });

        if (!response.ok) {
          throw new TRPCError({
            code: "INTERNAL_SERVER_ERROR",
            message: "Failed to create job in Tenxsom AI",
          });
        }

        const job = await response.json();

        // Store job reference in our database
        await ctx.db.job.create({
          data: {
            id: job.id,
            userId: ctx.session.user.id,
            type: input.type,
            prompt: input.prompt,
            status: "processing",
            tenxsomJobId: job.tenxsomId,
            createdAt: new Date(),
          },
        });

        return {
          jobId: job.id,
          status: "processing",
        };
      } catch (error) {
        console.error("Error creating Tenxsom job:", error);
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: "Failed to create content generation job",
        });
      }
    }),

  // Get job status
  getJobStatus: protectedProcedure
    .input(jobStatusSchema)
    .query(async ({ input, ctx }) => {
      // First check our database
      const job = await ctx.db.job.findUnique({
        where: {
          id: input.jobId,
          userId: ctx.session.user.id,
        },
      });

      if (!job) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Job not found",
        });
      }

      // If job is still processing, check Tenxsom backend
      if (job.status === "processing") {
        try {
          const response = await fetch(
            `${TENXSOM_API_URL}/api/cortex/job/${job.tenxsomJobId}`,
            {
              headers: {
                "Authorization": `Bearer ${process.env.TENXSOM_API_KEY}`,
              },
            }
          );

          if (response.ok) {
            const tenxsomJob = await response.json();
            
            // Update our database if status changed
            if (tenxsomJob.status !== job.status) {
              await ctx.db.job.update({
                where: { id: job.id },
                data: {
                  status: tenxsomJob.status,
                  result: tenxsomJob.result,
                  updatedAt: new Date(),
                },
              });
              
              job.status = tenxsomJob.status;
              job.result = tenxsomJob.result;
            }
          }
        } catch (error) {
          console.error("Error checking Tenxsom job status:", error);
        }
      }

      return {
        jobId: job.id,
        status: job.status,
        progress: job.progress || 0,
        result: job.result,
        createdAt: job.createdAt,
      };
    }),

  // List user's jobs
  listJobs: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(10),
        offset: z.number().min(0).default(0),
      })
    )
    .query(async ({ input, ctx }) => {
      const jobs = await ctx.db.job.findMany({
        where: {
          userId: ctx.session.user.id,
        },
        orderBy: {
          createdAt: "desc",
        },
        take: input.limit,
        skip: input.offset,
      });

      return {
        jobs: jobs.map((job) => ({
          id: job.id,
          type: job.type,
          prompt: job.prompt,
          status: job.status,
          createdAt: job.createdAt,
        })),
        total: await ctx.db.job.count({
          where: { userId: ctx.session.user.id },
        }),
      };
    }),

  // Get available tools
  getTools: publicProcedure.query(async () => {
    return {
      tools: [
        {
          id: "text-ai",
          name: "Text AI",
          description: "Generate high-quality text content",
          icon: "📝",
          category: "text",
        },
        {
          id: "image-ai",
          name: "Image AI",
          description: "Create stunning images from text",
          icon: "🎨",
          category: "visual",
        },
        {
          id: "video-ai",
          name: "Video AI",
          description: "Generate videos with Frame Pack",
          icon: "🎬",
          category: "visual",
        },
        {
          id: "audio-ai",
          name: "Audio AI",
          description: "Create music and sound effects",
          icon: "🎵",
          category: "audio",
        },
      ],
    };
  }),
});