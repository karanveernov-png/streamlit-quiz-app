aboutme=["karan",18,"ropar",1990.72]
# print(aboutme)
# aboutme[3]="Sir"
# print(aboutme)
# print(aboutme[-2])
print(18 in aboutme)                # to check that a element present in a list or not
# """list is immutable
#                i.e Every element of list can be changed
#                                                   but string can't do that"""

# print(len(aboutme))
#                                   # List slicing start here :
# """list _name[starting_idx:ending_idx]
#                                ending idx is not included 
#                                            the followings are the ways to use slicing"""
# print(aboutme[1:3])            #  #[starting : ending values:step(forward(0)or backward(-1))]
# print(aboutme[0:])
# print(aboutme[:3])
# print(aboutme[:])
#                                  # negative slicing
# print(aboutme[-4:])
print(aboutme[::-1])        # # revserse the list without changing original(sorting)             

# # List Methods
# aboutme=[24,35,67]
# aboutme.append(45)                       # adds one element at the end 
# print(aboutme)
# aboutme.extend([3,4])                    #adding multiple items at the end
# print(aboutme)
# aboutme.sort()                          #sort in ascending orders 
# print(aboutme)
# aboutme.sort(reverse=True)              # in descending order
# print(aboutme) 
#                     """only similar data types 
#                                          in alphabtes it uses alphabatically order"""
# aboutme=["a","d","v","g"]
# aboutme.sort()
# print(aboutme) 
# aboutme.reverse()            #reverses the list
# print(aboutme) 
# aboutme.insert(3,46)          #Insert at any index
# print(aboutme) 
# aboutme=[2,1,3,1]
# aboutme.remove(1)               #removes first occurrence of element
# print(aboutme) 
# aboutme.pop(2)              #remove element at idx
# print(aboutme) 



