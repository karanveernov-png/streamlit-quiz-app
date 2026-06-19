# with open("hello.txt","w")as f:
#     f.write("hi i am karan\n")
#     f.write("hi i am learning python\n")
#     f.write("hi i am using java\n")
#     f.write("i like java\n")
    
# # Waf that replace alll occurrence of "java"with "python"in above file.
# with open("hello.txt","r")as f:
#     data=f.read()
# new_data=data.replace("java","python")
# print(new_data)
# with open("hello.txt","w")as f:
#     f.write(new_data)   
#     # find word'learning' exist or not
# word="learning"
# with open("hello.txt","r")as f:
#     data=f.read() 
# if(word in data):
#     print("found")
# else:
#     print("not found")        
 
#  # find word'learning' in which line  a function if not found print -1
# def check_line():            # let make it a function
#     word="pyw"
#     data=True
#     line=1
#     with open("hello.txt","r")as f:
#         while data:
#             data=f.readline()
#             if(word in data):
#                 print(line)
#                 return
#             line+=1
#     return -1        

# print(check_line()) 

         # from a  file containig number seperated  by comma,print the count of even no
with open("hello.txt","r")as f:
    data=f.read()
    print(data)
    