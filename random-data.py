import random
import datetime
import os

words = open('/usr/share/dict/words').readlines()
names = open('/usr/share/dict/propernames').readlines()
connectives = open('/usr/share/dict/connectives').readlines()
severities = [0, 1, 2, 3, 4, 5, 6, 7]

# DATA='{ "severity": 0, "datetime": "1330676432", "long_desc": "This is my long description", "short_desc": "Shortdesc" }'

short_desc = "%s %s %s %s %s" % (
        random.choice(names).strip(),
        random.choice(connectives).strip(),
        random.choice(words).strip(),
        random.choice(connectives).strip(),
        random.choice(names).strip())
long_desc = short_desc.split(" ") * 50
random.shuffle(long_desc)
long_desc = " ".join(long_desc)
severity = random.choice(severities)
date_time = datetime.datetime.now().strftime("%s")

data = "{ 'severity': %s, 'datetime': '%s', 'long_desc': '%s', 'short_desc': '%s' }" % ( severity, date_time, long_desc, short_desc )

data = data.replace("'", "\"")

print "./example-curl.sh '%s'" % data
