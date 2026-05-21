# Fibinacci:> it is a number of series in which each number is made by previous two numbers addition
# n=(n-1)+(n-2)
# like 5=4+3
         # ......using loop.......
print(".........Fibinacci........")         
n=int(input("write here any no to find  fibinacci"))
a=0
b=1
for i in range(n,0,-1):
    print(a,end=" ")
    c=a+b
    a=b
    b=c
