   # factorial by using recursion
   # n!=n*(n-1)!
   #(n-1)!=(n-1)*(n-2)! and soo on
   
"""def fact(n):
    if (n==1 or n==0):
        return 1
    return  n * fact(n-1)
    
print(fact(5)) """
   
   # sum of n natural numbers
"""def sum(n): 
    if n==0:
        return n    
    return sum(n-1)+n
# cal_sum= sum(8)
# print(cal_sum)
print(sum(8))"""
  
       # write all the elments in a list using list and idx as parameter
def ele_list(list,idx=0):
    if idx==len(list):
        return  
    print(list[idx])
    return ele_list(list,idx+1)
          
cal=[45,12,63,85,75]  
ele_list(cal) 

     