"""
Mr. Box: practice box-sorting script

The MIT License:

Copyright (c) 2017 Deives Collins

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import tkinter, math

class Box:
    """ Class for representing and manipulating box data """
    def __init__(self, dim1, dim2, dim3):
        self.l = dim1
        self.w = dim2
        self.h = dim3

        self.bases = [ (self.l,self.w),
                       (self.l,self.h),
                       (self.w,self.h) ]

    def __repr__(self):
        return '(L:'+str(self.l)+',W:'+str(self.w)+',H:'+str(self.h)+')'

    def __lt__(self,other):
        return self.l < other.l

    def __gt__(self,other):
        return self.l > other.l

    def __le__(self,other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self,other):
        return self.__gt__(other) or self.__eq__(other)

    def rotateToBase(self,base):
        """ Reorder the values of the box to reflect the dimensions of the box
            when rotated to the given valid base """
        dims = [self.l,self.w,self.h]
        for dim in base:
            if dim in dims:
                dims.remove(dim)
        self.h = dims[0]
        self.l,self.w = base[0],base[1]

class Tracker:
    """ Class for tracking progress of iteratated tasks"""
    alignment = 40
    
    def __init__(self, total, text):
        self.count, self.percentage = 0, 0
        self.total, self.text = total, text
        self.progressBar()

    def incr(self):
        self.count += 1
        if int((self.count/self.total)*100) != self.percentage:
            self.percentage = int((self.count/self.total)*100)
            if self.percentage%5 == 0:
                self.progressBar()

    def progressBar(self):
        """ Display an updating progress bar reflecting the ratio current/total """
        steps = int(self.percentage/5)

        bar = '[' + '='*(steps) + '>' + ' '*(20-steps) + '] ' + '%02d'%self.percentage + '%'
        if self.count > 0:
            print('\b'*len(bar),end='',flush=True)
            if self.percentage == 100:
                print(' ',end='',flush=True)
        else:
            print(self.text,end=' ',flush=True)
            print(' '*(Tracker.alignment-(len(self.text)+1)),end='',flush=True)
        print(bar,end=(lambda x: '' if x < 100 else '\n')(self.percentage),flush=True)

def genBoxCombos(boxes):
    """ Generate all possible combinations of all possible lengths
        of the given set of boxes (independent of order) """
    def binaries(length, tracker):
        """ Generate binary sequence possibilities for given length """
        if length == 1:
            tracker.incr()
            return([0],[1])
        else:
            combos = []
            for combo in binaries(length-1, tracker):
                         # Recursive call
                for bit in ([0],[1]):
                    tracker.incr()
                    combos.append(bit+combo)
            return combos
        
    total = 1
    for x in range(len(boxes),1,-1):
        total += math.pow(2,x)
    tracker = Tracker(total, "Generating combination sequences:")
    bins = binaries(len(boxes),tracker)

    # Populate list of box combinations from binary sequences
    tracker = Tracker(len(bins),"Populating box combinations:")
    combos = []
    for sequence in bins:
        combo = [y for y in
                     map((lambda x: boxes[x[0]] if x[1] else None),
                         enumerate(sequence))
                 if y]
        combos.append(combo)
        tracker.incr()
        
    return combos
    
def genBaseHierarchy(boxes):
    """ Return:
            1. [ (l,w), (l,w), ... ]
               list of all bases (regardless of parent box) as tuples in
               descending order of area (l*w)
            2. { (l,w): { box:height } }
               dict, by base keys, of sub-dicts, by box keys, with heights
               corresponding to the vertical dimension of the given box
               with the given base """

    hierarchy = []
    for box in boxes:
        for base in box.bases:
            if not base in hierarchy:
                hierarchy.append(base)
    hierarchy.sort(key = lambda x: x[0]*x[1])

    baseDict = {}
    for base in hierarchy:
        heightDict = {}
        for box in boxes:
            if base in box.bases or (base[1],base[0]) in box.bases:
                box.rotateToBase(base)
                heightDict[box] = box.h
        baseDict[base] = heightDict

    return hierarchy, baseDict

def ruleCheck(baseCombo):
    """ Compare a list of base combinations for validity according to rule:
        length(baseA) > length(baseB) and width(baseA) > width(baseB);
        
        If the list does not satisfy the rule as given but does after
        horizontal rotation of one or more bases, the list is returned
        with these bases rotated """
    if len(baseCombo) <= 1:
        return True

    changed = False
    for index in range(len(baseCombo)-1):
        if not (baseCombo[index][0] > baseCombo[index+1][0] and
                baseCombo[index][1] > baseCombo[index+1][1]):

            # Try the base pair with the upper-most base rotated horizontally
            baseCombo[index+1] = (baseCombo[index+1][1],baseCombo[index+1][0])
            
            if (baseCombo[index][0] > baseCombo[index+1][0] and
                baseCombo[index][1] > baseCombo[index+1][1]):
                
                changed = True
            
            else:
                return False
            
    if changed:
        return baseCombo # Return corrected list
    else:
        return True

def stack(boxes):
    """ Determine the tallest stack of given boxes possible while satisfying
        ruleCheck() and output appropriately ordered and rotated boxes """    
    boxCombos = genBoxCombos(boxes)
    hierarchy, baseDict = genBaseHierarchy(boxes)
    tracker = Tracker(len(boxCombos),"Evaluating stacks:")
    
    tallest, maxHeight = [],0
    for combo in boxCombos:
        stack = []
        for base in hierarchy:
            if len(combo) > 0:
                boxChoice, boxHeight = 0, 0
                for box in combo:
                    if box in baseDict[base]:
                        if baseDict[base][box] > boxHeight:
                            boxChoice, boxHeight = box, baseDict[base][box]
                if boxChoice:
                    combo.remove(boxChoice)
                    stack.append((boxChoice,base,boxHeight))
                
        stack.reverse()
        validate = ruleCheck([x[1] for x in stack])
        if validate:
            if type(validate) == list:
                # Update corrected values from ruleCheck()
                for index in range(len(validate)):
                    stack[index] = (stack[index][0],validate[index],stack[index][2])

            stackHeight = 0
            for boxInfo in stack:
                stackHeight += boxInfo[2]
            if stackHeight > maxHeight:
                tallest, maxHeight = stack, stackHeight

        tracker.incr()
            
    final = [x[0] for x in tallest]
    for index in range(len(final)):
        box = final[index]
        base = tallest[index][1]
        box.rotateToBase(base)

    return final

def display(boxes):
    """ Display the solution stack in a tkinter window """
    window = tkinter.Tk()
    window.title("Mr. Box Graphical Output")
    bgcol, linecol, textcol = "#000050", "#FFFFFF", "#00FF00"
    canvas = tkinter.Canvas(window, width=800, height=600,bg=bgcol)
    canvas.pack()

    bottomTransform = boxes[0].l*math.sin(0.4) + boxes[0].w*math.sin(0.4)
    height = bottomTransform
    for box in boxes:
        height += box.h
    scale = 500/height
    center, stackHeight = 799/2, 550-bottomTransform*scale
    
    for box in boxes:
        lenTransform = ( box.l*scale*math.cos(0.4),
                         box.l*scale*math.sin(0.4) )
        widTransform = ( box.w*scale*math.cos(0.4),
                         box.w*scale*math.sin(0.4) )
        hgtTransform = box.h*scale

        origin = (center,stackHeight)

        # Lower
        activePoint = (origin[0]+lenTransform[0],origin[1]+lenTransform[1])
        endPoint = (activePoint[0]-widTransform[0],activePoint[1]+widTransform[1])
        textPoint = (activePoint[0]-widTransform[0]/2,activePoint[1]+widTransform[1]/2)
        canvas.create_line(activePoint,endPoint,fill=linecol)
        canvas.create_text(textPoint,text='\n'+str(box.w),fill=textcol)

        activePoint = (origin[0]-widTransform[0],origin[1]+widTransform[1])
        endPoint = (activePoint[0]+lenTransform[0],activePoint[1]+lenTransform[1])
        textPoint = (activePoint[0]+lenTransform[0]/2,activePoint[1]+lenTransform[1]/2)
        canvas.create_line(activePoint,endPoint,fill=linecol)
        canvas.create_text(textPoint,text='\n'+str(box.l),fill=textcol)
        textPoint = (activePoint[0]-5,activePoint[1]-hgtTransform/2)
        canvas.create_text(textPoint,text='  '+str(box.h),fill=textcol,anchor='e')
        

        # Upper
        activePoint = (origin[0],origin[1]-hgtTransform)
        endPoint = (activePoint[0]+lenTransform[0],activePoint[1]+lenTransform[1])
        canvas.create_line(activePoint,endPoint,fill=linecol)

        stackHeight = activePoint[1]
        
        activePoint = endPoint
        endPoint = (activePoint[0]-widTransform[0],activePoint[1]+widTransform[1])
        canvas.create_line(activePoint,endPoint,fill=linecol)
        canvas.create_line(activePoint,activePoint[0],activePoint[1]+hgtTransform,
                           fill=linecol)

        activePoint = endPoint
        endPoint = (activePoint[0]-lenTransform[0],activePoint[1]-lenTransform[1])
        textPoint = (origin[0],activePoint[1]+hgtTransform/2)
        canvas.create_line(activePoint,endPoint,fill=linecol)
        canvas.create_line(activePoint,activePoint[0],activePoint[1]+hgtTransform,
                           fill=linecol)
        
        activePoint = endPoint
        endPoint = (origin[0],origin[1]-hgtTransform)
        canvas.create_line(activePoint,endPoint,fill=linecol)
        canvas.create_line(activePoint,activePoint[0],activePoint[1]+hgtTransform,
                           fill=linecol)

    height = height-bottomTransform
    if height % 1 == 0:
        height = int(height)
    canvas.create_text(center,585,text="Total Height: "+str(height),fill=textcol,font=("TkDefaultFont",16))
    
    window.mainloop()

def main():
    print("""
####
#  #
######    MR. BOX:
#    #
########      The friendly box-stacking proof-of-concept script
#      #         2017 Deives Collins
######## \n""")

    print("Mr. Box is a practice program designed to solve the following problem:\n")

    print("Objective:  Find the tallest possible stack given a set of boxes\n")
    
    print("Constraint: Box A can only be stacked on top of Box B if both")
    print("            the length and width of Box B are larger than the")
    print("            length and width of Box A\n")

    print("Mr. Box will now request information about the set of boxes you wish")
    print("to use for the problem.\n")

    count = ''
    while not count.isnumeric():
        print("How many boxes will be in the set?")
        print("# of boxes:",end=' ')
        count = input()
        print("")
        if not count.isnumeric():
            print("Error:")
            print("# of boxes must be entered in numeric characters (1,2,3, ...) only\n")
    count = int(count)

    boxes = []
    for index in range(0,count):
        dims = ['','','']
        while not ( (type(dims[0]) == int or type(dims[0]) == float) and
                    (type(dims[1]) == int or type(dims[1]) == float) and
                    (type(dims[2]) == int or type(dims[2]) == float) ):
            print("For box "+str(index+1)+" of "+str(count)+":\n")
            print("Enter the length:",end=' ')
            dims[0] = input()
            print("           width:",end=' ')
            dims[1] = input()
            print("          height:",end=' ')
            dims[2] = input()
            print("")
            
            for idx in range(3):
                if dims[idx].isnumeric():
                    dims[idx] = int(dims[idx])
                elif '.' in dims[idx]:
                    fl = dims[idx]
                    if fl[:fl.index('.')].isnumeric() and \
                       fl[fl.index('.')+1:].isnumeric():
                        dims[idx] = float(fl)
                else:
                    print("Error:")
                    print("Dimensions must be entered in numeric characters (1,2,3, ...)")
                    print("and (optionally) a maximum of 1 decimal point\n")

        boxes.append(Box(dims[0],dims[1],dims[2]))

    print("Mr. Box will now irreversibly change your life.\n")

    boxes = stack(boxes)
    display(boxes)

if __name__ == "__main__":
    main()
        
