# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:41:18 2018

@author: Nguyen Thu Trang
"""
import re
import tree

#list of operators 
token = [' ', '~', '+', '-', '*', '/', '%', '&', '|', '>', '<', '^', '(', ')', '>>', '<<', '!','=', '!=', '==']
#list of biswise operators
bitwise_token = ['~', '&', '|', '>>', '<<']
#list of rules which has function for generating annotation
list_of_rules = ['int13', 'int33', 'int32', 'int34']

#is_a_function_call
#input: String s
#output: string if string == '' it means s is not a function call 
#check if a string is a function call or not
def is_a_function_call(s):
    function_name = ''
    for i in range(len(s)):
        if s[i] == '(':
            break
        elif s[i] != ' ' and s[i] in token:
            return ''
        elif s[i] != ' ' and s[i] != '(':
            function_name += s[i]
       
    if(len(function_name) > 0):
        return function_name
    return ''
    
#contain_array function
#input: string s
#output: Boolean
#check if an expression contain arrays or not 
#for example s = A[b % c] -> return True
def contain_array(s):
    for i in range(len(s)):
        if(s[i] == '['):
            return True
    return False

#dictionary_array_function
#input: string
#output: dictionary
#add all array variables of the expression into dictionary
#for example:
#s = A[b%c] + E[b%d]
#dict_of_array = {'A_0':'A[b%c]', 'A_1':'E[b%d]'}    
def dictionary_of_array(s):
    dict_of_array = {}
    key = 'A_'
    index = 0
    for i in range(len(s)):
        if(s[i] == '['):
            value = ''
            j = i
            while j >= 0:
                if s[j] not in token:
                    j -= 1
                else:
                    break
            j += 1
            while j < len(s) and s[j] != ']':
                value += s[j]
                j += 1
            
            value += s[j]
            i = j
            k = key + str(index)
            dict_of_array[k] = value
            index += 1
    return dict_of_array

#pre_processing function
#input: a String
#output: list
#example:
#input: s = "s = s >> 2 + 3 * 4;"
#output: ['s', '>>', '2', '+', '3', '4']
def pre_processing(s):
    print(s)
    #remove some special characters from string
    list_of_special_characters = ['\n', '\t', '{', '}', 'if', 'while', ';', 'signed', 'unsigned', 'uintptr', 'sintptr', 'int', 'long']
    for i in range(len(list_of_special_characters)):
        s = s.replace(list_of_special_characters[i], '')
    
    dict_of_array = {}
    if(contain_array(s) == True):
        dict_of_array = dictionary_of_array(s)
        for k in dict_of_array:
            s = s.replace(dict_of_array.get(k), k)
    if ("!=" not in s) and ("==" not in s):
       
        #Convert expression from a += b to a = a + b
        operator = ["~=", ">>=", "<<=", "&=", "^=", "|=", "/="]
        temp = []
        op = ""
        for i in range(len(operator)):
            #if expression s has one of symbol in list operator
            if operator[i] in s:
                #split s by symbol operator[i]
                if operator[i] == '|=':
                    temp = re.split('\|=', s)
                    op = operator[i]
                else:
                    temp = re.split(operator[i], s)
                    op = operator[i]
                break
       
        #op has form '+='     
        if(len(temp) > 0):
            op = re.split('=', op)
            #for example expression a += b
            #temp[0] = a
            #op[0] = '+'
            #temp[1] = b
            s = temp[0] + op[0] + " (" + temp[1] + ")"
        #convert expression from a = a+b to a+b (remove left side accoding to '=' operator)
        if '=' in s:
            temp = re.split('=', s)
            s = temp[1]
   
    #conver expression from string format to list    
    new_exp = ""
    for i in range(len(s)):
        if s[i] in token:
            #case ">>", '<<', '!=', '&&', '==', '->'...
            if (s[i] in token) and (i + 1 < len(s)) and (s[i + 1] in token) and (s[i] != ')' and s[i] != '(' and s[i+1] != ')' and s[i+1] != '('):
                if(s[i] != '-' and s[i+1] != ' '):
                    new_exp += " "
                new_exp += s[i]
                continue
            else:
                #adding white space before and after operator
                if (s[i] in token) and (i - 1 >= 0) and (s[i-1] in token) and (s[i] != ')' and s[i] != '(' and s[i-1] != ')' and s[i-1] != '('):
                    new_exp += s[i]
                else:
                    if i > 0 and s[i - 1] != " ":
                        new_exp += " "
                    new_exp += s[i]
                if (s[i] == '>' and s[i-1] == '-'):
                    continue
                if (i < len(s) - 1 and s[i+1] != " "):
                    new_exp += " "
        else:
            new_exp += s[i]
    print(new_exp)
    new_exp = new_exp.split(" ");
   
    list_of_elements = []
    for i in range(len(new_exp)):
        # remove function name
        if new_exp[i] is not token and i + 1 <  len(new_exp) and new_exp[i + 1] == '(':
            continue
        # remove empty elements
        if new_exp[i] != '':
            list_of_elements.append(new_exp[i])
    for i in range(len(list_of_elements)):
        v = dict_of_array.get(list_of_elements[i], -1)
        if v != -1:
            list_of_elements[i] = v
    print(list_of_elements)
    return list_of_elements

#epxression_to_postprefix function
#convert from expression to postprefix format   
#input: list
#output: list
#example:
#input: ['s', '>>', '2', '+', '3', '*', '4']
#output: ['s', '2', '3', '4', '*', '+', '>>']    
def expression_to_posprefix(list_of_elements):
    stack = []
    # p is a list that contain result
    p = []
    #the priority of operators
    operator_precedence = { '!=':1, '==': 1,'*': 2, '/':2, '%': 2, '+':3, '-': 3, '<<':4, '>>':4, '&':5, '^':6, '|':7}
    # if element is a token and different from ')'
        # if it is not an operator, it means it is a '(' symbol -> push it to stack
        # if it is an operator, before pushing it to stack we need to pop all of the operators that has
        # higher priorty and append these operators to result list (p)
    # if element is not a token -> append to result list (p)
    # if element is ')' -> pop from stack and append to result list until we meet '('    
    for i in range(len(list_of_elements)):
        if list_of_elements[i] in token and list_of_elements[i] != ')':
            if operator_precedence.get(list_of_elements[i], 0) == 0:
                stack.append(list_of_elements[i])
            else:
                while len(stack) > 0:
                    x = stack.pop()
                    if x != '(' and operator_precedence.get(x, 0) < operator_precedence.get(list_of_elements[i], 0):
                        p.append(x)
                    else:
                        stack.append(x)
                        break;
                    if len(stack) == 0:
                        break;
                stack.append(list_of_elements[i])
        elif list_of_elements[i] not in token:
            p.append(list_of_elements[i])
        else:
            x = stack.pop()
            while x != '(':
                p.append(x)
                if len(stack) > 0:
                    x = stack.pop()
                else:
                    break
    for i in range(len(stack)):
        p.append(stack.pop())
    return p

#postprefix_to_expression_tree function
#convert expression from postprefix format to tree format
#input: list
#output: Tree
#example
#input: ['s', '2', '3', '4', '*', '+', '>>']
#output: inorder travel ((s) >> ((2) + ((3)*(4))))        
def postprefix_to_expression_tree(p):
    stack = []
    #if element is not operator -> push it into stack
    #if element is operator, make it to be a node
        # if element is '~', it just has one operand
            #pop one value from stack, make it to be child of current node and
            #push current node again into stack
        # if element is different from '~'
            #pop two values from stack, make them to be children of current node 
            #push current node again into stack
    #At the end, only one element remains in stack, it will be the root of expression tree        
    for i in range(len(p)):
        if p[i] not in token:
            stack.append(tree.Tree(p[i]))
        else:
            parent = tree.Tree(p[i])
            if(p[i] == '~'):
                if len(stack) > 0:
                    _right = stack.pop()
                    _right.bitwise_operand = True
                    parent.right = _right
            else:
                if len(stack) > 0:
                    _right = stack.pop()
                    if parent.value in bitwise_token:
                        _right.bitwise_operand = True
                    parent.right = _right
                if len(stack) > 0:
                    _left = stack.pop()
                    if parent.value in bitwise_token:
                        _right.bitwise_operand = True
                    parent.left = _left
            stack.append(parent)
    return stack.pop()
