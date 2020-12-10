import re

dict={
    '2020-11-14 13:45:40':'abc',
    '2020-11-14 15:08:00':'abb',
    '2020-11-14 15:08:55':'abbb',
    '2020-11-14 13:05:40': 'abd',
    '2020-11-14 15:07:00': 'abdd',
    '2020-11-14 15:09:55': 'adccd',
    '2020-11-14 15:09:56': 'abccd'
}

flag="abc"+".*?"
regex_start = re.compile(flag)
for k,v in dict.items():
    print(k)
    print(v)
    print(re.match(regex_start, v))



