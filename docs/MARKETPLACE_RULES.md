# Marketplace rules for rigid accessories and classic clothing (read 2026-11-09)

Sources (re-read before paying anything; numbers change):
- Specs: https://create.roblox.com/docs/avatar/rigid-accessories/specifications
- Fees: https://create.roblox.com/docs/marketplace/marketplace-fees-and-commissions
- Publishing: https://create.roblox.com/docs/marketplace/publish-to-marketplace
- Classic clothing: https://create.roblox.com/docs/avatar/classic-clothing

## Rigid accessory limits
- <= 4000 triangles, single watertight mesh, texture <= 2048x2048, Material Plastic, Transparency 0, no extra objects (Scripts, extra Parts).
- Box per type in studs, W x H x D, measured in the attachment frame, centred on the attachment unless noted (front = -Z).

| Type | Classic | Rthro Normal | Rthro Slender |
|---|---|---|---|
| Hat | 3 x 4 x 3 | 1.87 x 2.5 x 1.87 | 1.78 x 2.5 x 1.78 |
| Hair | 3 x 5 (2 up, 3 down) x 3.5 (1.5 front, 2 behind) | 1.87 x 3.12 (1.25 up, 1.875 down) x 2.18 (0.9375 front, 1.25 behind) | 1.78 x 3.12 (1.25 up, 1.875 down) x 2.08 (page says "1.892 front, 1.189 behind": a typo, front + behind must be 2.08, so use **0.892 front**) |
| Face | 3 x 2 x 2 | 1.87 x 1.25 x 1.25 | 1.78 x 1.25 x 1.18 |
| Neck | 3 x 3 x 2 | 2.95 x 3.68 x 2.16 | 2.59 x 3.39 x 1.92 |
| Shoulder (shoulder attachments) | 3 x 3 x 3 | 2.67 x 4.40 x 3.09 | 2.37 x 3.96 x 2.75 |
| Front | 3 x 3 x 3 | 2.95 x 3.68 x 3.24 | 2.59 x 3.39 x 2.88 |
| Back | 10 x 7 x 4.5 (1.5 front, 3 behind) | 9.86 x 8.59 x 4.87 (1.623 front, 3.246 behind) | 8.64 x 7.91 x 4.32 (1.443 front, 2.886 behind) |
| Waist | 4 x 3.5 (1.5 up, 2 down) x 7 | 3.94 x 4.29 (1.842 up, 2.457 down) x 7.57 | 3.76 x 3.29 (1.414 up, 1.885 down) x 6.73 |

Which scale the upload validator enforces is not stated on the pages; target all three to be safe.
The official validation runs in Studio: Explorer > Save to Roblox > Submit As Avatar Asset > type ("validation begins upon
selection"); hover an error for details. That is the upload flow, so agents do not run it (fee). The Accessory Fitting Tool
(Avatar tab > Accessory) shows a red box when a rigid item is out of bounds. Our local pre-check is `docs/studio/ugc_check.lua`.

## Fees and requirements (Robux)
- Government-ID verification (or a verified parent account) to upload. The fees page does not list Premium; an earlier read of the
  marketplace policy page (tidewatch QUALITY_PLAN.md) said Premium is needed to publish and keep items on sale: unverified, check it.
- Upload fee: 80 per submission (500 with an emissive mask), not refunded if moderation rejects. Every update costs the upload fee again.
- Publishing advance (refundable against sales), non-limited / paid limited: Hat and Face 1500 / 13000; Hair 1000 / 6000;
  Neck, Shoulder, Front, Back, Waist 1000 / 15000. Emissive items have higher advances (Hat 7500, Back/Neck/Shoulder 5000).
- Classic shirt / pants / t-shirt: 80 upload fee, 10 publishing advance.
- Creator share 30% of a Marketplace sale (rises to 70% at 6x the price floor); in-experience sales 30% creator + 40% experience owner; 30-day escrow.
- Price must sit inside the per-type range shown at https://create.roblox.com/dashboard/creations/pricing.
Cost to list the whole Crystal Vanguard set as non-limited (6 rigid items + shirt + pants), before any sale:
- without glow (no emissive masks): uploads 8 x 80 = 640, advances 5 x 1000 (2 pauldrons, cape, scarf, sword) + 1000 (crown as
  Hair; 1500 as Hat) + 2 x 10 = 6,020; total about 6,660 Robux (7,160 with the crown as Hat).
- with glow as built in r10 (all 6 rigid items carry an emissive mask): uploads 6 x 500 + 2 x 80 = 3,160, advances from the
  emissive table (Hair 5000, Back/Neck/Shoulder 5000 each; the Waist emissive advance was not read) + 20: roughly 33,000
  Robux. PARTIAL estimate: re-read the fees page before any decision. Glow is a big cost
  multiplier: ship emissive only on the items that need it (sword, cape) or not at all.
Never pay without the owner's yes.
