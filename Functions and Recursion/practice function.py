         # average of 3 number
"""def give_average(a,b,c):
    average=(a+b+c)/3
    print(average)
    return average


a=give_average(5,10,15)   # without print written in function def
print(a)
give_average(5,10,15) # after written print in function def"""

                # print the length of a list.( list is the parameter)
             
"""Cities=["Delhi","Rupnagar","Jaipur","Noida","Bengluru"]  
heroes=["Batman","ironman","Thor","Captain America"]
# print(len(Cities) )      # without  function
def print_len(list):        # function 
    print(len(list))

# print_len(heroes)
# print_len(Cities)   

              # print elements of a list in a single line.abs
                  
def print_list(list):
    for item in list:
         print(item,end=" ")    
         
print_list(Cities) 
print()    # for spacing 
print_list(heroes)"""
       
                     # factorial

"""def cal_fact(n):
    fact=1
    for i in range(1,n+1):
        fact*=i
    print(fact)    
cal_fact(5)
cal_fact(6)"""
                    # currency converter
"""def currency(usd_val):
    inr_value=usd_val*93
    print(usd_val,"$","=",inr_value)
    
currency(5)""" 
                       #  for finding even and odd
"""def checker(num):
    if num%2==0:
        print("even")
    else:
        print("odd")      
        
checker(int(input("write no to find even or odd"))) """
           
                   #  differnce between return and print 
"""def add(a, b):
    total = a + b
    print(total)

x = add(2, 3)
print(x * 10)"""

# def add(a, b):
#     total = a + b
#     return total
# x = add(2, 3)

# print(x * 10)    
              # larger no
"""def larg(a,b):
    if (a<b):
        print(b," is largest no ") 
    else:
        print(a,"is largest no")   
        
larg(5,10)
larg(15,20)"""

              # square of a number
def sq(n):
    num=n*n
    return num
                 
print(sq(5)) 
           
                      
                                     