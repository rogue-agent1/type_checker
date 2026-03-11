#!/usr/bin/env python3
"""Simple type checker for a mini language."""
import sys, re
class TypeEnv:
    def __init__(self): self.vars={}; self.errors=[]
    def declare(self,name,typ): self.vars[name]=typ
    def check(self,name): return self.vars.get(name)
    def error(self,msg): self.errors.append(msg)
def infer(expr,env):
    expr=expr.strip()
    if expr.isdigit(): return 'int'
    if re.match(r'^\d+\.\d+$',expr): return 'float'
    if expr.startswith('"') and expr.endswith('"'): return 'string'
    if expr in ('true','false'): return 'bool'
    if expr in env.vars: return env.vars[expr]
    if '+' in expr:
        parts=expr.split('+',1); lt,rt=infer(parts[0],env),infer(parts[1],env)
        if lt==rt and lt in ('int','float','string'): return lt
        env.error(f"Cannot add {lt} + {rt}"); return 'error'
    if '>' in expr or '<' in expr:
        return 'bool'
    return 'unknown'
env=TypeEnv()
stmts=['x: int = 42','y: float = 3.14','z: string = "hello"','w = x + 5','bad = x + z']
for s in stmts:
    if ':' in s.split('=')[0]:
        m=re.match(r'(\w+):\s*(\w+)\s*=\s*(.*)',s)
        if m:
            name,declared,expr=m.groups(); actual=infer(expr,env)
            env.declare(name,declared)
            ok='✓' if declared==actual else f'✗ expected {declared}, got {actual}'
            print(f"  {s:30s} → {ok}")
    elif '=' in s:
        m=re.match(r'(\w+)\s*=\s*(.*)',s)
        if m:
            name,expr=m.groups(); t=infer(expr,env); env.declare(name,t)
            print(f"  {s:30s} → {t}")
if env.errors:
    print(f"\nErrors:"); [print(f"  ✗ {e}") for e in env.errors]
