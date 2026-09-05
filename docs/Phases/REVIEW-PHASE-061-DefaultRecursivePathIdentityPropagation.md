REVIEW VERDICT:
Not Approved

CRITICAL ISSUES:
None

MAJOR ISSUES:
Issue:
Confidence-gated probe retention can leave `device.vendor` as `"auto"` while retaining a higher-confidence identity with a concrete vendor.

Why It Matters:
`execute_device_collection()` selects profiles from `device.vendor`, so this valid state still triggers generic-profile fallback despite the preserved identity.

Recommended Fix:
When an existing identity wins the confidence gate, synchronize `device.vendor` to its vendor before collection and add a regression for `vendor="auto"` plus high-confidence identity metadata.

DDR REVIEW:
UNCHANGED DD:DD-015

OUTSTANDING RISKS:
- The separate field "unreachable" symptom remains out of scope.

OPEN QUESTIONS:
None

RECOMMENDED NEXT PHASE:
PHASE-061A-DefaultRecursivePathIdentityConfidenceGateRemediation