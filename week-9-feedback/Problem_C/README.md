# Problem C — Guideline 2 Critique: Code Artifacts

## Files

| File | Description |
|------|-------------|
| `checkout_service.py` | Original starter code (unmodified, contains 6 planted bugs) |
| `test_checkout_v1_spec_based.py` | **Step 1** — Tests generated from the spec using Guideline 1. Assertions reflect the *specification*, not the code. Result: 9 failed, 1 passed. |
| `test_checkout_v2_repaired.py` | **Step 2** — Tests after applying Guideline 2's repair loop. The LLM "fixed" all failing tests to match the buggy code. Result: 10 passed — **all bugs erased**. |
| `test_checkout_v3_spec_anchored.py` | **Step 3** — Tests produced by the *updated* guideline (spec-anchored repair). Impl bugs are preserved as `xfail` markers. Result: 4 passed, 7 xfailed — **all bugs preserved**. |
| `prompt_cards.md` | Prompt cards and run records for all 3 runs (per Guideline 6). |
| `pytest_log_v1.txt` | Full pytest output for V1. |
| `pytest_log_v2.txt` | Full pytest output for V2. |
| `pytest_log_v3.txt` | Full pytest output for V3. |

## How to reproduce

```bash
cd problem_C_code
pip install pytest
python -m pytest test_checkout_v1_spec_based.py -v      # 9 failed, 1 passed
python -m pytest test_checkout_v2_repaired.py -v         # 10 passed (bugs hidden)
python -m pytest test_checkout_v3_spec_anchored.py -v    # 4 passed, 7 xfailed (bugs documented)
```

## Planted bugs in checkout_service.py

| # | Line | Bug |
|---|------|-----|
| 1 | 125  | Stock check inverted (`if check_stock` raises instead of `if not check_stock`) |
| 2 | 138  | Bundle threshold `>` instead of `>=` (off-by-one) |
| 3 | 171  | SUMMER20 cap uses `max()` instead of `min()` |
| 4 | 175  | FLASH5 + VIP incompatibility not enforced |
| 5 | 193  | Shipping checks pre-discount `subtotal` instead of `discounted_subtotal` |
| 6 | 199  | Tax computed on `subtotal` instead of post-discount amount |
