# The 'r' tells Python to ignore backslashes
# f = open("input_output/FR.PY", "r")

# data=f.read(5)     # you can also add any paramter like(5),or let it default()
# data=f.readline()    # reads one line at a time 
# print(data)
# line2=f.readline()
# print(line2)


# f.close()              # Always remember to close your files!
              
               # writing 
                      
# f = open("input_output/FR.PY", "w")
# f.write("this is new line.1234")   #overwrite the entire files

# f = open("input_output/FR.PY", "a")      # here a is adds to the file or append into the file  at the end   
# f.write("\n this is new line")
# f = open("hi.txt", "a")              # writing and adding any file ,if file does not exist like this then python automatically created that file
# f.write("\n this is new line")  
# f = open("hi.txt", "r+")    # for overwriting in starting
# f.write("aaaaabc")
# print(f.read())
# f.close()
# f = open("hi.txt", "w+")   # the file is in trunkated mode, all data is erased
# print(f.read())
# f.close() 

# 'r+' read + overwrite the existing data, pointer is in starting mode (no truncate)
# 'w+'read+overwrite  no truncate
# 'a+'read + append (pointer end) no truncate
                    # with syntax
with open("hi.txt","r") as f:              # with this syntax we doesnot need to close the file like before 
    data = f.read()
    print(data)
    
with open("hi.txt","w") as f:              # overwrite the data
    f.write("new data")