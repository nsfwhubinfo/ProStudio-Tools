import { PrismaAdapter } from "@auth/prisma-adapter";
import { type DefaultSession, type NextAuthConfig } from "next-auth";
import DiscordProvider from "next-auth/providers/discord";
import CredentialsProvider from "next-auth/providers/credentials";

import { db } from "~/server/db";

/**
 * Module augmentation for `next-auth` types. Allows us to add custom properties to the `session`
 * object and keep type safety.
 *
 * @see https://next-auth.js.org/getting-started/typescript#module-augmentation
 */
declare module "next-auth" {
  interface Session extends DefaultSession {
    user: {
      id: string;
      // ...other properties
      // role: UserRole;
    } & DefaultSession["user"];
  }

  // interface User {
  //   // ...other properties
  //   // role: UserRole;
  // }
}

/**
 * Options for NextAuth.js used to configure adapters, providers, callbacks, etc.
 *
 * @see https://next-auth.js.org/configuration/options
 */
export const authConfig = {
  providers: [
    // Discord provider (only if credentials are provided)
    ...(process.env.AUTH_DISCORD_ID && process.env.AUTH_DISCORD_SECRET 
      ? [DiscordProvider] 
      : []),
    
    // Development credentials provider
    ...(process.env.NODE_ENV === "development" 
      ? [CredentialsProvider({
          name: "Development",
          credentials: {
            email: { label: "Email", type: "email", placeholder: "dev@example.com" }
          },
          async authorize(credentials) {
            // For development, accept any email
            if (credentials?.email) {
              // Check if user exists
              let user = await db.user.findUnique({
                where: { email: credentials.email }
              });
              
              // Create user if doesn't exist
              if (!user) {
                user = await db.user.create({
                  data: {
                    email: credentials.email,
                    name: credentials.email.split('@')[0],
                  }
                });
              }
              
              return { id: user.id, email: user.email, name: user.name };
            }
            return null;
          }
        })]
      : []),
  ],
  adapter: PrismaAdapter(db),
  callbacks: {
    session: ({ session, user }) => ({
      ...session,
      user: {
        ...session.user,
        id: user.id,
      },
    }),
  },
} satisfies NextAuthConfig;
