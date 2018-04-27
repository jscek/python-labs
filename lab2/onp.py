import re
from string import ascii_lowercase


all_vars = ascii_lowercase
ops = '~^&|/>'


def vars_set(expr):
  return ''.join(sorted(set([c for c in expr if c.isalpha()])))


def skip_whitespaces(expr):
  expr = ''.join(expr.split())
  return expr


def correct(expr):
  state = True
  parens = 0

  for c in expr:
    if state:
      if c in all_vars:
        state = False
      elif c in (')' + ops):
        return False
    else:
      if c in ops:
        state = True
      elif c in (all_vars + '('):
        return False

    if c == '(':
      parens += 1
    if c == ')':
      parens -= 1

    if parens < 0:
      return False

  if parens != 0:
    return False

  return not state


# OK
def bal(expr, ops):
  parens = 0

  for i in range(len(expr) - 1, -1, -1):
    if expr[i] == '(':
      parens += 1
    elif expr[i] == ')':
      parens -= 1
    elif expr[i] in ops and parens == 0:
      return i
  
  return -1


def onp(expr):

  while (len(expr) > 2 and expr[0] == '(') and (expr[len(expr) - 1] == ')') and correct(expr[1:-1]):
    expr = expr[1:-1]
  
  p = bal(expr, '>')
  
  if p >= 0:
    return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]
  
  p = bal(expr, '&|/')

  if p >= 0:
    return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]

  p = bal(expr, '^')

  if p >= 0:
    return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]

  p = bal(expr, '~')

  if p >= 0:
    return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]

  return expr


# OK
def onp_map(expr, values):
  symbols = list(expr)
  for i, s in enumerate(symbols):
    p = vars_set(expr).find(s)
    if p >= 0:
      l[i] = values[p]

  return ''.join(symbols)
  

def value(onp_expr, valuess):
  onp_expr = onp_map(onp_expr, values)
  stack = []

  for c in onp_expr:
    if c in '01':
      stack.append(int(c))
    elif c == '~':
      stack.append(1 - stack.pop())
    elif c == '|':
      stack.append(stack.pop() | stack.pop())
    elif c == '&':
      stack.append(stack.pop() & stack.pop())
    elif c == '>':
      stack.append(stack.pop() | (1 - stack.pop()))

  return stack.pop()


def generate_bin(n):
  for i in range(2**n):
    yield bin(i)[2:].rjust(n, '0')


def main():
  f = open('vector', 'w+')

  while True:
    expr = input('> ')

    if not correct(expr):
      print('ERROR')
      exit()

    expr = skip_whitespaces(expr)
    expr = onp(expr)
    print(expr)

    expr_vars = vars_set(expr)

    #for v in gen(len(expr_vars)):
     # if value(expr, v, expr_vars) == 1:
      #  f.write(v + '\n')

  f.close()

if __name__ == "__main__":
  main()