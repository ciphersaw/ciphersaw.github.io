# Python 3.6
import requests
import re

url = 'http://120.24.86.145:8002/qiumingshan/'
s = requests.Session()
source = s.get(url)

# Method1: Use the split() of string object.
# expression = source.text.split('<div>')[1].split('=?')[0]

# Method2: Use re.search() of regular expression module (re).
expression = re.search(r'(\d+[+\-*])+(\d+)', source.text).group()

# Solution1: Use Python Built-in Function eval().
result = eval(expression)

# Solution2: Divide the numbers and operators respectively, then calculate the operations one by one.
# number = re.split('\D', expression)
# operator = re.split('\d+',expression)[1:11]

# for i in range(len(number)):
# 	number[i] = int(number[i])

# while len(operator) > 0:
# 	if len(operator) > 1 and operator[1] == '*':
# 		number[1] = number[1] * number[2]
# 		number.pop(2)
# 		operator.pop(1)
# 	else:
# 		if operator[0] == '+':
# 			number[0] = number[0] + number[1]
# 		elif operator[0] == '-':
# 			number[0] = number[0] - number[1]
# 		elif operator[0] == '*':
# 			number[0] = number[0] * number[1]
# 		number.pop(1)
# 		operator.pop(0)

# result = number[0]

# The flag is not out when the length of result is too long.
# print(result) 

post = {'value': result}
print(s.post(url, data = post).text)