---
name: reviewing-code
description: Reviews code for bugs, security issues, performance, readability and maintainability, and returns a structured review with prioritised findings and suggested fixes. Use when the user asks you to review code, check a pull request or diff, give feedback on a script or function, find bugs, or asks "is this code OK?" or "what would you improve?", even if they don't say "code review" explicitly.
---

# Code Review

Review code the way a careful senior engineer would: find what is wrong or risky, explain why it matters, and show how to fix it. The goal is a review the author can act on immediately, not a list of opinions.

## Review process

1. **Understand the intent first.** Work out what the code is meant to do from the context, names, comments and any description the user gave. If the purpose is unclear and it changes the review, ask one short question before reviewing.
2. **Check correctness.** Logic errors, off-by-one errors, wrong conditions, unhandled edge cases (empty input, nulls, zero, very large values, concurrency), incorrect error handling.
3. **Check security.** Injection, unvalidated input, hard-coded secrets, unsafe deserialisation, overly broad permissions, sensitive data in logs.
4. **Check performance.** Unnecessary loops, repeated work, inefficient data structures, N+1 queries, memory growth. Only flag what plausibly matters at the expected scale.
5. **Check readability and maintainability.** Naming, function length, duplication, dead code, magic numbers, missing or misleading comments, consistency with the surrounding code.
6. **Check tests.** Whether the change is tested, and which important cases are missing.

## Depth calibration

Choose how deep to go before you start, because a thorough review of a throwaway script wastes the author's time, and a quick glance at production code can miss what matters. Pick one of three levels from the signals below.

| Level | When to use | What to cover | Output |
|-------|-------------|---------------|--------|
| **Quick check** | Short snippet, prototype, notebook, one-off script, or the user asks for a "quick look" | Correctness and obvious security issues only | Summary, verdict, critical/major findings. Skip minor, suggestions and tests unless important |
| **Standard** | Typical feature code, a normal pull request, no special signals | All six process steps, with proportionate attention | Full template |
| **Deep** | Production or shared libraries, security-sensitive code (auth, payments, user data), financial or numerical calculations, concurrency, or the user asks for a "thorough" or "detailed" review | All six steps in detail, plus edge cases, failure modes, numerical stability, thread safety, and how the code behaves under unexpected input | Full template, with fixes for every critical and major finding and a fuller tests section |

**Signals to weigh:**
- **What the user asked for.** An explicit "quick" or "thorough" always decides the level.
- **Stakes.** The more costly a bug would be (money, data, security, users affected), the deeper the review.
- **Size and complexity.** A few lines rarely need a deep review; a large or intricate change rarely suits a quick one.
- **Maturity.** Prototype and exploratory code deserve lighter scrutiny than code about to be merged or deployed.
- **Author's level.** For a learner, explain more and focus on the most instructive issues. For an experienced engineer, be brief and skip the basics.

**State the level.** Open the review with one line saying which depth you used and why (e.g. "Quick check — short prototype script"), so the author knows what was and wasn't covered and can ask for a deeper pass.

**Escalate when needed.** If a quick check reveals a serious problem (a security hole, a data-corruption risk), say so clearly and recommend a deeper review rather than staying shallow.

## Examples

These show how depth changes the review. They are illustrations of calibration, not templates to copy word for word.

### Example 1 — Quick check

**Input:** "Quick look at this, it's just for a notebook."
```python
def average(values):
    return sum(values) / len(values)
```

**Output:**
~~~markdown
# Code Review — average()
_Depth: Quick check — short notebook helper, user asked for a quick look._

## Summary
Simple helper that returns the mean of a list. Works for normal input but crashes on an empty list.

**Verdict:** Approve with minor changes

## Findings
### 🟠 Major — should fix
**Crash on empty input** — `average()`
- **Issue:** `len(values)` is 0 for an empty list, raising `ZeroDivisionError`.
- **Why it matters:** Any empty filter result upstream will stop the notebook.
- **Fix:**
  ```python
  def average(values):
      if not values:
          return None
      return sum(values) / len(values)
  ```
~~~

### Example 2 — Standard

**Input:** "Can you review this PR function?"
```python
def get_order_totals(orders):
    totals = []
    for order in orders:
        customer = db.get_customer(order.customer_id)
        total = 0
        for item in order.items:
            total = total + item.price * item.qty
        totals.append({"customer": customer.name, "total": total})
    return totals
```

**Output (findings only):**
~~~markdown
_Depth: Standard — typical feature code in a pull request._

### 🟠 Major — should fix
**One database call per order (N+1)** — `get_order_totals()`, Line 4
- **Issue:** `db.get_customer` runs inside the loop, so 1,000 orders means 1,000 queries.
- **Why it matters:** Response time grows linearly with order count and will degrade under load.
- **Fix:** Fetch all customers in one query before the loop.
  ```python
  ids = {o.customer_id for o in orders}
  customers = db.get_customers(ids)  # returns {id: customer}
  ```

### 🟡 Minor — nice to have
- Lines 6–7 — Replace the inner loop with `sum(i.price * i.qty for i in order.items)` for clarity.

## Tests
- Empty `orders` list.
- Order with no items (total should be 0).
- Customer ID that doesn't exist.
~~~

### Example 3 — Deep

**Input:** "Thorough review please, this goes into the billing service."
```python
def monthly_interest(balance, annual_rate):
    return round(balance * annual_rate / 12, 2)
```

**Output (findings only):**
~~~markdown
_Depth: Deep — financial calculation in a production billing service._

### 🔴 Critical — must fix before merging
**Floating-point arithmetic for money** — `monthly_interest()`
- **Issue:** `float` cannot represent most decimal amounts exactly (e.g. 0.1), so results drift by fractions of a cent.
- **Why it matters:** Small errors compound across many accounts and months, causing reconciliation breaks and incorrect customer charges.
- **Fix:**
  ```python
  from decimal import Decimal, ROUND_HALF_EVEN

  def monthly_interest(balance: Decimal, annual_rate: Decimal) -> Decimal:
      interest = balance * annual_rate / Decimal(12)
      return interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
  ```

### 🟠 Major — should fix
**Rounding convention not explicit** — Line 2
- **Issue:** Python's `round()` uses banker's rounding, which may not match the rounding rule in the contract or regulation.
- **Why it matters:** A mismatch with the agreed convention produces disputable charges.
- **Fix:** Set the rounding mode explicitly and confirm it with the business owner.

**No input validation**
- **Issue:** Negative balances, negative rates or a rate passed as 5 instead of 0.05 are silently accepted.
- **Fix:** Validate ranges and document whether `annual_rate` is a decimal or a percentage.

### 💡 Suggestions
- Confirm whether the product uses simple monthly division or a day-count convention (e.g. Actual/365).

## Tests
- Known values checked against a reference calculation to the cent.
- Zero balance, zero rate, very large balance.
- Rounding boundary cases (x.xx5).
~~~

### Example 4 — Escalating from a quick check

**Input:** "Just a quick glance, I'm in a hurry."
```python
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)
```

**Output:**
~~~markdown
_Depth: Quick check requested — escalated: security issue found._

### 🔴 Critical — must fix before merging
**SQL injection** — Line 1
- **Issue:** User input is inserted directly into the SQL string.
- **Why it matters:** An attacker can read or delete any data in the database.
- **Fix:** Use a parameterised query.
  ```python
  cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
  ```

I kept this a quick check as asked, but I'd recommend a deeper review of anywhere else user input reaches the database.
~~~

## Output format

Use this structure. If a section has nothing in it, write "None found" rather than removing it.

~~~markdown
# Code Review — [File, PR or component name]

## Summary
[2–3 sentences: what the code does, overall quality, and the verdict.]

**Verdict:** [Approve | Approve with minor changes | Changes requested]

## Findings

### 🔴 Critical — must fix before merging
**[Short title]** — `[file]`, Line [N]
- **Issue:** [What is wrong.]
- **Why it matters:** [Impact: bug, data loss, security risk, outage.]
- **Fix:**
  ```[language]
  [Corrected code]
  ```

### 🟠 Major — should fix
**[Short title]** — `[file]`, Line [N]
- **Issue:** [...]
- **Why it matters:** [...]
- **Fix:** [Code or clear description.]

### 🟡 Minor — nice to have
- `[file]`, Line [N] — [Issue and suggested change in one or two lines.]

### 💡 Suggestions
- [Optional improvements, alternative approaches, refactoring ideas.]

## Positives
- [What is done well and should be kept.]

## Tests
- [Missing test cases worth adding.]

## Next steps
1. [Ordered list of what the author should do, highest priority first.]
~~~

## Severity guide

- **Critical:** causes incorrect results, crashes, data loss, or a security vulnerability. Blocks merging.
- **Major:** likely to cause bugs later, significant performance problems, or seriously hurts maintainability.
- **Minor:** style, naming, small clarity improvements. Does not block merging.
- **Suggestion:** optional ideas the author can take or leave.

## Terminology

Use these terms consistently so reviews read the same every time and readers don't wonder whether two words mean two things.

- **"Parameterised query"**, not "prepared statement" or "binding", when describing the fix for SQL built from user input.
- **"Error handling"**, not "exception handling", unless the point is specifically about exceptions (e.g. a bare `except:` or a swallowed exception).
- **"Line N"** to give a location (e.g. "Line 12"), not "here" or "this line", so the author can find it without guessing.

## Guidelines

**Prioritise.** Put the most serious issues first and keep severity honest. If everything is marked critical, nothing is, and the author can't tell where to start.

**Explain the why.** Every critical and major finding states its impact. "This fails when the list is empty because index 0 doesn't exist" is useful; "this is bad" is not.

**Show the fix.** For critical and major issues, give corrected code, kept minimal and in the same style as the original. The author should be able to apply it directly.

**Be specific.** Point to the file and Line N, or the exact function. Quote the problematic line when it helps.

**Stay faithful to the code.** Only report problems you can see in the code provided. If something depends on code you haven't seen (a called function, a config, a schema), say so as an assumption rather than presenting it as a defect.

**Respect the existing style.** Follow the conventions already used in the codebase (naming, formatting, patterns) rather than imposing your own preferences. Don't flag pure style choices as defects unless they hurt readability.

**Don't nitpick at the expense of substance.** If there are critical issues, keep the minor list short so the important points aren't buried.

**Be constructive.** Review the code, not the author. Always include genuine positives, since knowing what to keep is as useful as knowing what to change.

**Group related findings.** For a large change, group findings by file or theme so the review stays scannable.