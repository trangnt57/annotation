# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:39:59 2018

@author: Nguyen Thu Trang
"""
import utilities
#Class Tree
class Tree:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.bitwise_operand = False
    #inorder_travel function
    #left parent right
    def inorder_travel(self):
        #s = "("
        s = ""
        if self.left != None:
            s += self.left.inorder_travel() 
        s += str(self.value)
        if self.right != None:
            s += self.right.inorder_travel()
        #s += ")"
        return str(s)
    #contain_operator function
    #check whether a tree is an expression or just an operand
    def contain_operator(self):
        flag = False
        if self.value in utilities.token:
            flag = True
        if flag == False and self.left != None:
            flag = self.left.contain_operator()
        if flag == False and self.right != None:
            flag = self.right.contain_operator()
        return flag

