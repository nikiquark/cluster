from models import Point, Status

data = [(left, right) for left in [5.4, 5.5, 5.6] for right in [5.4, 5.5, 5.6]]
for left, right in data:
    point = Point(l=left, r=right, status=Status.PENDING)
    point.save()
