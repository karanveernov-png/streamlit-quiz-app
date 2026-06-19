# print mumbers from 1 to 100
# i=1
# while i<=100:
#     print(i)
#     i+=1
# # Print 100 to 1
# i=100
# while i>=1:
#     print(i)
#     i-=1    
# # Print multiplication table of number n
# n=int(input("enter the no:",))
# i=1
# while i<=10:
#     print(n*i)
#     i+=1
# #print this
# #nums=[1,4,9,25,36,49,64,81,100]     
#  Way-1
# nums=[]
# i=1
# while i<=10:
#     nums.append(i*i)
#     i+=1
# print(nums)   
# search any no in tupples using loops
# nums=(1,4,9,16,25,36,49,64,81,100)
t=(1,4,9,16,25,36,49,64,81,100)
i=0
x=int(input("Tell me which no you want to check:",))
while i<len(t):
    if(t[i]==x):
        print("yes,found at:",i) 
    else:
        print("not found")         # it's working but still have an issue

    i+=1        

