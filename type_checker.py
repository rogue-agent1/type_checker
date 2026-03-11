#!/usr/bin/env python3
"""type_checker — Hindley-Milner type inference engine. Zero deps."""

class Type:
    pass

class TVar(Type):
    _next = 0
    def __init__(self, name=None):
        if name is None:
            TVar._next += 1
            name = f"t{TVar._next}"
        self.name = name
        self.instance = None
    def __repr__(self): return str(self.prune())
    def prune(self):
        if self.instance: self.instance = self.instance.prune(); return self.instance
        return self

class TCon(Type):
    def __init__(self, name, args=None):
        self.name, self.args = name, args or []
    def __repr__(self):
        if not self.args: return self.name
        if self.name == '->': return f"({self.args[0]} -> {self.args[1]})"
        return f"{self.name}[{', '.join(map(str, self.args))}]"

TInt = TCon('Int')
TBool = TCon('Bool')
TStr = TCon('Str')
def TFun(a, b): return TCon('->', [a, b])
def TList(t): return TCon('List', [t])

def unify(t1, t2):
    t1, t2 = t1.prune() if isinstance(t1, TVar) else t1, t2.prune() if isinstance(t2, TVar) else t2
    if isinstance(t1, TVar):
        if t1 is not t2:
            if occurs(t1, t2): raise TypeError(f"Recursive type: {t1} in {t2}")
            t1.instance = t2
    elif isinstance(t2, TVar):
        unify(t2, t1)
    elif isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            raise TypeError(f"Cannot unify {t1} with {t2}")
        for a, b in zip(t1.args, t2.args):
            unify(a, b)

def occurs(tvar, typ):
    typ = typ.prune() if isinstance(typ, TVar) else typ
    if typ is tvar: return True
    if isinstance(typ, TCon): return any(occurs(tvar, a) for a in typ.args)
    return False

# AST
class Expr: pass
class EInt(Expr):
    def __init__(self, val): self.val = val
class EBool(Expr):
    def __init__(self, val): self.val = val
class EVar(Expr):
    def __init__(self, name): self.name = name
class EApp(Expr):
    def __init__(self, fn, arg): self.fn, self.arg = fn, arg
class ELam(Expr):
    def __init__(self, param, body): self.param, self.body = param, body
class ELet(Expr):
    def __init__(self, name, val, body): self.name, self.val, self.body = name, val, body

def infer(expr, env=None):
    if env is None: env = {}
    if isinstance(expr, EInt): return TInt
    if isinstance(expr, EBool): return TBool
    if isinstance(expr, EVar):
        if expr.name not in env: raise TypeError(f"Unbound: {expr.name}")
        return env[expr.name]
    if isinstance(expr, EApp):
        fn_type = infer(expr.fn, env)
        arg_type = infer(expr.arg, env)
        ret = TVar()
        unify(fn_type, TFun(arg_type, ret))
        return ret.prune() if isinstance(ret, TVar) else ret
    if isinstance(expr, ELam):
        param_type = TVar()
        new_env = {**env, expr.param: param_type}
        body_type = infer(expr.body, new_env)
        return TFun(param_type, body_type)
    if isinstance(expr, ELet):
        val_type = infer(expr.val, env)
        new_env = {**env, expr.name: val_type}
        return infer(expr.body, new_env)

def main():
    env = {
        '+': TFun(TInt, TFun(TInt, TInt)),
        'not': TFun(TBool, TBool),
        'id': TFun(a := TVar('a'), a),
    }
    tests = [
        ("42", EInt(42)),
        ("true", EBool(True)),
        ("λx.x", ELam("x", EVar("x"))),
        ("(+ 1)", EApp(EVar("+"), EInt(1))),
        ("let x = 5 in (+ x)", ELet("x", EInt(5), EApp(EVar("+"), EVar("x")))),
        ("not true", EApp(EVar("not"), EBool(True))),
    ]
    print("Hindley-Milner Type Inference:\n")
    for name, expr in tests:
        try:
            t = infer(expr, {**env})
            result = t.prune() if isinstance(t, TVar) else t
            print(f"  {name:.<30} : {result}")
        except TypeError as e:
            print(f"  {name:.<30} : ERROR: {e}")

if __name__ == "__main__":
    main()
