import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    category: z.enum(['Mental Health', 'Cycle Syncing', 'Burnout']),
    image: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

const directory = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/directory' }),
  schema: z.object({
    practitionerName: z.string(),
    specialty: z.enum(['Therapist', 'Life Coach', 'Fitness Instructor']),
    bio: z.string(),
    location: z.string(),
    image: z.string().optional(),
    externalWebsiteUrl: z.string().url(),
  }),
});

export const collections = { blog, directory };
