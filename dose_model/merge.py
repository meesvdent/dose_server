#merge arrays
# par: pass nested list of dicts (k:v, time:value).
# return: merged parts of nested list

class interval():
    def __init__(self, keys, values):
        self.keys = keys
        self.values = values
        self.start = keys[0]
        self.end = keys[len(self.keys)-1]
    def getKeys(self):
        return self.keys
    def getValues(self):
        return self.values
    def getStart(self):
        return self.start
    def getEnd(self):
        return self.end
    def setEnd(self, value):
        self.end = value
        return
        
    
class intervalArray():
    def __init__(self, intervals):
        self.intervals = intervals
    def merge(self):
        if(len(self.intervals) <= 0):
            return
        
        #intitialize stack
        stack = []
        
        #sort array of intervals by start
        sorted(self.intervals, key = lambda interval: interval.start)
        
        stack.append(self.intervals[0])
        
        for x in range(1, len(self.intervals)):
            top = stack[len(stack)-1]
            
            if(top.getEnd() < self.intervals[x].getStart()):
                stack.append(self.intervals[x])
            
            elif(top.getEnd() < self.intervals[x].getEnd()):
                top.setEnd(self.intervals[x].getEnd())
                stack.pop()
                stack.append(top)
        
        print("merged intervals are: ")
        while(len(stack) != 0):
            i = stack.pop()
            print("[" + str(i.getStart()) + ", " + str(i.getEnd()) + "]")
            
        return
            
        
        
int1 = interval([0, 1, 2], [14, 17, 18])
int2 = interval([2, 3, 4], [14, 19, 17])
int3 = interval([4, 5, 6, 7], [20, 18, 21, 10])
int4 = interval([10, 11, 12, 13], [1, 12, 12, 13])

input_arr = [int1, int2, int3, int4]

int_arr = intervalArray(input_arr)
    
int_arr.merge()