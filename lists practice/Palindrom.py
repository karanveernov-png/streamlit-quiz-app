list=[1,2,3]                    #[1,2,3,2,1] for palindrome
list2=list.copy() #for copy any list
list2.reverse()
if list==list2:
    print("Palindrome")
else:
    print("no palindrome")    


