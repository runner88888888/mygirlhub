/** Curated Unsplash imagery — hotlinked with format/crop params for performance */
export const images = {
  hero:
    'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1600&q=80',
  blog: {
    burnout:
      'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
    cycleSyncing:
      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80',
    selfCare:
      'https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=800&q=80',
    smartHomeWellness: '/images/blog/smart-home-wellness-hero.png',
  },
  og: {
    smartHomeWellness: '/images/blog/smart-home-wellness-og.png',
  },
  shop: {
    planner:
      'https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=600&q=80',
    book: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80',
    therapy:
      'https://images.unsplash.com/photo-1573497019940-88c009e05fda?auto=format&fit=crop&w=600&q=80',
    selfCareKit:
      'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=600&q=80',
  },
} as const;
