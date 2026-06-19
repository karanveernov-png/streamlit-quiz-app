print("        ......Multiple Choice questions......  ")
questions=[
    {
        "question":"how many counteries are the members of UN(United Nations) ?",
        "options":{ 
             "A": 194,
             "B": 192, 
             "C": 193,
             "D": 191 
             },
        "answer":"A" 
    },
    {   "question":"when was India got its independence ?",
        "options":{
             "A" : 1948,
             "B" : 1947,
             "C" : 1946,
             "D" : 1945
             },
        "answer":"B"
    },
    {
        "question":"where is The Taj Mahal situated?",
        "options":{ 
             "A" :"Agra",
             "B" :"Mumbai" ,
             "C" :"Delhi",
             "D" : "Rupnagar",
             },
        "answer":"A"
    },
    {
        "question":"Tell me how many bones in a human being?",
        "options":{
             "A":204,
             "B": 205,
             "C":206,
             "D": 207 
             },
        "answer":"C"
    },
    {
        "question":"how many countries have hydrogen bomb?",
        "options":{
              "A": 6,
             "B": 5,
             "C": 9,
             "D": 8
             },
        "answer":"A"
    }
]
wrong=[]
credit=0
for q in questions:
    print("\n",q["question"])
    print(q["options"])
    user=input("tellme your response:").upper()
    if user not in ["A","B","C","D"]:
        print("enter the correct options") 
        print("you are wrong,and exact answer is",q["answer"]) 
        wrong.append(q["question"]) 
        wrong.append(q["options"][q["answer"]])
    else:
        if user==q["answer"]:
            print("you are absolutely right")
            credit+=1
        else:
            print("you are wrong,and exact answer is",q["answer"],q["options"][q["answer"]]) 
            wrong.append(q["question"]) 
            wrong.append(q["options"][q["answer"]])
print("your credit score is:",credit)
percentage=(credit/len(questions))*100
print("percentage:",percentage)
if percentage>=80:
    print("Excellent Performance😎")
elif percentage>=60:
    print("not bad,good work😊")
else:
    print("failed ,try again😰")        
response=input("if you want to see your mistakes then write yes or otherwise say no:").lower()
if response =='yes'  :
    for w in wrong:
        print(w)
    print("thanks")    
else:
    print("okay,thanks")