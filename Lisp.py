import re
import sys
import operator as op
import functools

operators = {
    "+": op.add, "-": op.sub, "*": op.mul, "/": op.truediv,
    ">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le, "=": op.eq,
    'abs':     abs,
    'append':  op.add,  
    'begin':   lambda *x: x[-1],
    'car':     "dummy",
    'cdr':     "dummy", 
    'cons':    lambda x,y: [x] + y,
    'map':     map,
    'max':     max,
    'min':     min,
    'list':    "dummy",
    'isList':  "dummy"
}

env = {}
global_local = {}

def open_parentheses_parser(data):
    if data[0] == "(":
        return [data[0],data[1:]]
 
def close_parentheses_parser(data):
    if data[0] == ")":
        return [data[0],data[1:]]
    
def space_parser(data):
    space_value = re.findall("^[\s\n]",data)
    if space_value:
        space_len = len(space_value[0])
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
    for parser in parsers:
        output = parser(data)
        if output is None:
            return None
        result.append(output[0])
        data = output[1]
    return[result,data]

def parse_lambda(data):
    if data.startswith('lambda'):
        return ['lambda',data[6:]]

def parse_print(data):
    if data.startswith('print'):
        return ['print',data[5:]]

def arguments_parser(data):
    result = []
    output = open_parentheses_parser(data)
    if output[0] is not None:
        while output[1][0] != ")":
            output = identifier_parser(output[1])
            if output[0] is not None:
                result.append(output[0])
            output = space_parser(output[1])
        output = close_parentheses_parser(output[1])
        output = space_parser(output[1])
    return [result,output[1]]

def body_parser(data):
    output = open_parentheses_parser(data)
    value = output[1]
    body = output[0]
    pos = 0
    open_br = 1
    while open_br != 0:
        if value[pos] == "(": open_br += 1
        if value[pos] == ")": open_br -= 1
        body += value[pos]
        pos += 1
    return [body,value[pos:]]

def lambda_parser(data):
    output = all_parsers(data,open_parentheses_parser, parse_lambda, 
                         space_parser, arguments_parser,space_parser, 
                         body_parser,close_parentheses_parser)
    if output is not None:
        args = output[0][3]
        body = output[0][5]
        obj = {
        'type': 'lambda',
        'objargs': args,
        'objbody': body,
        'env_local': {}        
        }
        unparsed = output[1]
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
    id_index = data.find(" ")
    index_temp = data.find(")")
    if id_index > index_temp or id_index == -1:
        id_index = index_temp
    identifier = data[:id_index]
    if(identifier.isalnum()):
        return[identifier,data[id_index:]]
    raise SyntaxError("One alpha character should present in identifier")

def evaluate(data):
    if data[0] == 'list': return list(data[1:])
    if data[0] == 'car' : return data[1][0]
    if data[0] == 'cdr' : return data[1][1:]
    if data[0] == 'isList' : return isinstance(data[1],list)
    operators.update(env)
    user_function = operators[data[0]]
    if type(user_function) == dict:
        env_dict = user_function['env_local']
        if user_function['type'] == 'lambda':
            argument = user_function['objargs']
            len_arg = len(argument)
            for i in range(len_arg):
                env_dict[argument[i]] = data[i + 1]
                global_local[argument[i]] = data[i+1]
            value = eval_lambda(operators[data[0]])
            return value
    return functools.reduce(operators[data[0]],data[1:])

''' eval_lambda Input: Dictionary
    process: pass env_local values to objbody expression, evaluate it
    and return the final result '''
def eval_lambda(data):
    eval_arg = data['env_local']
    eval_body = data['objbody']
    eval_body = open_parentheses_parser(eval_body)
    eval_body = operator_parser(eval_body[1])
    return eval_body[0]


def operator_parser(data):
    ops = ("+","-","*","/",">","<","=")
    if data[0] in ops:
        if data[1] == "=":
            element = data[:2]
            data = data[2:]
        else:
            element = data[0]
            data = data[1:]
    else:
        env_key = identifier_parser(data)
        if env_key[0] is None:
            return [None,data]
        element = env_key[0]
        data = env_key[1]
    parsed_data = arithmetic_parser(element,data)
    eval_data = evaluate(parsed_data[0])
    return[eval_data,parsed_data[1]]
    
def arithmetic_parser(element,data):
    number = None
    parsed_array = []
    parsed_array.append(element)
    while data[0] != ")" :
        data = space_parser(data)
        if(data[1][0] == "("):
            number = operator_parser(data[1][1:])
        else:
            number = number_parser(data[1])
            if number[0] is None:
                key = identifier_parser(data[1])
                if key[0] in global_local:
                    number[0] = global_local[key[0]]
                else:
                    number[0] = env[key[0]]
                number[1] = key[1]
        data = space_parser(number[1])
        parsed_array.append(number[0])
        parse = parsed_array
        if data is '':
            return[parse,'']
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
    parsers = [define_parser, print_parser]
    for parser in parsers:
        output = parser(data)
        if (output[0] is not None):
            return output

def print_parser(data):
    if data[:5] == "print":
        unparsed_data = data[5:]
        value = space_parser(unparsed_data)
        value = number_parser(value[1])
        if value[0] is None and value[1][0:8] == "((lambda":
            value = lambda_parser(value[1][1:])
            env['lambda_in_print'] = value[0]
            value[0] = 'lambda_in_print'
            value = arithmetic_parser(value[0],value[1])
            value[0] = evaluate(value[0])
        if value[0] is None and value[1][0] == "(":
            value = open_parentheses_parser(value[1])
            value = operator_parser(value[1])
        if value[0] is None:
            value = identifier_parser(value[1])
            value[0] = env[value[0]]

        result = value[0]
        value = space_parser(value[1])
        value = close_parentheses_parser(value[1])
        value = space_parser(value[1])
    return [result,value[1]]

def define_parser(data):
    if data[:6] == "define":
        unparsed_data = data[6:]
        identifier_unparsed_data = space_parser(unparsed_data)
        key = identifier_parser(identifier_unparsed_data[1])
        number_unparsed_data = space_parser(key[1])
        value = lambda_parser(number_unparsed_data[1])
        if value[0] is None:
            value = number_parser(number_unparsed_data[1])
        if value[0] is None:
            value = open_parentheses_parser(value[1])
            value = operator_parser(value[1])
        env[key[0]] = value[0]
        value = space_parser(value[1])
        value = close_parentheses_parser(value[1])
        value = space_parser(value[1])
        return [env,value[1]]
    else:
        return [None,data]
    
def program_parser(data):
    parsers = [open_parentheses_parser, space_parser, 
              statement_parser]
    temp = 0
    parsed_data = open_parentheses_parser(data)
    if parsed_data:
        while data != '':
            parsed_data = parsers[temp](data)
            if parsed_data:
                if parsed_data[0] not in ("(", None):
                    print("parsed data are:",parsed_data[0])
                data = parsed_data[1]
            if(temp == 2): 
                data = space_parser(data)
                data = data[1]
                temp = -1
            if(temp < 2): temp = temp + 1
        return parsed_data[0]

if __name__ == '__main__':
    with open("text2","r") as f:
        data = f.read()
    print(sys.version_info)
    print(sys.version)
    print("Input data is:",data)
    Interpreter = program_parser(data)
    