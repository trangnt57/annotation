# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 15:03:52 2018

@author: Nguyen Thu Trang
"""
import utilities
#int13_generate_annotation function
#int 13: Use bitwise operators only on unsigned operands
#generate annotation according to rule int 13    
#input: Tree
#output: String
#example: 
#input: tree inorder travel ((s) >> ((2) + ((3)*(4))))
#output:    /*@ assert (s) >= 0;*/
#           /*@ assert ((2) + ( (3)* (4))) >= 0;*/    
def int13_generate_annotation(tree):
    print("int13")
    annotation = "";
    #if node is a biswise operator, generate annotation for both left and right child of it
    print(tree.value)
    if tree.value in utilities.bitwise_token or tree.bitwise_operand == True:
        if tree.left != None and tree.left.contain_operator() == False:
            s = tree.left.inorder_travel()
            if s.isdigit() == False:
                annotation += "/*@ assert " + s + " >= 0;*/ \n"
        if tree.right != None and tree.right.contain_operator() == False:
            s = tree.right.inorder_travel()
            if s.isdigit() == False:
                annotation += "/*@ assert " + s + " >= 0;*/ \n"
    if tree.left != None:
        annotation += int13_generate_annotation(tree.left)
    if tree.right != None:
        annotation += int13_generate_annotation(tree.right)
    return annotation

#int33_generate_annotation function
#int33: Ensure that division and remainder operations do not result in divide-by-zero errors    
#generate annotation according to rule int 33
#input: Tree
#output: String    
def int33_generate_annotation(tree):
    annotation = ""
    #if node is a '/' or '%' operator, generate annotation for right child of it
    if tree.value == '/' or tree.value == '%':
        if tree.right != None:
            annotation += "/*@ assert " + tree.right.inorder_travel() + " != 0;*/ \n"
    if tree.left != None:
        annotation += int33_generate_annotation(tree.left)
    if tree.right != None:
        annotation += int33_generate_annotation(tree.right)
    return annotation

#int32_generate_annotation function
#int32: Ensure that operations on signed integers do not result in overflow
#generate annotation according to rule int 32
#input: Tree
#output: string
#notes: Rosecheckers only checks unary negation case so this function just 
#generate annotation for that case
def int32_generate_annotation(tree):
    annotation = ""
    #if node is a '-' operator and it has only right child
    if tree.value == '-' and tree.left == None and tree.right != None:
        annotation += "/*@ assert " + tree.right.inorder_travel() + " > -2147483648;*/ \n"
    if tree.left != None:
        annotation += int32_generate_annotation(tree.left)
    if tree.right != None:
        annotation += int32_generate_annotation(tree.right)
    return annotation    

    
#int34_generate_annotation function
#int34: Do not shift an expression by a negative number of bits or by greater than
#or equal to the number of bits than exits in the operand
#generate annotation according to rule int 34
#input: Tree
#output: String    
def int34_generate_annotation(tree):
    annotation = ""
    #if node is "<<" or ">>" operator, generate annotation for right child of it
    if tree.value == '<<' or tree.value == '>>':
        if tree.right != None:
            annotation += "/*@ assert 0 <= " + tree.right.inorder_travel() + " < 32;*/ \n"
    if tree.left != None:
        annotation += int34_generate_annotation(tree.left)
    if tree.right != None:
        annotation += int34_generate_annotation(tree.right)
    return annotation        

