#!/usr/bin/env python3
from shared.policies.email_priority_policy_v1 import classify_priority

cases = [
    ({"to": ["laia@grid-code.tech"], "cc": []}, "P1"),
    ({"to": ["otro@x.com"], "cc": ["laia@grid-code.tech"]}, "P2"),
    ({"to": ["otro@x.com"], "cc": []}, None),
    ({"to": ["laia@grid-code.tech"], "cc": ["laia@grid-code.tech"]}, "P1"),
]

ok = True
for i, (inp, exp) in enumerate(cases, 1):
    got = classify_priority(inp["to"], inp["cc"])
    print(f"case_{i}: expected={exp} got={got}")
    if got != exp:
        ok = False

if not ok:
    raise SystemExit(1)

print("priority_rule_ok")
