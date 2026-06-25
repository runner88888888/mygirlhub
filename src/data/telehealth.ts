import { AFFILIATE_TAG } from './shop';

export type TelehealthPartner = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  features: string[];
  image: string;
  imageAlt: string;
  ctaLabel: string;
  ctaHref: string;
};

/** Replace with your approved BetterHelp & Talkspace affiliate URLs */
export const telehealthPartners: TelehealthPartner[] = [
  {
    id: 'betterhelp',
    name: 'BetterHelp',
    tagline: 'Online Therapy',
    description:
      'Connect with licensed, professional therapists worldwide — by video, phone, or secure messaging. Ideal when waitlists are long, you travel for work, or you want flexible support between in-person sessions.',
    features: [
      '24/7 messaging with matched therapists',
      'Video and phone sessions on your schedule',
      'Licensed clinicians in multiple countries',
      'Switch therapists if the fit is not right',
    ],
    image:
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
    imageAlt: 'Professional woman in a supportive therapy conversation',
    ctaLabel: 'Get started with BetterHelp',
    ctaHref: `https://www.betterhelp.com/get-started/?utm_source=affiliate&utm_medium=referral&utm_campaign=${AFFILIATE_TAG}`,
  },
  {
    id: 'talkspace',
    name: 'Talkspace',
    tagline: 'Virtual Mental Health Care',
    description:
      'Flexible text-and-video-based mental health support from credentialed providers. Many plans include psychiatry options where available — a strong fit for busy professionals who prefer async check-ins.',
    features: [
      'Text, audio, and video therapy options',
      'Psychiatry and medication management (where offered)',
      'Insurance accepted on eligible plans (US; check regional availability)',
      'Secure, HIPAA-compliant platform',
    ],
    image:
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
    imageAlt: 'Professional woman using laptop for virtual care',
    ctaLabel: 'Explore Talkspace',
    ctaHref: `https://www.talkspace.com/?utm_source=affiliate&utm_medium=referral&utm_campaign=${AFFILIATE_TAG}`,
  },
];
