def ex_key(x):
    return x


def merge(a, b, key=ex_key):
    n, m = len(a), len(b)
    i, j = 0, 0
    ans = []
    while i + j < n + m:
        if j == m or (i != n and key(a[i]) < key(b[j])):
            ans.append(a[i])
            i += 1
        else:
            ans.append(b[j])
            j += 1
    return ans


def mergesort(a, key=ex_key):
    if len(a) < 2:
        return a
    m = len(a) // 2
    return merge(mergesort(a[:m], key), mergesort(a[m:], key), key)


def f(x, a, b): # a<b
    return a+((x-a)*(b-a))**0.5


def flashsort(a, key=ex_key):
    if type(a) != list:
        a = list(a)
    n = len(a)
    if n <= 1:
        return a
    if n <= 4:
        return mergesort(a, key)
    mn = min(a, key=key)
    mx = max(a, key=key)
    if mx == mn:
        return a
    m = n
    buckets = [[] for _ in range(m)]
    broken_ind = -1
    half = []
    for i in range(n):
        x1, y1, z1 = key(a[i]), key(mn), key(mx)
        x, y, z = f(x1, y1, z1), f(y1, y1, z1), f(z1, y1, z1)
        ind = max(0, min(m - 1, int((x - y) * (m - 1) / (z - y))))
        buckets[ind].append(a[i])
        if len(buckets[ind]) >= n // 2:
            half = buckets[ind].copy()
            buckets[ind] = []
            broken_ind = ind
    ans = []
    for i in range(m):
        if i == broken_ind:
            ans += merge(flashsort(buckets[i], key), flashsort(half, key), key)
        else:
            ans += flashsort(buckets[i], key)
    return ans
