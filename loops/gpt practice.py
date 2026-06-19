# 1. printfrom number 1to 10 using for loop
"""for i in range(1,11):
    print(i)"""
# 2. print 10 to 1 using while loop
"""i=10
while i>=1:
    print(i)
    i-=1    """
# 3. print all even from 1 to20
# for even 
"""for i in range(0,21,2):
    print(i)  """  
# for odd
"""for i in range(1,21,2):
    print(i)   """
# 4.print the following elements
"""a=[10,20,30,40]      
for i in a:
    print(i)"""
# 5. sum of the following element
"""a=[5,10,15]
sum=0
for i in a:
    sum=sum+i
print("sum is",sum)  """
# 6. how many no greater than 20
"""a=[10,25,30,5,40]
number=0
for i in a:
    if(i>20):
        number+=1
print(number) """
# 7. find maximum
"""largest=a[0] 
for i in a:
    if(largest < i):
        largest=i
print(largest)"""      
# 8. reverse a list
"""a=[10,20,30,40]
for i  in range(len(a)-1,0,-1):
        print(a[i])"""
# 9. how many times 10 repeats
"""a=[10,20,30,10,40,10,50,10]
repeat=0
for i in a:
    if(10==i):
        repeat+=1
print(repeat)  """
#10. remove all occurance of 20
"""a=[10,20,30,40,20,50]
for i in a:
    if(20==i):
        a.remove(20)
print(a) """ 
# 11. create a new list only of even another for odd
a=[1,20,30,15,6,7,8,10]
"""even=[]
odd=[]
for i in a:
    if(i%2==0):
        even.append(i)
    else:
        odd.append(i)    
print(even)
print(odd)"""
#find the 2nd largest no
largest=a[0]
second_largest=a[0]
for i in a:
    if(largest<i and max(a)):
        largest=i
        prin
print(largest)  
     
        
 
