import re
from string import ascii_lowercase
from itertools import product, combinations


all_vars = ascii_lowercase
ops = '>&|/^~'
consts = 'TF'


def vars_list(expr):
  return ''.join(sorted(set([c for c in expr if c in all_vars])))


def eat_whitespaces(expr):
  expr = ''.join(expr.split())
  return expr


def correct(expr):
  state = True
  parens = 0

  for c in expr:
    if c == '~':
      state = True
      continue
    if state:
      if c in (all_vars + consts):
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


def cut_parens(expr):
  while (len(expr) > 2 and expr[0] == '(') and (expr[-1] == ')') and correct(expr[1:-1]):
    expr = expr[1:-1]

  return expr

# OK
def balanced(expr, divider):
  parens = 0

  for i in range(len(expr)):
    if expr[i] == '(': parens += 1
    elif expr[i] == ')': parens -= 1
    elif expr[i] == divider and parens == 0: return i
  
  return -1


def rpn(expr):
  expr = cut_parens(expr)  
  
  for o in ops:
    p = balanced(expr, o)
    if p >= 0: return rpn(expr[:p]) + rpn(expr[p + 1:]) + expr[p]

  return expr


# OK
def rpn_map(expr, values):
  symbols = list(expr)
  for i, s in enumerate(symbols):
    if s == 'T':
      symbols[i] = '1'
    elif s == 'F':
      symbols[i] = '0'
    else:
      p = vars_list(expr).find(s)
      if p >= 0:
        symbols[i] = values[p]

  return ''.join(symbols)
  

def value(rpn_expr, values):
  rpn_expr = rpn_map(rpn_expr, values)
  stack = []

  for c in rpn_expr:
    if c in '01':
      stack.append(int(c))
    elif c in ops:
      if c == '~':
        a = stack.pop()

        stack.append(1 - a)
      else:
        a = stack.pop()
        b = stack.pop()

        if c == '^': stack.append((a & (1 - b)) | ((1 - a) & b))
        elif c == '|': stack.append(a | b)
        elif c == '&': stack.append(a & b)
        elif c == '/': stack.append(1 - (a & b))
        elif c == '>': stack.append(a | (1 - b))

  return stack.pop()


def generate_bin(n):
  for i in range(2**n):
    yield bin(i)[2:].rjust(n, '0')

def count_ones(bin_num):
  ones = 0
  for b in bin_num:
    if b == '1':
      ones += 1
  
  return ones


def group_by_ones(vector, vars_num):
  grouped = [[] for i in range(vars_num + 1)]

  for v in vector:
    grouped[count_ones(v)].append(v)

  return grouped


def merge(s1, s2):
  result = ''
  counter = 0

  for c1, c2 in zip(s1, s2):
    if c1 == c2:
      result += c1
    else:
      result += '-'
      counter += 1

  if counter == 1:
    return result
  else:
    return False


def reduce(vector):
  result = set()
  b2 = False
  for e1 in vector:
    b1 = False
    for e2 in vector:
      m = merge(e1, e2)
      if m:
        b1 = b2 = True
        result.add(m)
    
    if not b1:
      result.add(e1)

  if b2:
    return reduce(result)

  return result


def show(s, vars):
  m_res = ''
  for w in s:
    res = ''
    for i, j in zip(w, vars[:len(w)]):
      if i == '0':
        res += '~' + j + '&'
      elif i == '1':
        res += j + '&'

    m_res += '(' + res[:-1] + ')|'

  return m_res[:-1]


def main():
  while True:
    l = []
    expr = input('> ')

    if not correct(expr):
      print('ERROR')
      continue


    expr = eat_whitespaces(expr)
    expr = rpn(expr)

    expr_vars = vars_list(expr)
    
    for v in generate_bin(len(expr_vars)):      
      if value(expr, v) == 1:
        l.append(v)
        

    # jesli zaden wektor wartosci nie zwraca prawdy
    if (len(l) == 0):
      final = 'F'
    #jesli wszystkie zwracaja prawde
    elif (len(l) == 2**len(l[0])):
      final = 'T'
    else:
      final = show(reduce(l), expr_vars)

    print(final)


if __name__ == '__main__':
  main()