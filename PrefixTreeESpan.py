"""
File: PrefixTreeESpan.py
Author: jiaqi
E-mail: jiaqi97@pku.edu.cn
Created: 2018-12-21
Description:
    Implementation of PrefixTreeESpan
    A Frequent Subtree Mining Algorithm

Copyrgiht (c) 2018 by jiaqi. All rights reserved.
"""

from optparse import OptionParser
from time import time


class Node:
    """Node in a tree

    Attributes:
        label: the label of the node
        range_end: range in string represented tree
    """
    def __init__(self, label=""):
        self.label = label
        self.range_end = -1


class Tree:
    """class of tree

    Attributes:
        nodes: the collection of nodes
    """
    def __init__(self,root):
        self.nodes = [root]
    
    def add(self,node):
        self.nodes.append(node)

class Project:
    """class of Project

    Attributes:
        tree_id: id of the tree in the tree_list
        start_index_list: start_index for each subset of projection database
        end_index_list: corresponding end_index for each offset
    """
    def __init__(self, tree_id):
        self.tree_id = tree_id
        self.start_index_list = []
        self.end_index_list = []
    
    def add(self, s, e):
        self.start_index_list.append(s)
        self.end_index_list.append(e)


class PrefixTreeESpan:
    """
    implemention of PrefixTreeESpan algorithm 
    
    Attributes:
        in_path : path of input file
        out_path : path of output file
        min_propotion : the min propotion of frequent prefix subtree in all trees

        tree_list : list of all input trees
        fre_pre_tree : list of frequent prefix subtree
        min_support : min support
        length_one_patterns : store the frequent patterns of length 1

        t_start : start time of program
        t_stop : end time of program

    """
    def __init__(self, in_path, out_path, min_propotion):
        self.in_path = in_path
        self.out_path = out_path
        self.min_propotion = min_propotion

        self.tree_list = []
        self.fre_pre_tree = []
        self.min_support = -1
        self.length_one_patterns = {}

        self.t_start = None
        self.t_stop = None
        
    
    def read_tree(self):
        with open(self.in_path, "r") as f:
            for line in f.readlines():
                l = line.strip().split(' ')
                root = Node(l[0])
                stack = [(root, 0)]
                ptr = 1
                tree = Tree(root)
                while stack:
                    node = Node(l[ptr])
                    if node.label == '-1':
                        stack[-1][0].range_end = ptr
                        stack.pop()
                    else:
                        stack.append((node, ptr))
                    tree.add(node)
                    ptr += 1
                self.tree_list.append(tree)

                labels = set([(_node.label, 0) for _node in tree.nodes if _node.label != '-1'])
                for pattern in labels:
                    if pattern not in self.length_one_patterns:
                        self.length_one_patterns[pattern] = 0
                    self.length_one_patterns[pattern] += 1

        self.min_support = int(self.min_propotion * float(len(self.tree_list)))
        print ("%d input trees." % (len(self.tree_list)))
        print ("min_support: ", self.min_support)
        

    def get_fre(self, pre_tree, n, proj_db):
        """
        Get n+1 order frequent subtree according to
        prefix tree and projection database
        """
        pattern_dict = {}
        for proj in proj_db:
            tree = self.tree_list[proj.tree_id]
            for i in range(len(proj.start_index_list)):
                for j in range(proj.start_index_list[i], proj.end_index_list[i]):
                    if tree.nodes[j].label != '-1':
                        patt = (tree.nodes[j].label, i+1)
                        if patt not in pattern_dict:
                            pattern_dict[patt] = set([])
                        pattern_dict[patt].add(proj.tree_id)


        fre_patterns = set([p for p in pattern_dict if len(pattern_dict[p])>=self.min_support])

        for fre_patt in fre_patterns:

            new_pre_tree = pre_tree[:]
            new_pre_tree.insert(-fre_patt[1], fre_patt[0])
            new_pre_tree.insert(-fre_patt[1], '-1')
            
            self.fre_pre_tree.append(new_pre_tree)
            

            
            proj_db_new = []
            for proj in proj_db:
                tree = self.tree_list[proj.tree_id]
                for i in range(len(proj.start_index_list)):
                    for j in range(proj.start_index_list[i], proj.end_index_list[i]):
                        if tree.nodes[j].label == fre_patt[0]:
                            proj_new = Project(proj.tree_id)
                            if tree.nodes[j+1].label != '-1':
                                proj_new.add(j+1, tree.nodes[j].range_end)
                            ss = tree.nodes[j].range_end + 1
                            while tree.nodes[ss].label != '-1' and ss < proj.end_index_list[i]:
                                proj_new.add(ss, tree.nodes[ss].range_end)
                                ss = tree.nodes[ss].range_end + 1
                            proj_db_new.append(proj_new)
            self.get_fre(new_pre_tree, n+1, proj_db_new)


    def output_result(self):
            with open(self.out_path, "w") as f:
                timer = "Run Time: %.04f secends.  Total %d results are as follows:\n" % (self.t_stop - self.t_start,len(self.fre_pre_tree))
                print timer
                f.write(timer)
                for each in self.fre_pre_tree:
                    #print each
                    f.write(" ".join(each) + "\n")


    def run(self):
        self.t_start = time()
        self.read_tree()
        fre_labels = [p[0] for p in self.length_one_patterns if self.length_one_patterns[p] >= self.min_support]
        for fre_lb in fre_labels:
            prefix_subtree = [fre_lb, '-1']
            self.fre_pre_tree.append([item for item in prefix_subtree])
            project_db = []
            for i in range(len(self.tree_list)):
                tree = self.tree_list[i]
                for j in range(len(tree.nodes)):
                    if tree.nodes[j].label == prefix_subtree[0] and tree.nodes[j+1].label != '-1':
                        proj = Project(i)
                        proj.add(j+1, tree.nodes[j].range_end)
                        project_db.append(proj)
            
            self.get_fre(prefix_subtree, 1, project_db)
        self.t_stop = time()
        self.output_result()
        pass


def main():
    parser = OptionParser("Help for PrerixTreeESpan algorithm",
        description="PrefixTreeESpan algorithm implemented in python.",
        version="1.0"
    )
    parser.add_option("-i", "--input", action="store", dest="input", help="Input file")
    parser.add_option("-o", "--output", action="store", dest="output", help="Output file")
    parser.add_option("-m", "--min_propotion", action="store", dest="mp", type=float, help="Min propotion of frequent prefix subtree in all trees")

    options, args = parser.parse_args()

    p = PrefixTreeESpan(options.input, options.output, options.mp)
    p.run()

if __name__ == '__main__':
    main()