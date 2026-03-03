"""
test_payroll.py  –  Correctness tests for problem_file.py

Runs independently and verifies that:
  1. compute_gross returns the right value (reg + 1.5x OT)
  2. YearlyTracker snapshots are independent per month
  3. month_over_month_delta returns accurate deltas
  4. format_report does not accumulate state across calls
"""

import copy
import math
import sys
import importlib

# --------------------------------------------------------------------------
# Import the module under test
# --------------------------------------------------------------------------
import problem_file as p

def _ref_gross(rate, reg, ot):
    return rate * reg + rate * 1.5 * ot

def _ref_compute_tax(gross):
    brackets = [
        (0,     3000,  0.10),
        (3000,  7000,  0.22),
        (7000,  15000, 0.24),
        (15000, math.inf, 0.35),   # correct top rate
    ]
    tax = 0.0
    for low, high, rate in brackets:
        if gross <= low:
            break
        taxable = min(gross, high) - low
        tax += taxable * rate
    return round(tax, 2)

PASS = "PASS"
FAIL = "FAIL"
results = []

def check(name, actual, expected, tol=0.01):
    ok = abs(actual - expected) <= tol
    tag = PASS if ok else FAIL
    results.append((tag, name, actual, expected))
    print(f"  [{tag}]  {name}")
    if not ok:
        print(f"         actual={actual}  expected={expected}")

# --------------------------------------------------------------------------
# Test 1: compute_gross  (one case per employee, month 1)
# --------------------------------------------------------------------------
print("\n=== Test 1: compute_gross ===")
for emp in p.EMPLOYEES:
    name, dept, rate, reg, ot = emp
    got = p.compute_gross(rate, reg, ot)
    exp = _ref_gross(rate, reg, ot)
    check(f"gross {name} M1", got, exp)

# --------------------------------------------------------------------------
# Test 2: compute_gross with overrides (month 2 & 3)
# --------------------------------------------------------------------------
print("\n=== Test 2: compute_gross with hour overrides ===")
for m_idx, overrides in enumerate(p.MONTHLY_HOURS_ADJUSTMENTS[1:], start=2):
    for emp in p.EMPLOYEES:
        name, dept, rate, base_reg, base_ot = emp
        if name in overrides:
            reg, ot = overrides[name]
            got = p.compute_gross(rate, reg, ot)
            exp = _ref_gross(rate, reg, ot)
            check(f"gross {name} M{m_idx}", got, exp)

# --------------------------------------------------------------------------
# Test 3: YearlyTracker snapshots are independent (not aliased)
# --------------------------------------------------------------------------
print("\n=== Test 3: YearlyTracker snapshot independence ===")
tracker = p.YearlyTracker()
all_month_records = []
for overrides in p.MONTHLY_HOURS_ADJUSTMENTS:
    records = p.build_month_records(overrides)
    all_month_records.append(records)
    tracker.add_month(records, len(all_month_records))

# Snapshots should differ from each other;
# snap[0] should only contain month-1 cumulative, not months 1+2+3
snap0 = tracker.get_snapshot(0)
snap1 = tracker.get_snapshot(1)
snap2 = tracker.get_snapshot(2)

# Build reference cumulative totals per month independently
def ref_cumulative(month_records_list, up_to):
    totals = {}
    for records in month_records_list[:up_to]:
        for name, dept, gross, net in records:
            if dept not in totals:
                totals[dept] = {"gross": 0.0}
            totals[dept]["gross"] += gross
    return totals

ref0 = ref_cumulative(all_month_records, 1)
ref1 = ref_cumulative(all_month_records, 2)
ref2 = ref_cumulative(all_month_records, 3)

for dept in sorted({e[1] for e in p.EMPLOYEES}):
    check(f"snap[0] gross {dept}", snap0[dept]["gross"], ref0[dept]["gross"])
    check(f"snap[1] gross {dept}", snap1[dept]["gross"], ref1[dept]["gross"])
    check(f"snap[2] gross {dept}", snap2[dept]["gross"], ref2[dept]["gross"])

# --------------------------------------------------------------------------
# Test 4: month_over_month_delta
# --------------------------------------------------------------------------
print("\n=== Test 4: month_over_month_delta ===")
for dept in sorted({e[1] for e in p.EMPLOYEES}):
    exp_d12 = round(ref1[dept]["gross"] - ref0[dept]["gross"], 2)
    exp_d23 = round(ref2[dept]["gross"] - ref1[dept]["gross"], 2)
    check(f"delta M1->M2 {dept}", tracker.month_over_month_delta(dept, 0, 1), exp_d12)
    check(f"delta M2->M3 {dept}", tracker.month_over_month_delta(dept, 1, 2), exp_d23)

# --------------------------------------------------------------------------
# Test 5: format_report does not accumulate state across calls
# The mutable default `history=[]` grows on every call.
# After N calls the hidden history list has N*lines_per_call entries.
# We detect this by inspecting the function's default argument directly.
# --------------------------------------------------------------------------
print("\n=== Test 5: format_report statelessness ===")
sample = {"Engineering": {"gross": 1000.0, "net": 800.0, "headcount": 2}}
# Reset any state from earlier in this test run
p.format_report.__defaults__[0].clear()

p.format_report(sample, "Run 1")
p.format_report(sample, "Run 2")

hidden_history = p.format_report.__defaults__[0]
# After 2 calls with 1 dept each, history should be empty (2 header + 2 dept = 4 lines if buggy)
expected_history_len = 0
ok_stateless = len(hidden_history) == expected_history_len
tag = PASS if ok_stateless else FAIL
results.append((tag, "format_report stateless", len(hidden_history), expected_history_len))
print(f"  [{tag}]  format_report stateless  "
      f"(hidden history length after 2 calls: {len(hidden_history)}, expected: {expected_history_len})")

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
print("\n" + "=" * 55)
total  = len(results)
passed = sum(1 for r in results if r[0] == PASS)
failed = total - passed
print(f"Results: {passed}/{total} passed,  {failed} failed")
if failed:
    sys.exit(1)
