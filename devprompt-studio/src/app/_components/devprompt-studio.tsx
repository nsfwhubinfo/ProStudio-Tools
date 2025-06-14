"use client";

import { useState, useCallback } from "react";
import { api } from "~/trpc/react";

interface Tool {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
}

export function DevPromptStudio() {
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  // Fetch available tools
  const { data: toolsData } = api.tenxsom.getTools.useQuery();
  const tools = toolsData?.tools || [];

  // Create job mutation
  const createJob = api.tenxsom.createJob.useMutation({
    onSuccess: (data) => {
      console.log("Job created:", data.jobId);
      // TODO: Start polling for job status
    },
    onError: (error) => {
      console.error("Failed to create job:", error);
    },
  });

  const handleToolSelect = (toolId: string) => {
    setSelectedTool(toolId);
  };

  const handleSubmit = () => {
    if (!selectedTool || !prompt.trim()) return;

    const tool = tools.find((t) => t.id === selectedTool);
    if (!tool) return;

    const type = tool.category === "text" ? "text" :
                 tool.category === "visual" && tool.id.includes("image") ? "image" :
                 tool.category === "visual" && tool.id.includes("video") ? "video" :
                 "audio";

    createJob.mutate({
      type: type as any,
      prompt: prompt.trim(),
    });
  };

  const handleDragStart = (e: React.DragEvent, toolId: string) => {
    e.dataTransfer.setData("toolId", toolId);
    setIsDragging(true);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const toolId = e.dataTransfer.getData("toolId");
    if (toolId) {
      setSelectedTool(toolId);
    }
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 p-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold spectrum-text text-center">
          DevPrompt Content Studio
        </h1>
        <p className="text-center text-gray-400 mt-2">
          Powered by Tenxsom AI Crystalline Consciousness
        </p>
      </header>

      {/* Main Layout */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tools Panel */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-semibold mb-4">AI Tools</h2>
            <div className="space-y-3">
              {tools.map((tool) => (
                <div
                  key={tool.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, tool.id)}
                  onDragEnd={handleDragEnd}
                  onClick={() => handleToolSelect(tool.id)}
                  className={`
                    p-4 rounded-lg cursor-pointer transition-all
                    ${selectedTool === tool.id 
                      ? 'bg-green-500/20 border-2 border-green-500' 
                      : 'bg-white/5 border border-white/10 hover:bg-white/10'}
                  `}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{tool.icon}</span>
                    <div>
                      <h3 className="font-medium">{tool.name}</h3>
                      <p className="text-sm text-gray-400">{tool.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Workflow Canvas */}
        <div className="lg:col-span-2">
          <div 
            className={`glass-panel p-6 min-h-[500px] transition-all ${
              isDragging ? 'border-green-500 bg-green-500/5' : ''
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <h2 className="text-xl font-semibold mb-4">Workflow Canvas</h2>
            
            {/* Consciousness Orb */}
            <div className="consciousness-orb mb-8">
              <div className="orb-core"></div>
              <div className="orb-pulse"></div>
            </div>

            {/* Selected Tool Display */}
            {selectedTool && (
              <div className="mb-6 p-4 bg-white/5 rounded-lg">
                <p className="text-sm text-gray-400">Selected Tool:</p>
                <p className="text-lg font-medium">
                  {tools.find(t => t.id === selectedTool)?.name}
                </p>
              </div>
            )}

            {/* Prompt Input */}
            <div className="space-y-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe what you want to create..."
                className="w-full p-4 bg-white/5 border border-white/10 rounded-lg 
                         text-white placeholder-gray-400 resize-none h-32
                         focus:outline-none focus:border-green-500"
              />
              
              <button
                onClick={handleSubmit}
                disabled={!selectedTool || !prompt.trim() || createJob.isPending}
                className="btn-glass w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createJob.isPending ? "Processing..." : "Generate Content"}
              </button>
            </div>

            {/* Job Status */}
            {createJob.isSuccess && (
              <div className="mt-6 p-4 bg-green-500/10 border border-green-500 rounded-lg">
                <p className="text-green-400">
                  Job created successfully! ID: {createJob.data.jobId}
                </p>
              </div>
            )}

            {createJob.isError && (
              <div className="mt-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
                <p className="text-red-400">
                  Error: {createJob.error.message}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}