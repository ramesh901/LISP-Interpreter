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
keyword = []


def open_parentheses_parser(data):
    if data[0] == "(":
        return [data[0],data[1:]]
 
def close_parentheses_parser(data):
    if data[0] == ")":
        return [data[0],data[1:]]

def space_parser(data):
    space_value = re.findall("^\s+",data)
    if space_value:
        space_len = len(space_value[0])
        #print("space length:",space_len)
        return data[:space_len],data[space_len:]
    else:
        return None,data

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

def statement_parser(data):
    #'Parsed_data variable is just to display the first value in the return type.'
    if(data[:6] == "define"):
        keyword.append("define")
        #parsed_data = data[:6]
        unparsed_data = data[6:]
        identifier_unparsed_data = space_parser(unparsed_data)
        #parsed_data += identifier_unparsed_data[0]
        key = identifier_parser(identifier_unparsed_data[1])
        #parsed_data += key[0]
        number_unparsed_data = space_parser(key[1])
        #parsed_data += number_unparsed_data[0]
        value = number_parser(number_unparsed_data[1])
        #parsed_data += str(value[0])
        print("the key is:",key)
        env[key[0]] = value[0]
        print("env is",env)
        return [data[:6],value[1]]
    else:
        return [None,data]
    '''
    In the statement_parser return parsed data we are assigning only 'define'. Do we need to assign
    full expression
    '''
    '''
    association of key and value happen within define parser. finally append to global ENV.
    
    a = key
    10 = value
    env[a] = 10
    env = {a: 10}
    
    
    have seperate parser for open and close paren
    do it in main 
    ''' 
    '''

    '''
def identifier_parser(data):
    print("input data for identifier_parser is:",data)
    id_index = data.find(" ")
    identifier = data[:id_index]
    if(identifier.isalpha()):
        #print("id index is:",id_index)
        return[identifier,data[id_index:]]
    raise SyntaxError("Atleast one alpha character should present in identifier")

def evaluate(data):
    return functools.reduce(operators[data[0]],data[1:])
    

def operator_parser(data):
    if data[0] == "+":
        parsed_data = plus_parser(data)
        print("parsed data in OPERATOR PARSER:",parsed_data)
        eval_data = evaluate(parsed_data[0])

        return[eval_data,parsed_data[1]]

def plus_parser(data):
    number = None
    parsed_array = []
    if data[0] != "+":
        return None
    parsed_array.append(data[0])
    print("parsed array adding plus is:",parsed_array)
    data = data[1:]
    print("input data for space parser in plus_parser",data)
    
    while data[0] != ")" :

        print("Data in while loop:",data)
        data = space_parser(data)
        if(data[1][0] == "("):
            number = operator_parser(data[1][1:])
            print("OPERATOR PARSER to num1",number)
        else:
            number = number_parser(data[1])
            print("assign number to number directly",number)
        print("number is:",number)
        data = space_parser(number[1])
        '''
        if(data[1][0] == "("):
            print("assign operator parser to num2")
            number2 = operator_parser(data[1][1:])
            print("num2 after prog parser",number2)
        number2 = number_parser(data[1])
        print("num1 int:",number)
        print("num2 int:",number2)
        value += number[0] + number2[0]
        '''
        parsed_array.append(number[0])
        parse = parsed_array
        print("parsed array in plus is:",parsed_array)
        #data = data[1:]
        if data is '':
            return[parse,'']
        print("final data in plus is:",parse,"and",data)
        print('len of data in plus:',len(data))
        data = data[1]

    return [parse, data[1:]]

def  expression_parser(data):
    parsers = [number_parser,operator_parser]
    for parser in parsers:
        output = parser(data)
        if output != null:
            return output


         
    

def program_parser(data):
    parsers = [open_parentheses_parser, space_parser, 
              statement_parser,operator_parser]
    temp = 0
    parsed_data = open_parentheses_parser(data)
    if parsed_data:
        while data != '':
            parsed_data = parsers[temp](data)
            if parsed_data:
                print("parsed data are:",parsed_data[0])
                data = parsed_data[1]
                print("remaining data are:",data)
            if(temp == 3):
                temp = -1
            if(temp < 3):
                temp = temp + 1

        return parsed_data[0]

if __name__ == '__main__':
    with open("text1","r") as f:
        data = f.read()
    print("Input data is:",data)
    print("input data type is:",type(data))
    '''
    if(data.rstrip().isdigit()):
        print("I am in isdigit")
        numdata = int(data)
    print("input data type is:",type(numdata))    
    '''
    Interpreter = program_parser(data)
    print("Final value:",Interpreter)