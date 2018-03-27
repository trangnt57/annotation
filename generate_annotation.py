# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 16:56:50 2018

@author: Nguyen Thu Trang
"""
import re

#list of operators 
token = [' ', '~', '+', '-', '*', '/', '%', '&', '|', '>', '>', '^', '(', ')', '>>', '<<', '=', '!=', '==']
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
        #print(s[i])
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
                if (s[j] not in token) or (s[j] != ' '):
                    j -= 1
                else:
                    break
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
    #case expession is used as index of an array Array[expression]
   
    #conver expression from string format to list    
    new_exp = ""
    for i in range(len(s)):
        if s[i] in token:
            #case ">>", '<<', '!=', '&&', '==', '->'...
            if (s[i] in token) and (i + 1 < len(s)) and (s[i + 1] in token) and (s[i] != ')' and s[i] != '(' and s[i+1] != ')' and s[i+1] != '('):
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
   #print(new_exp)
    new_exp = new_exp.split(" ");
    #print("new_exp")
    #print(new_exp)
   
    list_of_elements = []
    for i in range(len(new_exp)):
        # remove function name
        if new_exp[i] is not token and i + 1 <  len(new_exp) and new_exp[i + 1] == '(':
            #print(new_exp[i])
            #print(new_exp[i+1])
            continue
        # remove empty elements
        if new_exp[i] != '':
            list_of_elements.append(new_exp[i])
    for i in range(len(list_of_elements)):
        v = dict_of_array.get(list_of_elements[i], -1)
        if v != -1:
            list_of_elements[i] = v
    #print(list_of_elements)
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
        if self.value in token:
            flag = True
        if flag == False and self.left != None:
            flag = self.left.contain_operator()
        if flag == False and self.right != None:
            flag = self.right.contain_operator()
        return flag
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
            stack.append(Tree(p[i]))
        else:
            parent = Tree(p[i])
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
    annotation = "";
    #if node is a biswise operator, generate annotation for both left and right child of it
    if tree.value in bitwise_token or tree.bitwise_operand == True:
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
    print("int32 - function")
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

#read_output_of_rosecheckers function
#input: 
#   rosecheckers_output_file_name: string - file name of rosechecker output
#output: distionary 
#example of ouput: {'target/socfpga_gcc/cache.c': [{'33':['INT13-C', 'INT14-C']}, {'48':['INT13-C']} ] }
#file 'target/socfpga_gcc/cache.c' contains violations
#line 33 violated rule INT13-C, INT14-C
#line 48 violated rule INT13-C       
def read_output_of_rosecheckers(rosecheckers_output_file_name):    
    rosecheckers_output = open(rosecheckers_output_file_name, "r")

    #target_file is file which contains violations
    target_file = ""
    
    #dictionary which target_file is key and values are line and which rule that line violated
    list_of_violations = {}
    
    for line in rosecheckers_output:
        list_words = line.split(" ")
        #According to format of rosechecker output: 
        #rosecheckers -c adf afda dfa ../../target/socfpga_gcc/cache.c
        #if first word of a line is rosecheckers, that line may contain target_file
        #else which one contains 'error:' or 'warning:' 
        #that line may contain report of violation
        
        if list_words[0] == 'rosecheckers':
            target_file = list_words[len(list_words) - 1]
            target_file = target_file.replace('\n','')
            target_file = target_file.replace('../','')
        elif (('warning:' in list_words) or ('error:' in list_words)) and ('line' not in list_words):
            #fomat of report of violation
            #cache.c:33: warning: INT13-C: dafdafda
            file_violation = list_words[0].split(':')
            file_violation.remove('')
            if(len(file_violation) > 0):
                temps = target_file.split('/')
                #check whether file in report of violation is the same to target_file or not
                #temps = ['target', 'socfpga_gcc', 'cache.c']
                #file_violation = ['cache.c', '33']
                if file_violation[0] == temps[len(temps) -1]:
                    if(len(list_words) > 2):
                        file_violation.append(list_words[2].replace(":", ""))
                        #if target_file doesn't exit in dictionary
                        #add target_file is a key of dictionary 
                        if(list_of_violations.get(target_file, -1) == -1):              
                            values = []
                            d = {}
                            dvalue = []
                            #file_violation[2] = INT13
                            dvalue.append(file_violation[2])
                            #file_violation[1] = 33
                            d[file_violation[1]] = dvalue
                            #d = {'33':['INT13']}
                            values.append(d)
                            list_of_violations[target_file] = values
                        #if target_file exits in dictionary
                        #append values of target_file
                        else:
                            #get value of target_file
                            list_values = list_of_violations.get(target_file)
                            flag = False
                            for v in list_values:
                                #file_violation[1] = 33
                                tmp = v.get(file_violation[1], -1)
                                # if this line exits in the values of target_file
                                if tmp != -1:
                                    #file_violation[2] = INT13
                                    #if rule INT13 is value of key 33 ({'33':['INT13'...]}) -> ignore 
                                    #otherwhile append INT13 list violated rule of line 33 
                                    if file_violation[2] not in tmp:
                                        tmp.append(file_violation[2])
                                        v[file_violation[1]] = tmp
                                    flag = True
                                    break
                                
                            # flag = False, means file_violation haven't added to dictionary yet         
                            if flag == False:
                                d = {}
                                dvalue = []
                                dvalue.append(file_violation[2])
                                d[file_violation[1]] = dvalue  
                                list_values.append(d)
                                list_of_violations[target_file] = list_values
    return list_of_violations
#genertate_annotation function
#input: 
#       file: write annotation into this file
#       key: position (line number)
#       value: list of rules that line violated
#       s: expression    
#output: void
#generate annotation for expression s
def generate_annotation(file, key, value, s):    
    print ("genreated function")
    pre_processed = pre_processing(s)
    print("pre")
    print (pre_processed)
    post_prefix_expression = expression_to_posprefix(pre_processed)
    expression_tree = postprefix_to_expression_tree(post_prefix_expression)
    #decide which rule to generate annotation for s 
    #values = dicts.get(key, -1)
    for v in value:
        v = v.replace('-C','').lower()
        print("rule")
        print (v)
        if v in list_of_rules:
            annotation = eval(v + "_generate_annotation(expression_tree)")
            file.write(annotation)
    if (contain_array(s)):
        dict_of_array = dictionary_of_array(s)
        for kArray in dict_of_array:
            vArray = dict_of_array.get(kArray)
            if vArray in pre_processed:
                j = 0
                sArray = ''
                while j < len(vArray):
                    if vArray[j] != '[':
                        j += 1
                    else:
                        j += 1
                        break
                while j < len(vArray):
                    if vArray[j] != ']':
                        sArray += vArray[j]
                        j += 1
                    else:
                        break
                sArray = pre_processing(sArray)
                sArray = expression_to_posprefix(sArray)
                sArray = postprefix_to_expression_tree(sArray)
                for v in value:
                    v = v.replace('-C','').lower()
                    if v in list_of_rules:
                        print("rule")
                        print(v)
                        annotation = eval(v + "_generate_annotation(sArray)")
                        file.write(annotation)        

#write_annotations_to_file function
#input:
#   list_of_violations: dictionary - contains file, violated line and rule
#   source: root address of violated file
#output: void
#write annotation to appropriate file    
def write_annotations_to_file(list_of_violations, source):
    for key in list_of_violations:
        file_name = source + key
        print(file_name)
        violation_positions = list_of_violations.get(key)
        original_file = open(file_name, "r", errors = 'ignore')
        tmp = str(key).split('/')
        generated_file_name =  'annotated_' + tmp[len(tmp) - 1] 
        generated_file = open(generated_file_name, "w")
        
        data_file = original_file.readlines()
        num_of_line = 1
        
        #read each line of original file
        for l in data_file:
            #with each violation
            for i in range(len(violation_positions)):
                dicts = violation_positions[i]
                print("dict")
                print(dicts)
                flag = True
                for k in dicts:
                    #if violated line equals to current line (line is being read)
                    if int(k) == num_of_line:
                        
                        line = l
                        line = line.replace('\n','')
                        s = ""
                        #line ends with '{' symbol 
                        #example if(expression) {
                        if line[len(line) - 1] == '{':
                            s = line
                        #line doesn't end with ';', that means this line hasn't finished
                        #read one more line
                        elif line[len(line) - 1] != ';':
                            line += data_file[num_of_line]
                            #line += linecache.getline(file_name, int(k) + 1)
                            line = line.replace('\n', ' ')
                            s = line
                        else:
                            s = line
                        #s is expression that need to be generated annotation
                        #check if s is a function call or not
                        #if s is a function call, get all paramenter of that 
                        #function and consider each as an expression
                        if (is_a_function_call(s) != ''):
                            s = s.replace(b,'')
                            s = s.replace('\t', '')
                            s = s.replace(' ', '')
                            s = s[1: len(s)-2]
                            s = s.split(',')
                            print(s)
                            for si in range(len(s)):
                                generate_annotation(generated_file, k, dicts.get(k), s[si]) 
                        else:   
                            generate_annotation(generated_file, k, dicts.get(k), s)
                            
                        flag = False
                        break
                    elif int(k) > num_of_line:
                        flag = False
                        break
                    if flag == False:
                        break
            generated_file.write(l)
            num_of_line += 1
        original_file.close()
        generated_file.close() 

#main
rosecheckers_output_file_name = "C:/Users/nguye/Google Drive/JAIST/Project/code/rosecheckers_output.txt"        
source = "C:/Users/nguye/Google Drive/JAIST/Project/code/atk2-sc1_arm/"        
list_of_violations = read_output_of_rosecheckers(rosecheckers_output_file_name)
write_annotations_to_file(list_of_violations, source)
s = "convert((uintptr) (-val), 10U, raddec,width, TRUE, padzero, outputc);"
b = is_a_function_call(s)
print(b)
s = s.replace(b,'')
s = s[1: len(s)-2]
s = s.split(',')
print(s)
print(b)
