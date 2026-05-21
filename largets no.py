a=int(input("enter 1st no:"))
b=int(input("enter 2nd no:"))
c=int(input("enter 3rd no:"))
# Largest=max(a,b,c)                   # ctrl+/=comment any text
# print("largest no is",Largest )


                                   # 2nd way for finding largest no without max()

if a<=b & b>=c:
        print("The largest no is b:",b)  
elif a>=c:
     print("The largest no is a:",a)
else:
     print("The largest no is c:",c)                           