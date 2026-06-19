                 #  Function
""" Block of stament that perform a specific taslk.
inputs are also called parameter
# It decerease redundancy (lines of codes written again and again)
   def func_name(parameter 1,parameter2...):      <- # function definiton  
        # some work
          return value
                 # when we want you the function after writtnig the above we se function call
                     as shown below and whatever value we want to store we write in the form of argument
           funct_name(arg1,arg2..)# function call """
# Ex
"""def calc_sum(a,b):
    sum=a+b
    print(sum)
    return sum   
calc_sum(5,10)           # a= 5, b= 10

calc_sum(2,10)           # a=2,b=10"""
# better way 
# the following are called function definition
"""def calc_sum(a,b):  # parameter
    return a+b


sum = calc_sum(1,2) # function call; arguments
print(sum)"""
# def print_hello():
#     print("hello")
    
# print_hello()    
# print_hello()    
# print_hello()    
# print_hello()    
# output = print_hello()    
# print(output)   # none becuase the function does not give return value
                 
                 # types of funtions
"""# 1. Built-in Functions      # already defined functions
#.............. print()................
print("hi",) # sep=""
print("hello") # end="\n"
             # or for same line with space
print("hi", end=" # ") # sep=""
print("hello") # end="\n"
#...............len()..................
#...............type()..................
#...............range().................."""
# 2. User defined Function
"""        #  3. default parameters
 # Assigning a default value to parameter, which is used when no argument is passed.
# ex =>   
 def cal_prod(a,b):
     print(a*b)
     return a*b

cal_prod()                           # it gives an error
 to handle it we used a deafult value of a and b
def cal_prod(a=1,b=1):                # a=1 and b=1 is default value
    print(a * b)
    return a * b
cal_prod() """
