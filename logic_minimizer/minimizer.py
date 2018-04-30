from string import ascii_lowercase

all_vars = ascii_lowercase
ops = '>&|/^~'
consts = 'TF'

# dla zadanego wyrażenia  zwraca string zawierający wszystkie zmienne występujące w wyrażeniu
def vars_list(expr):
  return ''.join(sorted(set([c for c in expr if c in all_vars])))

# zwraca string z wyrażeniem bez białych znaków
def eat_whitespaces(expr):
  expr = ''.join(expr.split())
  return expr

#  sprawdza poprawność wyrażenia
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
      if c in ops :
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

# zwraca string z wyrażeniem, bez zewnętrznych, niepotrzebnych nawiasów
def eat_parens(expr):
  while (len(expr) > 2 and expr[0] == '(') and (expr[-1] == ')') and correct(expr[1:-1]):
    expr = expr[1:-1]

  return expr

# 'dzieli' wyrażenie, zwraca indeks, pod którym występuje operator dzielący (divider) lub -1 w przypadku braku możliwości podzielenia
def partition(expr, divider):
  parens = 0

  for i in range(len(expr)):
    if expr[i] == '(': parens += 1
    elif expr[i] == ')': parens -= 1
    elif expr[i] == divider and parens == 0: return i
  
  return -1

# zamienia wyrażenie na to samo wyrażenie zapisane w odwrotnej notacji polskiej
def rpn(expr):
  expr = eat_parens(expr)  
  
  for o in ops:
    p = partition(expr, o)
    if p >= 0: return rpn(expr[:p]) + rpn(expr[p + 1:]) + expr[p]

  return expr

# zwraca string reprezentujący wartości zmiennych
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
  
# zwraca logiczną wartość wyrażenia
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

# generator liczb binarnych o długości n
def generate_bin(n):
  for i in range(2**n):
    yield bin(i)[2:].rjust(n, '0')

# 'łączy' dwie liczby binarne różniące się cyfrą tylko na jednej pozycji, wstawiając w to miejsce '-'
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

# zwraca zbior implikantów połączeń
def reduced(vector):
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
    return reduced(result)

  return result

# z wyrażenia o postaci: `op` P (dla negacji) lub L `op` P (dla pozostałych operatorów) tworzy listę (drzewo) o postaci [`op`, L] lub [`op`, L, P]
def make_tree(expr):
  expr = eat_parens(expr)
  tree = []
  
  if len(expr) == 1: return expr

  for o in ops:
    p = partition(expr, o)
      
    if p >= 0: 
      if o == '~':
        tree.append(expr[p])
        tree.append(make_tree(expr[(p + 1):]))
      else:
        tree.append(expr[p])
        tree.append(make_tree(expr[:p]))
        tree.append(make_tree(expr[(p + 1):]))

      return tree


# zwraca drzewo wyrażeń jako string
def show(expr_values):
  # przypadek gdy element to zmienna
  if (len(expr_values) == 1): return expr_values

  # przypadek gdy element to zanegowana zmienna
  if (len(expr_values) == 2): return expr_values[0] + show(expr_values[1])

  # sklejanie stron operatorem
  return show(expr_values[1]) + expr_values[0] + show(expr_values[2])


# dla wyrażenia o wartościach zapisanych w s, zwraca to wyrażenie jako suma koniunkcji
def show_normalized(s, vars):
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


# sprawdza czy da się uprościć wyrażenie zapisane w drzewie (wyszukiwanie xor'ów, implikacji i dysjunkcji)
def check_simplifies(tree):
  if len(tree) == 1: return tree

  if (len(tree) == 3):
    if (len(tree[1]) == 3):
      tree[1] = check_simplifies(tree[1])

    if (len(tree[2]) == 3):
      tree[2] = check_simplifies(tree[2])

  if tree[0] == '|':
      # xor
      if len(tree[1]) == 3 and len(tree[2]) == 3:
        if tree[1][0] == '&' and tree[2][0] == '&':
          if len(tree[1][1]) == 2 and len(tree[2][2]) == 2:
            tree[0] = '^'
            p = tree[2][1]
            q = tree[1][2]
            tree[1] = p
            tree[2] = q
          elif len(tree[1][2]) == 2 and len(tree[2][1]) == 2:
            tree[0] = '^'
            p = tree[1][1]
            q = tree[2][2]
            tree[1] = p
            tree[2] = q
      # implikacja
      if (len(tree[1]) == 1 and len(tree[2]) == 2):
          tree[0] = '>'
          q = tree[1]
          p = tree[2][1]
          tree[1] = p
          tree[2] = q
      if (len(tree[1]) == 2 and len(tree[2]) == 1):
          tree[0] = '>'
          tree[1] = tree[1][1]
      # dysjunkcja (gdy wejsciowe drzewo to alternatywa negacji)
      if (len(tree[1]) == 2 and len(tree[2]) == 2):
        tree[0] = '/'
        p = tree[2][1]
        q = tree[1][1]
        tree[1] = p
        tree[2] = q

  return tree


def main():
  while True:
    # lista, w której przechowywane będą wartośći zmiennych, dla których wyrażenie zwraca 1
    expr_values = []
    expr = input('> ')

    if not correct(expr):
      print('ERROR')
      continue

    expr = eat_whitespaces(expr)
    expr = eat_parens(expr)

    original_expr = expr
    # ilość znakow wyrazenia wejściowego (ilość zmiennych i operatorów)
    original_len = len(show(make_tree(expr)))

    expr = rpn(expr)
    expr_vars = vars_list(expr)

    for b in generate_bin(len(expr_vars)):      
      if value(expr, b) == 1:
        expr_values.append(b)
        
    # jeśli żaden wektor wartości nie zwraca prawdy
    if (len(expr_values) == 0):
      reulst = 'F'
    #jeśli wszystkie zwracają prawdę
    elif (len(expr_values) == 2**len(expr_values[0])):
      result = 'T'
    else:
      result = show_normalized(reduced(expr_values), expr_vars)
      result = make_tree(result)
      result = check_simplifies(result)
      result = show(result)

    result_len = len(result)

    if result_len < original_len:
      print('{0}, reduction: {1:.2f}%'.format(result, result_len / original_len * 100))
    else:
      print(original_expr)


if __name__ == '__main__':
  main()
