from __future__ import annotations

import json
from eval.reference import TICKET_EXPECTATIONS
from question1.agent import SupportCopilot
from question2.agent import SupportPipeline
from shared.billing import CostSession

ALL_TICKETS = ["T-1001", "T-1002", "T-1003", "T-1004", "T-1091"]
PUBLIC_TICKETS = ["T-1001", "T-1002", "T-1003", "T-1004"]


def run_q1_diagnostics():
    print("=" * 80)
    print("QUESTION 1 (SupportCopilot) — PER-CALL DIAGNOSTIC REPORT")
    print("=" * 80)
    grand_total = 0
    for tid in ALL_TICKETS:
        session = CostSession()
        copilot = SupportCopilot(session=session)
        res = copilot.handle_ticket(tid)
        exp = TICKET_EXPECTATIONS[tid]
        match = (res.action == exp.action and res.kb_article == exp.kb_article)
        total_pts = session.total_points()
        if tid in PUBLIC_TICKETS:
            grand_total += total_pts

        print(f"\nTicket {tid}:")
        print(f"  Decision: {res.action} (Expected: {exp.action}) | Match: {match}")
        print(f"  KB Article: {res.kb_article} (Expected: {exp.kb_article})")
        print(f"  Total Ticket Points: {total_pts}")

        for i, c in enumerate(session.calls, 1):
            cached = min(c.cached_prefix_tokens, c.input_tokens)
            uncached = c.input_tokens - cached
            print(f"  Call {i} [{c.label}]:")
            print(f"    Input tokens:          {c.input_tokens}")
            print(f"    Cached input tokens:   {cached}")
            print(f"    Uncached input tokens: {uncached}")
            print(f"    Output tokens:         {c.output_tokens}")
            print(f"    Call Points:           {c.points()}")

    print(f"\nQ1 Public Tickets Total Points: {grand_total}")
    print(f"Q1 Public Tickets Average Points: {grand_total / len(PUBLIC_TICKETS):.2f}")


def run_q2_diagnostics():
    print("\n" + "=" * 80)
    print("QUESTION 2 (SupportPipeline) — PER-CALL DIAGNOSTIC REPORT")
    print("=" * 80)
    grand_total = 0
    for tid in ALL_TICKETS:
        session = CostSession()
        pipe = SupportPipeline(session=session)
        res = pipe.handle_ticket(tid)
        exp = TICKET_EXPECTATIONS[tid]
        match = (res.action == exp.action and res.kb_article == exp.kb_article)
        total_pts = session.total_points()
        if tid in PUBLIC_TICKETS:
            grand_total += total_pts

        print(f"\nTicket {tid}:")
        print(f"  Decision: {res.action} (Expected: {exp.action}) | Match: {match}")
        print(f"  KB Article: {res.kb_article} (Expected: {exp.kb_article})")
        print(f"  Total Ticket Points: {total_pts}")

        for i, c in enumerate(session.calls, 1):
            cached = min(c.cached_prefix_tokens, c.input_tokens)
            uncached = c.input_tokens - cached
            print(f"  Call {i} [{c.label}]:")
            print(f"    Input tokens:          {c.input_tokens}")
            print(f"    Cached input tokens:   {cached}")
            print(f"    Uncached input tokens: {uncached}")
            print(f"    Output tokens:         {c.output_tokens}")
            print(f"    Call Points:           {c.points()}")

    print(f"\nQ2 Public Tickets Total Points: {grand_total}")
    print(f"Q2 Public Tickets Average Points: {grand_total / len(PUBLIC_TICKETS):.2f}")


if __name__ == "__main__":
    run_q1_diagnostics()
    run_q2_diagnostics()
