import re
import sys

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
    space_len = len(space_value[0])
    #print("space length:",space_len)
    return data[:space_len],data[space_len:]

def number_parser(data):
    parse_num = re.findall("^(-?(?:\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)",
                            data)
    if not parse_num:
        return None
    pos = len(str(parse_num))
    # if our parse_num is 123 then pos value comes as 7. 
    #It counts brackets and quotes also in the length as ['123'].
    #To avoid it we are subtracting 4
    try:
        return [int(parse_num[0]), data[pos-4:].strip()]
    except ValueError:
        return [float(parse_num[0]), data[pos-4:].strip()]

def statement_parser(data):
    #'Parsed_data variable is just to display in the return type.'
    if(data[:6] == "define"):
        keyword.append("define")
        parsed_data = data[:6]
        unparsed_data = data[6:]
        identifier_unparsed_data = space_parser(unparsed_data)
        parsed_data += identifier_unparsed_data[0]
        key = identifier_parser(identifier_unparsed_data[1])
        parsed_data += key[0]
        number_unparsed_data = space_parser(key[1])
        parsed_data += number_unparsed_data[0]
        value = number_parser(number_unparsed_data[1])
        parsed_data += str(value[0])
        print("the key is:",key)
        env[key[0]] = value[0]
        print("env is",env)
    return [parsed_data,value[1]]
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
def identifier_parser(data):
    print("input data for identifier_parser is:",data)
    id_index = data.find(" ")
    identifier = data[:id_index]
    if(identifier.isalpha()):
        #print("id index is:",id_index)
        return[identifier,data[id_index:]]
    raise SyntaxError("Atleast one alpha character should present in identifier")

def program_parser(data):
    parsers = [open_parentheses_parser, space_parser, 
              statement_parser,identifier_parser, close_parentheses_parser]
    temp = 0
    parsed_data = open_parentheses_parser(data)
    if parsed_data:
        while data != ")":
            parsed_data = parsers[temp](data)
            if parsed_data:
                print("parsed data are:",parsed_data[0])
                data = parsed_data[1]
                print("remaining data are:",data)
            temp = temp + 1;

if __name__ == '__main__':
    with open("text","r") as f:
        data = f.read()
    print("Input data is:",data)
    #print("input data type is:",type(data))
    Interpreter = program_parser(data)
    #print(Interpreter)