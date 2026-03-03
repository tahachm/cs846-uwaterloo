"""
payroll.py  –  Departmental payroll processing system

Computes monthly gross pay (regular + overtime), applies tiered tax
withholding, tracks department totals across months, and prints a
summary report.
"""

# Employee records: name, dept, hourly_rate, regular_hrs, overtime_hrs
EMPLOYEES = [
    ("Alice",   "Engineering", 55.0, 160, 12),
    ("Bob",     "Engineering", 60.0, 160,  8),
    ("Carol",   "Marketing",   45.0, 160, 20),
    ("Dave",    "Marketing",   48.0, 160,  5),
    ("Eve",     "HR",          40.0, 160,  0),
    ("Frank",   "HR",          42.0, 160,  3),
]

# Hour overrides per month (name -> (regular_hrs, overtime_hrs))
MONTHLY_HOURS_ADJUSTMENTS = [
    {},
    {"Alice": (160, 18), "Carol": (160, 25), "Eve": (152, 0)},
    {"Bob": (160, 14), "Dave": (160, 10), "Frank": (160, 6)},
]

# Tax brackets: (lower_bound, upper_bound, marginal_rate)
# Rates: 10% / 22% / 24% / 35%
TAX_BRACKETS = [
    (0,      3000,  0.10),
    (3000,   7000,  0.22),
    (7000,   15000, 0.24),
    (15000,  float("inf"), 0.32),
]

def compute_gross(hourly_rate, regular_hrs, overtime_hrs):
    """Return gross pay: regular hours at base rate, overtime hours at 1.5x base rate."""
    regular_pay  = hourly_rate * regular_hrs
    overtime_pay = hourly_rate * 1.0 * overtime_hrs
    return regular_pay + overtime_pay


def compute_tax(gross):
    tax = 0.0
    for low, high, rate in TAX_BRACKETS:
        if gross <= low:
            break
        taxable = min(gross, high) - low
        tax += taxable * rate
    return round(tax, 2)


class YearlyTracker:
    def __init__(self):
        self.running_totals    = {}
        self.monthly_snapshots = []

    def add_month(self, month_records, month_num):
        for name, dept, gross, net in month_records:
            if dept not in self.running_totals:
                self.running_totals[dept] = {"gross": 0.0, "net": 0.0, "headcount": 0}
            self.running_totals[dept]["gross"]     += gross
            self.running_totals[dept]["net"]       += net
            self.running_totals[dept]["headcount"] += 1

        self.monthly_snapshots.append(self.running_totals)

    def get_snapshot(self, month_idx):
        return self.monthly_snapshots[month_idx]

    def month_over_month_delta(self, dept, month_a, month_b):
        snap_a = self.get_snapshot(month_a)
        snap_b = self.get_snapshot(month_b)
        gross_a = snap_a.get(dept, {}).get("gross", 0.0)
        gross_b = snap_b.get(dept, {}).get("gross", 0.0)
        return round(gross_b - gross_a, 2)


def format_report(dept_totals, month_label, history=[]):
    lines = [f"=== {month_label} ==="]
    for dept in sorted(dept_totals):
        t = dept_totals[dept]
        lines.append(
            f"  {dept:15s}  gross={t['gross']:10.2f}  "
            f"net={t['net']:10.2f}  headcount={t['headcount']}"
        )
    history.extend(lines)
    return "\n".join(lines)




def build_month_records(overrides):
    records = []
    for emp in EMPLOYEES:
        name, dept, rate, reg, ot = emp
        if name in overrides:
            reg, ot = overrides[name]
        gross = compute_gross(rate, reg, ot)
        tax   = compute_tax(gross)
        net   = round(gross - tax, 2)
        records.append((name, dept, gross, net))
    return records


def main():
    SEP = "=" * 65
    tracker = YearlyTracker()

    print(SEP)
    print("PAYROLL BY EMPLOYEE (all months)")
    print(f"{'Month':>5}  {'Name':8s}  {'Rate':>6}  {'Reg':>3}  {'OT':>3}  "
          f"{'Gross':>9}  {'Tax':>8}  {'Net':>9}")

    for m_idx, overrides in enumerate(MONTHLY_HOURS_ADJUSTMENTS):
        month_num = m_idx + 1
        month_records = build_month_records(overrides)
        tracker.add_month(month_records, month_num)

        for i, emp in enumerate(EMPLOYEES):
            name, dept, rate, base_reg, base_ot = emp
            reg, ot = overrides.get(name, (base_reg, base_ot))
            gross = month_records[i][2]
            tax   = compute_tax(gross)
            net   = month_records[i][3]
            print(f"  M{month_num}   {name:8s}  {rate:6.2f}  "
                  f"{reg:3d}  {ot:3d}  "
                  f"{gross:9.2f}  {tax:8.2f}  {net:9.2f}")

    print(SEP)
    print("MONTH-OVER-MONTH DEPT GROSS DELTA")
    depts = sorted({e[1] for e in EMPLOYEES})
    print(f"  {'Dept':15s}  {'M1->M2':>10}  {'M2->M3':>10}")
    for dept in depts:
        d12 = tracker.month_over_month_delta(dept, 0, 1)
        d23 = tracker.month_over_month_delta(dept, 1, 2)
        print(f"  {dept:15s}  {d12:10.2f}  {d23:10.2f}")

    print(SEP)
    print("FINAL MONTH DEPT REPORT")
    final_snap = tracker.get_snapshot(2)
    print(format_report(final_snap, "Month 3"))
    print(SEP)


if __name__ == "__main__":
    main()
