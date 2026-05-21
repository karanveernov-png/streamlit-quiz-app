while True:
    a = int(input("Enter first number: "))
    b = int(input("Enter second number: "))
    print("1: Addition\n2: Subtraction\n3: Multiplication\n4: Division\n5: Remainder")
    operation=int(input("Choose operation (1-5): "))
    if operation==1:
        result=a+b
    elif operation==2:
        result=a-b
    elif operation==3:
        result=a*b
    elif operation==4:
        if b!=0:
             result=a / b 
        else:
            print("you press zero no.")   
    elif operation == 5:
        if b != 0: 
            result = a % b 
        else:
            print("Error (Div by 0)" )   
    else:
        print("Invalid choice.")
        continue

    print("Current Result:", result)

    while True:
        choice = input("\nDo you want to perform a further calculation on this result? (yes/no): ").lower()
        if choice != 'yes':
            break
            
        new_element = int(input("Enter next number: "))
        print("\n1: Addition\n2: Subtraction\n3: Multiplication\n4: Division\n5: Remainder")
        op = int(input("Choose operation: "))

        if op == 1: result += new_element
        elif op == 2: result -= new_element
        elif op == 3: result *= new_element
        elif op == 4:
            if new_element!=0:
             result/= new_element
            else:
                print("you press zero no.")   
        elif operation == 5:
             if new_element != 0: 
                 result%=new_element
             else:
                
                 print("Error (Div by 0)" )   
        else:
             print("Invalid choice.")
             continue
        
        print("Updated Result:", result)

    if input("\nStart a brand new calculation? (yes/no): ").lower() != 'yes':
        break

print("The calculator has stopped.")