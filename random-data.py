import random
import datetime
import os

words = open('/usr/share/dict/words').readlines()
names = open('/usr/share/dict/words').readlines()
connectives = open('/usr/share/dict/words').readlines()
severities = [0, 1, 2, 3, 4, 5, 6, 7]

# DATA='{ "severity": 0, "timestamp": "1330676432", "long_desc": "This is my long description", "short_desc": "Shortdesc" }'

short_desc = "%s %s %s %s %s" % (
        random.choice(names).strip(),
        random.choice(connectives).strip(),
        random.choice(words).strip(),
        random.choice(connectives).strip(),
        random.choice(names).strip())
short_desc = short_desc.replace("'", "")
long_desc = short_desc.split(" ") * 50
random.shuffle(long_desc)
long_desc = " ".join(long_desc)
severity = random.choice(severities)
timestamp = datetime.datetime.now().strftime("%s")

data = "{ 'severity': %s, 'timestamp': '%s', 'long_desc': '%s', 'short_desc': '%s' }" % ( severity, timestamp, long_desc, short_desc )

data = data.replace("'", "\"")

print "./example-curl.sh '%s'" % data
