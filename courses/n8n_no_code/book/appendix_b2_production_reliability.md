# [Production Reliability](appendix_b2_production_reliability): Production Reliability

*[Going Live](appendix_b_going_live) (Going Live)* got your workflow onto a server. This one keeps it **trustworthy** once real traffic, flaky APIs, and impatient users hit it. None of it is exotic — it's a handful of settings and habits that separate a demo from something you'd let touch a customer's money or calendar.

The theme: **hope is not a strategy.** A workflow *will* be called twice, an API *will* return an error, and two people *will* click at the same second. Reliability is deciding — in advance — what happens when they do.

**Workflow in this appendix:**

| File | What it does | GitHub Link |
|------|-------------|-------------|
| `23_reliability_drills.json` | An HTTP call with Retry + Timeout whose failure routes to a **Stop And Error** node (a real hard stop) | [View](https://github.com/ezponda/ai-agents-course/blob/main/courses/n8n_no_code/book/_static/workflows/23_reliability_drills.json) |

> **Import via URL:**
> ```
> https://raw.githubusercontent.com/ezponda/ai-agents-course/main/courses/n8n_no_code/book/_static/workflows/23_reliability_drills.json
> ```
>
> **Download:** {download}`23_reliability_drills.json <_static/workflows/23_reliability_drills.json>`

---

## Retries, timeouts, and rate limits

Every node has a **Settings** tab with reliability controls. For anything that calls the outside world (HTTP Request, an email node, a Data Table write), these matter:

| Setting | What it does | Good default |
|---|---|---|
| **Retry On Fail** | Automatically re-runs the node if it errors | On, for API calls |
| **Max Tries** | How many attempts before giving up | 3 |
| **Wait Between Tries** | A delay before retrying (**back-off**) so you don't hammer a struggling API | 1–5 seconds |
| **Timeout** (in Options) | Give up on a hung request instead of freezing forever | 10–30 s |
| **On Error** | Stop the workflow, continue on the normal output, or continue on a separate **error output** | Depends — see fail open/closed |

### HTTP 429 and `Retry-After`

A `429 Too Many Requests` means you're calling an API faster than it allows (its **rate limit**). It often replies with a `Retry-After` header — *"wait N seconds"*. The right response is not to retry instantly (that makes it worse) but to **back off**: wait, then try again. In n8n:

- **Retry On Fail + Wait Between Tries** on the node — the simple version. **Note:** this waits a **fixed delay you configure** (e.g. 2s); it does **not** automatically read the API's `Retry-After` header.
- **Batching** ([Working with Multiple Items](03b_working_with_multiple_items)) — process items in small groups with a **Wait** node between them, so you never burst past the limit in the first place.

```{note}
**Honouring `Retry-After` is a separate pattern.** To wait *exactly* as long as the API asks, you must **read the `Retry-After` value** off the response (or the error) and feed that number into a **Wait** node — n8n's built-in Retry On Fail can't do this on its own. Reach for the dynamic version only when an API returns `Retry-After` and you need to respect it precisely.
```

### Which errors to retry — and which not to

| Error | Retry? | Why |
|---|---|---|
| `429`, `500`, `503`, timeout | **Yes** | **Transient** — the same request may succeed moments later |
| `400` bad request, `422` validation | **No** | The request itself is wrong — retrying sends the same broken thing |
| `401` / `403` auth/permission | **No** | Fix the credential or permissions; retrying won't help |

```{warning}
**Never auto-retry a validation or permission failure.** A rejected refund shouldn't be retried until it "works" — that's not a glitch, it's the system correctly saying *no*. Retries are for *transient* faults only.
```

---

## Fail open vs. fail closed

When a step fails, you have two choices, and picking the wrong one is a real bug:

| | **Fail open** (continue anyway) | **Fail closed** (stop / deny) |
|---|---|---|
| **Meaning** | The failure is non-critical — proceed without it | The failure is critical — do **not** proceed |
| **Use for** | *Optional enrichment*: a "nice-to-have" lookup, an analytics ping, a weather add-on | *Security & correctness*: authentication, authorisation, payment, availability, policy checks |
| **In n8n** | *On Error → Continue* (skip the bad step) | *On Error → Stop Workflow*, or route the error output to a hard stop |

Ask: *if this step fails and we continue, what's the worst outcome?* If it's "the reply is slightly less rich" → fail open. If it's "we booked an unavailable slot" or "we skipped the permission check" → **fail closed**, every time.

```{note}
**The drill workflow shows a *real* fail-closed.** In `23_reliability_drills.json`, the API node's **error output** feeds a **Stop And Error** node, so a failure makes the whole execution **fail** — not a workflow that finishes 'green' while quietly returning `{status: "failed"}`. The URL is set to `https://httpbin.org/status/503`, so it actually fails: run it and watch the **retry attempts**, the **wait between them**, the **error output**, and the final **Stop And Error** (the execution ends in a *failed* state). Change the URL to `https://httpbin.org/get` to see the success path instead. Open the node's **Settings** to see Retry On Fail, Max Tries, Wait Between Tries, and *On Error → Continue (error output)*.
```

---

## Duplicate webhooks, idempotency, and partial failures

These three are the same underlying problem: **a thing runs more than once, or runs half-way.** They cause the scariest bugs — duplicate charges, double bookings, two identical emails.

### Duplicate webhooks
Webhook providers (Stripe, Telegram, calendar apps) will sometimes deliver the **same event twice** — by design, so nothing is ever lost. If your workflow logs an expense or sends an email on each delivery, one real event becomes two. You must make repeat deliveries **harmless**.

### Idempotency — the fix, done right
*Idempotent* means: running it twice has the same effect as running it once. The **wrong** way to attempt this is *"check if the record exists, and if not, write it"* — because between your check and your write, the **duplicate** can slip in and both pass the check. An in-memory list or a plain Data Table look-up **is not** safe against this.

```{warning}
**A Data Table "check-then-write" is not production idempotency.** It looks safe and works in a demo, but two simultaneous runs can both read "not there yet" and both write. Real idempotency needs an **atomic** mechanism — one indivisible operation the datastore guarantees:

- a **provider-supported idempotency key** (e.g. Stripe's `Idempotency-Key` header — send the same key twice, it charges once);
- a **database unique constraint** (a duplicate write is rejected by the database, not by your check);
- an **atomic upsert** (insert-or-do-nothing in a single operation);
- a **queue or single serialised writer** (only one write happens at a time);
- a **transactionally stored operation id**.

The common idea: give each real operation a **stable id** (order id + action, the webhook's event id) and let the *datastore* enforce "once" — not a prompt, and not a two-step check in your workflow.
```

### Partial failure — the sneaky one
The nastiest case: **the external action succeeds, but your workflow fails before recording it.** The email *was* sent; the booking *was* made — but the row saying so never got written. On the next run you send/book again. Guard the **irreversible** step: do it as late as possible, give it an idempotency key, and record success as close to the action as you can. When in doubt, prefer *"might not record a success that happened"* (safe: you can reconcile) over *"might repeat an action"* (dangerous: double charge).

---

## Race conditions

A **race condition** is two runs competing for the same thing at the same instant — the double-booking the *Salon Booking* project ([Salon Booking Assistant](project_7_salon_booking_assistant)) flagged, and the same risk in the `book_appointment` sub-workflow ([Reliable Tools and Sub-workflows](07b_reliable_tools_and_subworkflows)). Both *check* the slot is free, both see "free", both *write* — now it's booked twice.

You cannot fix this in the prompt (*"never double-book"* is a wish, not a guarantee) and you cannot fix it with a check-then-write. The fix lives in the **data layer**, and it's the same toolkit as idempotency:

- a **unique constraint** on (date, time, resource) so the *second* insert simply fails;
- a **single serialised writer** or queue so writes never overlap;
- an **atomic reserve** operation.

```{important}
**This is why [Reliable Tools and Sub-workflows](07b_reliable_tools_and_subworkflows)'s booking workflow is labelled "educational".** Its ownership check and validation are correct and important — but making the *write* safe against a simultaneous second booking needs a database guarantee, not more workflow nodes. Know the boundary: n8n orchestrates; the datastore enforces "exactly once".
```

---

## Failure drills

Reliability sticks when you *feel* the failure. Run these five thought-drills against your own workflows — for each, ask *"what happens today, and what should happen?"*

**Drill 1 — the doubled webhook.** Your booking webhook fires **twice** for one request. *Today:* two bookings? *Should:* the second is a no-op. *Fix:* an idempotency key / unique constraint on the event id.

**Drill 2 — the 429.** An API you call returns `429 Too Many Requests` mid-run. *Today:* the run dies? *Should:* back off and retry (a fixed Wait Between Tries, or read `Retry-After` into a Wait node), or batch so it never bursts. *Fix:* Retry On Fail + Wait Between Tries, or batching.

**Drill 3 — the partial failure.** The email **sends**, then the *"log it as sent"* step crashes. *Today:* next run emails again? *Should:* no duplicate. *Fix:* idempotency key on the send; record success next to the action.

**Drill 4 — the tie.** Two customers book the **same slot** in the same second. *Today:* both succeed? *Should:* one wins, one is told it's taken. *Fix:* a unique constraint / atomic reserve in the datastore.

**Drill 5 — the optional add-on.** A "nice-to-have" enrichment API (e.g. a weather lookup) is **down**. *Today:* the whole workflow fails? *Should:* skip it and continue. *Fix:* **fail open** — *On Error → Continue* on that one node.

Notice drills 1–4 **fail closed** (a wrong outcome is worse than stopping) and drill 5 **fails open** (a missing extra is fine). Sorting your steps into those two buckets is 80% of production reliability.

---

## Keeping workflows maintainable

Reliability isn't only run-time — it's also *"can a human still understand and fix this in six months?"* A short operational checklist, no DevOps required:

| Habit | Why it matters |
|---|---|
| **Clear names** | `Book Appointment (prod)` beats `My workflow 3` — you'll thank yourself at 2am |
| **Tags & folders** | Group by project/owner so workflows don't become a junk drawer |
| **Sticky Notes** | Document *inside* the canvas: what it does, inputs, side effects, expected failures |
| **Ownership** | One named person responsible per workflow — no orphans |
| **One responsibility** | One workflow = one job; reuse logic via sub-workflows ([Reliable Tools and Sub-workflows](07b_reliable_tools_and_subworkflows)) |
| **Credential reuse** | One shared credential, not a copy pasted into ten nodes |
| **Dev vs. prod** | Test on a draft/instance separate from the live one ([Going Live](appendix_b_going_live)) |
| **Version history** | n8n keeps past versions — you can roll back a bad change |
| **Export & backup** | Periodically export workflow JSON (as this course ships them) so you can restore |
| **Clean up** | Delete dead workflows and unused credentials — less to break, less to leak |

```{tip}
**Document the contract, not just the nodes.** For any workflow others depend on, a Sticky Note that states its **inputs, outputs, side effects, and expected failures** is worth more than the prettiest diagram. It's the difference between "reusable" and "nobody dares touch it".
```

---

## Summary

| Concept | What you learned |
|---------|------------------|
| **Retry + back-off** | Auto-retry *transient* errors with a delay; not validation/permission errors |
| **429 / Retry-After** | Slow down and respect the rate limit; batch to avoid bursts |
| **Timeouts** | Don't let a hung API freeze the workflow |
| **Fail open vs. closed** | Optional enrichment fails open; security/payment/availability fail closed |
| **Duplicate webhooks / idempotency** | Make repeats harmless with an **atomic** mechanism, not check-then-write |
| **Partial failure** | Guard the irreversible step; prefer reconcile over repeat |
| **Race conditions** | Fix in the data layer (unique constraint / serialised writer), never the prompt |
| **Maintainability** | Names, tags, sticky notes, ownership, versions, backups |

**Key ideas:**
- Decide **in advance** what happens when a step fails — that decision *is* reliability.
- **Prompts don't solve concurrency or idempotency** — the datastore does.
- Critical writes need **atomic** protection: idempotency key, unique constraint, upsert, or a queue.

**Docs:**
- [Error handling](https://docs.n8n.io/flow-logic/error-handling/)
- [HTTP Request pagination](https://docs.n8n.io/code/cookbook/http-node/pagination/)
- [Wait node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/)
- [Workflow settings](https://docs.n8n.io/workflows/settings/)
