

class Avg:
    """ Represents a collections of numbers.
    Why? Because using tuples isn't as expressive. """
    def __init__(self, sum_=0, count=0):
        self.sum = sum_
        self.count = count

    def add(self, n):
        self.sum += n
        self.count += 1
    
    def avg(self):
        return self.sum / self.count

    def __str__(self):
        return "avg: " + str(self.avg())
    
    def __repr__(self):
        return "[avg {}]".format(self.avg())


