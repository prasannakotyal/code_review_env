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
        "code": """from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import json

def get_user_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Missing Django REST Framework - should use DRF views for proper REST API",
                line_start=1,
                line_end=1,
                fix_suggestion="Use rest_framework.views.APIView",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Catching bare Exception is anti-pattern",
                line_start=12,
                line_end=12,
                fix_suggestion="Catch specific exceptions",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No authentication/permission classes defined",
                line_start=3,
                line_end=3,
                fix_suggestion="Add @permission_classes",
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": """import asyncio
import aiohttp
from typing import Dict, List, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers, params=params)
            return await response.json()

    async def fetch_multiple(self, endpoints: List[str]) -> List[Dict]:
        tasks = [self.fetch_data(ep) for ep in endpoints]
        return await asyncio.gather(*tasks)

client = APIClient("https://api.example.com", "secret-key-12345")
results = asyncio.run(client.fetch_multiple(["users", "posts"]))""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Hardcoded API key - security risk",
                line_start=21,
                line_end=21,
                fix_suggestion="Use environment variable",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Creating new session for each request - inefficient",
                line_start=12,
                line_end=12,
                fix_suggestion="Reuse session",
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": """from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'super-secret-key-123'

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_pw = generate_password_hash(password)
    return jsonify({'user': username, 'token': jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}, app.config['SECRET_KEY'])}), 201

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    return jsonify({'id': user_id, 'role': 'admin'})""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Hardcoded secret key in production code",
                line_start=9,
                line_end=9,
                fix_suggestion="Use environment variable",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No authentication check on protected endpoint",
                line_start=16,
                line_end=16,
                fix_suggestion="Add @login_required",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No input validation on username/password",
                line_start=13,
                line_end=13,
                fix_suggestion="Add validation",
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": """const express = require('express');
const jwt = require('jsonwebtoken');
const mysql = require('mysql2');
const app = express();

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'password123',
  database: 'app_db'
});

app.post('/api/users', (req, res) => {
  const { username, email, role } = req.body;
  const token = req.headers.authorization?.split(' ')[1];
  try {
    const decoded = jwt.verify(token, 'secret-key');
    pool.query('INSERT INTO users (username, email, role) VALUES (?, ?, ?)', [username, email, role], (err, result) => {
      if (err) throw err;
      res.json({ id: result.insertId });
    });
  } catch (e) {
    res.status(401).json({ error: 'Unauthorized' });
  }
});
app.listen(3000);""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Hardcoded database password",
                line_start=10,
                line_end=10,
                fix_suggestion="Use env variables",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="Hardcoded JWT secret",
                line_start=14,
                line_end=14,
                fix_suggestion="Use env variable",
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": """import React, { useState, useEffect } from 'react';
import axios from 'axios';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`/api/users/${userId}`)
      .then(res => setUser(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div><h1>{user.name}</h1><p>{user.email}</p></div>;
}
export default UserProfile;""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="No error boundary for component errors",
                line_start=15,
                line_end=15,
                fix_suggestion="Wrap in ErrorBoundary",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No cleanup in useEffect - potential memory leak",
                line_start=8,
                line_end=8,
                fix_suggestion="Add cleanup function",
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": """import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

interface User { id: string; username: string; role: string; }

declare global { namespace Express { interface Request { user?: User; } } }

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'default-secret') as User;
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="Fallback to default secret - security risk",
                line_start=13,
                line_end=13,
                fix_suggestion="Throw error if JWT_SECRET not set",
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": """import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Product { id: number; name: string; price: number; }

@Component({ selector: 'app-product-list', template: `<div *ngFor="let p of products"><h3>{{p.name}}</h3><p>{{p.price | currency}}</p></div>` })
export class ProductListComponent implements OnInit {
  products: Product[] = [];
  constructor(private http: HttpClient) {}
  ngOnInit(): void {
    this.http.get<Product[]>('/api/products').subscribe({
      next: (data) => this.products = data,
      error: (err) => console.error('Error:', err)
    });
  }
}""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="No unsubscribe - memory leak",
                line_start=10,
                line_end=10,
                fix_suggestion="Use takeUntilDestroyed",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No loading indicator",
                line_start=9,
                line_end=9,
                fix_suggestion="Add loading state",
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": """import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_model(data_path: str, target_col: str) -> float:
    df = pd.read_csv(data_path)
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)

accuracy = train_model('data.csv', 'target')
print(f"Model accuracy: {accuracy}")""",
        "issues": [
            Issue(
                issue_type=IssueType.STYLE,
                description="No data preprocessing for missing values",
                line_start=9,
                line_end=9,
                fix_suggestion="Add imputation",
            ),
            Issue(
                issue_type=IssueType.STYLE,
                description="No model persistence - trained model lost",
                line_start=14,
                line_end=14,
                fix_suggestion="Use joblib to save model",
            ),
        ],
    },
}

BUG_SNIPPETS = {
    "py001": {
        "language": Language.PYTHON,
        "code": """def get_user(user_id):
    users = {1: {'name': 'Alice'}, 2: {'name': 'Bob'}}
    return users.get(user_id)

user = get_user(5)
print(user['name'])""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Dictionary returns None for missing key - accessing .name on None causes TypeError",
                line_start=5,
                line_end=5,
                fix_suggestion="Add null check",
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": """import json

def process_json_data(json_string):
    data = json.loads(json_string)
    return data['results'][0]['items'][0]['name']

result = process_json_data('{"results": []}')
print(result)""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Accessing nested keys on empty list causes KeyError",
                line_start=4,
                line_end=4,
                fix_suggestion="Add validation",
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": """async function getUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    const data = await response.json();
    return data.profile.settings.theme;
  } catch (error) {
    console.log(error);
    return null;
  }
}

const theme = getUserData(123);
console.log(theme.toUpperCase());""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Calling async function synchronously - returns Promise not value",
                line_start=11,
                line_end=11,
                fix_suggestion="Use await",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="No null check on theme - calling .toUpperCase() on null throws",
                line_start=12,
                line_end=12,
                fix_suggestion="Add null check",
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": """function updateUserPreferences(userId, preferences) {
  const user = users.find(u => u.id === userId);
  user.preferences = preferences;
  return user;
}

function deleteUser(userId) {
  const index = users.findIndex(u => u.id === userId);
  users.splice(index, 1);
}

updateUserPreferences(1, { theme: 'dark' });
deleteUser(1);""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="find returns undefined if user not found - accessing .preferences throws",
                line_start=2,
                line_end=2,
                fix_suggestion="Add null check",
            ),
            Issue(
                issue_type=IssueType.BUG,
                description="findIndex returns -1 when not found - splice(-1, 1) removes last element",
                line_start=7,
                line_end=7,
                fix_suggestion="Check index !== -1",
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": """interface User { id: number; name: string; email?: string; }

function processUser(user: User): string {
  return user.email.toLowerCase();
}

const user: User = { id: 1, name: 'John' };
const result = processUser(user);
console.log(result);""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Optional property email could be undefined - calling .toLowerCase() throws",
                line_start=5,
                line_end=5,
                fix_suggestion="Use optional chaining",
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": """def calculate_discount(prices, discount_percent):
    discount_amount = 0
    for price in prices:
        discount_amount += price * discount_percent / 100
    return prices[0] - discount_amount

total = calculate_discount([], 10)
print(total)""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Empty list - returns prices[0] which raises IndexError",
                line_start=5,
                line_end=5,
                fix_suggestion="Add validation for empty list",
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": """class EventEmitter {
  constructor() { this.events = {}; }
  on(event, callback) {
    if (!this.events[event]) this.events[event] = [];
    this.events[event].push(callback);
  }
  emit(event, data) {
    if (this.events[event]) this.events[event].forEach(cb => cb(data));
  }
}

const emitter = new EventEmitter();
emitter.on('data', (d) => console.log(d));
emitter.emit('data', { value: 42 });""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No error handling in callback - one error crashes all handlers",
                line_start=7,
                line_end=7,
                fix_suggestion="Wrap in try-catch",
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": """function parseServerResponse(response: any): { data: string[], status: number } {
  if (typeof response === 'string') return JSON.parse(response);
  return response;
}

const result = parseServerResponse(null);
console.log(result.data);""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="No null check - accessing .data throws on null",
                line_start=6,
                line_end=6,
                fix_suggestion="Add null check",
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": """import concurrent.futures
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

urls = ['https://api.example.com/data/1', 'https://api.example.com/data/2']
results = [fetch_data(url) for url in urls]
print(results)""",
        "issues": [
            Issue(
                issue_type=IssueType.BUG,
                description="Sequential execution defeats purpose of concurrent.futures",
                line_start=8,
                line_end=8,
                fix_suggestion="Use ThreadPoolExecutor",
            ),
        ],
    },
}

SECURITY_SNIPPETS = {
    "py001": {
        "language": Language.PYTHON,
        "code": """from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
    return render_template_string(f"<h1>Results for {query}</h1>")

@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    result = subprocess.run(f'ping -c 1 {host}', shell=True, capture_output=True)
    return result.stdout""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection vulnerability",
                line_start=8,
                line_end=8,
                fix_suggestion="Use parameterized queries",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection - shell=True with user input",
                line_start=14,
                line_end=14,
                fix_suggestion="Use list args, not shell=True",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Template injection - user input in render_template_string",
                line_start=9,
                line_end=9,
                fix_suggestion="Use Jinja2 templates",
            ),
        ],
    },
    "js001": {
        "language": Language.JAVASCRIPT,
        "code": """const express = require('express');
const crypto = require('crypto');
const session = require('express-session');

const app = express();
app.use(express.urlencoded({ extended: true }));

app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const hash = crypto.createHash('md5').update(password).digest('hex');
  const user = users.find(u => u.username === username && u.password === hash);
  if (user) { req.session.userId = user.id; res.redirect('/dashboard'); }
  else { res.redirect('/login?error=Invalid credentials'); }
});""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Using MD5 for password hashing - cryptographically broken",
                line_start=10,
                line_end=10,
                fix_suggestion="Use bcrypt",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No session secret configured",
                line_start=5,
                line_end=5,
                fix_suggestion="Configure secure secret",
            ),
        ],
    },
    "py002": {
        "language": Language.PYTHON,
        "code": """import pickle
import os

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

def load_user_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

user = load_user_data(os.path.expanduser('~/uploads/user.pkl'))
if user.role == 'admin':
    os.system('rm -rf /tmp/*')""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Pickle deserialization of untrusted data - arbitrary code execution",
                line_start=8,
                line_end=8,
                fix_suggestion="Use JSON or msgpack",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal - user controls filename",
                line_start=8,
                line_end=8,
                fix_suggestion="Validate path",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No authorization check before admin action",
                line_start=13,
                line_end=13,
                fix_suggestion="Verify permissions",
            ),
        ],
    },
    "js002": {
        "language": Language.JAVASCRIPT,
        "code": """const fs = require('fs');
const path = require('path');

app.get('/download', (req, res) => {
  const filename = req.query.file;
  const filepath = path.join(__dirname, 'uploads', filename);
  fs.readFile(filepath, (err, data) => {
    if (err) { res.status(404).send('File not found'); return; }
    res.send(data);
  });
});

app.post('/upload', (req, res) => {
  fs.writeFile(`/tmp/${req.body.filename}`, req.body.content, (err) => {
    res.send('Uploaded');
  });
});""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Path traversal - .. in filename allows access outside uploads",
                line_start=6,
                line_end=6,
                fix_suggestion="Validate path stays within directory",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Arbitrary file write - filename from user input",
                line_start=14,
                line_end=14,
                fix_suggestion="Generate random filename",
            ),
        ],
    },
    "ts001": {
        "language": Language.TYPESCRIPT,
        "code": """import { exec } from 'child_process';
import { Request, Response } from 'express';

function runCommand(req: Request, res: Response) {
  const cmd = req.body.command;
  exec(cmd, (error, stdout, stderr) => {
    res.json({ output: stdout, error: stderr });
  });
}

function queryDatabase(req: Request, res: Response) {
  const query = req.body.query;
  const conn = mysql.createConnection({
    host: 'localhost', user: 'root',
    password: process.env.DB_PASS || 'admin'
  });
  conn.query(query, (err, results) => { res.json(results); });
}""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Command injection - direct user input in exec",
                line_start=7,
                line_end=7,
                fix_suggestion="Never pass user input to exec",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SQL injection - user query passed directly",
                line_start=14,
                line_end=14,
                fix_suggestion="Use parameterized queries",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Hardcoded database credentials",
                line_start=12,
                line_end=12,
                fix_suggestion="Use environment variables",
            ),
        ],
    },
    "py003": {
        "language": Language.PYTHON,
        "code": """import jwt
import base64
import json

def create_token(user_id, role='user'):
    header = {'alg': 'none', 'typ': 'JWT'}
    payload = {'user_id': user_id, 'role': role}
    encoded = base64.b64encode(json.dumps(header).encode()).decode() + '.' + \
              base64.b64encode(json.dumps(payload).encode()).decode() + '.'
    return encoded

def verify_token(token):
    try:
        parts = token.split('.')
        if len(parts) != 3: return None
        payload = json.loads(base64.b64decode(parts[1]))
        return payload
    except: return None

token = create_token(123, 'admin')
print(verify_token(token))""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="JWT 'none' algorithm - no signature verification",
                line_start=5,
                line_end=5,
                fix_suggestion="Use RS256 or HS256",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No signature verification - tokens can be forged",
                line_start=14,
                line_end=14,
                fix_suggestion="Verify signature properly",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="No expiration claim - tokens never expire",
                line_start=6,
                line_end=6,
                fix_suggestion="Add 'exp' claim",
            ),
        ],
    },
    "js003": {
        "language": Language.JAVASCRIPT,
        "code": """const axios = require('axios');

async function fetchUserData(userId) {
  return (await axios.get(`https://api.example.com/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` }
  })).data;
}

async function handleRequest(req, res) {
  const data = await fetchUserData(req.params.id);
  res.cookie('user_data', JSON.stringify(data), { httpOnly: false, secure: false });
  res.json(data);
}""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="Cookie not httpOnly - vulnerable to XSS",
                line_start=10,
                line_end=10,
                fix_suggestion="Set httpOnly: true",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Cookie sent over HTTP - should require secure flag",
                line_start=10,
                line_end=10,
                fix_suggestion="Set secure: true",
            ),
        ],
    },
    "ts002": {
        "language": Language.TYPESCRIPT,
        "code": """import * as crypto from 'crypto';

function generateApiKey(): string {
  return crypto.randomBytes(16).toString('hex');
}

function hashPassword(password: string): string {
  return crypto.createHash('sha256').update(password).digest('hex');
}

function verifySignature(data: string, sig: string, pubKey: string): boolean {
  return crypto.createVerify('SHA256').update(data).end().verify(pubKey, sig, 'base64');
}""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="API key with insufficient entropy",
                line_start=4,
                line_end=4,
                fix_suggestion="Use 32 bytes or crypto.randomUUID",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="SHA256 unsuitable for password hashing",
                line_start=8,
                line_end=8,
                fix_suggestion="Use bcrypt or argon2",
            ),
        ],
    },
    "py004": {
        "language": Language.PYTHON,
        "code": """import yaml

def load_config(filename):
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def execute_script(filename):
    config = load_config(filename)
    if config.get('run'): exec(config['run'])

config = load_config('config.yaml')
print(f"App: {config.get('app_name')}")""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="YAML deserialization vulnerability - arbitrary code execution",
                line_start=4,
                line_end=4,
                fix_suggestion="Use yaml.safe_load",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Code injection - exec with untrusted input",
                line_start=8,
                line_end=8,
                fix_suggestion="Never use exec with user data",
            ),
        ],
    },
    "py005": {
        "language": Language.PYTHON,
        "code": """import xml.etree.ElementTree as ET

def parse_xml_file(filename):
    return ET.parse(filename).getroot()

def process_user_xml(xml_string):
    root = ET.fromstring(xml_string)
    for user in root.findall('.//user'):
        username = user.get('username')
        password = user.findtext('password')
        print(f"User: {username}, Password: {password}")

xml = '''<users><user username="admin"><password>secret</password></user></users>'''
process_user_xml(xml)""",
        "issues": [
            Issue(
                issue_type=IssueType.SECURITY,
                description="XXE vulnerability - XML with external entity could read files",
                line_start=6,
                line_end=6,
                fix_suggestion="Disable external entities",
            ),
            Issue(
                issue_type=IssueType.SECURITY,
                description="Sensitive data printed in plain text",
                line_start=10,
                line_end=10,
                fix_suggestion="Never log passwords",
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
