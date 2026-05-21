# using loop

"""n=int(input("enter the no:"))
fact=1
for i in range(1,n+1):   # working: fact variable stores every value and used them for next to multiplication
    fact*=i
print("factorial of ",n,"is",fact)"""

# using recursion
def fact(n):
    if ( n==0 or n==1):
        return 1
    return fact(n-1)*n
print(fact(5) )
    