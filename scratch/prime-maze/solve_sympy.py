#!/usr/bin/env python3
"""Решение prime-maze: из каждого M-узла идём по исходящему ребру с наибольшим простым числом."""
import json
from collections import defaultdict
from sympy import isprime

D = json.load(open('/mnt/extra/vibe/scratch/prime-maze/maze.json'))
nodes = {n['id']: n['letter'] for n in D['nodes']}
out_edges = defaultdict(list)  # node -> [(number, to)]
in_edges = defaultdict(list)   # node -> [(number, from)]
for e in D['edges']:
    out_edges[e['from']].append((e['number'], e['to']))
    in_edges[e['to']].append((e['number'], e['from']))

# Кэш простоты — много рёбер
prime_cache = {}
def is_prime(n):
    if n in prime_cache:
        return prime_cache[n]
    r = isprime(n)
    prime_cache[n] = r
    return r

def walk(start):
    """Идём по наибольшему простому исходящему ребру, без посещения дважды."""
    path = [start]
    visited = {start}
    cur = start
    while True:
        outs = out_edges.get(cur, [])
        # отсортировать по числу убыв., взять первое простое, чей to не в visited
        cand = sorted(outs, key=lambda x: -x[0])
        nxt = None
        for num, to in cand:
            if is_prime(num):
                nxt = to
                break  # САМОЕ большое простое — даже если ведёт в visited
        if nxt is None:
            break
        if nxt in visited:
            # цикл — остановка
            path.append(nxt)
            break
        path.append(nxt)
        visited.add(nxt)
        cur = nxt
    return path

m_nodes = [nid for nid, l in nodes.items() if l == 'M']
print(f"M-узлов: {len(m_nodes)}")

results = []
for mid in sorted(m_nodes):
    path = walk(mid)
    word = ''.join(nodes[p] for p in path)
    # входящие
    in_all = in_edges.get(mid, [])
    in_prime = [x for x in in_all if is_prime(x[0])]
    results.append((mid, len(path), word, len(in_all), len(in_prime)))

print("\n=== Все 24 запуска ===")
print(f"{'M-id':8} {'len':>4} {'in':>3} {'inP':>3}  word")
for mid, ln, word, ina, inp in results:
    print(f"{mid:8} {ln:>4} {ina:>3} {inp:>3}  {word}")

# Кандидаты: источники
print("\n=== M-узлы БЕЗ входящих рёбер ===")
for mid, ln, word, ina, inp in results:
    if ina == 0:
        print(f"  {mid}  word={word}")

print("\n=== M-узлы БЕЗ входящих ПРОСТЫХ рёбер ===")
for mid, ln, word, ina, inp in results:
    if inp == 0:
        print(f"  {mid}  word={word}")

# Уникальные слова
print("\n=== Уникальные слова (отсорт. по длине убыв.) ===")
seen = {}
for mid, ln, word, ina, inp in results:
    seen.setdefault(word, []).append(mid)
for w, mids in sorted(seen.items(), key=lambda x: -len(x[0])):
    print(f"  len={len(w):>3}  count={len(mids)}  {w[:80]}{'...' if len(w)>80 else ''}  from {mids[:3]}")
