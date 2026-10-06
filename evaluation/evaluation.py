import csv

from .evaluation_cases import EVALUATION_CASES
from .evaluation_runner import (
    run_react,
    run_plan_execute,
    run_hybrid
)


AGENTS = [
    ("ReAct", run_react),
    ("Plan-then-Execute", run_plan_execute),
    ("Hybrid", run_hybrid)
]


results = []


for case in EVALUATION_CASES:

    print("\n========================================")
    print("CASE:", case["name"])
    print("========================================")

    for agent_name, runner in AGENTS:

        print(f"\nRunning {agent_name}...")

        result = runner(case)

        results.append(result)

        print(result)


fieldnames = [
    "case",
    "agent",
    "expected_success",
    "task_completed",
    "behavior_correct",
    "permission_ok",
    "booking_code",
    "selected_flight_id",
    "final_status",
    "replan_count",
    "latency_seconds"
]


with open(
    "evaluation_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print("\n========================================")
print("Evaluation completed.")
print("Results saved to evaluation_results.csv")
print("========================================")