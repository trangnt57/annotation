# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 16:56:50 2018

@author: Nguyen Thu Trang
"""
import utilities
import int_rule

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
    pre_processed = utilities.pre_processing(s)
    post_prefix_expression = utilities.expression_to_posprefix(pre_processed)
    expression_tree = utilities.postprefix_to_expression_tree(post_prefix_expression)
    #decide which rule to generate annotation for s 
    #values = dicts.get(key, -1)
    for v in value:
        v = v.replace('-C','').lower()
        if v in utilities.list_of_rules:
            annotation = eval("int_rule." + v + "_generate_annotation(expression_tree)")
            file.write(annotation)
    if (utilities.contain_array(s)):
        dict_of_array = utilities.dictionary_of_array(s)
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
                sArray = utilities.pre_processing(sArray)
                sArray = utilities.expression_to_posprefix(sArray)
                sArray = utilities.postprefix_to_expression_tree(sArray)
                for v in value:
                    v = v.replace('-C','').lower()
                    if v in utilities.list_of_rules:
                        annotation = eval("int_rule." + v + "_generate_annotation(sArray)")
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
                        b = utilities.is_a_function_call(s)
                        if (b != ''):
                            s = s.replace(b,'')
                            s = s.replace('\t', '')
                            s = s.replace(' ', '')
                            s = s[1: len(s)-2]
                            s = s.split(',')
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

