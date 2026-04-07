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
    # PYTHON STYLE - 25 snippets
    "py001": {
        "language": Language.PYTHON,
        "code": "from django.db import models\nclass User(models.Model):\n    name = models.CharField(max_length=100)\n    email = models.EmailField()\n    created = models.DateTimeField(auto_now_add=True)\n    def __str__(self): return self.name",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Model should have verbose_name and help_text for fields",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": "import pytest\ndef test_login():\n    assert login('admin', 'password') == True\ndef test_logout():\n    assert logout() == False",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="No setup/teardown for test isolation",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "data = {'name': 'John', 'age': 30, 'city': 'NYC'}\nfor key in data.keys():\n    print(key, data[key])",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use data.items() instead of keys() + indexing",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "result = []\nfor i in range(10):\n    if i % 2 == 0:\n        result.append(i)\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension: [i for i in range(10) if i % 2 == 0]",
                line_start=2,
                line_end=4,
            )
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "try:\n    data = json.loads(text)\nexcept:\n    print('error')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Bare except catches everything - specify exception type",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "from typing import List\ndef get_items() -> List:\n    return ['a', 'b', 'c']",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use List[str] instead of plain List for type safety",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "if x > 0 and y > 0 and z > 0:\n    print('positive')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use all() for readability: if all([x>0, y>0, z>0])",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "print('Hello ' + name + '!')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-string instead of concatenation",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py009": {
        "language": Language.PYTHON,
        "code": "if flag == True:\n    do_something()",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use 'if flag:' instead of 'if flag == True:'",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py010": {
        "language": Language.PYTHON,
        "code": "items = [1,2,3,4,5]\nfiltered = []\nfor item in items:\n    if item > 2:\n        filtered.append(item)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension instead of append loop",
                line_start=2,
                line_end=4,
            )
        ],
    },
    "py011": {
        "language": Language.PYTHON,
        "code": "text = 'hello world'\nwords = text.split(' ')\ncount = len(words)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use text.split() without argument for whitespace",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py012": {
        "language": Language.PYTHON,
        "code": "for i in range(len(items)):\n    print(items[i])",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use enumerate(items) instead of range(len())",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py013": {
        "language": Language.PYTHON,
        "code": "def foo(x, y=10, z):\n    return x + y + z",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Non-default parameter follows default parameter",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py014": {
        "language": Language.PYTHON,
        "code": "import time\ntime.sleep(1)",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Unused import time - remove or use it",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py015": {
        "language": Language.PYTHON,
        "code": "output = ''\nfor item in items:\n    output += str(item) + ','",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use join instead of string concatenation in loop",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py016": {
        "language": Language.PYTHON,
        "code": "if condition:\n    return True\nelse:\n    return False",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Simplify to 'return condition'",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "py017": {
        "language": Language.PYTHON,
        "code": "class Foo:\n    def bar(self):\n        pass",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Add docstring to class",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py018": {
        "language": Language.PYTHON,
        "code": "if x < 5:\n    print('small')\nelif x < 10:\n    print('medium')\nelif x < 15:\n    print('large')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use match/case for multiple conditions",
                line_start=1,
                line_end=5,
            )
        ],
    },
    "py019": {
        "language": Language.PYTHON,
        "code": "temp = a\na = b\nb = temp",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use tuple unpacking: a, b = b, a",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "py020": {
        "language": Language.PYTHON,
        "code": "from module import *",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid wildcard imports - specify what you need",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py021": {
        "language": Language.PYTHON,
        "code": "config = {'debug': True, 'port': 8080}\nif config['debug'] == True:\n    print('Debug mode')",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use config.get() with default for missing keys",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py022": {
        "language": Language.PYTHON,
        "code": "def process(items):\n    result = {}\n    for item in items:\n        result[item.id] = item\n    return result",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use dict comprehension: {item.id: item for item in items}",
                line_start=2,
                line_end=4,
            )
        ],
    },
    "py023": {
        "language": Language.PYTHON,
        "code": "x = 1\nwhile x < 100:\n    x += 1",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use range(1, 100) instead of while loop",
                line_start=1,
                line_end=2,
            )
        ],
    },
    "py024": {
        "language": Language.PYTHON,
        "code": "data = [(1, 'a'), (2, 'b'), (3, 'c')]\nids = []\nfor item in data:\n    ids.append(item[0])",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension: [item[0] for item in data]",
                line_start=2,
                line_end=4,
            )
        ],
    },
    "py025": {
        "language": Language.PYTHON,
        "code": "def greet(name):\n    return 'Hello ' + name.title() + '!'",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Add type hints: def greet(name: str) -> str:",
                line_start=1,
                line_end=1,
            )
        ],
    },
    # JAVASCRIPT STYLE - 25 snippets
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "const users = ['alice', 'bob', 'charlie'];\nusers.forEach(function(user) {\n    console.log(user);\n});",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function: users.forEach(user => console.log(user))",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "function getData() {\n    var data = fetch('/api/data');\n    return data;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const/let instead of var",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": "if (user !== null && user !== undefined) {\n    console.log(user.name);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use optional chaining: user?.name",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "const result = arr.filter(x => x > 5).map(x => x * 2).reduce((a, b) => a + b, 0);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Chain is too long - break into separate variables",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "const handler = function(event) {\n    event.preventDefault();\n    console.log(event.target);\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function with named function for readability",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const ids = users.map(function(user) {\n    return user.id;\n});",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use concise arrow: users.map(u => u.id)",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "if (items.length > 0) {\n    return items[0];\n} else {\n    return null;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use nullish coalescing: items[0] ?? null",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "async function fetchData() {\n    const response = await fetch(url);\n    const data = response.json();\n    return data;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Add error handling with try-catch",
                line_start=1,
                line_end=4,
            )
        ],
    },
    "js009": {
        "language": Language.JAVASCRIPT,
        "code": "const config = {\n    apiKey: 'abc123',\n    debug: true,\n    timeout: 5000\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Move to environment variables",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js010": {
        "language": Language.JAVASCRIPT,
        "code": "users.forEach((user, index) => {\n    console.log(index + ': ' + user.name);\n});",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literals: `${index}: ${user.name}`",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js011": {
        "language": Language.JAVASCRIPT,
        "code": "function handleClick(e) {\n    e.preventDefault();\n    e.stopPropagation();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Extract to named function for reusability",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js012": {
        "language": Language.JAVASCRIPT,
        "code": "const keys = Object.keys(obj);\nfor (let i = 0; i < keys.length; i++) {\n    console.log(obj[keys[i]]);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use Object.values or Object.entries",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js013": {
        "language": Language.JAVASCRIPT,
        "code": "const data = JSON.stringify(user, null, 2);\nconsole.log(data);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use JSON.stringify with replacer for circular refs",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js014": {
        "language": Language.JAVASCRIPT,
        "code": "if (status === 200 || status === 201 || status === 204) {\n    return true;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use array.includes: [200, 201, 204].includes(status)",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js015": {
        "language": Language.JAVASCRIPT,
        "code": "function createUser(name, email, age) {\n    return { name: name, email: email, age: age };\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use shorthand: { name, email, age }",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js016": {
        "language": Language.JAVASCRIPT,
        "code": "const filtered = items.filter(x => x !== null).filter(x => x !== undefined);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Combine filters: items.filter(x => x != null)",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js017": {
        "language": Language.JAVASCRIPT,
        "code": "document.querySelector('#submit').addEventListener('click', () => {\n    form.submit();\n});",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Check element exists before adding listener",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js018": {
        "language": Language.JAVASCRIPT,
        "code": "const timeout = setTimeout(() => {\n    console.log('done');\n}, 1000);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Store timeout ID for potential cleanup",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js019": {
        "language": Language.JAVASCRIPT,
        "code": "const date = new Date(2024, 0, 1);\nconsole.log(date.getMonth() + '/' + date.getDate());",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use Intl.DateTimeFormat for proper formatting",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js020": {
        "language": Language.JAVASCRIPT,
        "code": "const regex = new RegExp(pattern, 'g');\nconst matches = str.match(regex);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use literal regex: /pattern/g when possible",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js021": {
        "language": Language.JAVASCRIPT,
        "code": "class UserService {\n    constructor() {\n        this.baseUrl = 'http://localhost:3000';\n    }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Move baseUrl to constructor parameter",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js022": {
        "language": Language.JAVASCRIPT,
        "code": "const result = value !== null && value !== undefined ? value : defaultValue;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use nullish coalescing: value ?? defaultValue",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js023": {
        "language": Language.JAVASCRIPT,
        "code": "const items = [1, 2, 3, 4, 5];\nconst total = 0;\nfor (const item of items) {\n    total += item;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use reduce: items.reduce((a, b) => a + b, 0)",
                line_start=2,
                line_end=4,
            )
        ],
    },
    "js024": {
        "language": Language.JAVASCRIPT,
        "code": "const params = new URLSearchParams();\nparams.set('page', '1');\nparams.set('limit', '10');",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use object: new URLSearchParams({ page: '1', limit: '10' })",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "js025": {
        "language": Language.JAVASCRIPT,
        "code": "async function loadData() {\n    const cached = localStorage.getItem('data');\n    if (cached) return JSON.parse(cached);\n    const response = await fetch('/api/data');\n    const data = await response.json();\n    localStorage.setItem('data', JSON.stringify(data));\n    return data;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Add expiration logic to cache",
                line_start=1,
                line_end=7,
            )
        ],
    },
    # TYPESCRIPT STYLE - 25 snippets
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": "interface User {\n    id: number;\n    name: string;\n}\nfunction getUser(id: number): User {\n    return { id, name: 'John' };\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Add return type to interface method",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "const handleSubmit = (data: any) => {\n    console.log(data);\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid any type - define proper type",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "type Status = 'pending' | 'active' | 'completed';\nconst status: Status = 'pending';\nconst status2: Status = 'unknown';",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="TypeScript should error on 'unknown' - this is test case",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "class Handler {\n    private data: string;\n    constructor() { this.data = ''; }\n    getData(): string { return this.data; }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Initialize in constructor parameter",
                line_start=1,
                line_end=4,
            )
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "const parse = (input: string): any => {\n    return JSON.parse(input);\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Return specific type instead of any",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": "interface Config {\n    url: string;\n    timeout?: number;\n}\nconst config: Config = { url: '/api', timeout: undefined };",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Omit optional properties when undefined",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": "type Callback = (error: Error, data: string) => void;\nfunction invoke(cb: Callback) {\n    cb(null, 'success');\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use Promise-based callbacks or async/await",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "interface Response<T> {\n    data: T;\n    status: number;\n}\nconst response: Response = { data: {}, status: 200 };",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Generic type not provided - use Response<T>",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "ts009": {
        "language": Language.TYPESCRIPT,
        "code": "function process(items: Array<any>) {\n    return items.map(x => x);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use Array<T> instead of Array<any>",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts010": {
        "language": Language.TYPESCRIPT,
        "code": "class Service {\n    private endpoint: string = 'http://api.com';\n    private apiKey: string = 'secret123';\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Move sensitive data to environment",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts011": {
        "language": Language.TYPESCRIPT,
        "code": "const keys: ReadonlyArray<string> = Object.keys(obj) as string[];",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use type predicate or proper casting",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts012": {
        "language": Language.TYPESCRIPT,
        "code": "const value = data as string as number;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Double casting indicates type design issue",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts013": {
        "language": Language.TYPESCRIPT,
        "code": "interface Options {\n    [key: string]: any;\n}\nconst opts: Options = { debug: true };",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use Record<string, T> instead of index signature",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts014": {
        "language": Language.TYPESCRIPT,
        "code": "const handler = (event: Event) => {\n    const target = event.target as HTMLInputElement;\n    console.log(target.value);\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Check target is HTMLInputElement",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts015": {
        "language": Language.TYPESCRIPT,
        "code": "type JsonObject = { [key: string]: JsonValue };\ntype JsonValue = string | number | JsonObject;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use built-in unknown for JSON types",
                line_start=1,
                line_end=2,
            )
        ],
    },
    "ts016": {
        "language": Language.TYPESCRIPT,
        "code": "const fetchData = async (url: string): Promise<Response> => {\n    const response = await fetch(url);\n    return response;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Check response.ok before returning",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "ts017": {
        "language": Language.TYPESCRIPT,
        "code": "type UserRole = 'admin' | 'user' | 'guest';\nconst role: UserRole = 'superadmin';",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Invalid role - TypeScript should catch this",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts018": {
        "language": Language.TYPESCRIPT,
        "code": "class Manager {\n    private employees: Employee[];\n    addEmployee(emp: Employee) {\n        this.employees.push(emp);\n    }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Initialize employees in constructor",
                line_start=1,
                line_end=4,
            )
        ],
    },
    "ts019": {
        "language": Language.TYPESCRIPT,
        "code": "const config = {\n    env: process.env.NODE_ENV || 'development'\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Type process.env properly",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts020": {
        "language": Language.TYPESCRIPT,
        "code": "interface Handler {\n    (event: Event): void;\n    priority: number;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use type alias for callable interface",
                line_start=1,
                line_end=3,
            )
        ],
    },
    "ts021": {
        "language": Language.TYPESCRIPT,
        "code": "const clone = (obj: object): object => {\n    return { ...obj };\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use proper generic: <T extends object>(obj: T): T",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts022": {
        "language": Language.TYPESCRIPT,
        "code": "type Result<T> = { success: true; data: T } | { success: false; error: string };\nfunction handle(result: Result<string>) {\n    if (result.success) {\n        console.log(result.data.toUpperCase());\n    }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use type narrowing properly",
                line_start=3,
                line_end=4,
            )
        ],
    },
    "ts023": {
        "language": Language.TYPESCRIPT,
        "code": "const validate = (value: string | null): boolean => {\n    return value !== null && value.length > 0;\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use non-null assertion or proper null check",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts024": {
        "language": Language.TYPESCRIPT,
        "code": "enum Status {\n    Pending = 0,\n    Active = 1,\n}\nconst status: number = Status.Pending;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const enum or union type",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "ts025": {
        "language": Language.TYPESCRIPT,
        "code": "function transform<T>(input: T): T {\n    return JSON.parse(JSON.stringify(input));\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Deep clone is unnecessary for many cases",
                line_start=1,
                line_end=1,
            )
        ],
    },
}

BUG_SNIPPETS = {
    # PYTHON BUG - 25 snippets
    "py001": {
        "language": Language.PYTHON,
        "code": "def get_first(items):\n    return items[0]\nprint(get_first([]))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="IndexError on empty list",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": "data = {'a': 1, 'b': 2}\nvalue = data['c']",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="KeyError when key doesn't exist",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "result = []\nfor i in range(10):\n    if i % 2:\n        result.append(i)\nprint(sum(result))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Logic error - i%2 is truthy for odd, not even numbers",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "def divide(a, b):\n    return a / b\nprint(divide(10, 0))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="ZeroDivisionError",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "text = 'hello'\nprint(text[10])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="String index out of range",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "items = [1, 2, 3]\nfor item in items:\n    if item == 2:\n        items.remove(item)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="RuntimeError during iteration - use list comprehension",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "data = {'name': 'John', 'age': '30'}\nage = int(data['age'])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Works here but fails if string contains non-numeric",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "def func(x, items=[]):\n    items.append(x)\n    return items\nprint(func(1))\nprint(func(2))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Mutable default argument persists between calls",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py009": {
        "language": Language.PYTHON,
        "code": "value = 'True'\nif value:\n    print('yes')\nelse:\n    print('no')",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="String 'True' is truthy but not boolean True",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py010": {
        "language": Language.PYTHON,
        "code": "import json\ndata = json.loads('{\"key\": \"value\"}')\nprint(data['key2'])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="KeyError on missing key",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py011": {
        "language": Language.PYTHON,
        "code": "class Counter:\n    def __init__(self):\n        self.count = 0\n    def increment(self):\n        self.count += 1\nc1 = Counter()\nc2 = Counter\nc2.increment()",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="c2 is class, not instance - missing parentheses",
                line_start=7,
                line_end=7,
            )
        ],
    },
    "py012": {
        "language": Language.PYTHON,
        "code": "result = 0\nfor i in range(5):\n    result = result + i\nprint(result)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Sum includes 0-4 but should be 1-5 or use range(1,6)",
                line_start=2,
                line_end=3,
            )
        ],
    },
    "py013": {
        "language": Language.PYTHON,
        "code": "text = 'hello world'\nwords = text.split()\nfor i in range(len(words)):\n    words[i] = words[i].capitalize()",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Modifying list while iterating - unexpected results",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py014": {
        "language": Language.PYTHON,
        "code": "import math\nvalue = math.sqrt(-1)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="ValueError: math domain error for negative",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py015": {
        "language": Language.PYTHON,
        "code": "data = [1, 'two', 3]\nresult = sum(data)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: cannot sum int and str",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py016": {
        "language": Language.PYTHON,
        "code": "items = [1,2,3]\nitem = items.pop()\nprint(item)\nitems.pop()\nitems.pop()\nprint(items[0])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="IndexError after popping more than length",
                line_start=6,
                line_end=6,
            )
        ],
    },
    "py017": {
        "language": Language.PYTHON,
        "code": "text = 'hello'\nfor i in range(len(text)):\n    print(text[i+1])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="IndexError on last iteration",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py018": {
        "language": Language.PYTHON,
        "code": "result = None\nif result is not None:\n    print(result.name)\nprint(result.name)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="AttributeError on None",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "py019": {
        "language": Language.PYTHON,
        "code": "data = [{'id': 1}, {'id': 2}]\nfor item in data:\n    if item['id'] == 1:\n        del item",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="RuntimeError during iteration",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py020": {
        "language": Language.PYTHON,
        "code": "class Person:\n    def __init__(self, name):\n        self.name = name\np = Person()",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: missing required argument",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "py021": {
        "language": Language.PYTHON,
        "code": "numbers = [1, 2, 3, 4, 5]\navg = sum(numbers) / len(numbers[:-1])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one: divides by 4 not 5",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py022": {
        "language": Language.PYTHON,
        "code": "import re\npattern = r'(\\d+)'\ntext = 'abc123def'\nmatch = re.search(pattern, text)\nprint(match.group(0))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Works but match.group(1) would return just number",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "py023": {
        "language": Language.PYTHON,
        "code": "data = {'a': 1, 'b': 2}\nif 'c' in data:\n    print(data['c'])",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Dead code - condition always false",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py024": {
        "language": Language.PYTHON,
        "code": "x = 5\ny = 10\nx, y = y, x\nprint(x, y)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Works correctly - but edge case if swapping same variable",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py025": {
        "language": Language.PYTHON,
        "code": "def get_nested(data, key1, key2):\n    return data[key1][key2]\nprint(get_nested({'a': {}}, 'a', 'b'))",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="KeyError on nested access",
                line_start=2,
                line_end=2,
            )
        ],
    },
    # JAVASCRIPT BUG - 25 snippets
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "const items = [1, 2, 3];\nconsole.log(items[5]);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="undefined for out of bounds index",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "const obj = { a: 1 };\nconsole.log(obj.b.c);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: Cannot read property 'c' of undefined",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": "const nums = [1, 2, 3];\nfor (let i = 0; i <= nums.length; i++) {\n    console.log(nums[i]);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one: logs undefined on last iteration",
                line_start=2,
                line_end=3,
            )
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "async function getData() {\n    return fetch('/api').then(r => r.json());\n}\nconst data = getData();\nconsole.log(data.results);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="getData returns Promise, not data object",
                line_start=5,
                line_end=5,
            )
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "const users = [{name: 'Alice'}, {name: 'Bob'}];\nconst user = users.find(u => u.name === 'Charlie');\nconsole.log(user.name);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: Cannot read name of undefined",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const arr = [1, 2, 3];\narr.push(4);\narr = [5, 6];",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: const cannot be reassigned",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const result = '5' + 3;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="String concatenation: result is '53' not 8",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "const value = null;\nconsole.log(value.property);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeError: Cannot read property of null",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js009": {
        "language": Language.JAVASCRIPT,
        "code": "const items = [1, 2, 3];\nitems.forEach(i => {\n    if (i === 2) return;\n    console.log(i);\n});",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="return in forEach doesn't break - continues to next",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js010": {
        "language": Language.JAVASCRIPT,
        "code": "function foo() { console.log(this); }\nfoo();",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="this is undefined in strict mode, window otherwise",
                line_start=1,
                line_end=2,
            )
        ],
    },
    "js011": {
        "language": Language.JAVASCRIPT,
        "code": "const nums = [1, 2, 3];\nconst doubled = nums.map(i => { i * 2; });",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="map returns [undefined, undefined, undefined] - missing return",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js012": {
        "language": Language.JAVASCRIPT,
        "code": "const obj = {};\nobj[undefined] = 'value';\nconsole.log(obj[null]);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="undefined and null are different keys",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js013": {
        "language": Language.JAVASCRIPT,
        "code": "const date = new Date('invalid');\nconsole.log(date.getTime());",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Invalid Date returns NaN",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js014": {
        "language": Language.JAVASCRIPT,
        "code": "const str = 'hello';\nstr[0] = 'H';\nconsole.log(str);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Strings are immutable - assignment is ignored",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js015": {
        "language": Language.JAVASCRIPT,
        "code": "const x = 0.1 + 0.2;\nconsole.log(x === 0.3);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Floating point precision: false, x is 0.30000000000000004",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js016": {
        "language": Language.JAVASCRIPT,
        "code": "const users = ['a', 'b'];\nconsole.log(users[users.length]);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Index out of bounds - returns undefined",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js017": {
        "language": Language.JAVASCRIPT,
        "code": "function test(a, b) {\n    return a + b;\n}\nconsole.log(test(1));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="b is undefined, returns NaN",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js018": {
        "language": Language.JAVASCRIPT,
        "code": "const data = {name: 'John'};\ndelete data.name;\nconsole.log(data.name);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="property is deleted, returns undefined",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js019": {
        "language": Language.JAVASCRIPT,
        "code": "const obj = {a: 1};\nconst keys = Object.keys(obj);\nkeys.forEach(k => console.log(obj[k.toUpperCase()]));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Key 'A' doesn't exist - undefined",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js020": {
        "language": Language.JAVASCRIPT,
        "code": "const num = '10';\nif (num == 10) console.log('equal');",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Loose equality works but type coercion is confusing",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js021": {
        "language": Language.JAVASCRIPT,
        "code": "const arr = [1, 2, 3];\narr.splice(1, 1, 4, 5);\nconsole.log(arr);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Result is [1, 4, 5, 3] - unexpected for some",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js022": {
        "language": Language.JAVASCRIPT,
        "code": "const fn = () => ({ value: 1 });\nconsole.log(fn().value);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Arrow function returns object correctly, but tricky syntax",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js023": {
        "language": Language.JAVASCRIPT,
        "code": "const items = [{}, {}];\nitems[0] = items[1];\nitems[0].value = 100;\nconsole.log(items[1].value);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Both reference same object - 100, not 0",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "js024": {
        "language": Language.JAVASCRIPT,
        "code": "const str = '5';\nconsole.log(+str + 5);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Unary + converts to 10, but confusing",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js025": {
        "language": Language.JAVASCRIPT,
        "code": "const fn = function() { return 1; };\nfn.key = 'value';\nconsole.log(fn.key);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Function can have properties - but unusual",
                line_start=3,
                line_end=3,
            )
        ],
    },
    # TYPESCRIPT BUG - 25 snippets
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": "function getFirst(arr: string[]): string {\n    return arr[0];\n}\nconsole.log(getFirst([]));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Returns undefined for empty array",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "const user: { name: string } = { name: 'John', age: 30 };",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="TypeScript error: object literal has extra property",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "const nums: number[] = [1, 2, 'three'];",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: string not assignable to number",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "const data: string = null;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: null not assignable to string",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "const obj: Record<string, number> = { a: 1 };\nconsole.log(obj.b);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Property 'b' does not exist on type",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": "const fn = (a: number, b: number) => a + b;\nconsole.log(fn(1));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Expected 2 arguments, got 1",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": "type Value = string | number;\nconst val: Value = true;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: boolean not in union",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "interface Config { url: string; }\nconst cfg: Config = { url: 'http://test.com', timeout: 5000 };",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Object literal has unknown property 'timeout'",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts009": {
        "language": Language.TYPESCRIPT,
        "code": "const result: string = 123;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: number not assignable to string",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts010": {
        "language": Language.TYPESCRIPT,
        "code": "const arr: string[] = [];\narr.push(123);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Argument of type number not assignable to string",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts011": {
        "language": Language.TYPESCRIPT,
        "code": "function process<T>(value: T): T {\n    return value;\n}\nconsole.log(process<string>('hi').toFixed());",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="toFixed doesn't exist on string",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "ts012": {
        "language": Language.TYPESCRIPT,
        "code": "const num: number = parseInt('abc');",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="parseInt returns number but can be NaN",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts013": {
        "language": Language.TYPESCRIPT,
        "code": "const date: Date = '2024-01-01';",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: string not assignable to Date",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts014": {
        "language": Language.TYPESCRIPT,
        "code": "const fn = (x: number) => x * 2;\nconsole.log(fn('5'));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Argument of type string not assignable to number",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts015": {
        "language": Language.TYPESCRIPT,
        "code": "type User = { name: string };\nconst user: User = null;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: null not assignable to User",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts016": {
        "language": Language.TYPESCRIPT,
        "code": "const keys = Object.keys({a: 1});\nconsole.log(keys.toUpperCase());",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="keys is string[], toUpperCase is on string",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts017": {
        "language": Language.TYPESCRIPT,
        "code": "class Container<T> {\n    private value: T;\n}\nconst c = new Container<string>();\nc.value = 123;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Argument of type number not assignable to string",
                line_start=4,
                line_end=4,
            )
        ],
    },
    "ts018": {
        "language": Language.TYPESCRIPT,
        "code": "const func: () => void = () => 'return string';",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: return string not assignable to void",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts019": {
        "language": Language.TYPESCRIPT,
        "code": "const data: Array<{id: number}> = [{id: 1}];\nconsole.log(data[0].name);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Property 'name' does not exist",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts020": {
        "language": Language.TYPESCRIPT,
        "code": "const handler = (e: MouseEvent) => e.clientX;\ndocument.addEventListener('keydown', handler);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Event type mismatch: keydown event is KeyboardEvent",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts021": {
        "language": Language.TYPESCRIPT,
        "code": "type Result<T> = T extends string ? number : boolean;\nconst r1: Result<string> = 'hello';\nconst r2: Result<number> = true;",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Type error: string not assignable to number",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts022": {
        "language": Language.TYPESCRIPT,
        "code": "interface Person { name: string; }\nconst p: Partial<Person> = {};\nconsole.log(p.name.toUpperCase());",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Property 'name' is optional, can be undefined",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "ts023": {
        "language": Language.TYPESCRIPT,
        "code": "const val: unknown = 'test';\nconsole.log(val.toUpperCase());",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Property 'toUpperCase' does not exist on unknown",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts024": {
        "language": Language.TYPESCRIPT,
        "code": "const fn = <T>(arr: T[]): T => arr[0];\nconsole.log(fn([]));",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Returns undefined for empty array",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts025": {
        "language": Language.TYPESCRIPT,
        "code": "const callback: (err: Error) => void = (err) => { throw err; };",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Throwing in callback can crash caller",
                line_start=1,
                line_end=1,
            )
        ],
    },
}

SECURITY_SNIPPETS = {
    # PYTHON SECURITY - 25 snippets
    "py001": {
        "language": Language.PYTHON,
        "code": 'query = f"SELECT * FROM users WHERE id = {user_id}"\ncursor.execute(query)',
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": "os.system('rm -rf ' + user_input)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "import pickle\ndata = pickle.loads(user_data)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Pickle deserialization vulnerability",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "password = 'admin123'\nif check_password(password): login()",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded password in source",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "eval(user_expression)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via eval",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "secret_key = 'sk-1234567890abcdef'\napi_key = base64.b64encode(secret_key)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Encoding is not encryption",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "subprocess.run(cmd, shell=True)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="shell=True enables command injection",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "user_file = open(user_path, 'r')\ncontent = user_file.read()",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal vulnerability",
                line_start=1,
                line_end=2,
            )
        ],
    },
    "py009": {
        "language": Language.PYTHON,
        "code": "yaml.load(data, Loader=yaml.FullLoader)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="YAML deserialization attack",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py010": {
        "language": Language.PYTHON,
        "code": "jwt.encode(payload, 'secret', algorithm='HS256')",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Weak JWT secret or algorithm",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py011": {
        "language": Language.PYTHON,
        "code": "session['user_id'] = user_id\nsession['role'] = 'admin'",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Session stored without proper serialization",
                line_start=1,
                line_end=2,
            )
        ],
    },
    "py012": {
        "language": Language.PYTHON,
        "code": "import hashlib\nhash = hashlib.md5(password).hexdigest()",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 is cryptographically broken",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py013": {
        "language": Language.PYTHON,
        "code": "xml.etree.parse(user_xml_file)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="XXE vulnerability in XML parsing",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py014": {
        "language": Language.PYTHON,
        "code": "print(f'User: {username}, Password: {password}')",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Sensitive data logged in plain text",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py015": {
        "language": Language.PYTHON,
        "code": "requests.get(url + user_input)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="URL injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py016": {
        "language": Language.PYTHON,
        "code": "import tempfile\nfd, path = tempfile.mkstemp()\nos.chmod(path, 0o777)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="World-readable temp file",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py017": {
        "language": Language.PYTHON,
        "code": "token = secrets.token_urlsafe(8)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Token too short - only 8 bytes",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py018": {
        "language": Language.PYTHON,
        "code": "redis.set(key, user_data)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No TTL on sensitive data in cache",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py019": {
        "language": Language.PYTHON,
        "code": "hmac.new(key, msg, hashlib.md5)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 in HMAC is insecure",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py020": {
        "language": Language.PYTHON,
        "code": "urllib.request.urlopen(url)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No SSL verification by default",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "py021": {
        "language": Language.PYTHON,
        "code": "data = json.loads(user_json)\nexec(data['code'])",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via JSON",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py022": {
        "language": Language.PYTHON,
        "code": "class User: pass\nu = User()\nu.__dict__ = {'is_admin': True}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Object attribute injection",
                line_start=3,
                line_end=3,
            )
        ],
    },
    "py023": {
        "language": Language.PYTHON,
        "code": "config = {'debug': True, 'secret': 'key123'}\neval('config[\"secret\"]')",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using eval with config data",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py024": {
        "language": Language.PYTHON,
        "code": "from cryptography.fernet import Fernet\ncipher = Fernet(key)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using default/weak key",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "py025": {
        "language": Language.PYTHON,
        "code": "logging.basicConfig(level=logging.DEBUG)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Debug logging may expose sensitive data",
                line_start=1,
                line_end=1,
            )
        ],
    },
    # JAVASCRIPT SECURITY - 25 snippets
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "const query = `SELECT * FROM users WHERE id = ${userId}`;\ndb.query(query);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "eval(userInput);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via eval",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": "const token = jwt.sign(payload, 'secret123');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded JWT secret",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "document.cookie = 'token=' + token;",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Cookie without HttpOnly flag",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "exec('rm -rf ' + userFile);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const hash = crypto.createHash('md5').update(password).digest();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 is cryptographically broken",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const html = '<div>' + userContent + '</div>';\nelement.innerHTML = html;",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="XSS vulnerability",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "const key = crypto.randomBytes(8).toString('hex');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Insufficient entropy - only 8 bytes",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js009": {
        "language": Language.JAVASCRIPT,
        "code": "const params = new URLSearchParams(userInput);\nredirect('/?' + params);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Parameter pollution or injection",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js010": {
        "language": Language.JAVASCRIPT,
        "code": "fetch('/api?token=' + localStorage.getItem('token'))",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Token in URL query param",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js011": {
        "language": Language.JAVASCRIPT,
        "code": "const user = JSON.parse(localStorage.getItem('user'));",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No integrity check on stored data",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js012": {
        "language": Language.JAVASCRIPT,
        "code": "const regex = new RegExp(userPattern);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Regex denial of service (ReDoS)",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js013": {
        "language": Language.JAVASCRIPT,
        "code": "process.env.API_KEY = 'secret123';",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Setting env variable at runtime not secure",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js014": {
        "language": Language.JAVASCRIPT,
        "code": "const data = fs.readFileSync('/etc/passwd');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal - arbitrary file read",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js015": {
        "language": Language.JAVASCRIPT,
        "code": "const vm = require('vm');\nvm.runInNewContext(userCode);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via vm",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js016": {
        "language": Language.JAVASCRIPT,
        "code": "const pwd = crypto.createHash('sha1').update(password).digest();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA1 is cryptographically broken",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js017": {
        "language": Language.JAVASCRIPT,
        "code": "socket.emit('message', userData);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="WebSocket without origin check",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js018": {
        "language": Language.JAVASCRIPT,
        "code": "const deserialized = JSON.parse(untrustedData);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="No prototype pollution check",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js019": {
        "language": Language.JAVASCRIPT,
        "code": "function handler(req, res) {\n  res.setHeader('Access-Control-Allow-Origin', '*');\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="CORS allowing all origins",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "js020": {
        "language": Language.JAVASCRIPT,
        "code": "const secret = Buffer.from(password, 'base64');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Encoding is not encryption",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js021": {
        "language": Language.JAVASCRIPT,
        "code": "child_process.execSync(userCommand);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary command execution",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js022": {
        "language": Language.JAVASCRIPT,
        "code": "const session = { userId: user.id, role: 'admin' };",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Role stored in client-side session",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js023": {
        "language": Language.JAVASCRIPT,
        "code": "new Function(userCode)();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via Function constructor",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js024": {
        "language": Language.JAVASCRIPT,
        "code": "const key = '1234567890123456';",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Short encryption key",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "js025": {
        "language": Language.JAVASCRIPT,
        "code": "sessionStorage.setItem('token', token);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Sensitive data in sessionStorage",
                line_start=1,
                line_end=1,
            )
        ],
    },
    # TYPESCRIPT SECURITY - 25 snippets
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": "const query = `SELECT * FROM users WHERE id = ${userId}`;\ndb.query(query);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "const hash = crypto.createHash('md5').update(password).digest('hex');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 is cryptographically broken",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "exec(`rm -rf ${userPath}`);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection vulnerability",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "document.cookie = `token=${token}`;",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Cookie without HttpOnly and Secure flags",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "const fn = new Function(userCode);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via Function constructor",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": "const jwt = require('jsonwebtoken');\nconst token = jwt.sign(payload, 'secret');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded JWT secret",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": "innerHTML = userContent;",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="XSS vulnerability via innerHTML",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "const crypto = require('crypto');\nconst key = crypto.randomBytes(8);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Only 8 bytes of entropy",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts009": {
        "language": Language.TYPESCRIPT,
        "code": "import { exec } from 'child_process';\nexec(`ls ${userDir}`);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection vulnerability",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts010": {
        "language": Language.TYPESCRIPT,
        "code": "const serializer = new Serializer();\nconst data = serializer.unserialize(untrusted);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Insecure deserialization",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts011": {
        "language": Language.TYPESCRIPT,
        "code": "const sha1 = crypto.createHash('sha1').update(data).digest();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA1 is cryptographically broken",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts012": {
        "language": Language.TYPESCRIPT,
        "code": "res.setHeader('Access-Control-Allow-Origin', '*');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="CORS allowing all origins",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts013": {
        "language": Language.TYPESCRIPT,
        "code": "const key = process.env.SECRET || 'default-secret';",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Fallback secret is weak",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts014": {
        "language": Language.TYPESCRIPT,
        "code": "const buffer = Buffer.from(sensitive, 'utf-8');",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Encoding is not encryption",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts015": {
        "language": Language.TYPESCRIPT,
        "code": "fs.writeFileSync('/tmp/' + filename, data);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal in file write",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts016": {
        "language": Language.TYPESCRIPT,
        "code": "eval(userExpression);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via eval",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts017": {
        "language": Language.TYPESCRIPT,
        "code": "const regex = new RegExp(input, 'g');\nregex.test(input);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Regular expression DoS (ReDoS)",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts018": {
        "language": Language.TYPESCRIPT,
        "code": "const hmac = crypto.createHmac('sha1', key).update(data).digest();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA1 in HMAC is insecure",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts019": {
        "language": Language.TYPESCRIPT,
        "code": "const parsed = JSON.parse(userJson);\nparsed.__proto__.isAdmin = true;",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Prototype pollution vulnerability",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts020": {
        "language": Language.TYPESCRIPT,
        "code": "const secure = require('crypto').createCipheriv('aes-128-cbc', key, iv);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Weak cipher AES-128-CBC",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts021": {
        "language": Language.TYPESCRIPT,
        "code": "import { load } from 'js-yaml';\nconst data = load(untrustedYaml);",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="YAML deserialization vulnerability",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts022": {
        "language": Language.TYPESCRIPT,
        "code": "ws.on('message', (data) => {\n  eval(data.toString());\n});",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via WebSocket",
                line_start=2,
                line_end=2,
            )
        ],
    },
    "ts023": {
        "language": Language.TYPESCRIPT,
        "code": "const { data } = await axios.get(url, { params: { apiKey: key } });",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="API key in URL query parameters",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts024": {
        "language": Language.TYPESCRIPT,
        "code": "const session = { userId: 123, role: 'admin' };",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Sensitive role in session data",
                line_start=1,
                line_end=1,
            )
        ],
    },
    "ts025": {
        "language": Language.TYPESCRIPT,
        "code": "new (Function('return ' + userCode))();",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Dynamic code execution vulnerability",
                line_start=1,
                line_end=1,
            )
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
                    done=False, reward=0.0, message="Duplicate issue already reported"
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

    # Keyword groups that indicate the same concept
    KEYWORD_ALIASES = {
        # Style concepts
        "fstring": [
            "f-string",
            "fstring",
            "f string",
            "format string",
            "string interpolation",
            "concatenation",
            "template literal",
            "string formatting",
        ],
        "listcomp": [
            "list comprehension",
            "listcomp",
            "comprehension",
            "append loop",
            "for loop append",
            "filter(",
            "map(",
        ],
        "snakecase": [
            "snake_case",
            "snakecase",
            "snake case",
            "naming convention",
            "camelcase",
            "camel_case",
            "PascalCase",
            "naming style",
        ],
        "docstring": [
            "docstring",
            "doc string",
            "documentation",
            "missing docs",
            "undocumented",
            "jsdoc",
            "comment",
        ],
        "typehinit": [
            "type hint",
            "type annotation",
            "typing",
            "return type",
            "parameter type",
            "List[",
            "type safety",
            ": any",
            "explicit type",
        ],
        "verbosename": [
            "verbose_name",
            "verbose name",
            "help_text",
            "helptext",
            "field metadata",
            "model field",
        ],
        "bareexcept": [
            "bare except",
            "except:",
            "exception type",
            "specific exception",
            "catches everything",
            "catch all",
            "generic exception",
        ],
        "enumerate": ["enumerate", "range(len", "index loop", "for i in range"],
        "items": ["items()", ".items", "keys()", ".keys", "dict iteration"],
        "unused": ["unused", "not used", "never used", "dead code", "unreachable"],
        "arrow": [
            "arrow function",
            "arrow =>",
            "=> ",
            "lambda",
            "anonymous function",
            "function expression",
        ],
        "const": [
            "const",
            "let",
            "var",
            "immutable",
            "reassign",
            "constant",
        ],
        "equality": [
            "===",
            "==",
            "strict equality",
            "type coercion",
            "loose equality",
        ],
        "semicolon": [
            "semicolon",
            "semi-colon",
            "missing ;",
            "statement terminator",
        ],
        # Bug concepts
        "nullcheck": [
            "null",
            "none",
            "undefined",
            "nil",
            "nullable",
            "optional chaining",
            "null check",
        ],
        "offbyone": ["off by one", "off-by-one", "index error", "boundary", "bounds"],
        "division": ["division", "divide", "zero", "zerodivision", "divisor"],
        "async": ["async", "await", "promise", "asynchronous", "callback"],
        "initialization": [
            "uninitial",
            "not initial",
            "undefined variable",
            "used before",
            "declaration",
        ],
        # Security concepts
        "sqli": [
            "sql injection",
            "sqli",
            "sql query",
            "parameterized",
            "prepared statement",
            "user input",
        ],
        "xss": [
            "xss",
            "cross-site",
            "script injection",
            "innerhtml",
            "dangerouslysetinnerhtml",
            "unsanitized",
        ],
        "hardcoded": [
            "hardcoded",
            "hard-coded",
            "hardcode",
            "secret",
            "password",
            "api key",
            "credential",
        ],
        "eval": ["eval", "exec", "code execution", "arbitrary code", "dynamic code"],
        "path": [
            "path traversal",
            "directory traversal",
            "../",
            "file path",
            "user-controlled path",
        ],
        "csrf": ["csrf", "cross-site request", "token", "forgery"],
    }

    def _extract_keywords(self, text: str) -> set:
        """Extract normalized keywords from text."""
        text_lower = text.lower()
        found = set()
        # Check for keyword aliases
        for concept, aliases in self.KEYWORD_ALIASES.items():
            for alias in aliases:
                if alias in text_lower:
                    found.add(concept)
                    break
        # Also add individual words
        words = set(re.findall(r"\b[a-z_][a-z0-9_]*\b", text_lower))
        found.update(words)
        return found

    def _description_matches(self, gt: str, rep: str) -> bool:
        gt_lower = gt.lower()
        rep_lower = rep.lower()

        # Direct substring match
        if gt_lower in rep_lower or rep_lower in gt_lower:
            return True

        # Extract keywords from both
        gt_keywords = self._extract_keywords(gt)
        rep_keywords = self._extract_keywords(rep)

        # Check for concept matches (high-value keywords)
        concept_keys = set(self.KEYWORD_ALIASES.keys())
        gt_concepts = gt_keywords & concept_keys
        rep_concepts = rep_keywords & concept_keys

        # If they share a concept, it's a match
        if gt_concepts & rep_concepts:
            return True

        # Word overlap - need at least 1 significant word in common
        common_words = gt_keywords & rep_keywords
        # Filter out very common words
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "to",
            "for",
            "of",
            "in",
            "on",
            "and",
            "or",
            "use",
            "should",
            "be",
            "with",
        }
        significant_common = common_words - stopwords

        if len(significant_common) >= 1:
            return True

        return False

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


def clamp_reward(reward: float) -> float:
    """Clamp reward to (0.01, 0.99) to avoid validator rejection at boundaries."""
    if reward <= 0.0:
        return 0.01
    elif reward >= 1.0:
        return 0.99
    return reward


class StyleCheckGrader:
    """Grader for style_check task - evaluates code style issue detection."""

    def grade(self, observation: CodeReviewObservation) -> float:
        """
        Grade the agent's performance on style checking.
        Returns a clamped score between 0.01 and 0.99.
        """
        if observation.issues_found is None or len(observation.issues_found) == 0:
            return 0.01

        correct_count = sum(1 for issue in observation.issues_found if issue.is_correct)
        total_found = len(observation.issues_found)

        if total_found == 0:
            return 0.01

        # Precision-based scoring
        precision = correct_count / total_found
        return clamp_reward(precision)


class BugHuntGrader:
    """Grader for bug_hunt task - evaluates bug detection accuracy."""

    def grade(self, observation: CodeReviewObservation) -> float:
        """
        Grade the agent's performance on bug hunting.
        Returns a clamped score between 0.01 and 0.99.
        """
        if observation.issues_found is None or len(observation.issues_found) == 0:
            return 0.01

        correct_count = sum(1 for issue in observation.issues_found if issue.is_correct)
        total_found = len(observation.issues_found)

        if total_found == 0:
            return 0.01

        # Precision-based scoring with slight bonus for finding more bugs
        precision = correct_count / total_found
        recall_bonus = min(0.1, correct_count * 0.02)

        return clamp_reward(precision + recall_bonus)


class FullReviewGrader:
    """Grader for full_review task - evaluates security issue detection and fix suggestions."""

    def grade(self, observation: CodeReviewObservation) -> float:
        """
        Grade the agent's performance on full code review (security focus).
        Returns a clamped score between 0.01 and 0.99.
        """
        if observation.issues_found is None or len(observation.issues_found) == 0:
            return 0.01

        correct_count = sum(1 for issue in observation.issues_found if issue.is_correct)
        fix_count = sum(
            1
            for issue in observation.issues_found
            if issue.is_correct and issue.fix_suggestion is not None
        )
        total_found = len(observation.issues_found)

        if total_found == 0:
            return 0.01

        # Combined scoring: 50% precision, 50% fix quality
        precision = correct_count / total_found
        fix_quality = fix_count / max(1, correct_count) if correct_count > 0 else 0.0

        combined_score = (precision * 0.5) + (fix_quality * 0.5)
        return clamp_reward(combined_score)
