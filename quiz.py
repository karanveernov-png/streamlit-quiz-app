import time
import threading
import sys

print(" ......Multiple Choice questions...... ")

questions = [
    {
        "question": "How many countries are members of UN (United Nations)?",
        "options": {"A": 194, "B": 192, "C": 193, "D": 191},
        "answer": "C"
    },
    {
        "question": "When did India get its independence?",
        "options": {"A": 1948, "B": 1947, "C": 1946, "D": 1945},
        "answer": "B"
    },
    {
        "question": "Where is the Taj Mahal situated?",
        "options": {"A": "Agra", "B": "Mumbai", "C": "Delhi", "D": "Rupnagar"},
        "answer": "A"
    },
    {
        "question": "How many bones are in a human body?",
        "options": {"A": 204, "B": 205, "C": 206, "D": 207},
        "answer": "C"
    },
    {
        "question": "How many countries have a hydrogen bomb?",
        "options": {"A": 6, "B": 5, "C": 9, "D": 8},
        "answer": "A"
    }
]


def timed_input(timeout=10):
    """
    Shows a live countdown (10, 9, 8 ...) while waiting for user input.
    Returns (user_answer, timed_out).
    """
    answer = [None]
    done = threading.Event()

    # Thread 1: waits for user to type and press Enter
    def read_input():
        answer[0] = sys.stdin.readline().strip().upper()
        done.set()

    input_thread = threading.Thread(target=read_input, daemon=True)
    input_thread.start()

    # Thread 2 (main): shows live countdown
    for remaining in range(timeout, 0, -1):
        if done.is_set():
            break
        # \r moves cursor back to start of line so numbers overwrite each other
        print(f"\r⏰ Time remaining: {remaining}s  ", end="", flush=True)
        done.wait(1)  # wait 1 second OR until user answers

    print()  # move to new line after countdown ends

    if not done.is_set():
        return None, True   # timed out
    return answer[0], False


# ── Main quiz loop ──────────────────────────────────────────────

wrong = []
credit = 0

for i, q in enumerate(questions, 1):
    print(f"\nQ{i}: {q['question']}")
    for key, value in q["options"].items():
        print(f"   {key} : {value}")

    print("Tell me your response: ", end="", flush=True)

    user, timed_out = timed_input(timeout=10)

    # ── Timeout ──
    if timed_out:
        print("⏰ Time's up! Moving to next question.")
        wrong.extend([
            "⏰ Skipped (timeout):", q["question"],
            "Correct answer:", f"{q['answer']} : {q['options'][q['answer']]}"
        ])
        continue

    # ── Invalid option ──
    if user not in ["A", "B", "C", "D"]:
        print(f"❌ Invalid option! Correct answer was: {q['answer']} : {q['options'][q['answer']]}")
        wrong.extend([
            "❌ Invalid input:", q["question"],
            "Correct answer:", f"{q['answer']} : {q['options'][q['answer']]}"
        ])

    # ── Correct ──
    elif user == q["answer"]:
        print("✅ Absolutely right!")
        credit += 1

    # ── Wrong ──
    else:
        print(f"❌ Wrong! Correct answer: {q['answer']} : {q['options'][q['answer']]}")
        wrong.extend([
            "❌ Wrong:", q["question"],
            "Correct answer:", f"{q['answer']} : {q['options'][q['answer']]}"
        ])

# ── Results ────────────────────────────────────────────────────

print("\n" + "=" * 35)
print(f"  Your score : {credit} / {len(questions)}")
percentage = (credit / len(questions)) * 100
print(f"  Percentage : {percentage:.1f}%")

if percentage >= 80:
    print("  Excellent Performance 😎")
elif percentage >= 60:
    print("  Not bad, good work 😊")
else:
    print("  Failed, try again 😰")
print("=" * 35)

if wrong:
    response = input("\nWant to review your mistakes? (yes/no): ").lower()
    if response == "yes":
        print("\n====== YOUR MISTAKES ======\n")
        for line in wrong:
            print(line)
    else:
        print("Okay, thanks! Keep practising.")
else:
    print("\n🎉 Perfect score — no mistakes to review!")