/** Replace with your live Typeform, Tally, or Stripe Payment Link + form URL */
export const LISTING_APPLICATION = {
  /** External intake form (Tally / Typeform) */
  formUrl: 'https://tally.so/r/REPLACE_WITH_YOUR_FORM_ID',
  /** Optional: Stripe Payment Link for paid listing review (e.g. $49 AUD) */
  listingFeeUrl: 'https://buy.stripe.com/test_REPLACE_LISTING_FEE',
  listingFeeLabel: '$49 AUD listing review fee',
  contactEmail: 'hello@mygirlhub.com',
} as const;
