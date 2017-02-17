import bpy,bmesh
from random import random
from mathutils import Vector
#import branch
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#  Variables
#===========================
name = "tree"
size = 15  

offset = Vector((0,0,10))
segment = 0.5
lMagnet = segment * size * 0.01
maxDist = 6
minDist = 1
maxLeafs = 1000
#===========================

def randomVector():
    fi = random() * 2 * math.pi
    th = math.acos(1 - 2 * random())
    x = math.cos(fi) * math.sin(th)
    y = math.sin(fi) * math.sin(th)
    z = math.cos(th)
    v = Vector((x,y,z))
    return v

class Leaf():
    def __init__(self):
        self.pos = randomVector() * size/2 * random() + offset
        self.reached = False
    
    def reached(self):
        self.reached = True
  
class Branch():
    def __init__(self,  parent = None, pos = Vector((0,0,0)), dir = Vector((0,0,1)), len = segment):
        self.pos = pos.copy()
        self.dir = dir.copy()
        self.len = len
        self.childCount = 0
        self.parent = parent
        self.count = 0
        self.totalDir = dir.copy()
        self.weight = 1

    def reset(self):
        self.count = 0
        self.totalDir = self.dir.copy()
#------------------------------------------------------------

    def nextBranch(self):
        pos = self.dir * self.len + self.pos
        return Branch(self, pos, self.totalDir)
  
     
class Tree():
    def __init__(self):
        self.branches = []
        self.leaves = []
        
        for i in range(maxLeafs):      
            leaf = Leaf()
            self.leaves.append(leaf)
              
        self.root = Branch(None)
        self.branches.append(self.root)
        current = self.root
        n = 0
        while (not self.closeEnough(current)):
            self.closeEnough(current)
            trank = current.nextBranch()
            self.branches.append(trank)
            current = trank
            n += 1
            if n > 100:
                break
    
    def closeEnough(self, b):
        for l in self.leaves:
            d = (b.pos - l.pos).length

            if d < maxDist:
                return True
            return False

    def grow(self):
        
        for l in self.leaves:
            lShifted = l
            closest = None
            record = -1
            for b in self.branches: 
                if b.weight != 0:
                    b.weight -= 0.001
                d = (l.pos - b.pos - (b.dir * b.len)).length
                if d < minDist:
                    l.reached = True
                    closest = None
                    break
                elif d > maxDist:
                    pass
                elif closest == None or d <= record:
                    closest = b
                    record = d
                    lS = (lShifted.pos - b.pos) * (lShifted.pos - b.pos).length**-2
                    lShifted.pos -= lS * lMagnet
            if closest != None:
                closest.totalDir += (l.pos - b.pos).normalized()
                closest.count += 1
            l = lShifted
        newBranches = []
        for i in range(len(self.branches) - 1, -1, -1):
            b = self.branches[i]
            if b.count > 0:
                newDir = (b.totalDir/b.count + randomVector() * 0.3).normalized()
                newBranches.append(Branch(b, b.pos + b.dir*b.len, newDir))
                b.reset()
        self.branches += newBranches

        self.leaves = [leaf for leaf in self.leaves if not leaf.reached]


    def draw(self, trankObj, leavesObj):
        self.drawTrank(trankObj)
        self.drawLeafs(leavesObj)
 
    def drawTrank(self,trankObj):
        me = trankObj.data
        trankObj.vertex_groups.new("weight")
        bpy.context.scene.objects.active = trankObj
        bpy.ops.object.mode_set(mode='EDIT')    
        for b in self.branches:
            bm = bmesh.from_edit_mesh(me)
            v1 = bm.verts.new(b.pos)
            v2 = bm.verts.new(b.pos + b.dir * b.len)
            
            bm.edges.new((v1, v2))
            bmesh.update_edit_mesh(trankObj.data)  
        me.update()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.update()
                           
                           
    def drawLeafs(self,leavesObj):
        me = leavesObj.data
        bpy.context.scene.objects.active = leavesObj
        bpy.ops.object.mode_set(mode='EDIT')
        for l in self.leaves:
            bm = bmesh.from_edit_mesh(me)
            v = bm.verts.new(l.pos)
            bmesh.update_edit_mesh(leavesObj.data)
        me.update()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.update()        
                    

def main():
   #Trank object=====================================
    trankMesh = bpy.data.meshes.new("Trank")
    trankObj = bpy.data.objects.new("Trank", trankMesh)
    bpy.context.scene.objects.link(trankObj)
    #Leafs object=====================================    
    leavesMesh = bpy.data.meshes.new("Leafs")
    leavesObj = bpy.data.objects.new("Leafs", leavesMesh)
    bpy.context.scene.objects.link(leavesObj)
    
    tree = Tree()
    n = 0
    while n < 1000 and not len(tree.leaves) == 0:
        tree.grow()
        n += 1
        print(len(tree.leaves))
    print("n ",n)
    
    tree.drawTrank(trankObj)
    tree.drawLeafs(leavesObj)    
              
main()
print("===END===")
