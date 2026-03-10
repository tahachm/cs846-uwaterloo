# Prompt Cards & Run Records — Problem C (Guideline 2 Critique)

## Run 1: V1 — Spec-Based Test Generation (Guideline 1)

```
Prompt ID:    C_v1_spec_based
Model:        GPT-4 (as specified by Problem A instructions)
Target:       problem_A/checkout_service.py :: CheckoutService.process_checkout
Prompt:
    Generate pytest unit tests for CheckoutService.process_checkout in
    checkout_service.py.
    Framework: pytest + unittest.mock.MagicMock for InventoryService and
    PaymentGateway.
    Cover each rule per the specification:
      - Stock check: error when out of stock, success when in stock
      - Flash-sale discount (5%), bundle discount (quantity >= 3, 5%)
      - SAVE10 (10%, min $100), SUMMER20 (20% capped at $30, min $75)
      - VIP discount (15%) incompatible with SAVE10/SUMMER20;
        FLASH5 incompatible with VIP
      - Loyalty credit applied only when points >= 500
      - Shipping: $10 if discounted subtotal < $50, else $0
      - Tax: 13% on post-discount, post-loyalty-credit amount
      - Payment failure -> CheckoutError
      - Total must never be negative
Command:      python -m pytest test_checkout_v1_spec_based.py -v
Artifacts:    test_checkout_v1_spec_based.py
Result:       9 failed, 1 passed
Notes:        All spec-correct assertions. Stock inversion blocks 8 tests.
              FLASH5+VIP test passes (correctly expects CheckoutError).
```

---

## Run 2: V2 — Repair Loop (Original Guideline 2)

```
Prompt ID:    C_v2_repair_loop
Model:        GPT-4
Target:       problem_A/checkout_service.py :: CheckoutService.process_checkout
Prompt:
    Running the tests produced these failures:

    [pasted full pytest -v output from Run 1 showing 9 failures]

    Are these bugs in the tests or the implementation? Explain the root
    cause and return a corrected test file. Do not modify
    checkout_service.py.
Command:      python -m pytest test_checkout_v2_repaired.py -v
Artifacts:    test_checkout_v2_repaired.py
Result:       10 passed, 0 failed
Notes:        LLM "repaired" all 6 bug-detecting assertions to match
              buggy code. Suite is green but encodes bugs as expected
              behavior. Zero defect-revealing tests remain.
```

---

## Run 3: V3 — Spec-Anchored Repair (Updated Guideline 2)

```
Prompt ID:    C_v3_spec_anchored
Model:        GPT-4
Target:       problem_A/checkout_service.py :: CheckoutService.process_checkout
Prompt:
    Running the tests produced 9 failures. For each failure:

    1. Compare the test's expected value against the ORIGINAL
       SPECIFICATION (the InventoryService docstring says "Returns True
       if available"; the prompt spec says "bundle discount quantity >= 3";
       "SUMMER20 capped at $30"; "tax on post-discount amount"; "shipping
       on discounted subtotal"; "FLASH5 incompatible with VIP").

    2. Classify each failure as:
       (A) TEST BUG  — the test contradicts the spec. Fix the test.
       (B) IMPL BUG  — the test matches the spec but the code disagrees.
           Keep the spec-correct assertion. Mark with
           @pytest.mark.xfail(reason="IMPL BUG: <description>") so the
           suite runs green.
       (C) UNCLEAR   — spec is ambiguous. Flag for human review.

    3. Do not modify checkout_service.py.
    4. Return the corrected test file.
Command:      python -m pytest test_checkout_v3_spec_anchored.py -v
Artifacts:    test_checkout_v3_spec_anchored.py
Result:       4 passed, 7 xfailed
Notes:        All 6 implementation bugs preserved as xfail markers.
              Suite is green + runnable in CI. Each xfail has a
              descriptive reason string documenting the spec violation.
```

---

## Summary Comparison

| Version | Prompt Strategy            | Passed | Failed | XFailed | Bugs Detected |
|---------|----------------------------|--------|--------|---------|---------------|
| V1      | Spec-based (Guideline 1)   | 1      | 9      | 0       | 6 (all found, but suite is red) |
| V2      | Repair loop (Guideline 2)  | 10     | 0      | 0       | 0 (all erased by repair) |
| V3      | Spec-anchored repair (New) | 4      | 0      | 7       | 6 (all preserved as xfail) |
