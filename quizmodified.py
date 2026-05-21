import multiprocessing
import time


# Helper function that runs in a parallel process to capture user input safely
def get_user_input(shared_response):
    try:
        user_choice = input("Tell me your response (A, B, C, or D): ").upper()
        shared_response.value = user_choice
    except Exception:
        pass  # Gracefully catch interruptions when the main process terminates this worker


if __name__ == "__main__":
    print("        ......Multiple Choice questions......  ")
    questions = [
        {
            "question": "How many countries are members of the UN (United Nations)?",
            "options": {"A": 194, "B": 192, "C": 193, "D": 191},
            "answer": "C",
        },
        {
            "question": "When did India get its independence?",
            "options": {"A": 1948, "B": 1947, "C": 1946, "D": 1945},
            "answer": "B",
        },
        {
            "question": "Where is the Taj Mahal situated?",
            "options": {"A": "Agra", "B": "Mumbai", "C": "Delhi", "D": "Rupnagar"},
            "answer": "A",
        },
        {
            "question": "How many bones are there in an adult human body?",
            "options": {"A": 204, "B": 205, "C": 206, "D": 207},
            "answer": "C",
        },
        {
            "question": "How many countries are known to have deployed thermonuclear (hydrogen) bombs?",
            "options": {"A": 6, "B": 5, "C": 9, "D": 8},
            "answer": "B",
        },
    ]

    wrong = []
    credit = 0

    # We use a multiprocessing Manager to dynamically communicate strings between parallel tracks
    manager = multiprocessing.Manager()

    for q in questions:
        print("\n", q["question"])
        for option, value in q["options"].items():
            print(f"{option}: {value}")

        print("⏰ You have EXACTLY 10 seconds to hit Enter!")

        # Set up a shared string container for the parallel input process to write into
        shared_response = manager.Value(str, "")

        # Create and spin up the separate input process track
        input_process = multiprocessing.Process(
            target=get_user_input, args=(shared_response,)
        )
        input_process.start()

        # Monitor the process for up to 10 seconds max
        input_process.join(timeout=10)

        # Evaluate if the process completed or timed out
        if input_process.is_alive():
            # If it's still alive after 10 seconds, force terminate it!
            input_process.terminate()
            input_process.join()
            print("\n❌ TIME'S UP! You took too long to answer.")
            print("The exact answer is:", q["answer"])
            wrong.append(q["question"])
            wrong.append(
                f"Correct Answer: {q['options'][q['answer']]} (Timed Out)"
            )
        else:
            # The user pressed enter within 10 seconds
            user = shared_response.value

            if user not in ["A", "B", "C", "D"]:
                print("Invalid choice! That counts as incorrect.")
                print("The exact answer is:", q["answer"])
                wrong.append(q["question"])
                wrong.append(q["options"][q["answer"]])
            else:
                if user == q["answer"]:
                    print("You are absolutely right 🎉")
                    credit += 1
                else:
                    print(
                        "You are wrong! The exact answer is:",
                        q["answer"],
                        "-",
                        q["options"][q["answer"]],
                    )
                    wrong.append(q["question"])
                    wrong.append(q["options"][q["answer"]])

    print("\n----------------------------------------")
    print("Your final credit score is:", credit)
    percentage = (credit / len(questions)) * 100
    print(f"Percentage: {percentage:.1f}%")

    if percentage >= 80:
        print("Excellent Performance😎")
    elif percentage >= 60:
        print("Not bad, good work😊")
    else:
        print("Failed, try again😰")

    response = input(
        "\nIf you want to see your mistakes then write 'yes', otherwise say 'no': "
    ).lower()
    if response == "yes":
        print("\n--- Your Mistakes ---")
        for i in range(0, len(wrong), 2):
            print(f"❌ Question: {wrong[i]}")
            print(f"✅ {wrong[i+1]}")
            print("-" * 20)
    else:
        print("Okay, thanks for playing!")