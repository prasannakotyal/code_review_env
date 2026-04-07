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
    # STYLE snippets: 24 curated snippets with 1-2 issues each
    "py001": {
        "language": Language.PYTHON,
        "code": 'def CalculateTotal(price, tax_rate):\n    message = "Total: " + str(price + tax_rate)\n    return message',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-string instead of string concatenation",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": 'def get_active_users(users):\n    active_names = []\n    for user in users:\n        if user["is_active"] == True:\n            active_names.append(user["name"])\n    return active_names',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use 'if user[\"is_active\"]:' instead of comparison with True",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension instead of append loop",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "class ReportBuilder:\n    def build(self, rows):\n        cleaned = []\n        for i in range(len(rows)):\n            cleaned.append(rows[i].strip())\n        return cleaned",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use direct iteration instead of range(len(...))",
                line_start=4,
                line_end=5,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "import json\n\ndef parse_payload(text):\n    try:\n        return json.loads(text)\n    except:\n        return {}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Bare except catches everything - specify exception type",
                line_start=6,
                line_end=6,
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": 'def csv_line(values):\n    output = ""\n    for value in values:\n        output += str(value) + ","\n    return output',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use join instead of string concatenation in loop",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Add type hints to function parameters and return value",
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "def is_valid(a, b, c):\n    if a > 0 and b > 0 and c > 0:\n        return True\n    else:\n        return False",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use all() for readability in chained comparisons",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Simplify to 'return a > 0 and b > 0 and c > 0'",
                line_start=3,
                line_end=5,
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "def print_user(user):\n    for key in user.keys():\n        print(key, user[key])",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use user.items() instead of keys() + indexing",
                line_start=2,
                line_end=3,
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": 'def greet(name, excited=True):\n    if excited == True:\n        return "Hello, {}!".format(name)\n    return "Hello, {}".format(name)',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use 'if excited:' instead of comparison with True",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-strings instead of .format()",
                line_start=3,
                line_end=4,
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": 'function formatUser(name, age) {\n  var prefix = name;\n  const label = prefix + " (" + age + ")";\n  return label;\n}',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const instead of var",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal instead of string concatenation",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "const numbers = [1, 2, 3, 4];\nlet total = 0;\nnumbers.forEach(function (n) {\n  total += n;\n});",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function instead of function expression",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use reduce instead of mutable accumulator loop",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": 'const status = "1";\nif (status == 1) {\n  console.log("ok");\n}',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use strict equality (===) instead of ==",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": 'const user = { firstName: "Ada", lastName: "Lovelace" };\nconst firstName = user.firstName;\nconst fullName = firstName + " " + user.lastName;\nconsole.log(fullName);',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal instead of string concatenation",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use object destructuring for firstName and lastName",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "const values = [];\nfor (let i = 0; i < items.length; i++) {\n  values.push(items[i].id);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use map() or for...of instead of index-based loop",
                line_start=2,
                line_end=3,
            ),
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const config = {};\nconfig.timeout = config.timeout ? config.timeout : 5000;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use nullish coalescing (??) or ??= for defaults",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const data = response.data;\nconst userName = data.user.name;\nconst userEmail = data.user.email;\nconsole.log(userName, userEmail);",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use object destructuring to extract nested fields",
                line_start=2,
                line_end=3,
            ),
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": 'const message = "User " + user.id + " has " + user.items.length + " items";\nconsole.log(message);',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal instead of string concatenation",
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": 'function renderUser(user: any): string {\n  return user.firstName + " " + user.lastName;\n}',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid 'any' - define a specific user type",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal instead of string concatenation",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "interface ApiResponse {\n  data: any;\n}\nconst handle = (response: ApiResponse) => response.data;",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid 'any' in ApiResponse - use a concrete or generic type",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": 'const getLabel = function (value: string) {\n  return "Value: " + value;\n};',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function instead of function expression",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal instead of string concatenation",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "type User = { id: number; name: string };\nfunction printUser(user: User) {\n  const id = user.id;\n  const name = user.name;\n  console.log(id, name);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use object destructuring for user properties",
                line_start=3,
                line_end=4,
            ),
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": 'const list: Array<string> = ["a", "b"];\nfor (let i = 0; i < list.length; i++) {\n  console.log(list[i]);\n}',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Use for...of loop for array iteration",
                line_start=2,
                line_end=3,
            ),
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": 'const result = value !== null && value !== undefined ? value : "default";',
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description='Use nullish coalescing: value ?? "default"',
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": "const parse = (input: string): any => {\n  return JSON.parse(input);\n};",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid 'any' return type - define parsed shape",
                line_start=1,
                line_end=1,
            ),
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "function isReady(flag: boolean): boolean {\n  if (flag === true) {\n    return true;\n  } else {\n    return false;\n  }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid comparison to true - use 'if (flag)'",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Simplify to return flag directly",
                line_start=3,
                line_end=6,
            ),
        ],
    },
}

BUG_SNIPPETS = {
    # BUG snippets: 24 curated snippets with 2-3 issues each
    "py001": {
        "language": Language.PYTHON,
        "code": "def average(values):\n    total = 0\n    for i in range(len(values) + 1):\n        total += values[i]\n    return total / len(values)",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one loop causes IndexError on last iteration",
                line_start=3,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Division by zero when values is empty",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": 'import json\n\ndef read_config(path):\n    with open(path) as f:\n        config = json.loads(f.read())\n    timeout = int(config["timeout"])\n    retries = int(config["retries"])\n    return timeout / retries',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Missing timeout key raises KeyError",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Non-numeric retries raises ValueError during int conversion",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Division by zero when retries is 0",
                line_start=8,
                line_end=8,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": 'def get_user_name(users, user_id):\n    user = users.get(user_id)\n    name = user["name"]\n    return name.strip()',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="users.get can return None, causing TypeError on subscript",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="name can be None, causing AttributeError on strip()",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "def process_items(items):\n    result = []\n    for i in range(len(items)):\n        result[i] = items[i] * 2\n    return result[-1]",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Assigning to result[i] before index exists raises IndexError",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="result[-1] raises IndexError when items is empty",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": 'def merge_defaults(options={}):\n    options["retry"] = options.get("retry", 3)\n    options["timeout"] = int(options.get("timeout", "fast"))\n    return options',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Mutable default argument persists state across calls",
                line_start=1,
                line_end=1,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description='Default timeout "fast" raises ValueError in int conversion',
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": 'def parse_line(line):\n    parts = line.split(",")\n    id_value = int(parts[0])\n    raw_score = parts[2]\n    score = float(raw_score)\n    return id_value, score',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Non-numeric id raises ValueError",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Missing third column raises IndexError",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Non-numeric score raises ValueError",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": 'def build_lookup(records):\n    lookup = {}\n    for rec in records:\n        key = rec["id"]\n        lookup[key] += 1\n    return lookup',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Missing id key raises KeyError",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Incrementing uninitialized key raises KeyError",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": 'def run(tasks):\n    for task in tasks:\n        if task["enabled"]:\n            continue\n        task["fn"]()\n    first_task = tasks[0]\n    return first_task["result"]',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Logic is inverted: disabled tasks run while enabled tasks are skipped",
                line_start=3,
                line_end=5,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Accessing tasks[0] raises IndexError when list is empty",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Missing result key raises KeyError",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "function sum(values) {\n  let total = 0;\n  let count = 0;\n  for (let i = 0; i <= values.length; i++) {\n    if (!values[i]) continue;\n    total += values[i].amount;\n    count += 1;\n  }\n  return total / values.length;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one loop condition should use < values.length",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Average denominator should use processed item count, not values.length",
                line_start=9,
                line_end=9,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Division by zero when values is empty",
                line_start=3,
                line_end=3,
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "function getTitle(post) {\n  const title = post.meta.title.trim();\n  const limit = parseInt(post.limit, 10);\n  return title.slice(0, limit + 1);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Nested property access can throw when post/meta/title is missing",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="parseInt can return NaN for invalid limit",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one slice includes one extra character",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": "async function loadUsers(ids) {\n  const users = [];\n  ids.forEach(async (id) => {\n    const res = await fetch(`/api/users/${id}`);\n    users.push(await res.json());\n  });\n  return users[0].name.toUpperCase();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="forEach with async callback is not awaited",
                line_start=3,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="users[0] can be undefined when return executes",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "function parseSettings(raw) {\n  const settings = JSON.parse(raw);\n  settings.retry = settings.retry || 3;\n  return settings.timeout.toFixed(2);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="JSON.parse throws on invalid JSON input",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Using || overwrites valid retry value 0",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="timeout can be undefined or non-number before toFixed",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "function pick(ids, index) {\n  if (index > ids.length) {\n    return ids[index];\n  }\n  return ids[index - 1];\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Boundary check should use >= to prevent out-of-bounds access",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="index 0 returns ids[-1], which is undefined",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": 'function updateUser(user, patch) {\n  const merged = { ...user, ...patch };\n  if (merged.role === "admin") {\n    merged.permissions.push("all");\n  }\n  return merged.permissions.join(",");\n}',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="permissions may be undefined before push",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="permissions may be undefined before join",
                line_start=6,
                line_end=6,
            ),
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": 'function getValue(map, key) {\n  const value = map[key].trim();\n  if (value === "") {\n    throw new Error("empty");\n  }\n  return value.toFixed(2);\n}',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="map[key] can be undefined, causing trim() to throw",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="toFixed is not available on string values",
                line_start=6,
                line_end=6,
            ),
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "function firstActive(users) {\n  const active = users.filter((u) => u.active);\n  active.sort((a, b) => a.score - b.score);\n  return active[0].name.toLowerCase();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="users may be null or undefined before filter",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Sorting by possibly undefined score values can produce invalid ordering",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="active[0] can be undefined when no active users exist",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": 'type User = { id: string; name?: string };\nfunction formatUser(user: User): string {\n  const id = parseInt(user.id, 10).toFixed(0);\n  return user.name.trim() + "-" + id;\n}',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="parseInt can return NaN for non-numeric id values",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="user.name is optional and may be undefined before trim()",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "function getFirst(items: string[]): string {\n  return items[0].toUpperCase();\n}\nconst value = getFirst([]);\nconsole.log(value.length);",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="items[0] is undefined for empty arrays",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Calling getFirst with [] triggers runtime failure in toUpperCase()",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "type Config = { timeout?: number; retries: number };\nfunction run(config: Config): number {\n  const timeoutMs = config.timeout * 1000;\n  return timeoutMs / config.retries;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="timeout is optional and can produce NaN when undefined",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Division by zero when retries is 0",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "async function fetchData(urls: string[]): Promise<string> {\n  const results: string[] = [];\n  urls.forEach(async (url) => {\n    const res = await fetch(url);\n    results.push(await res.text());\n  });\n  return results[0].toUpperCase();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="forEach with async callback is not awaited",
                line_start=3,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="results[0] may be undefined when accessed",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "interface Item { price: number; qty: number }\nfunction total(items: Item[]): number {\n  let sum = 0;\n  for (let i = 0; i <= items.length; i++) {\n    sum += items[i].price * items[i].qty;\n  }\n  return sum;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one loop condition should use < items.length",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="items[i] can be undefined on last iteration",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": "type Response = { data?: { values: number[] } };\nfunction average(response: Response): number {\n  const values = response.data.values;\n  return values.reduce((a, b) => a + b, 0) / values.length;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="response.data is optional and may be undefined",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Division by zero when values array is empty",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": 'function toMap(items: Array<{ id: string; value: number }>): Record<string, number> {\n  const map: Record<string, number> = {};\n  for (const item of items) {\n    map[item.id] += item.value;\n  }\n  return map;\n}\nconst result = toMap([{ id: "a", value: 1 }]);\nconsole.log(result["b"].toFixed(2));',
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Adding to uninitialized map key produces NaN",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description='result["b"] can be undefined before toFixed()',
                line_start=9,
                line_end=9,
            ),
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "function normalize(input: string | null): string {\n  const trimmed = input.trim();\n  if (trimmed.length === 0) {\n    return null;\n  }\n  return trimmed.toLowerCase();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="input can be null before trim() call",
                line_start=2,
                line_end=2,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Function returns null despite string return type",
                line_start=4,
                line_end=4,
            ),
        ],
    },
}

# FULL_REVIEW_SNIPPETS: Multi-issue snippets with STYLE + BUG + SECURITY issues
# Each snippet has 3-4 issues of mixed types for the "hard" difficulty
FULL_REVIEW_SNIPPETS = {
    # PYTHON FULL REVIEW - 8 snippets with 3-4 issues each
    "py001": {
        "language": Language.PYTHON,
        "code": "import os\npassword = 'admin123'\nquery = f\"SELECT * FROM users WHERE pass = '{password}'\"\ncursor.execute(query)\nresults = []\nfor row in cursor.fetchall():\n    results.append(row)\nprint(results)",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded password in source code",
                line_start=2,
                line_end=2,
                fix_suggestion="Use environment variable: os.environ.get('DB_PASSWORD')",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability via string formatting",
                line_start=3,
                line_end=3,
                fix_suggestion="Use parameterized query: cursor.execute('SELECT * FROM users WHERE pass = ?', (password,))",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use list comprehension instead of append loop",
                line_start=5,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No error handling for database operations",
                line_start=4,
                line_end=4,
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": "import pickle\nimport os\n\ndef load_user_data(user_input):\n    file_path = '/data/' + user_input\n    with open(file_path, 'rb') as f:\n        data = pickle.load(f)\n    for key in data.keys():\n        print(key, data[key])\n    return data",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal vulnerability - user input in file path",
                line_start=5,
                line_end=5,
                fix_suggestion="Validate and sanitize user_input, use os.path.basename() or allowlist",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Pickle deserialization of untrusted data can execute arbitrary code",
                line_start=7,
                line_end=7,
                fix_suggestion="Use json.load() for untrusted data, or cryptographically sign pickled data",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use data.items() instead of keys() with indexing",
                line_start=8,
                line_end=9,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No exception handling for file not found or invalid pickle",
                line_start=6,
                line_end=7,
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": "import hashlib\nimport subprocess\n\ndef process_user_request(username, password, command):\n    hash = hashlib.md5(password.encode()).hexdigest()\n    print('User: ' + username + ', Hash: ' + hash)\n    result = subprocess.run(command, shell=True, capture_output=True)\n    return result.stdout",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 is cryptographically broken for password hashing",
                line_start=5,
                line_end=5,
                fix_suggestion="Use bcrypt, scrypt, or argon2 for password hashing",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Logging sensitive data (password hash) to console",
                line_start=6,
                line_end=6,
                fix_suggestion="Remove password hash from log output",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No check for subprocess return code can hide command failures",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-string instead of string concatenation",
                line_start=6,
                line_end=6,
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": "import yaml\nimport json\n\ndef parse_config(user_yaml, user_json):\n    config = yaml.load(user_yaml, Loader=yaml.FullLoader)\n    data = json.loads(user_json)\n    exec(data.get('init_code', ''))\n    items = []\n    for i in range(len(config.get('items', []))):\n        items.append(config['items'][i])\n    return items",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="YAML deserialization vulnerability with FullLoader",
                line_start=5,
                line_end=5,
                fix_suggestion="Use yaml.safe_load() for untrusted input",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via exec() with user data",
                line_start=7,
                line_end=7,
                fix_suggestion="Remove exec() call or validate/sanitize init_code strictly",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use direct iteration instead of range(len())",
                line_start=9,
                line_end=10,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="KeyError if 'items' key missing and accessed via index",
                line_start=10,
                line_end=10,
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": "import jwt\nimport secrets\n\nSECRET_KEY = 'my-secret-key-123'\n\ndef create_token(user_id, role):\n    token = secrets.token_urlsafe(8)\n    payload = {'user_id': user_id, 'role': role, 'token': token}\n    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')\n\ndef verify_token(token):\n    try:\n        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    except:\n        return None",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded secret key in source code",
                line_start=4,
                line_end=4,
                fix_suggestion="Load from environment variable: os.environ.get('JWT_SECRET')",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Token entropy too low - only 8 bytes",
                line_start=7,
                line_end=7,
                fix_suggestion="Use at least 32 bytes: secrets.token_urlsafe(32)",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Bare except catches everything - specify exception type",
                line_start=14,
                line_end=14,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Returning None on error hides the actual exception cause",
                line_start=15,
                line_end=15,
            ),
        ],
    },
    "py006": {
        "language": Language.PYTHON,
        "code": "import requests\n\nAPI_KEY = 'sk-1234567890abcdef'\n\ndef fetch_data(user_url, params):\n    url = user_url + '?' + '&'.join([k + '=' + v for k, v in params.items()])\n    response = requests.get(url, headers={'Authorization': API_KEY})\n    data = response.json()\n    return data['results'][0]",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded API key in source code",
                line_start=3,
                line_end=3,
                fix_suggestion="Use environment variable: os.environ.get('API_KEY')",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="URL injection vulnerability - user controls URL",
                line_start=6,
                line_end=6,
                fix_suggestion="Validate URL against allowlist or use urllib.parse.urljoin with base URL",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use f-strings or urllib.parse.urlencode for URL building",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="IndexError if results array is empty",
                line_start=9,
                line_end=9,
            ),
        ],
    },
    "py007": {
        "language": Language.PYTHON,
        "code": "import tempfile\nimport os\n\ndef save_upload(filename, content):\n    path = '/uploads/' + filename\n    os.chmod('/uploads', 0o777)\n    with open(path, 'w') as f:\n        f.write(content)\n    eval(content.split('\\n')[0])\n    return path",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal - filename can contain ../",
                line_start=5,
                line_end=5,
                fix_suggestion="Use os.path.basename(filename) and validate",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid magic permission value 0o777 - use a named constant",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via eval() on user content",
                line_start=9,
                line_end=9,
                fix_suggestion="Remove eval() call entirely",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="IndexError if content is empty",
                line_start=9,
                line_end=9,
            ),
        ],
    },
    "py008": {
        "language": Language.PYTHON,
        "code": "import redis\nimport logging\n\nlogging.basicConfig(level=logging.DEBUG)\n\ndef cache_user_session(user_id, session_data, password):\n    r = redis.Redis()\n    logging.debug(f'Caching session for user {user_id}, password: {password}')\n    r.set(f'session:{user_id}', str(session_data))\n    return True",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid configuring root logger in module code; use module-level logger",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Logging sensitive data (password) in plain text",
                line_start=8,
                line_end=8,
                fix_suggestion="Never log passwords, remove password from log statement",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No TTL on cached session data",
                line_start=9,
                line_end=9,
                fix_suggestion="Add expiration: r.setex(key, 3600, value)",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No connection error handling for Redis",
                line_start=7,
                line_end=7,
            ),
        ],
    },
    # JAVASCRIPT FULL REVIEW - 8 snippets with 3-4 issues each
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": "const crypto = require('crypto');\nconst API_KEY = 'secret-api-key-123';\n\nasync function authenticateUser(username, password) {\n    const hash = crypto.createHash('md5').update(password).digest('hex');\n    var query = `SELECT * FROM users WHERE username = '${username}' AND hash = '${hash}'`;\n    const result = await db.query(query);\n    return result[0];\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded API key in source code",
                line_start=2,
                line_end=3,
                fix_suggestion="Use environment variable: process.env.API_KEY",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection via template literal string interpolation",
                line_start=6,
                line_end=6,
                fix_suggestion="Use parameterized query: db.query('SELECT * FROM users WHERE username = ? AND hash = ?', [username, hash])",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const instead of var",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No null check - result[0] undefined if no match",
                line_start=8,
                line_end=8,
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": "function processUserInput(userContent, userCode) {\n    const html = '<div class=\"content\">' + userContent + '</div>';\n    document.getElementById('output').innerHTML = html;\n    \n    const items = [1, 2, 3];\n    items.forEach(function(item) {\n        console.log(item);\n    });\n    \n    eval(userCode);\n    return items[5];\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="XSS vulnerability - unsanitized user content in innerHTML",
                line_start=3,
                line_end=3,
                fix_suggestion="Use textContent or sanitize with DOMPurify: DOMPurify.sanitize(userContent)",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via eval()",
                line_start=10,
                line_end=10,
                fix_suggestion="Remove eval() - use safer alternatives like JSON.parse for data",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function instead of function expression",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Array index out of bounds - items[5] returns undefined",
                line_start=11,
                line_end=11,
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": "const jwt = require('jsonwebtoken');\nconst SECRET = 'jwt-secret-123';\n\nfunction createSession(req, res) {\n    const token = jwt.sign({ userId: req.body.userId }, SECRET);\n    document.cookie = 'session=' + token;\n    \n    const key = crypto.randomBytes(8).toString('hex');\n    \n    res.setHeader('Access-Control-Allow-Origin', '*');\n    return { token, key };\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded JWT secret in source code",
                line_start=2,
                line_end=2,
                fix_suggestion="Use environment variable: process.env.JWT_SECRET",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use template literal for cookie string construction",
                line_start=6,
                line_end=6,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="ReferenceError: crypto is not defined",
                line_start=8,
                line_end=8,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="CORS allowing all origins is insecure",
                line_start=10,
                line_end=10,
                fix_suggestion="Specify allowed origins: res.setHeader('Access-Control-Allow-Origin', 'https://trusted-domain.com')",
            ),
        ],
    },
    "js004": {
        "language": Language.JAVASCRIPT,
        "code": "const fs = require('fs');\nconst { exec } = require('child_process');\n\nfunction handleFileOperation(userPath, userCommand) {\n    const data = fs.readFileSync('/data/' + userPath);\n    \n    exec(userCommand, (error, stdout) => {\n        console.log(stdout);\n    });\n    \n    const items = JSON.parse(data);\n    for (var i = 0; i <= items.length; i++) {\n        console.log(items[i].name);\n    }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal vulnerability in file read",
                line_start=5,
                line_end=5,
                fix_suggestion="Validate path: use path.resolve() and verify it's within allowed directory",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection via exec() with user input",
                line_start=7,
                line_end=7,
                fix_suggestion="Use execFile with arguments array, never exec with user input",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const/let instead of var",
                line_start=12,
                line_end=12,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one error: <= should be < in loop condition",
                line_start=12,
                line_end=12,
            ),
        ],
    },
    "js005": {
        "language": Language.JAVASCRIPT,
        "code": "async function fetchUserData(userId, apiToken) {\n    const url = '/api/users?id=' + userId + '&token=' + apiToken;\n    const response = await fetch(url);\n    const data = response.json();\n    \n    localStorage.setItem('userData', JSON.stringify(data));\n    localStorage.setItem('apiToken', apiToken);\n    \n    return data.profile.name;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="API token exposed in URL query parameter",
                line_start=2,
                line_end=2,
                fix_suggestion="Send token in Authorization header instead",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Storing sensitive API token in localStorage",
                line_start=7,
                line_end=7,
                fix_suggestion="Use httpOnly cookies for sensitive tokens, or sessionStorage with caution",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use await response.json() and explicit response typing",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No null check - data.profile.name throws if profile undefined",
                line_start=9,
                line_end=9,
            ),
        ],
    },
    "js006": {
        "language": Language.JAVASCRIPT,
        "code": "const vm = require('vm');\n\nfunction executeUserScript(userCode, userRegex) {\n    const regex = new RegExp(userRegex);\n    const match = 'test'.match(regex);\n    \n    const context = { result: null };\n    vm.runInNewContext(userCode, context);\n    \n    const fn = new Function('return ' + userCode);\n    return fn();\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Invalid user regex can throw SyntaxError",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via vm.runInNewContext",
                line_start=8,
                line_end=8,
                fix_suggestion="Never execute untrusted code - use sandboxed environment like isolated-vm",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection via Function constructor",
                line_start=10,
                line_end=10,
                fix_suggestion="Remove dynamic code execution entirely",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Remove unused variable match or use it",
                line_start=5,
                line_end=5,
            ),
        ],
    },
    "js007": {
        "language": Language.JAVASCRIPT,
        "code": "const crypto = require('crypto');\n\nfunction hashPassword(password) {\n    const hash = crypto.createHash('sha1').update(password).digest('hex');\n    return hash;\n}\n\nfunction verifyUser(inputPassword, storedHash) {\n    const inputHash = hashPassword(inputPassword);\n    if (inputHash == storedHash) {\n        return true;\n    }\n    return false;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA1 is cryptographically broken for password hashing",
                line_start=4,
                line_end=4,
                fix_suggestion="Use bcrypt: await bcrypt.hash(password, 12)",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use === instead of == for strict equality",
                line_start=10,
                line_end=10,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Simplify to return inputHash === storedHash",
                line_start=12,
                line_end=13,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Timing attack vulnerability - use crypto.timingSafeEqual",
                line_start=10,
                line_end=10,
            ),
        ],
    },
    "js008": {
        "language": Language.JAVASCRIPT,
        "code": "function handleWebSocket(ws, userData) {\n    ws.on('message', function(data) {\n        const parsed = JSON.parse(data);\n        parsed.__proto__.isAdmin = true;\n        \n        eval(parsed.command);\n    });\n    \n    const session = { userId: userData.id, role: 'admin' };\n    ws.send(JSON.stringify(session));\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Prototype pollution vulnerability",
                line_start=4,
                line_end=4,
                fix_suggestion="Use Object.create(null) or validate parsed object doesn't contain __proto__",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via eval()",
                line_start=6,
                line_end=6,
                fix_suggestion="Remove eval() - use validated command pattern instead",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Business logic bug: role is hardcoded to admin",
                line_start=9,
                line_end=9,
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use arrow function for callback",
                line_start=2,
                line_end=2,
            ),
        ],
    },
    # TYPESCRIPT FULL REVIEW - 8 snippets with 3-4 issues each
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": "import { exec } from 'child_process';\nimport * as crypto from 'crypto';\n\nconst DB_PASSWORD = 'password123';\n\nasync function runQuery(userInput: string, command: string): Promise<any> {\n    const query = `SELECT * FROM data WHERE id = ${userInput}`;\n    const result = await db.query(query);\n    \n    exec(command, (err, stdout) => {\n        console.log(stdout);\n    });\n    \n    return result[0].data;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid hardcoded config values in source code",
                line_start=4,
                line_end=4,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection via template literal interpolation",
                line_start=7,
                line_end=7,
                fix_suggestion="Use parameterized query with placeholders",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection via exec() with user input",
                line_start=10,
                line_end=10,
                fix_suggestion="Never use exec with user input, use execFile with validated arguments",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No null check - result[0] may be undefined",
                line_start=14,
                line_end=14,
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": "import jwt from 'jsonwebtoken';\n\nconst SECRET = 'my-jwt-secret';\n\ninterface User {\n    id: number;\n    role: any;\n}\n\nfunction createToken(user: User): string {\n    const token = jwt.sign(user, SECRET, { expiresIn: '24h' });\n    document.cookie = `auth=${token}`;\n    return token;\n}\n\nfunction verifyToken(token: string): User | null {\n    try {\n        return jwt.verify(token, SECRET) as User;\n    } catch {\n        return null;\n    }\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded JWT secret",
                line_start=3,
                line_end=3,
                fix_suggestion="Use environment variable: process.env.JWT_SECRET",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Cookie without HttpOnly and Secure flags",
                line_start=12,
                line_end=12,
                fix_suggestion="Add flags: `auth=${token}; HttpOnly; Secure; SameSite=Strict`",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid any type - define proper type for role",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Bare catch clause hides error details",
                line_start=19,
                line_end=19,
            ),
        ],
    },
    "ts003": {
        "language": Language.TYPESCRIPT,
        "code": "import * as fs from 'fs';\nimport * as yaml from 'js-yaml';\n\nfunction processConfig(userPath: string, yamlContent: string): any {\n    const filePath = '/config/' + userPath;\n    const fileData = fs.readFileSync(filePath, 'utf8');\n    \n    const config = yaml.load(yamlContent);\n    \n    const items: any[] = [];\n    for (var i = 0; i < config.items.length; i++) {\n        items.push(config.items[i]);\n    }\n    \n    return { fileData, items };\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal vulnerability in file path",
                line_start=5,
                line_end=5,
                fix_suggestion="Use path.resolve() and verify path is within allowed directory",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Unsafe YAML parsing can execute arbitrary code",
                line_start=8,
                line_end=8,
                fix_suggestion="Use yaml.safeLoad() or yaml.load with safe schema",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use const/let instead of var",
                line_start=11,
                line_end=11,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="config.items can be undefined, causing runtime error in loop",
                line_start=11,
                line_end=11,
            ),
        ],
    },
    "ts004": {
        "language": Language.TYPESCRIPT,
        "code": "import * as crypto from 'crypto';\n\nfunction hashData(data: string, password: string): string {\n    const hash = crypto.createHash('md5').update(data).digest('hex');\n    const pwHash = crypto.createHash('sha1').update(password).digest('hex');\n    \n    console.log('Password hash:', pwHash);\n    \n    const key = crypto.randomBytes(8).toString('hex');\n    \n    return hash + ':' + key;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="MD5 is cryptographically broken",
                line_start=4,
                line_end=4,
                fix_suggestion="Use SHA-256 or better: crypto.createHash('sha256')",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA1 is cryptographically broken for password hashing",
                line_start=5,
                line_end=5,
                fix_suggestion="Use bcrypt or argon2 for password hashing",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Use structured logger instead of console.log for diagnostics",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Short random key length increases collision risk for derived IDs",
                line_start=9,
                line_end=9,
            ),
        ],
    },
    "ts005": {
        "language": Language.TYPESCRIPT,
        "code": "function handleRequest(req: any, res: any): void {\n    const userHtml = req.body.content;\n    res.setHeader('Access-Control-Allow-Origin', '*');\n    \n    document.getElementById('output')!.innerHTML = userHtml;\n    \n    const regex = new RegExp(req.query.pattern);\n    const match = req.body.text.match(regex);\n    \n    eval(req.body.code);\n}",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Move CORS origin policy to centralized config",
                line_start=3,
                line_end=3,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="XSS vulnerability via innerHTML with user content",
                line_start=5,
                line_end=5,
                fix_suggestion="Use textContent or sanitize with DOMPurify",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Invalid user regex can throw SyntaxError and crash request",
                line_start=7,
                line_end=7,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via eval()",
                line_start=10,
                line_end=10,
                fix_suggestion="Never use eval with user input",
            ),
        ],
    },
    "ts006": {
        "language": Language.TYPESCRIPT,
        "code": "import axios from 'axios';\n\nconst API_KEY = 'sk-live-1234567890';\n\nasync function fetchData(endpoint: string): Promise<any> {\n    const { data } = await axios.get(endpoint, {\n        params: { apiKey: API_KEY }\n    });\n    \n    const results: any = [];\n    for (let i = 0; i <= data.items.length; i++) {\n        results.push(data.items[i].name);\n    }\n    \n    return results;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded API key in source code",
                line_start=3,
                line_end=3,
                fix_suggestion="Use environment variable: process.env.API_KEY",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="API key sent in URL query parameters",
                line_start=7,
                line_end=7,
                fix_suggestion="Send in Authorization header instead",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid any type - define proper interface",
                line_start=10,
                line_end=10,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="Off-by-one error: <= should be < in loop",
                line_start=11,
                line_end=11,
            ),
        ],
    },
    "ts007": {
        "language": Language.TYPESCRIPT,
        "code": "import * as fs from 'fs';\n\nfunction writeUserData(filename: string, content: string, code: string): boolean {\n    const path = '/uploads/' + filename;\n    fs.writeFileSync(path, content);\n    \n    const fn = new Function('return ' + code);\n    fn();\n    \n    const config = { debug: true, secret: 'config-secret' };\n    console.log('Config:', JSON.stringify(config));\n    \n    return true;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No error handling if writeFileSync fails (missing dir or permissions)",
                line_start=5,
                line_end=5,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary code execution via Function constructor",
                line_start=7,
                line_end=7,
                fix_suggestion="Never execute user-provided code",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid inline secret literals in object definitions",
                line_start=10,
                line_end=10,
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Logging sensitive config with secret",
                line_start=11,
                line_end=11,
                fix_suggestion="Filter sensitive fields before logging",
            ),
        ],
    },
    "ts008": {
        "language": Language.TYPESCRIPT,
        "code": "interface SessionData {\n    userId: number;\n    token: string;\n}\n\nfunction handleSession(data: string): SessionData | null {\n    const parsed = JSON.parse(data);\n    (parsed as any).__proto__.isAdmin = true;\n    \n    localStorage.setItem('session', data);\n    \n    const session: SessionData = {\n        userId: parsed.userId,\n        token: parsed.token || 'default-token'\n    };\n    \n    return session;\n}",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Prototype pollution vulnerability",
                line_start=8,
                line_end=8,
                fix_suggestion="Never modify __proto__ - use Object.create(null) for safe objects",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Storing potentially sensitive session data in localStorage",
                line_start=10,
                line_end=10,
                fix_suggestion="Use httpOnly cookies for sensitive session data",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Avoid magic default token value; validate token explicitly",
                line_start=14,
                line_end=14,
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No validation of parsed.userId - could be undefined",
                line_start=13,
                line_end=13,
            ),
        ],
    },
}

CODE_SNIPPETS = {
    TaskName.STYLE_CHECK: STYLE_SNIPPETS,
    TaskName.BUG_HUNT: BUG_SNIPPETS,
    TaskName.FULL_REVIEW: FULL_REVIEW_SNIPPETS,
}


class MyEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    MAX_STEPS = {
        TaskName.STYLE_CHECK: 7,
        TaskName.BUG_HUNT: 12,
        TaskName.FULL_REVIEW: 18,
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

        # Word overlap - require stronger overlap to avoid generic matches
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
            "using",
            "should",
            "be",
            "with",
            "instead",
            "code",
            "issue",
            "line",
            "error",
            "function",
            "variable",
            "possible",
            "can",
            "could",
        }
        significant_common = common_words - stopwords

        if len(significant_common) >= 2:
            return True

        if len(significant_common) == 1:
            word = next(iter(significant_common))
            if len(word) >= 8:
                return True

        return False

    def _calculate_reward(self, action: CodeReviewAction, match: dict) -> float:
        issue_weight = 1.0 / self._initial_issue_count
        matched_issue = match["issue"]
        if self._task_name == TaskName.STYLE_CHECK:
            return issue_weight * 0.9
        if self._task_name == TaskName.BUG_HUNT:
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
