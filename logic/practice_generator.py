"""
logic/practice_generator.py

Генератор практики йоги с логичной структурой:
  1. Разминка   — мягкие стоячие и дыхательные позы
  2. Основная часть — силовые, балансовые, скручивания, прогибы
  3. Заминка    — расслабляющие и лёжа позы + Шавасана

Алгоритм учитывает:
  - уровень сложности (beginner / intermediate / advanced)
  - продолжительность практики (total_minutes)
  - время удержания асаны (hold_seconds) — нужно чтобы посчитать кол-во асан
  - активные фильтры типов (filters) — учитываются только в основной части
  - эвристику «порядка внутри фазы»: позы идут от лёгких к более сложным
    в разминке и от сложных к лёгким в заминке
"""

import random
import math
from utils.data_loader import load_asanas


# ---------------------------------------------------------------------------
# Порядок типов внутри каждой фазы
# Чем меньше индекс — тем раньше поза появляется в фазе.
# ---------------------------------------------------------------------------

WARMUP_ORDER = [
    "warmup",      # таdasana, поза горы — самое начало
    "stretch",     # лёгкие растяжки стоя
    "balance",     # лёгкие балансы (только beginner-уровня)
]

MAIN_ORDER = [
    "strength",    # силовые — воины, уткатасана
    "balance",     # балансы
    "backbend",    # прогибы назад
    "stretch",     # глубокие растяжки
    "twist",       # скручивания
]

COOLDOWN_ORDER = [
    "twist",       # мягкие скручивания лёжа
    "stretch",     # лёжа или сидя
    "backbend",    # мягкие прогибы (поза ребёнка-прогиб)
    "relax",       # восстановительные
    # Шавасана добавляется всегда последней отдельно
]

# Типы, которые относятся к разминке
WARMUP_TYPES = {"warmup", "stretch"}

# Типы, которые относятся к заминке
COOLDOWN_TYPES = {"relax"}

# Типы основной части
MAIN_TYPES = {"strength", "balance", "backbend", "stretch", "twist"}

# Асаны-«якоря» — фиксированные позиции в практике
SAVASANA_NAMES = {"Savasana", "Shavasana"}  # всегда финал

# ---------------------------------------------------------------------------
# Готовые последовательности («шаблоны»)
# Используются как seed-порядок для beginner-уровня
# ---------------------------------------------------------------------------

SURYA_NAMASKAR = [
    "Tadasana",
    "Hasta Uttanasana",
    "Uttanasana",
    "Ashwa Sanchalanasana",
    "Adho Mukha Svanasana",
    "Bhujangasana",
    "Adho Mukha Svanasana",
    "Ashwa Sanchalanasana",
    "Uttanasana",
    "Hasta Uttanasana",
    "Tadasana",
]


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _level_rank(level: str) -> int:
    """Числовой ранг уровня: меньше = проще."""
    return {"beginner": 0, "intermediate": 1, "advanced": 2}.get(level, 0)


def _type_order(asana: dict, order_list: list) -> int:
    """Позиция типа асаны в заданном порядке (для сортировки)."""
    t = asana.get("type", "")
    try:
        return order_list.index(t)
    except ValueError:
        return len(order_list)


def _pick(pool: list, n: int, shuffle: bool = True) -> list:
    """Берём до n асан из pool без повторов."""
    if not pool:
        return []
    n = min(n, len(pool))
    if shuffle:
        selected = random.sample(pool, n)
    else:
        selected = pool[:n]
    return selected


def _filter_by_level(asanas: list, level: str) -> list:
    """
    Возвращает асаны подходящего уровня.
    Для beginner — только beginner.
    Для intermediate — beginner + intermediate.
    Для advanced — все.
    """
    rank = _level_rank(level)
    return [a for a in asanas if _level_rank(a.get("level", "beginner")) <= rank]


def _count_from_time(total_minutes: int, hold_seconds: int) -> int:
    """Сколько асан помещается в практику заданной длины."""
    if hold_seconds <= 0:
        hold_seconds = 30
    # +5 секунд переход между асанами
    total_sec = total_minutes * 60
    count = max(4, total_sec // (hold_seconds + 5))
    return int(count)


# ---------------------------------------------------------------------------
# Попытка вставить Сурья Намаскар в начало разминки
# ---------------------------------------------------------------------------

def _build_surya_prefix(asanas: list, level: str) -> list:
    """
    Если уровень beginner/intermediate — вставляем доступные позы
    из Сурья Намаскар в начало разминки (только те, что есть в базе).
    Возвращает список асан в нужном порядке.
    """
    if _level_rank(level) > 1:  # advanced — не обязательно
        return []

    by_name = {a["name"]: a for a in asanas}
    result = []
    for name in SURYA_NAMASKAR:
        if name in by_name:
            asana = by_name[name]
            if asana not in result:
                result.append(asana)
    return result


# ---------------------------------------------------------------------------
# Основная функция
# ---------------------------------------------------------------------------

def generate_practice(
    level: str = "beginner",
    total_minutes: int = 20,
    hold_seconds: int = 30,
    filters: list = None,
    selected_asana_names: list = None,
) -> list:
    """
    Генерирует логичную последовательность асан.

    Параметры
    ----------
    level           : "beginner" | "intermediate" | "advanced"
    total_minutes   : желаемая длительность практики в минутах
    hold_seconds    : время удержания каждой асаны в секундах
    filters         : список разрешённых типов для основной части
                      (None = все типы)
    selected_asana_names : конкретные имена асан — если пользователь
                      выбрал их вручную (режим «своя практика»)

    Возвращает
    ----------
    list of dict — упорядоченный список асан
    """

    all_asanas = load_asanas()
    available = _filter_by_level(all_asanas, level)

    if not available:
        return []

    # ── Если пользователь выбрал конкретные асаны ───────────────────────────
    if selected_asana_names:
        return _arrange_selected(all_asanas, selected_asana_names)

    total_count = _count_from_time(total_minutes, hold_seconds)

    # Пропорции фаз (примерно)
    # Разминка ~15-20%, основная ~65-70%, заминка ~15-20%
    warmup_count  = max(2, math.ceil(total_count * 0.18))
    cooldown_count = max(2, math.ceil(total_count * 0.18))
    main_count    = max(2, total_count - warmup_count - cooldown_count)

    # ── РАЗМИНКА ────────────────────────────────────────────────────────────
    warmup_pool = [a for a in available if a.get("type") in WARMUP_TYPES]

    # Пробуем вставить Сурья Намаскар как основу разминки
    surya = _build_surya_prefix(available, level)
    if surya:
        # Берём первые warmup_count асан из Сурьи, остальное добираем из пула
        warmup = surya[:warmup_count]
        if len(warmup) < warmup_count:
            used_names = {a["name"] for a in warmup}
            extra_pool = [a for a in warmup_pool if a["name"] not in used_names]
            warmup += _pick(extra_pool, warmup_count - len(warmup))
    else:
        # Сортируем: сначала тип "warmup", потом "stretch"
        warmup_pool.sort(key=lambda a: _type_order(a, WARMUP_ORDER))
        warmup = warmup_pool[:warmup_count]
        # Лёгкое перемешивание внутри каждой группы типов, но не между группами
        warmup = _soft_shuffle_by_type(warmup, WARMUP_ORDER)

    warmup_names = {a["name"] for a in warmup}

    # ── ОСНОВНАЯ ЧАСТЬ ──────────────────────────────────────────────────────
    main_pool = [
        a for a in available
        if a.get("type") in MAIN_TYPES
        and a["name"] not in warmup_names
    ]
    if filters:
        main_pool_filtered = [a for a in main_pool if a.get("type") in filters]
        # Если после фильтров мало асан — дополняем нефильтрованными
        if len(main_pool_filtered) < main_count:
            extra = [a for a in main_pool if a not in main_pool_filtered]
            main_pool_filtered += extra
        main_pool = main_pool_filtered

    # Внутри основной части — упорядочиваем по типу (силовые → балансы → прогибы → растяжки → скручивания)
    main = _build_main_sequence(main_pool, main_count, level)
    main_names = {a["name"] for a in main}

    # ── ЗАМИНКА ─────────────────────────────────────────────────────────────
    cooldown_pool = [
        a for a in available
        if a.get("type") in (COOLDOWN_TYPES | {"stretch", "twist"})
        and a["name"] not in warmup_names
        and a["name"] not in main_names
        and a["name"] not in SAVASANA_NAMES
    ]
    cooldown_pool.sort(key=lambda a: _type_order(a, COOLDOWN_ORDER))
    cooldown = cooldown_pool[:cooldown_count]
    cooldown = _soft_shuffle_by_type(cooldown, COOLDOWN_ORDER)

    # Шавасана — всегда последней (если есть в базе)
    savasana = _find_savasana(available)
    if savasana:
        # Убираем из cooldown если попала туда
        cooldown = [a for a in cooldown if a["name"] not in SAVASANA_NAMES]
        cooldown.append(savasana)

    practice = warmup + main + cooldown

    # Финальная проверка: убираем дубликаты, сохраняя порядок
    seen = set()
    result = []
    for a in practice:
        if a["name"] not in seen:
            seen.add(a["name"])
            result.append(a)

    return result


# ---------------------------------------------------------------------------
# Вспомогательные функции построения последовательности
# ---------------------------------------------------------------------------

def _build_main_sequence(pool: list, count: int, level: str) -> list:
    """
    Строит основную часть: группируем по типу согласно MAIN_ORDER,
    внутри каждой группы — случайный порядок.
    """
    groups = {}
    for t in MAIN_ORDER:
        groups[t] = [a for a in pool if a.get("type") == t]
        random.shuffle(groups[t])

    # Распределяем слоты по типам равномерно
    result = []
    slots_left = count
    types_left = [t for t in MAIN_ORDER if groups[t]]

    for i, t in enumerate(types_left):
        if not slots_left:
            break
        # Сколько взять из этого типа
        share = max(1, slots_left // (len(types_left) - i))
        taken = groups[t][:share]
        result.extend(taken)
        slots_left -= len(taken)

    # Если не добрали — дополняем из любого типа
    if slots_left > 0:
        used = {a["name"] for a in result}
        extra = [a for a in pool if a["name"] not in used]
        random.shuffle(extra)
        result.extend(extra[:slots_left])

    return result[:count]


def _soft_shuffle_by_type(asanas: list, order: list) -> list:
    """
    Перемешивает асаны внутри каждой группы типов,
    но сохраняет относительный порядок групп.
    """
    groups = {}
    for a in asanas:
        t = a.get("type", "")
        groups.setdefault(t, []).append(a)

    result = []
    for t in order:
        if t in groups:
            grp = groups[t][:]
            random.shuffle(grp)
            result.extend(grp)

    # Типы вне order — добавляем в конец
    for t, grp in groups.items():
        if t not in order:
            result.extend(grp)

    return result


def _arrange_selected(all_asanas: list, selected_names: list) -> list:
    """
    Если пользователь выбрал конкретные асаны —
    расставляем их в логичном порядке: разминка → основная → заминка.
    """
    by_name = {a["name"]: a for a in all_asanas}
    chosen = [by_name[n] for n in selected_names if n in by_name]

    if len(chosen) < 3:
        return chosen  # слишком мало — не трогаем

    warmup   = [a for a in chosen if a.get("type") in WARMUP_TYPES]
    cooldown = [a for a in chosen if a.get("type") in COOLDOWN_TYPES]
    savasana_list = [a for a in chosen if a["name"] in SAVASANA_NAMES]
    main     = [
        a for a in chosen
        if a not in warmup and a not in cooldown and a["name"] not in SAVASANA_NAMES
    ]

    warmup.sort(key=lambda a: _type_order(a, WARMUP_ORDER))
    main.sort(key=lambda a: _type_order(a, MAIN_ORDER))
    cooldown.sort(key=lambda a: _type_order(a, COOLDOWN_ORDER))

    result = warmup + main + cooldown
    # Шавасана всегда в самом конце
    for s in savasana_list:
        if s not in result:
            result.append(s)

    return result


def _find_savasana(asanas: list) -> dict | None:
    """Ищет Шавасану в базе данных."""
    for a in asanas:
        if a.get("name") in SAVASANA_NAMES or a.get("ru_name") in {"Поза трупа", "Шавасана"}:
            return a
    return None