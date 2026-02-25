import sys
import re
from collections import defaultdict, deque

def normalize(word):
    """Приводит слово к нижнему регистру, оставляет только буквы и апострофы"""
    cleaned = re.sub(r"[^a-z']", "", word.lower())
    return cleaned if cleaned else None

def is_similar(w1, w2):
    """Проверяет, похожи ли два слова по правилам задачи"""
    if w1 == w2:
        return True
    if len(w1) == 1 or len(w2) == 1:
        return False

    len1, len2 = len(w1), len(w2)
    # Случай 1: одинаковая длина, разница в одной букве
    if len1 == len2:
        diff = sum(1 for a, b in zip(w1, w2) if a != b)
        return diff == 1
    # Случай 2: разница в длине 1 символ
    if abs(len1 - len2) == 1:
        short, long = (w1, w2) if len1 < len2 else (w2, w1)
        return long[:-1] == short and long[-1] in ('e', 's')
    return False

def main():
    data = sys.stdin.read().strip().split('\n')
    if not data or len(data) == 1:
        return
    
    K = int(data[0])
    words = []
    for line in data[1:]:
        if line:
            words.extend(line.split())

    # Нормализация и фильтрация
    norm_words = [w for w in (normalize(w) for w in words) if w and len(w) > 1]

    if not norm_words:
        return

    # Построение графа похожести
    graph = defaultdict(set)
    length_groups = defaultdict(list)
    
    for i, w in enumerate(norm_words):
        length_groups[len(w)].append((i, w))

    # Проверяем возможные пары
    for length in list(length_groups.keys()):
        for l in [length-1, length, length+1]:
            if l in length_groups:
                for i1, w1 in length_groups[length]:
                    for i2, w2 in length_groups[l]:
                        if i1 != i2 and is_similar(w1, w2):
                            graph[w1].add(w2)
                            graph[w2].add(w1)

    # Поиск компонент связности (групп)
    visited = set()
    groups = []
    
    for word in graph:
        if word not in visited:
            stack = [word]
            component = set()
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    component.add(node)
                    stack.extend(graph[node] - visited)
            groups.append(component)

    # Добавляем одиночные слова как отдельные группы
    all_words = set(norm_words)
    for word in all_words:
        if word not in visited:
            groups.append({word})

    # Сопоставление слов с группами
    word_to_group = {}
    for group in groups:
        rep = min(group)  # представитель
        for word in group:
            word_to_group[word] = rep

    # Подсчёт контекстной частоты
    freq = defaultdict(int)
    for i, word in enumerate(norm_words):
        if word not in word_to_group:
            continue
        group_rep = word_to_group[word]
        left = max(0, i - K)
        right = min(len(norm_words) - 1, i + K)
        found = False
        for j in range(left, right + 1):
            if j != i and norm_words[j] in word_to_group:
                if word_to_group[norm_words[j]] == group_rep:
                    found = True
                    break
        if found:
            freq[group_rep] += 1

    # Вывод результата
    result = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    for rep, count in result:
        if count > 0:
            print(f"{rep}: {count}")

if __name__ == "__main__":
    main()
