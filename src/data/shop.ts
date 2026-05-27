import { images } from './images';

/** Replace placeholder IDs with your live Stripe, Gumroad, and Amazon Associates tags */
export const AFFILIATE_TAG = 'mygirlhub-22';

export type ShopProduct = {
  id: string;
  type: 'digital' | 'affiliate';
  title: string;
  description: string;
  price?: string;
  priceNote?: string;
  image: string;
  imageAlt: string;
  ctaLabel: string;
  ctaHref: string;
  ctaExternal?: boolean;
  badge?: string;
  highlight?: boolean;
};

export const shopProducts: ShopProduct[] = [
  {
    id: 'cycle-planner-pdf',
    type: 'digital',
    title: 'The Ultimate 28-Day Cycle Syncing & Energy Planner (PDF)',
    description:
      'Printable daily prompts, phase-specific meal ideas, movement cues, and energy tracking sheets — designed for real schedules, not perfectionism.',
    price: '$14.99',
    priceNote: 'AUD · Instant download',
    image: images.shop.planner,
    imageAlt: 'Journal and planner on a calm workspace',
    ctaLabel: 'Buy now — secure checkout',
    ctaHref: 'https://buy.stripe.com/test_REPLACE_WITH_YOUR_STRIPE_LINK',
    ctaExternal: true,
    badge: 'Our #1 digital product',
    highlight: true,
  },
  {
    id: 'in-the-flo',
    type: 'affiliate',
    title: 'In the FLO by Alisa Vitti',
    description:
      'The foundational read on cycle syncing — hormone balance, food as medicine, and working with your infradian rhythm.',
    price: 'From ~$22',
    priceNote: 'Amazon.com.au',
    image: images.shop.book,
    imageAlt: 'Woman in restorative yoga pose',
    ctaLabel: 'Buy on Amazon',
    ctaHref: `https://www.amazon.com.au/In-FLO-Alisa-Vitti/dp/006287048X?tag=${AFFILIATE_TAG}`,
    ctaExternal: true,
    badge: 'Essential reading',
  },
  {
    id: 'betterhelp',
    type: 'affiliate',
    title: 'Therapy & Mental Health Support via BetterHelp',
    description:
      'Licensed therapists by video, phone, or chat — flexible scheduling for burnout, anxiety, and life transitions. Many Australians use online therapy between in-person care.',
    price: 'Plans from ~$90/week',
    priceNote: 'Cancel anytime',
    image: images.shop.therapy,
    imageAlt: 'Professional woman in a supportive conversation',
    ctaLabel: 'Get matched with a therapist',
    ctaHref: `https://www.betterhelp.com/get-started/?utm_source=affiliate&utm_medium=referral&utm_campaign=${AFFILIATE_TAG}`,
    ctaExternal: true,
    badge: 'Professional support',
  },
  {
    id: 'self-care-kit',
    type: 'affiliate',
    title: 'Premium Weighted Anxiety Blanket & Pure Magnesium Flakes',
    description:
      'High-converting evening ritual duo: deep-pressure calm for your nervous system plus magnesium bath flakes for muscle release and sleep prep.',
    price: 'Bundle from ~$89',
    priceNote: 'Amazon Associates',
    image: images.shop.selfCareKit,
    imageAlt: 'Woman practicing mindfulness and rest',
    ctaLabel: 'Shop self-care essentials',
    ctaHref: `https://www.amazon.com.au/s?k=weighted+blanket+magnesium+flakes&tag=${AFFILIATE_TAG}`,
    ctaExternal: true,
    badge: 'Editor’s pick',
  },
];
