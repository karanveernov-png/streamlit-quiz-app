#                         #........Lists........
#   #Answer-1          
# a=[10,20,30,40,50]
# a[0]=0
# a[4]=0
# print(a)  
# # Answer-2  
# a.insert(2,100) 
# print(a) 
# # Answer-3  
# a.remove(40)
# print(a)
# # Answer-4       
# print(a[1:3])
# # Answer-5
# print(25 in a ) 
#                          #.......Tuples......
# t=(5,10,15,20)       
# # answer-6
# print(t[3])  
# #Answer -7
# print(10 in t) 
# # Answer-8
# l=list(t)
# l.remove(15)
# print(l)
# # Answer-9
# print(t[0:3])
#                           #.......Sets........
# s={1,2,3,4} 
# # answer-10 
# s.add(5) 
# #answer-11
# s.remove(2)       
# print(s)   
# answer-12
# a={1,2,3}
# b={3,4,5}
# print(a.union(b))
# # answer-13
# c=a.intersection(b)
# print(c)
# # answer-14
# way-1
# print(6 in s)
# # way-2
# if(6 in s):
#     print("yes")
# else:
#     print("no")  
  
#                             # .....Dictionary.......
# d={
#     "name":"Karanveer singh",
#     "Age": 18
#  } 
#  # Answer-16
# d["City"]="Delhi"  
# print(d)          
# #Answer-17             
# d["Age"]=25
# print(d)   
# # Answer-18
# print("keys" in (d.keys()))
# # Answer-19
# d.pop("name")
# print(d)

#                       #.....Mixed_Logic.....

# # Answer-20                    
# a=[10,20,30]
# if(20 in a):
#     a.insert(1,200)
# else:
#     print("not exist")  
# print(a) 
# # Answer-21
# d={
#     "marks":80
# }   
# if("marks" in d):
#     d["marks"]=90
# else:
#      print("not exist")   
# print(d)  
# #Answer-22
# s={10,20,30}
# if(40 in s):
#     print("yes")
# else:
#     s.add(40)
# print(s)            
# #Answer-23
# t=(1,2,3)
# S=list(t)
# S.append(4)
# t=tuple(S)
# print(t)
# a = [10, 20, 30, 40]

# # If 30 exists:
# # remove it and add 300 at same position
# if(30 in a):
#     index=a.index(30)
#     a[index]=300
# else:
#     print("not")
# print(a)        
# a = [10, 20, 30, 40, 30]
# Replace ONLY first occurrence of 30 with 300
# if(30 in a):
#     a.sort(reverse=True)
#     index=a.index((30))
#     a[index]=300
#     a.sort()
# else:
#     print("notexist")
# print(a)
# print(a[::-1])      
# if(30 in a):
#     b=a[::-1]
#     index=b.index(30)
#     b[index]=300
#     a=b[::-1]
#     print(a)
# else:
#     print("nope")