while True:
    # Initial input
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    
    print("\n--- Operations ---")
    print("1: Addition (+)")
    print("2: Subtraction (-)")
    print("3: Multiplication (*)")
    print("4: Division (/)")
    print("5: Remainder (%)")
    print("6: Power (**)")
    print("7: Square Root (of both)")
    
    operation = int(input("Choose operation (1-7): "))
    
    if operation == 1:
        result = a + b
    elif operation == 2:
        result = a - b
    elif operation == 3:
        result = a * b
    elif operation == 4:
        if b != 0:
            result = a / b
        else:
            print("Error: Zero division.")
            continue
    elif operation == 5:
        if b != 0:
            result = a % b
        else:
            print("Error: Zero division.")
            continue
    elif operation == 6:
        result = a ** b
    elif operation == 7:
        print("Square root of", a, "is:", a ** 0.5)
        print("Square root of", b, "is:", b ** 0.5)
        result = a ** 0.5 
    else:
        print("Invalid choice.")
        continue

    print("Current Result:", result)

    while True:
        choice = input("\nPerform more math on this result? (yes/no): ").lower()
        if choice != 'yes':
            break
            
        print("\n1: Add \n 2: Sub \n 3: Mult \n 4: Div \n 5: Rem \n 6: Power \n7: Sq Root")
        op = int(input("Choose operation: "))

        if op == 7:
            result = result ** 0.5
        else:
            new_val = float(input("Enter next number: "))
            if op == 1: result += new_val
            elif op == 2: result -= new_val
            elif op == 3: result *= new_val
            elif op == 4:
                if new_val != 0: result /= new_val
                else: print("Error: Zero division.")
            elif op == 5:
                if new_val != 0: result %= new_val
                else: print("Error: Zero division.")
            elif op == 6:
                result = result ** new_val
            else:
                print("Invalid choice.")
                continue
        
        print("Updated Result:", result)

    if input("\nStart a brand new calculation? (yes/no): ").lower() != 'yes':
        break

print("Goodbye,dude")