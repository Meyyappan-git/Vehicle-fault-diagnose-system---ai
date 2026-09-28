"""Print the top-1 accuracy on the included illustrative labeled cases."""
from backend.diagnosis import run_diagnosis
from backend.tests.cases import CASES


def main() -> None:
    correct = 0
    for index, (payload, expected) in enumerate(CASES, start=1):
        predicted = run_diagnosis(payload)["top_faults"][0]["fault"]
        passed = predicted == expected
        correct += int(passed)
        print(f"{index:02d}. expected={expected:<44} predicted={predicted:<44} {'OK' if passed else 'MISS'}")
    print(f"Top-1 accuracy: {correct}/{len(CASES)} ({correct / len(CASES):.1%})")


if __name__ == "__main__":
    main()
