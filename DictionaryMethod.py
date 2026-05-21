dic={
    "key":"value",
    "year":2026,
    "learning":[24,45,65],
    12.6:94.5
}
# print(dic.keys())              #for finding all the keys
print(dic.get("year"))          # best for finding all the keys or values 
# print(dic.values())            # for finding all the values
# print(list((dic.keys())))       #type casting keys and values
# print(len(list((dic.keys()))) )
# print(len(dic))                # no of key's
# print(dic.items())               # make them into tuple or  in a groups
# pairs=list(dic.items())           
# print(pairs[0])
dic.update({"city": "delhi"})         # update of dictionary
print(dic)
new_dic={"my name is" :"magarobot" , "age":16}  # if there i use same key of another dictionary then it would not repeat 
dic.update(new_dic)                              # it just update it 
print(dic)