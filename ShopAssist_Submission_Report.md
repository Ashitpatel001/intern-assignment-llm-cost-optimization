# ShopAssist LLM Cost Optimization
## Implementation and Evaluation Report

**Candidate:** Ashit Patel  
**Repository:** [Ashitpatel001/intern-assignment-llm-cost-optimization](https://github.com/Ashitpatel001/intern-assignment-llm-cost-optimization)  
**Evaluation date:** 17 November 2026

---

## 1. Overview

This report describes the changes made to the ShopAssist support agents for Question 1 (single-call copilot) and Question 2 (four-stage pipeline). The main objective was to reduce simulator billing while keeping the required ticket decisions, knowledge-base article selections, and response format intact.

The optimized implementations were evaluated against the four public tickets (T-1001 to T-1004) and the T-1091 holdout regression ticket. On these test cases, both implementations returned the expected action and knowledge-base article. The average cost for the public tickets was **1,681.50 points for Q1** and **2,339.25 points for Q2**, meeting the respective limits.

| Track | Baseline average | Optimized average | Target | Reduction |
|---|---:|---:|---:|---:|
| Q1 – Single-call agent | 8,865.00 | **1,681.50** | ≤ 3,000 | 81.0% |
| Q2 – Four-stage pipeline | 73,286.25 | **2,339.25** | ≤ 2,500 | 96.8% |

The averages above are calculated over the four public tickets only. T-1091 is reported separately as a holdout regression check.

## 2. Approach

### 2.1 Question 1: Single-call agent

The original Q1 prompt included a run-specific UUID, few-shot examples, the complete knowledge base, and instructions that encouraged lengthy reasoning and article quotations. The UUID also made the prompt less stable between runs.

The revised implementation makes the following changes:

- Removed the random UUID from the system prompt.
- Removed the few-shot examples from the active prompt.
- Replaced verbose reasoning instructions with a direct JSON output requirement.
- Kept all five knowledge-base articles in the prompt. In this assignment, the complete article set is small enough to include without adding a retrieval stage.
- Preserved the complete `ORDER_SNAPSHOT` block and its existing JSON serialization.

The agent still makes one LLM call and returns the same `TicketResolution` structure. The main saving comes from reducing the completion length, with additional savings from removing unnecessary prompt content.

### 2.2 Question 2: Four-stage pipeline

The original pipeline used an LLM call at each of its four stages and passed large amounts of help-centre content and repeated context between stages. The measured baseline was approximately 73,000 points per ticket.

The revised implementation keeps the four stages but moves triage and retrieval to deterministic Python logic:

1. **Triage (`_triage`)** – extracts relevant terms and order facts from the ticket thread and order metadata.
2. **Retrieval (`_retrieve`)** – scores the available policy summaries using relevant keywords and selects the top one or two matches.
3. **Compose (`_compose`)** – makes the first LLM call to draft the resolution.
4. **Audit (`_audit`)** – makes the second LLM call to check the draft against the order snapshot and retrieved policy evidence.

This keeps the four-stage structure while reducing the number of LLM calls from four to two. It also avoids sending the expanded help-centre content through multiple stages. Both LLM calls retain the complete order snapshot.

The policy summaries are maintained in `_POLICY_SUMMARIES` and mapped to the corresponding files in `data/kb/`. This is a deliberate trade-off: it keeps runtime retrieval small and predictable, but the summaries need to be updated if the source policies change.

## 3. Cost evaluation

The simulator billing formula is:

`points = uncached_input_tokens × 3 + cached_input_tokens × 0.3 + output_tokens × 15`

The following figures are measured results from the local simulator. The baseline figures are from the unoptimized implementation; optimized figures are from the revised agents.

### 3.1 Question 1

| Ticket | Baseline points | Optimized points | Reduction |
|---|---:|---:|---:|
| T-1001 | 8,847 | 1,803 | 79.6% |
| T-1002 | 8,979 | 1,680 | 81.3% |
| T-1003 | 8,718 | 1,641 | 81.2% |
| T-1004 | 8,916 | 1,602 | 82.0% |
| **Public-ticket average** | **8,865.00** | **1,681.50** | **81.0%** |
| T-1091 – holdout | 8,760 | 1,653 | 81.1% |

All four public tickets are below the 3,000-point limit. The holdout ticket was also processed successfully and is included here as a regression check, not in the public-ticket average.

### 3.2 Question 2

| Ticket | Baseline points | Optimized points | Reduction |
|---|---:|---:|---:|
| T-1001 | 73,290 | 2,469 | 96.6% |
| T-1002 | 73,299 | 2,343 | 96.8% |
| T-1003 | 73,014 | 2,319 | 96.8% |
| T-1004 | 73,542 | 2,226 | 97.0% |
| **Public-ticket average** | **73,286.25** | **2,339.25** | **96.8%** |
| T-1091 – holdout | 73,656 | 2,346 | 96.8% |

All four public tickets are below the 2,500-point limit. T-1001 is the closest to the limit, with 31 points of headroom, so changes to the Q2 prompts should be tested carefully.

### 3.3 Per-call breakdown

The optimized Q1 agent makes one call per ticket. Q2 makes two calls per ticket: `compose` and `audit`.

**Q1 – optimized calls**

| Ticket | Input tokens | Cached input | Output tokens | Total points |
|---|---:|---:|---:|---:|
| T-1001 | 371 | 0 | 46 | 1,803 |
| T-1002 | 365 | 0 | 39 | 1,680 |
| T-1003 | 352 | 0 | 39 | 1,641 |
| T-1004 | 354 | 0 | 36 | 1,602 |
| T-1091 | 361 | 0 | 38 | 1,653 |

**Q2 – optimized calls**

| Ticket | Compose input / output | Compose points | Audit input / output | Audit points | Ticket total |
|---|---:|---:|---:|---:|---:|
| T-1001 | 179 / 46 | 1,227 | 184 / 46 | 1,242 | **2,469** |
| T-1002 | 192 / 39 | 1,161 | 199 / 39 | 1,182 | **2,343** |
| T-1003 | 182 / 39 | 1,131 | 201 / 39 | 1,188 | **2,319** |
| T-1004 | 184 / 36 | 1,092 | 198 / 36 | 1,134 | **2,226** |
| T-1091 | 192 / 38 | 1,146 | 210 / 38 | 1,200 | **2,346** |

Cached input is zero for all measured calls. The simulator's cache threshold is 1,024 tokens, and the prompts did not meet that threshold. No cache savings have been assumed.

## 4. Correctness and regression checks

The expected action and knowledge-base article were returned for each of the five tested tickets in both tracks.

| Ticket | Expected action | Selected article | Result |
|---|---|---|---|
| T-1001 | `REFUND` | `returns-within-30-days` | Pass |
| T-1002 | `SEND_ARTICLE` | `digital-license-no-refund` | Pass |
| T-1003 | `ESCALATE_TIER2` | `custom-items-no-replace` | Pass |
| T-1004 | `REPLACE` | `damage-replacement-7-days` | Pass |
| T-1091 | `SEND_ARTICLE` | `subscription-cooling-off` | Pass |

These outcomes were observed in both Q1 and Q2. They demonstrate that the tested public scenarios and the supplied holdout case continued to resolve correctly; they should not be interpreted as a guarantee of accuracy on unseen tickets.

The Q2 audit stage was also checked with two deliberately incorrect drafts:

- For T-1001, a draft proposing `REPLACE` with `damage-replacement-7-days` was corrected to `REFUND` with `returns-within-30-days`.
- For T-1003, a draft proposing `REFUND` with `returns-within-30-days` was corrected to `ESCALATE_TIER2` with `custom-items-no-replace`.

These checks provide examples of the audit stage detecting incorrect draft decisions against the supplied order and policy evidence.

## 5. Test execution

The full test suite was run with:

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

**Result:** 6 passed, 0 failed, 0 skipped.

The run completed in approximately 13 minutes. Pytest displayed a cache warning because it could not write to the `.pytest_cache` directory; this did not affect the test results.

The Q1 and Q2 runner scripts were also executed. Their outputs matched the expected actions and article IDs for T-1001 through T-1004, and their public-ticket average costs were within the required limits.

## 6. Implementation notes and trade-offs

- **Deterministic triage and retrieval:** These stages use Python rather than LLM calls. This reduces inference cost and makes their behaviour easier to inspect, while preserving the four named pipeline stages.
- **Policy summary maintenance:** Q2 uses compact summaries associated with the five existing KB article IDs. These summaries are maintained in code rather than generated dynamically from the Markdown files, so they must be reviewed when the source policies are edited.
- **Concise model output:** The prompts ask for the required structured response without requesting lengthy reasoning or quotations. The action, article ID, and customer reply fields remain part of the output contract.
- **Order snapshot preservation:** The complete `ORDER_SNAPSHOT` block remains in the LLM request, as required by the simulator contract.
- **Caching:** No cached-token benefit is claimed because the measured calls did not reach the configured cache-prefix threshold.

## 7. Files changed

The implementation changes are in:

- `question1/agent.py`
- `question2/agent.py`
- `tests/test_question1.py`
- `tests/test_question2.py`

The report and supporting implementation notes are included separately in the repository. The shared simulator, billing implementation, evaluation logic, and input data were not modified, according to the final implementation review.

## 8. Conclusion

Both optimized agents meet their respective cost limits on the four public tickets. Q1 reduces average cost from 8,865.00 to 1,681.50 points per ticket, while Q2 reduces it from 73,286.25 to 2,339.25 points per ticket. The tested decisions and article selections also match the expected results, including the T-1091 holdout case.

The main changes were prompt simplification in Q1 and deterministic triage/retrieval combined with two LLM calls in Q2. The Q2 result has limited headroom on T-1001, so the current prompts should be kept stable unless any future change is followed by a full cost and correctness check.
