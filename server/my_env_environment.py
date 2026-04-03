import random
import uuid
import re
from typing import Optional, List

from pydantic import BaseModel

try:
    from models import (
        Issue,
        IssueType,
        Language,
        TaskName,
        CodeReviewAction,
        CodeReviewObservation,
        CodeReviewState,
        FoundIssue,
    )
except ImportError:
    from ..models import (
        Issue,
        IssueType,
        Language,
        TaskName,
        CodeReviewAction,
        CodeReviewObservation,
        CodeReviewState,
        FoundIssue,
    )

try:
    from openenv.core.env_server.interfaces import Environment
except ImportError:
    from openenv.core.env_server import Environment


STYLE_SNIPPETS = {
    "py001": {
        "language": Language.PYTHON,
        "code": "def calculate(a,b):\n    return a+b\n\nresult=calculate(10,20)\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_start=1,
                line_end=1,
                fix_suggestion="calculate -> calculate_sum",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operator",
                line_start=2,
                line_end=2,
                fix_suggestion="a+b -> a + b",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Variable should use snake_case",
                line_start=4,
                line_end=4,
                fix_suggestion="result -> result_value",
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": "import os\n\ndef getData():\n    x = 10\n    return x\n\nprint(getData())",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_start=2,
                line_end=2,
                fix_suggestion="getData -> get_data",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Variable name should use snake_case",
                line_start=3,
                line_end=3,
                fix_suggestion="x -> value",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Unused import os",
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "def process_items(items):\n    result=[]\n    for item in items:\n        if item>0:\n            result.append(item*2)\n    return result\n\ndata = [1, -2, 3, -4, 5]\nprint(process_items(data))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after colon in list literal",
                line_start=2,
                line_end=2,
                fix_suggestion="result=[] -> result = []",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Space missing around comparison operator",
                line_start=4,
                line_end=4,
                fix_suggestion="item>0 -> item > 0",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Function should have docstring",
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "def add_numbers(a,b,c):\n    total = a + b + c\n    return total\nx=add_numbers(1,2,3)\nprint(x)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Variable name should use snake_case",
                line_start=2,
                line_end=2,
                fix_suggestion="total -> total_sum",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space around assignment",
                line_start=4,
                line_end=4,
                fix_suggestion="x= -> x = ",
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "def do_something(x,y):\n    if x>y:\n        return x-y\n    else:\n        return y-x\n\nresult=do_something(10,5)\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around comparison operator",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around arithmetic operators",
                line_start=2,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": 'def get_user(name,age):\n    return f"User: {name}, Age: {age}"\n\nuser=get_user("Alice",30)\nprint(user)',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_start=1,
                line_end=1,
                fix_suggestion="get_user -> get_user_info",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Parameter names should use snake_case",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "def filter_list(items):\n    result=[x for x in items if x>10]\n    return result\n\ndata=[5,15,25,8,12]\nfiltered=filter_list(data)\nprint(filtered)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after comma in list",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after comma in list",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "def calculate_average(numbers):\n    sum_val=sum(numbers)\n    count=len(numbers)\n    avg=sum_val/count\n    return avg\n\nnums=[10,20,30,40,50]\nresult=calculate_average(nums)\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Variable names should use snake_case",
                line_start=2,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=2,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after comma in list",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py009": {
        "language": Language.PYTHON,
        "code": "class UserController:\n    def GetUser(self,userId):\n        return {'id':userId,'name':'John'}\n\nobj=UserController()\nprint(obj.GetUser(1))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Class name should use PascalCase",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Method name should use snake_case",
                line_start=2,
                line_end=2,
                fix_suggestion="GetUser -> get_user",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Parameter should use snake_case",
                line_start=2,
                line_end=2,
                fix_suggestion="userId -> user_id",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py010": {
        "language": Language.PYTHON,
        "code": "def process_data(data:list[str])->dict:\n    result={}\n    for i,item in enumerate(data):\n        result[i]=item.upper()\n    return result\n\nprint(process_data(['a','b','c']))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after colon in type hint",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operator",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after comma in function call",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py011": {
        "language": Language.PYTHON,
        "code": "import json\n\ndef save_config(config:dict,filename:str):\n    with open(filename,'w') as f:\n        json.dump(config,f)\n\nsave_config({'debug':True},'config.json')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces after colon in type hints",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after comma in function call",
                line_start=5,
                line_end=5,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operator",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py012": {
        "language": Language.PYTHON,
        "code": "def fetch_records(query,limit=100,offset=0):\n    sql=f\"SELECT * FROM table WHERE {query} LIMIT {limit} OFFSET {offset}\"\n    return sql\n\nprint(fetch_records('active=1'))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing default values spacing",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="SQL injection vulnerability should use parameterized query",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py013": {
        "language": Language.PYTHON,
        "code": "def calculate_score(math,eng,science):\n    total=math+eng+science\n    avg=total/3\n    return total,avg\n\nscore=calculate_score(80,90,85)\nprint(score)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function parameters should use snake_case",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space around division operator",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py014": {
        "language": Language.PYTHON,
        "code": "class DataProcessor:\n    def __init__(self,Data,Threshold):\n        self.Data=Data\n        self.Threshold=Threshold\n    \n    def Process(self):\n        return [x for x in self.Data if x>self.Threshold]\n\nproc=DataProcessor([1,2,3],2)\nprint(proc.Process())",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Class attribute names should use snake_case",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Instance attribute names should use snake_case",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Instance attribute names should use snake_case",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Method name should use snake_case",
                line_start=6,
                line_end=6,
            ),
        ],
    },
    "py015": {
        "language": Language.PYTHON,
        "code": "def authenticate(username:str,password:str)->bool:\n    if username=='admin' and password=='admin123':\n        return True\n    return False\n\nprint(authenticate('admin','admin123'))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces in type hints",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around comparison operator",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use len instead of comparing to empty string",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py016": {
        "language": Language.PYTHON,
        "code": "numbers=[1,2,3,4,5,6,7,8,9,10]\nevens=[]\nfor n in numbers:\n    if n%2==0:\n        evens.append(n)\nprint(evens)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension instead of loop",
                line_start=2,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around modulo operator",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py017": {
        "language": Language.PYTHON,
        "code": "def get_user_info(user_id):\n    name='John'\n    age=30\n    email='john@example.com'\n    return {'id':user_id,'name':name,'age':age,'email':email}\n\nprint(get_user_info(1))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use dataclass or namedtuple instead of dictionary",
                line_start=5,
                line_end=5,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-string instead of string concatenation",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py018": {
        "language": Language.PYTHON,
        "code": "import os,sys,json\n\ndef read_file(path):\n    with open(path,'r') as f:return f.read()\n\ndata=read_file('data.txt')\nprint(len(data))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Multiple imports should be on separate lines",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing space after colon in with statement",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Body of with statement should be indented",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py019": {
        "language": Language.PYTHON,
        "code": "def validate_email(email):\n    if '@' in email and '.' in email:\n        return True\n    else:return False\n\nresult=validate_email('test@example.com')\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use ternary operator instead of if-else",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operators",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py020": {
        "language": Language.PYTHON,
        "code": "def process(items):\n    results=[]\n    for item in items:\n        if type(item)==str:\n            results.append(item.upper())\n        elif type(item)==int:\n            results.append(item*2)\n    return results\n\nprint(process(['a',1,'b',2]))",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use isinstance instead of type comparison",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use type() == str instead of ==",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing spaces around assignment",
                line_start=2,
                line_end=2,
            ),
        ],
    },
}

BUG_SNIPPETS = {
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "function findElement(arr, index) {\n    return arr[index];\n}\n\nconst data = [1, 2, 3];\nconsole.log(findElement(data, 3));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one error index is out of bounds for array",
                line_start=2,
                line_end=2,
                fix_suggestion="Check bounds or adjust index",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No bounds checking on index parameter",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "function process(items) {\n    let result = [];\n    for (let i = 0; i <= items.length; i++) {\n        result.push(items[i] * 2);\n    }\n    return result;\n}\n\nconsole.log(process([1, 2, 3]));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one error should use less than not less than or equal",
                line_start=3,
                line_end=3,
                fix_suggestion="i <= items.length -> i < items.length",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Will access undefined on last iteration causing NaN",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py001": {
        "language": Language.PYTHON,
        "code": "def append_to(element, to=[]):\n    to.append(element)\n    return to\n\nprint(append_to(1))\nprint(append_to(2))\nprint(append_to(3))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Mutable default argument causes state to persist across calls",
                line_start=1,
                line_end=1,
                fix_suggestion="Use to=None and check inside function",
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": 'def check_value(x):\n    if x == True:\n        return "yes"\n    elif x == False:\n        return "no"\n    else:\n        return "unknown"\n\nprint(check_value(1))\nprint(check_value(0))',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Using equality operator with boolean instead of identity operator",
                line_start=2,
                line_end=2,
                fix_suggestion="Use is True or if x pattern",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Same issue on line 4",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": "function getFirstElement<T>(arr: T[]): T {\n    return arr[0];\n}\n\nconst nums: number[] = [];\nconsole.log(getFirstElement(nums));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No null check returns undefined for empty array",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Empty array passed without validation",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": 'const users = [\n    { name: "Alice", age: 25 },\n    { name: "Bob", age: 30 }\n];\n\nfunction findUser(name) {\n    for (let i = 0; i <= users.length; i++) {\n        if (users[i].name === name) {\n            return users[i];\n        }\n    }\n}\n\nconsole.log(findUser("Alice"));',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one in loop condition",
                line_start=6,
                line_end=6,
                fix_suggestion="i <= users.length -> i < users.length",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Will throw error when i equals users.length",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": 'def multiply(a, b):\n    return a * b\n\nresult = multiply(10, "5")\nprint(result)',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No type checking multiplying int by string produces unexpected result",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Result is 10 repeated 5 times instead of 50",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": 'interface Config {\n    host: string;\n    port: number;\n}\n\nfunction connect(config: Config) {\n    return `Connecting to ${config.host}:${config.port}`;\n}\n\nconnect({ host: "localhost" });',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Missing required property port",
                line_start=9,
                line_end=9,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No validation for missing required field",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No division by zero check",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "def get_item(lst, idx):\n    return lst[idx]\n\nprint(get_item([1, 2, 3], 10))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No index bounds checking",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "function parseJSON(str) {\n    return JSON.parse(str);\n}\n\nconsole.parseJSON('{\"invalid\"}')",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No try-catch for JSON parse error",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "let x = 1;\nfunction foo() {\n    console.log(x);\n    let x = 2;\n}\nfoo()",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Temporal dead zone - variable used before declaration",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "function greet(name: string) {\n    return `Hello, ${name.toUpperCase()}`;\n}\n\ngreet(null)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No null check on parameter",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="null value passed to function expecting string",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "items = [1, 2, 3]\nfor i in range(len(items)):\n    print(items[i + 1])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Index out of bounds on last iteration",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const obj = { a: 1 };\nconsole.log(obj.b.c);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Accessing nested property on undefined",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "def update_dict(d, key, value):\n    d[key] = value\n    return d\n\noriginal = {'a': 1}\nupdated = update_dict(original, 'b', 2)\nprint(original)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Mutating input dictionary",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const arr = [1, 2, 3];\narr.push(4);\narr.push(5);\nconsole.log(arr.length);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Array mutated without tracking length",
                line_start=2,
                line_end=3,
            ),
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "interface User {\n    name: string;\n    age?: number;\n}\n\nconst user: User = { name: 'John' };\nconsole.log(user.age.toFixed(2));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Calling method on possibly undefined property",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "def find_in_list(lst, target):\n    for i in range(len(lst)):\n        if lst[i] == target:\n            return i\n    return -1\n\nprint(find_in_list([1, 2, 3], 5))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Using -1 as error indicator without checking",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "async function fetchData() {\n    const response = await fetch('/api/data');\n    return response;\n}\n\nconst data = fetchData();\nconsole.log(data.name);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Accessing promise result without await",
                line_start=6,
                line_end=6,
            ),
        ],
    },
}

SECURITY_SNIPPETS = {
    "py001": {
        "language": Language.PYTHON,
        "code": 'import sqlite3\n\ndef get_user(user_id):\n    conn = sqlite3.connect("app.db")\n    cursor = conn.cursor()\n    query = f"SELECT * FROM users WHERE id = {user_id}"\n    cursor.execute(query)\n    result = cursor.fetchone()\n    conn.close()\n    return result\n\nprint(get_user(1))',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability user input directly in query",
                line_start=5,
                line_end=5,
                fix_suggestion="Use parameterized query with question mark placeholder",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No input sanitization on user_id parameter",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No error handling for database operations",
                line_start=4,
                line_end=8,
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": 'import os\n\nAPI_KEY = "sk-1234567890abcdef"\n\ndef get_api_key():\n    return API_KEY\n\ndef call_api():\n    key = get_api_key()\n    print(f"Using API key: {key}")',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded API key in source code",
                line_start=3,
                line_end=3,
                fix_suggestion="Use environment variable or secrets manager",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="API key exposed in function output",
                line_start=8,
                line_end=8,
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "function evaluateExpression(expr) {\n    return eval(expr);\n}\n\nconst userInput = \"alert('xss')\";\nevaluateExpression(userInput);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using eval with user input allows code injection",
                line_start=2,
                line_end=2,
                fix_suggestion="Avoid eval, use safe parser if needed",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No sanitization of userInput",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": 'import pickle\n\ndef load_data(filename):\n    with open(filename, "rb") as f:\n        return pickle.load(f)\n\ndata = load_data("user_data.pkl")\nprint(data)',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using pickle load with untrusted data allows arbitrary code execution",
                line_start=4,
                line_end=4,
                fix_suggestion="Use JSON or safe deserialization",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No validation of file source",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "const crypto = require('crypto');\n\nfunction generateToken() {\n    return Math.random().toString(36).substring(2);\n}\n\nconsole.log(generateToken());",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using Math.random for security token predictable",
                line_start=4,
                line_end=4,
                fix_suggestion="Use crypto randomBytes",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Predictable random values can be guessed leading to vulnerabilities",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": 'function fetchUserData(userId: string) {\n    const url = `https://api.example.com/users/${userId}`;\n    return fetch(url).then(r => r.json());\n}\n\nfetchUserData("1 OR 1=1");',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No input validation or sanitization potential injection",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Direct string interpolation in URL without validation",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Example injection attack shown in line 5",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": 'import subprocess\nimport sys\n\ndef run_command(cmd):\n    return subprocess.call(cmd, shell=True)\n\nrun_command("ls -la " + sys.argv[1])',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Shell injection vulnerability user input in shell True",
                line_start=5,
                line_end=5,
                fix_suggestion="Use list args, not shell True",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No validation of command arguments",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": 'function htmlEscape(str) {\n    return str.replace(/</g, "&lt;").replace(/>/g, "&gt;");\n}\n\nconst userComment = "<script>alert(\'xss\')</script>";\ndocument.innerHTML = htmlEscape(userComment);',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Incomplete HTML escaping missing quotes and other chars",
                line_start=2,
                line_end=2,
                fix_suggestion="Use a proper library like DOMPurify",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Directly setting innerHTML even with escaping is risky",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "const crypto = require('crypto');\n\nfunction generateId() {\n    return Math.random().toString(36).substr(2, 16);\n}\n\nconsole.log(generateId());",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using Math.random for IDs is predictable",
                line_start=4,
                line_end=4,
                fix_suggestion="Use crypto.randomBytes",
            ),
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "const fs = require('fs');\nconst path = require('path');\n\nfunction readUserFile(filename) {\n    const content = fs.readFileSync('/var/www/uploads/' + filename, 'utf8');\n    return content;\n}\n\nreadUserFile('../../../etc/passwd')",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal vulnerability",
                line_start=5,
                line_end=5,
                fix_suggestion="Validate and sanitize file path",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Allowing arbitrary file read",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const http = require('http');\n\nconst options = {\n    hostname: 'example.com',\n    port: 80,\n    path: '/api?token=' + process.env.API_KEY,\n};\n\nhttp.get(options, (res) => { console.log(res); });",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Exposing API key in URL query parameter",
                line_start=7,
                line_end=7,
                fix_suggestion="Use headers for authentication",
            ),
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const express = require('express');\nconst app = express();\n\napp.get('/user/:id', (req, res) => {\n    const query = `SELECT * FROM users WHERE id = ${req.params.id}`;\n    db.query(query, (err, result) => { res.json(result); });\n});",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection via route parameter",
                line_start=5,
                line_end=5,
                fix_suggestion="Use parameterized queries",
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": 'function fetchUserData(userId: string) {\n    const url = `https://api.example.com/users/${userId}`;\n    return fetch(url).then(r => r.json());\n}\n\nfetchUserData("1 OR 1=1");',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No input validation or sanitization potential injection",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Direct string interpolation in URL without validation",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Example injection attack shown in line 5",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "import { exec } from 'child_process';\n\nfunction runCommand(cmd: string) {\n    exec(cmd, (error, stdout, stderr) => {\n        console.log(stdout);\n    });\n}\n\nrunCommand('ls -la ' + process.argv[2]);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection via user input",
                line_start=5,
                line_end=5,
                fix_suggestion="Use execFile with arguments array",
            ),
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "function loadConfig() {\n    const config = require('./config.json');\n    return config;\n}\n\nconst settings = loadConfig();\neval(settings.code);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Loading untrusted code with eval",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using require with unsanitized path",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "const jwt = require('jsonwebtoken');\n\nfunction verifyToken(token: string) {\n    return jwt.verify(token, 'secret-key');\n}\n\nconst decoded = verifyToken(token);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded secret key for JWT",
                line_start=4,
                line_end=4,
                fix_suggestion="Use environment variable for secret",
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": 'import pickle\n\ndef load_data(filename):\n    with open(filename, "rb") as f:\n        return pickle.load(f)\n\ndata = load_data("user_data.pkl")\nprint(data)',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using pickle load with untrusted data allows arbitrary code execution",
                line_start=4,
                line_end=4,
                fix_suggestion="Use JSON or safe deserialization",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No validation of file source",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": 'import subprocess\nimport sys\n\ndef run_command(cmd):\n    return subprocess.call(cmd, shell=True)\n\nrun_command("ls -la " + sys.argv[1])',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Shell injection vulnerability user input in shell True",
                line_start=5,
                line_end=5,
                fix_suggestion="Use list args, not shell True",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No validation of command arguments",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "import yaml\n\ndef load_config(filename):\n    with open(filename) as f:\n        return yaml.load(f, Loader=yaml.FullLoader)\n\nconfig = load_config('config.yaml')\nexec(config['code'])",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via yaml load",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using yaml FullLoader is unsafe",
                line_start=4,
                line_end=4,
                fix_suggestion="Use yaml.safe_load",
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "import hashlib\nimport secrets\n\ndef generate_token():\n    return hashlib.md5(secrets.token_bytes(16)).hexdigest()\n\nprint(generate_token())",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using MD5 for security tokens is insecure",
                line_start=4,
                line_end=4,
                fix_suggestion="Use hashlib.sha256 or secrets.token_urlsafe",
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "import base64\n\ndef decode_secret(encoded):\n    return base64.b64decode(encoded).decode('utf-8')\n\nsecret = decode_secret('c2VjcmV0LWtleQ==')\nprint(secret)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Base64 encoding is not encryption",
                line_start=3,
                line_end=3,
                fix_suggestion="Use proper encryption like cryptography library",
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "from werkzeug.security import generate_password_hash\n\npassword = \"password123\"\nhash = generate_password_hash(password, method='pbkdf2:sha256')\nprint(hash)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using weak hashing method",
                line_start=3,
                line_end=3,
                fix_suggestion="Use bcrypt or argon2",
            ),
        ],
    },
    "py009": {
        "language": Language.PYTHON,
        "code": "import os\nimport glob\n\ndef list_files(directory):\n    return glob.glob(directory + '/*')\n\nfiles = list_files('/tmp/' + os.getenv('USER_INPUT'))\nprint(files)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal via environment variable",
                line_start=5,
                line_end=5,
                fix_suggestion="Validate and sanitize path input",
            ),
        ],
    },
    "py010": {
        "language": Language.PYTHON,
        "code": "import tempfile\nimport os\n\ndef create_temp_file(content):\n    fd, path = tempfile.mkstemp()\n    os.write(fd, content)\n    os.close(fd)\n    return path\n\npath = create_temp_file(b'secret data')\nos.chmod(path, 0o777)\nprint(path)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Temporary file with world-readable permissions",
                line_start=8,
                line_end=8,
                fix_suggestion="Use restrictive file permissions",
            ),
        ],
    },
}

CODE_SNIPPETS = {
    TaskName.STYLE_CHECK: STYLE_SNIPPETS,
    TaskName.BUG_HUNT: BUG_SNIPPETS,
    TaskName.FULL_REVIEW: SECURITY_SNIPPETS,
}


class MyEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    MAX_STEPS = {
        TaskName.STYLE_CHECK: 5,
        TaskName.BUG_HUNT: 7,
        TaskName.FULL_REVIEW: 10,
    }

    def __init__(self):
        self._state = CodeReviewState()
        self._task_name = TaskName.STYLE_CHECK
        self._found_issues: List[FoundIssue] = []
        self._initial_issue_count = 0

    def reset(
        self, seed=None, episode_id=None, task_name: str = "style_check", **kwargs
    ) -> CodeReviewObservation:
        self._task_name = TaskName(task_name)

        snippets = CODE_SNIPPETS.get(self._task_name, STYLE_SNIPPETS)

        snippet_ids = sorted(snippets.keys())
        if seed is not None:
            random.seed(seed)
            idx = random.randint(0, len(snippet_ids) - 1)
        else:
            idx = 0

        snippet_id = snippet_ids[idx]
        snippet = snippets[snippet_id]

        self._found_issues = []
        self._initial_issue_count = len(snippet["issues"])

        self._state = CodeReviewState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            target_snippet_id=snippet_id,
            ground_truth_issues=list(snippet["issues"]),
            current_score=0.0,
            task_name=self._task_name,
            language=snippet["language"],
            code_snippet=snippet["code"],
        )

        return CodeReviewObservation(
            done=False,
            reward=None,
            code_snippet=snippet["code"],
            issues_found=[],
            issues_remaining=self._initial_issue_count,
            step_count=0,
            message=f"Task: {self._task_name.value}. Find all issues in this {snippet['language'].value} code snippet.",
            task_name=self._task_name,
            language=snippet["language"],
        )

    def step(
        self, action: CodeReviewAction, timeout_s=None, **kwargs
    ) -> CodeReviewObservation:
        self._state.step_count += 1

        if action.description.lower() == "done":
            return self._build_observation(
                done=True, reward=0.0, message="Agent finished early"
            )

        for fi in self._found_issues:
            if (
                fi.line_number == action.line_number
                and fi.issue_type == action.issue_type
            ):
                return self._build_observation(
                    done=False,
                    reward=0.0,
                    message="Duplicate issue already reported",
                )

        match = self._match_issue(action)

        found_issue = FoundIssue(
            issue_type=action.issue_type,
            description=action.description,
            line_number=action.line_number,
            fix_suggestion=action.fix_suggestion,
            is_correct=match["matched"],
        )

        self._found_issues.append(found_issue)

        if match["matched"]:
            reward = self._calculate_reward(action, match)

            self._state.ground_truth_issues = [
                gt
                for gt in self._state.ground_truth_issues
                if not (
                    gt.issue_type == action.issue_type
                    and gt.line_start <= action.line_number <= gt.line_end
                )
            ]
        else:
            reward = 0.0

        self._state.current_score = min(1.0, self._state.current_score + reward)

        issues_remaining = len(self._state.ground_truth_issues)

        done = (
            issues_remaining == 0
            or self._state.step_count >= self.MAX_STEPS[self._task_name]
        )

        return self._build_observation(done, reward, match["message"])

    def _match_issue(self, action: CodeReviewAction) -> dict:
        for gt in self._state.ground_truth_issues:
            if gt.issue_type != action.issue_type:
                continue

            if not (gt.line_start <= action.line_number <= gt.line_end):
                continue

            if self._description_matches(gt.description, action.description):
                return {
                    "matched": True,
                    "issue": gt,
                    "message": f"Correct: {gt.description}",
                }

        return {
            "matched": False,
            "issue": None,
            "message": "No matching issue found. Check line number and issue type.",
        }

    def _description_matches(self, gt: str, rep: str) -> bool:
        gt_words = set(re.findall(r"\b\w+\b", gt.lower()))
        rep_words = set(re.findall(r"\b\w+\b", rep.lower()))
        return len(gt_words & rep_words) >= 2

    def _calculate_reward(self, action: CodeReviewAction, match: dict) -> float:
        issue_weight = 1.0 / self._initial_issue_count
        matched_issue = match["issue"]

        if self._task_name != TaskName.FULL_REVIEW:
            return issue_weight

        if matched_issue.fix_suggestion is None:
            return issue_weight

        if action.fix_suggestion is None:
            return issue_weight * 0.5

        if self._description_matches(
            matched_issue.fix_suggestion, action.fix_suggestion
        ):
            return issue_weight

        return issue_weight * 0.5

    def _build_observation(
        self, done: bool, reward: float, message: str
    ) -> CodeReviewObservation:
        return CodeReviewObservation(
            done=done,
            reward=reward,
            code_snippet=self._state.code_snippet,
            issues_found=self._found_issues.copy(),
            issues_remaining=len(self._state.ground_truth_issues),
            step_count=self._state.step_count,
            message=message,
            task_name=self._task_name,
            language=self._state.language,
        )

    @property
    def state(self) -> CodeReviewState:
        return self._state
