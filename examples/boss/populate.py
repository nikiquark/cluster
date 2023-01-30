from models import Point, Status
import numpy as np
from controller import print_success
# r = 3
# xs0 = np.arange(5.5 - 2, 5.5 + 2, 0.5)
# xs1 = np.arange(5.5 - 3, 5.5 + 3, 0.5)
# xsl = np.arange(4.5-0.3, 4.5+0.5, 0.2)
xsl = np.arange(3.0, 8.0, 0.5)

# data0 = [(left, right) for left in xs0 for right in xs0]
# data1 = [(l, r) for l in xs1 for r in xs1]
# data = list(set(data1) - set(data0))
# data = sorted(data, key = lambda x:abs(x[0]-5.5)*10 + (abs(x[1]-5.5)))
data = [(l, 2.5) for l in xsl if l!=5.5]
print(len(data))
for left, right in data:
    left = float(f"{left:.5f}")
    right = float(f"{right:.5f}")

    Point.create(l=left, r=right, status=Status.PENDING)
    print_success(f"{left} - {right}")
#print(data)
