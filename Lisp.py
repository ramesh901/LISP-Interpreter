import re
import sys
import operator
import functools

operators = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "=": operator.eq
}

env = {}

def open_parentheses_parser(data):
    #print("enter open paranethesis",data)
    if data[0] == "(":
        return [data[0],data[1:]]
 
def close_parentheses_parser(data):
    #print("data in close para:",data)
    if data[0] == ")":
        return [data[0],data[1:]]
    
def space_parser(data):
    space_value = re.findall("^[\s\n]",data)
    if space_value:
        space_len = len(space_value[0])
        #print("space length:",space_len)
        return data[:space_len],data[space_len:]
    else:
        return [None,data]

def number_parser(data):
    parse_num = re.findall("^(-?(?:\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)",
                            data)
    if not parse_num:
        return [None,data]
    pos = len(str(parse_num))
    # if our parse_num is 123 then pos value comes as 7. 
    #It counts brackets and quotes also in the length as ['123'].
    #To avoid it we are subtracting 4
    try:
        return [int(parse_num[0]), data[pos-4:].strip()]
    except ValueError:
        return [float(parse_num[0]), data[pos-4:].strip()]

def all_parsers(data,*parsers):
    result = []
    #print("entering all_parser",data,"and parsers are:",parsers)
    for parser in parsers:
        output = parser(data)
        if output is None:
            return None
        result.append(output[0])
        data = output[1]
    #print("output of all_parser",result,"and remaining data:",data)
    return[result,data]

def parse_lambda(data):
    #print("entering parse_lambda",data)
    if data.startswith('lambda'):
        return ['lambda',data[6:]]

def parse_print(data):
    #print("entering parse_lambda",data)
    if data.startswith('print'):
        return ['print',data[5:]]

def arguments_parser(data):
    result = []
    output = open_parentheses_parser(data)
    #print("entering arg parser:",output)
    if output[0] is not None:
        while output[1][0] != ")":
            output = identifier_parser(output[1])
            if output[0] is not None:
                result.append(output[0])
            output = space_parser(output[1])
        output = close_parentheses_parser(output[1])
        output = space_parser(output[1])
    #print("output of arg parser:",result,"and",output[1])
    return [result,output[1]]

def body_parser(data):
    output = open_parentheses_parser(data)
    #print("entering body parser:",output)
    value = output[1]
    body = output[0]
    pos = 0
    open_br = 1
    while open_br != 0:
        if value[pos] == "(": open_br += 1
        if value[pos] == ")": open_br -= 1
        body += value[pos]
        pos += 1
    #print("output of body_parser",body,"and",value[pos:])
    return [body,value[pos:]]

def lambda_parser(data):
    output = all_parsers(data,open_parentheses_parser, parse_lambda, 
                         space_parser, arguments_parser,space_parser, 
                         body_parser,close_parentheses_parser)
    #print("entering lambda and output is",output)
    if output is not None:
        args = output[0][3]
        body = output[0][5]
        obj = {
        'type': 'lambda',
        'objargs': args,
        'objbody': body,
        'env': {}        
        }
        unparsed = output[1]
        #print("unparsed in lambda_parser",unparsed)
        return [obj, unparsed]
    return [None,data]

def parser_factory(data,*parsers):
    for parser in parsers:
        output = parser(data)
        if output is not None:
            return output
    return None

def check_type(data,env):
    if isinstance(data,str):
        if env is not None:
            data = env[data]
    elif ENV[data] is not None:
        input = ENV[input]
    elif (ENV[data] is None):
        raise SyntaxError("input is undefined")

def identifier_parser(data):
    #print("input data for identifier_parser is:",data)
    id_index = data.find(" ")
    index_temp = data.find(")")
    if id_index > index_temp:
        id_index = index_temp
    identifier = data[:id_index]
    #print("identifier is:",identifier)
    if(identifier.isalnum()):
        #print("id index is:",id_index)
        return[identifier,data[id_index:]]
    raise SyntaxError("Atleast one alpha character should present in identifier")

def evaluate(data):
    return functools.reduce(operators[data[0]],data[1:])
    
def operator_parser(data):
    if data[0] not in ("+","-","*","/"):
        return[None,data]
    else:
        parsed_data = arithmetic_parser(data)
        #print("parsed data in OPERATOR PARSER:",parsed_data)
        eval_data = evaluate(parsed_data[0])
    return[eval_data,parsed_data[1]]

def arithmetic_parser(data):
    number = None
    parsed_array = []
    parsed_array.append(data[0])
    #print("parsed array adding multiply is:",parsed_array)
    data = data[1:]
    #print("input data for space parser in multiply_parser",data)
    while data[0] != ")" :
        #print("Data in while loop:",data)
        data = space_parser(data)
        if(data[1][0] == "("):
            number = operator_parser(data[1][1:])
            #print("OPERATOR PARSER to num1",number)
        else:
            number = number_parser(data[1])
            #print("assign number to number directly",number)
            if number[0] is None:
                key = identifier_parser(data[1])
                #print("key is",key)
                number[0] = env[key[0]]
                number[1] = key[1]
        #print("number is:",number)
        data = space_parser(number[1])
        parsed_array.append(number[0])
        parse = parsed_array
        #print("parsed array in multiply is:",parsed_array)
        #data = data[1:]
        if data is '':
            return[parse,'']
        #print("final data in multiply is:",parse,"and",data)
        #print('len of data in multiply:',len(data))
        data = data[1]
    return [parse, data[1:]]

def expression_parser(data):
    parsers = [number_parser,operator_parser]
    for parser in parsers:
        output = parser(data)
        if output is not None:
            return output

def parser_factory(data,*parsers):
    for parser in parsers:
        output = parser(data)
        if (output is not None):
            return output
    
    
def statement_parser(data):
    #parser_factory(data,define_parser, print_parser)
    parsers = [define_parser, print_parser]
    #'Parsed_data variable is just to display the first value in the return type.'
    for parser in parsers:
        output = parser(data)
        if (output[0] is not None):
            return output
'''
def print_parser(data):
    output = all_parsers(data,parse_print, 
                         space_parser, expression_parser,
                         close_parentheses_parser)
    #print("entering lambda and output is",output)
    if output is not None:
        value = output[0][3]
        unparsed = output[1]
        #print("unparsed in lambda_parser",unparsed)
        return [value, unparsed]
    return None
'''

def  print_parser(data):
    if data[:5] == "print":
        unparsed_data = data[5:]
        value = space_parser(unparsed_data)
        #print("value in print parser",value)
        value = number_parser(value[1])
        if value[0] is None and value[1][0] == "(":
            print("entering op parser",value)
            value = open_parentheses_parser(value[1])
            value = operator_parser(value[1])
        if value[0] is None:
            print("entering id parser",value)
            value = identifier_parser(value[1])
            value[0] = env[value[0]]

        result = value[0]
        print("VALUE IN PRINT PARSER",result)
        #print("env in print_parser",env)
        value = space_parser(value[1])
        #print("value before close para:",value)
        value = close_parentheses_parser(value[1])
        value = space_parser(value[1])
        #print("value in PRINT",value)
    return [result,value[1]]

def define_parser(data):
    if data[:6] == "define":
        #keyword.append("define")
        #parsed_data = data[:6]
        unparsed_data = data[6:]
        identifier_unparsed_data = space_parser(unparsed_data)
        #parsed_data += identifier_unparsed_data[0]
        key = identifier_parser(identifier_unparsed_data[1])
        #print("the key is:",key)
        #parsed_data += key[0]
        number_unparsed_data = space_parser(key[1])
        #parsed_data += number_unparsed_data[0]
        value = lambda_parser(number_unparsed_data[1])
        #print("value after lambda",value)
        if value[0] is None:
            value = number_parser(number_unparsed_data[1])
        if value[0] is None:
            #print("entering op parser")
            value = open_parentheses_parser(value[1])
            value = operator_parser(value[1])
        #parsed_data += str(value[0])
        env[key[0]] = value[0]
        #print("env is",env)
        value = space_parser(value[1])
        #print("value before close para:",value)
        value = close_parentheses_parser(value[1])
        value = space_parser(value[1])
        #print("value in define:",value)
        return [env,value[1]]
    else:
        #print("enter else in statement")
        return [None]
    '''
    In the statement_parser return parsed data we are assigning only 'define'. Do we need to assign
    full expression
    '''   

def program_parser(data):
    parsers = [open_parentheses_parser, space_parser, 
              statement_parser,operator_parser]
    temp = 0
    parsed_data = open_parentheses_parser(data)
    if parsed_data:
        while data != '':
            parsed_data = parsers[temp](data)
            #print("PARSED DATA FULL:",parsed_data)
            if parsed_data:
                #print("temp value:",temp)
                #print("parser is",parsers[temp])
                if parsed_data[0] not in ("(", None):
                    print("parsed data are:",parsed_data[0])
                data = parsed_data[1]
                #print("remaining data are:",data)
            if(temp == 3): 
                data = space_parser(data)
                data = data[1]
                temp = -1
            #print("temp before reset",temp)
            if(temp < 3): temp = temp + 1
            #print("temp after reset",temp)
      

        return parsed_data[0]

if __name__ == '__main__':
    with open("text","r") as f:
        data = f.read()
    print("Input data is:",data)
    print("input data type is:",type(data))
    Interpreter = program_parser(data)
    #print("Final value:",Interpreter)