import timeit, random, statistics
import matplotlib.pyplot as plt

def measure_time(sort_func, data, repeats=5):
    times = []
    for _ in range(repeats):
        start = timeit.default_timer()
        # працюємо з копією
        out = sort_func(data[:])  
        times.append(timeit.default_timer() - start)
        # sanity-check: результат має збігатися з еталоном
        assert out == sorted(data), f"{sort_func.__name__} повернув некоректний результат"
    return statistics.mean(times), (statistics.stdev(times) if repeats > 1 else 0.0)

def insertion_sort(lst):
    for i in range(1, len(lst)):
        key = lst[i]
        j = i - 1
        while j >= 0 and key < lst[j]:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = key
    return lst

def merge(left, right):
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    if i < len(left): merged.extend(left[i:])
    if j < len(right): merged.extend(right[j:])
    return merged

def merge_sort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def timsort_inplace(a):
    b = a[:]
    # list.sort() — Timsort
    b.sort()      
    return b

random.seed(42)

datasets = [
    ("smallest(10)",  [random.randint(0, 1_000) for _ in range(10)]),
    ("small(100)",    [random.randint(0, 1_000) for _ in range(100)]),
    ("big(1000)",     [random.randint(0, 1_000) for _ in range(1_000)]),
    ("largest(10000)",[random.randint(0,10_000) for _ in range(10_000)]),
]

algorithms = [
    ("Insertion", insertion_sort),
    ("Merge",     merge_sort),
    ("Timsort(sorted)", sorted),
    ("Timsort(.sort)",  timsort_inplace),
    # Bubble додамо умовно — тільки для невеликих
    ("Bubble",    bubble_sort),
]

print(f"{'dataset':<16} {'algo':<18} {'mean (ms)':>12} {'stdev':>10}")
print("-"*60)

for dname, data in datasets:
    for aname, afn in algorithms:
        # пропускаємо Bubble на надвеликих наборах
        if aname == "Bubble" and len(data) > 2000:
            continue
        mean_s, std_s = measure_time(afn, data, repeats=5 if len(data)<=1000 else 3)
        print(f"{dname:<16} {aname:<18} {mean_s*1000:12.2f} {std_s*1000:10.2f}")

# --- Графік 1: random, 1k..10k (Insertion vs Merge vs Timsort) ---
sizes = list(range(1000, 10001, 1000))
results = {aname: [] for aname, _ in algorithms if aname != "Bubble"}
stdevs  = {aname: [] for aname, _ in algorithms if aname != "Bubble"}

for size in sizes:
    data = [random.randint(0, 10_000) for _ in range(size)]
    for aname, afn in algorithms:
        if aname == "Bubble":
            continue
        mean_s, std_s = measure_time(afn, data, repeats=3)
        results[aname].append(mean_s * 1000)   # мс
        stdevs[aname].append(std_s * 1000)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
for aname, times in results.items():
    plt.plot(sizes, times, marker='o', label=aname)
    upper = [m+s for m, s in zip(times, stdevs[aname])]
    lower = [m-s for m, s in zip(times, stdevs[aname])]
    plt.fill_between(sizes, lower, upper, alpha=0.15)

plt.title("Масштабування на random: 1k..10k")
plt.xlabel("Розмір масиву")
plt.ylabel("Час (мс)")

plt.yscale("log")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# --- Графік 2: nearly-sorted (1%), Merge vs Timsort ---
def make_nearly_sorted(n, swaps_ratio=0.01):
    a = list(range(n))
    swaps = max(1, int(n * swaps_ratio))
    for _ in range(swaps):
        i = random.randrange(n); j = random.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a

sizes2 = [5000, 20000, 50000]
res2 = {"Merge": [], "Timsort(sorted)": [], "Timsort(.sort)": []}

for size in sizes2:
    data = make_nearly_sorted(size, 0.01)
    for aname, afn in algorithms:
        if aname.startswith("Timsort") or aname == "Merge":
            mean_s, _ = measure_time(afn, data, repeats=3)
            res2[aname].append(mean_s * 1000)

plt.figure(figsize=(10, 6))
for aname, times in res2.items():
    # пропускаємо пусті (на випадок відсутності)
    if not times:  
        continue
    plt.plot(sizes2, times, marker='o', label=aname)
plt.title("Nearly-sorted (1%): Merge vs Timsort — великі розміри")
plt.xlabel("Розмір масиву")
plt.ylabel("Час (мс)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()