import string

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


def reduc(vector):
  res = set()
  b2 = False
  for e1 in vector:
    b1 = False
    for e2 in vector:
      result = merge(e1, e2)
      if result:
        b1 = b2 = True
        res.add(result)
    
    if not b1:
      res.add(e1)

  if b2:
    return reduc(res)

  return res


def show(s):
  m_res = ''
  for w in s:
    res = ''
    for i, j in zip(w, string.ascii_lowercase[:len(w)]):
      if i == '0':
        res += '~' + j + '&'
      elif i == '1':
        res += j + '&'

    m_res = '(' + res[:-1] + ')|'

  return m_res[:-1]



with open('vector', 'r') as f:
  # zmienic na set
  v = list(f.read().split('\n'))

print(v)

r = reduc(v)

print(merge('1000', '0000'))

print(show(v))
print(show(r))

f.close()