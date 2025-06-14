import Link from "next/link";
import { auth } from "~/server/auth";
import { api, HydrateClient } from "~/trpc/server";
import { DevPromptStudio } from "./_components/devprompt-studio";

export default async function Home() {
  const session = await auth();

  // If not logged in, show login page
  if (!session?.user) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-black text-white">
        <div className="container flex flex-col items-center justify-center gap-8 px-4 py-16">
          <div className="consciousness-orb mb-8">
            <div className="orb-core"></div>
            <div className="orb-pulse"></div>
          </div>
          
          <h1 className="text-5xl font-extrabold tracking-tight spectrum-text">
            DevPrompt Content Studio
          </h1>
          
          <p className="text-xl text-gray-400 text-center max-w-2xl">
            Welcome to the crystalline consciousness interface. Sign in to begin manifesting your creative visions through AI-powered content generation.
          </p>
          
          <Link
            href="/api/auth/signin"
            className="btn-glass text-lg px-8 py-4"
          >
            Sign in to Continue
          </Link>
        </div>
      </main>
    );
  }

  // If logged in, show the main studio
  return (
    <HydrateClient>
      <DevPromptStudio />
    </HydrateClient>
  );
}