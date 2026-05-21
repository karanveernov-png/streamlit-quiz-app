
name=input("enter your name:")
print("Welcome,",name)
pas=input("Tell me password")
has_digit=False
has_upper=False
has_lower=False
for ch in pas:
    if ch .isdigit():
        has_digit=True
    if ch. isupper():
        has_upper=True
    if ch. islower():
        has_lower=True    
if len(pas)>=8 and has_upper and has_lower and has_digit:
    print(" strong passwords ",name)
elif len(pas)>=6:
    print(" medium password")
else:
    print("weak password")        
