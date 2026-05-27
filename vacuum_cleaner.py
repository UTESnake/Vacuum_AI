#py -3.13 "d:\Trí tuệ nhân tạo\Máy hút bụi\vacuum_cleaner.py"
import pygame
import copy
import sys
import time
import random
import heapq
from collections import deque

# ==============================================================================
# NODE & UTILITIES
# ==============================================================================
 
class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
 
def extract_path(node):
    path = []
    current = node
    while current is not None:
        path.append(current.state)
        current = current.parent
    return path[::-1]
 
def get_depth(node):
    depth = 0
    current = node
    while current.parent is not None:
        depth += 1
        current = current.parent
    return depth
 
def is_cycle(node):
    current_state = node.state
    check_node = node.parent
    while check_node is not None:
        if check_node.state == current_state:
            return True
        check_node = check_node.parent
    return False
 
def find_nearest(grid, start, algo_fn):
    best_p = best_g = None
    for g in grid.dirt_list():
        p = algo_fn(grid, start, g)
        if p and (best_p is None or len(p) < len(best_p)):
            best_p, best_g = p, g
    return best_p, best_g
 
 
# ==============================================================================
# PROBLEM CLASS (dùng cho IDS, Greedy, A*)
# ==============================================================================
 
class GridProblem:
    def __init__(self, grid, initial, goal):
        self.grid    = grid
        self.initial = initial
        self.goal    = goal
 
    def is_goal(self, state):
        return state == self.goal
 
    def expand(self, node):
        children = []
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            if self.grid.passable(*s):
                children.append(Node(state=s, parent=node))
        return children
 
    def h(self, state):
        """Heuristic Manhattan distance đến goal."""
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])
 
 
# ==============================================================================
# BFS
# ==============================================================================
 
def bfs1(grid, start, goal):
    """
    BFS chuẩn: đánh dấu reached ngay khi thêm vào frontier.
    Đảm bảo tìm đường đi ngắn nhất (theo số bước).
    """
    node = Node(state=start)
    if node.state == goal:
        return extract_path(node)
    frontier = deque([node])
    reached = {start}
    while frontier:
        node = frontier.popleft()
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            if grid.passable(*s):
                child = Node(state=s, parent=node)
                if s == goal:
                    return extract_path(child)
                if s not in reached:
                    reached.add(s)
                    frontier.append(child)
    return None
 
 
def bfs2(grid, start, goal):
    """
    BFS biến thể: kiểm tra goal khi pop ra khỏi frontier.
    Vẫn tìm được đường đi tối ưu nhưng expand nhiều node hơn bfs1.
    """
    node = Node(state=start)
    if node.state == goal:
        return extract_path(node)
    frontier = deque()
    frontier_states = set()
    frontier.append(node)
    frontier_states.add(node.state)
    reached = set()
    while frontier:
        node = frontier.popleft()
        frontier_states.remove(node.state)
        reached.add(node.state)
        if node.state == goal:
            return extract_path(node)
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            if grid.passable(*s):
                child = Node(state=s, parent=node)
                if child.state not in reached and child.state not in frontier_states:
                    frontier.append(child)
                    frontier_states.add(child.state)
    return None
 
 
# ==============================================================================
# DFS
# ==============================================================================
 
def dfs1(grid, start, goal):
    """
    DFS chuẩn dùng stack (list).
    KHÔNG đảm bảo tìm đường đi ngắn nhất.
    Đánh dấu reached khi thêm vào stack để tránh lặp.
    """
    node = Node(state=start)
    if node.state == goal:
        return extract_path(node)
    frontier = [node]
    reached = {start}
    while frontier:
        node = frontier.pop()          # pop từ cuối = LIFO (stack)
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            if grid.passable(*s):
                child = Node(state=s, parent=node)
                if s == goal:
                    return extract_path(child)
                if s not in reached:
                    reached.add(s)
                    frontier.append(child)
    return None
 
 
def dfs2(grid, start, goal):
    """
    DFS biến thể: kiểm tra goal khi pop.
    Tách frontier_states và reached để tránh revisit.
    KHÔNG đảm bảo tìm đường đi ngắn nhất.
    """
    node = Node(state=start)
    if node.state == goal:
        return extract_path(node)
    frontier = []
    frontier_states = set()
    frontier.append(node)
    frontier_states.add(node.state)
    reached = set()
    while frontier:
        node = frontier.pop()
        frontier_states.remove(node.state)
        reached.add(node.state)
        if node.state == goal:
            return extract_path(node)
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            if grid.passable(*s):
                child = Node(state=s, parent=node)
                if child.state not in reached and child.state not in frontier_states:
                    frontier.append(child)
                    frontier_states.add(child.state)
    return None
 
 
# ==============================================================================
# IDS (Iterative Deepening Search)
# ==============================================================================
 
FAILURE = "failure"
CUTOFF  = "cutoff"
 
def depth_limited_search(problem, l):
    """
    DFS có giới hạn độ sâu l.
    Trả về node nếu tìm thấy goal, CUTOFF nếu bị cắt, FAILURE nếu không tìm thấy.
    """
    frontier = [Node(problem.initial)]
    result = FAILURE
 
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        if get_depth(node) >= l:
            result = CUTOFF
        elif not is_cycle(node):
            for child in problem.expand(node):
                frontier.append(child)
    return result
 
 
def ids_problem(problem):
    depth = 0
    while True:
        result = depth_limited_search(problem, depth)
        if result != CUTOFF:
            return result
        depth += 1
 
 
def ids(grid, start, goal):
    """
    IDS: đảm bảo tìm đường đi ngắn nhất như BFS nhưng dùng ít bộ nhớ hơn.
    """
    problem = GridProblem(grid, start, goal)
    result = ids_problem(problem)
    if result is None or result == FAILURE:
        return None
    return extract_path(result)
 
 
# ==============================================================================
# UCS (Uniform Cost Search)
# ==============================================================================
 
def ucs(grid, start, goal):
    """
    UCS: mở rộng node có chi phí g(n) thấp nhất.
    Trên grid đồng nhất (cost = 1 mỗi bước) kết quả giống BFS.
    """
    counter = 0
    start_node = Node(state=start, parent=None)
    frontier = [(0, counter, start_node)]   # (g-cost, tie-break, node)
    reached = {start: 0}                    # state -> best g-cost đã thấy
 
    while frontier:
        cost, _, node = heapq.heappop(frontier)
 
        if node.state == goal:
            return extract_path(node)
 
        # Bỏ qua nếu đã tìm được đường tốt hơn đến node này
        if cost > reached.get(node.state, float('inf')):
            continue
 
        for dr, dc in DIRS:
            s = (node.state[0] + dr, node.state[1] + dc)
            new_cost = cost + 1
            if grid.passable(*s) and new_cost < reached.get(s, float('inf')):
                reached[s] = new_cost
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, Node(state=s, parent=node)))
    return None
 
 
# ==============================================================================
# GREEDY BEST-FIRST SEARCH
# ==============================================================================
 
def greedy(grid, start, goal):
    """
    Greedy Best-First: luôn mở rộng node có h(n) nhỏ nhất.
    KHÔNG đảm bảo tìm đường đi tối ưu.
    Dùng heapq để đảm bảo O(log n) thay vì O(n) với min().
    """
    problem = GridProblem(grid, start, goal)
    counter = 0
    start_node = Node(state=start, parent=None)
 
    # (h-cost, tie-break, node)
    frontier = [(problem.h(start), counter, start_node)]
    frontier_states = {start}
    reached = set()
 
    while frontier:
        h, _, node = heapq.heappop(frontier)
        frontier_states.discard(node.state)
 
        if problem.is_goal(node.state):
            return extract_path(node)
 
        reached.add(node.state)
 
        for child in problem.expand(node):
            m_state = child.state
            if m_state not in frontier_states and m_state not in reached:
                counter += 1
                heapq.heappush(frontier, (problem.h(m_state), counter, child))
                frontier_states.add(m_state)
 
    return None
 
 
# ==============================================================================
# A* SEARCH
# ==============================================================================
 
def a_star(grid, start, goal):
    """
    A*: mở rộng node có f(n) = g(n) + h(n) nhỏ nhất.
    Với heuristic admissible (Manhattan) đảm bảo tìm đường đi tối ưu.
    
    """
    problem = GridProblem(grid, start, goal)
    counter = 0
    start_node = Node(state=start, parent=None)
 
    g_costs = {start: 0}
    f_start = problem.h(start)                          # g=0 + h(start)
    frontier = [(f_start, counter, start_node)]
 
    while frontier:
        f, _, node = heapq.heappop(frontier)
 
        if problem.is_goal(node.state):
            return extract_path(node)
 
        # FIX: so sánh g trực tiếp từ dictionary thay vì tính ngược từ f
        current_g = f - problem.h(node.state)
        if current_g > g_costs.get(node.state, float('inf')):
            continue
 
        for child in problem.expand(node):
            m_state = child.state
            new_g = g_costs[node.state] + 1
 
            if new_g < g_costs.get(m_state, float('inf')):
                g_costs[m_state] = new_g
                f_cost = new_g + problem.h(m_state)
                counter += 1
                heapq.heappush(frontier, (f_cost, counter, child))
 
    return None
 

# ─── Màu sắc pastel sáng ─────────────────────────────────────────────────────
BG          = (240, 245, 250)   # nền trắng xanh nhạt
PANEL_BG    = (228, 236, 248)   # panel trái xanh pastel nhạt
BORDER      = (180, 200, 225)   # viền nhạt

# Màu nút pastel (idle / active-hover)
P_BLUE      = (168, 210, 245)   # xanh dương pastel  → BFS
P_BLUE_HI   = (110, 170, 230)
P_PURPLE    = (200, 175, 240)   # tím pastel         → DFS
P_PURPLE_HI = (165, 130, 220)
P_INDIGO    = (180, 190, 240)   # xanh chàm pastel   → IDS
P_INDIGO_HI = (140, 150, 220)
P_MINT      = (190, 240, 210)   # xanh mint pastel   → UCS
P_MINT_HI   = (150, 220, 170)
P_GREEN     = (170, 230, 185)   # xanh lá pastel     → Bat Dau
P_GREEN_HI  = (110, 200, 135)
P_RED       = (250, 185, 185)   # đỏ pastel          → Dung
P_RED_HI    = (235, 130, 130)
P_ORANGE    = (250, 215, 155)   # vàng cam pastel    → Reset
P_ORANGE_HI = (235, 175,  90)
P_CYAN      = (165, 230, 225)   # cyan pastel        → Ngau Nhien
P_CYAN_HI   = (100, 200, 195)
P_PINK      = (245, 185, 215)   # hồng pastel        → Ve Tuong
P_PINK_HI   = (230, 140, 185)
P_YELLOW    = (250, 235, 150)   # vàng pastel        → Ve Bui
P_YELLOW_HI = (235, 210,  90)
P_TEAL      = (160, 225, 215)   # teal pastel        → Dat Robot
P_TEAL_HI   = ( 95, 195, 182)

# Màu text trên nút (tối để dễ đọc trên nền sáng)
TXT_DARK    = ( 55,  65,  90)

# Màu ô lưới
CELL_EMPTY  = (210, 222, 238)   # ô trống xanh nhạt
CELL_WALL   = (140, 100, 175)   # tường tím vừa – dễ thấy
CELL_DIRTY  = (230, 175,  80)   # bụi vàng ấm
CELL_CLEAN  = (175, 225, 190)   # đã dọn – xanh lá nhạt
PATH_DOT    = (100, 160, 210)   # dot đường đi

GOLD        = (220, 160,  50)
GOLD_LIGHT  = (240, 195,  85)
GOLD_BRIGHT = (255, 225, 120)

WHITE       = (255, 255, 255)
LGRAY       = ( 90, 105, 135)   # text phụ
DGRAY       = (140, 155, 175)   # text mờ / nhãn

# ─── Layout ──────────────────────────────────────────────────────────────────
CELL_PX   = 58          # kích thước mỗi ô
COLS      = 8           # ma trận 8×6
ROWS      = 8
PANEL_W   = 210
GRID_X    = PANEL_W + 10
GRID_Y    = 76
LOG_LINES = 6           # số dòng log hiển thị dưới lưới
LOG_LINE_H = 18

WIN_W = GRID_X + COLS * CELL_PX + 14
WIN_H = 700   # cố định — đủ cho panel + lưới + log

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
EMPTY, DIRTY, WALL = 0, 1, 2

# ─── Pygame ──────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Vacuum Cleaner AI - BFS & DFS")
clock = pygame.time.Clock()

# ═══════════════════════════════════════════════════════════════════════════

# Cho phép dùng font hệ thống có hỗ trợ Emoji
def make_font(size, bold=False):
    # Ưu tiên các font có hỗ trợ Emoji lên đầu
    for name in ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Segoe UI", "Arial"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: return f
        except Exception:
            pass
    return pygame.font.Font(None, size + 4)

def make_mono(size):
    for name in ["Consolas", "Courier New", "DejaVu Sans Mono"]:
        try:
            f = pygame.font.SysFont(name, size)
            if f: return f
        except Exception:
            pass
    return pygame.font.Font(None, size + 4)

F_TITLE = make_font(20, bold=True)
F_MED   = make_font(14)
F_SM    = make_font(12)
F_MONO  = make_mono(12)


# ═══════════════════════════════════════════════════════════════════════════
class Grid:
    def __init__(self):
        self.cells = [[EMPTY] * COLS for _ in range(ROWS)]

    def reset(self):
        self.cells = [[EMPTY] * COLS for _ in range(ROWS)]

    def randomize(self):
        self.reset()
        for r in range(ROWS):
            for c in range(COLS):
                v = random.random()
                if v < 0.10:
                    self.cells[r][c] = WALL
                elif v < 0.38:
                    self.cells[r][c] = DIRTY

    def snapshot(self):
        return [row[:] for row in self.cells]

    def restore(self, saved):
        self.cells = [row[:] for row in saved]

    def passable(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS and self.cells[r][c] != WALL

    def dirt_list(self):
        return [(r, c) for r in range(ROWS) for c in range(COLS)
                if self.cells[r][c] == DIRTY]

    def clean(self, r, c):
        if self.cells[r][c] == DIRTY:
            self.cells[r][c] = EMPTY
            return True
        return False

# ═══════════════════════════════════════════════════════════════════════════
class Btn:
    """Nút đơn giản, chỉ dùng text ASCII."""
    def __init__(self, rect, text, bg_idle, bg_active):
        self.rect      = pygame.Rect(rect)
        self.text      = text
        self.bg_idle   = bg_idle
        self.bg_active = bg_active
        self.active    = False
        self.hovered   = False

    def draw(self, surf):
        bg = self.bg_active if (self.active or self.hovered) else self.bg_idle
        pygame.draw.rect(surf, bg,     self.rect, border_radius=8)
        pygame.draw.rect(surf, BORDER, self.rect, 2, border_radius=8)
        lbl = F_MED.render(self.text, True, TXT_DARK)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
                and self.rect.collidepoint(ev.pos))


# ═══════════════════════════════════════════════════════════════════════════
class VacuumApp:
    # Button layout constants
    BX = 10; BW = 190; BH = 32; GAP = 7
    

    def __init__(self):
        self.grid    = Grid()
        self.grid.randomize()
        self.vpos    = (0, 0)
        self.algo    = 'BFS1'
        self.edit    = 'none'   # 'wall' | 'dirt' | 'vacuum' | 'none'
        self.path    = []
        self.trail   = set()
        self.stimer  = 0.0
        self.delay   = 0.20    # giây/bước
        self.running = False
        self.done    = False
        self.n_steps = 0
        self.n_clean = 0
        self.log     = []
        self._last_painted = None
        self._build_ui()
        self._saved_grid = None   # snapshot lưới để Reset khôi phục

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        x, w, h, g = self.BX, self.BW, self.BH, self.GAP
        y = 100

        # --- Thuật toán ---
        # Chia đôi chiều rộng cho 2 cột
        half_w = (w - g) // 2
        x2 = x + half_w + g

        self.b_bfs1   = Btn((x,  y,         half_w, h), "🔍 BFS 1", P_BLUE,   P_BLUE_HI)
        self.b_bfs2   = Btn((x2, y,         half_w, h), "🔍 BFS 2", P_BLUE,   P_BLUE_HI)
        self.b_dfs1   = Btn((x,  y+h+g,     half_w, h), "📍 DFS 1", P_PURPLE, P_PURPLE_HI)
        self.b_dfs2   = Btn((x2, y+h+g,     half_w, h), "📍 DFS 2", P_PURPLE, P_PURPLE_HI)
        self.b_ids    = Btn((x,  y+2*(h+g), half_w, h), "🔄 IDS",    P_INDIGO, P_INDIGO_HI)
        self.b_ucs    = Btn((x2, y+2*(h+g), half_w, h), "⚖️ UCS",    P_MINT,   P_MINT_HI)
        self.b_greedy = Btn((x,  y+3*(h+g), half_w, h), "🎯 Greedy", P_CYAN,   P_CYAN_HI)
        self.b_astar  = Btn((x2, y+3*(h+g), half_w, h), "⭐ A*",      P_YELLOW, P_YELLOW_HI)

        y += 4*(h+g) + 8

        # --- Điều khiển ---
        self.b_go   = Btn((x, y,         w, h), "▶️ Start",    P_GREEN,  P_GREEN_HI)
        self.b_stop = Btn((x, y+h+g,     w, h), "⏹️ Stop",       P_RED,    P_RED_HI)
        self.b_rst  = Btn((x, y+2*(h+g), w, h), "🔄 Reset",      P_ORANGE, P_ORANGE_HI)
        self.b_rnd  = Btn((x, y+3*(h+g), w, h), "🎲 Random", P_CYAN,   P_CYAN_HI)
        y += 4*(h+g) + 24

        # --- Chỉnh sửa ---
        self.b_wall = Btn((x, y,         w, h), "🧱 Wall painting", P_PINK,   P_PINK_HI)
        self.b_dirt = Btn((x, y+h+g,     w, h), "✨ Dust painting", P_YELLOW, P_YELLOW_HI)
        self.b_vac  = Btn((x, y+2*(h+g), w, h), "🤖 Place Robot", P_TEAL,   P_TEAL_HI)
        self._edit_btn_bottom_y = y + 2*(h+g) + h

        # Đưa cả 4 nút mới vào danh sách
        self.all_btns = [
            self.b_bfs1, self.b_bfs2, self.b_dfs1, self.b_dfs2,
            self.b_ids, self.b_ucs, self.b_greedy, self.b_astar, # Đã thêm self.b_astar
            self.b_go, self.b_stop, self.b_rst, self.b_rnd,
            self.b_wall, self.b_dirt, self.b_vac,
        ]

        # Speed slider
        self.sl_rect = pygame.Rect(x, self._edit_btn_bottom_y + 26, w, 10)
        self.sl_drag = False
        self.spd_pct = 0.50   # 0=chậm 1=nhanh

        self._sync_algo()

    def _sync_algo(self):
        self.b_bfs1.active   = (self.algo == 'BFS1')
        self.b_bfs2.active   = (self.algo == 'BFS2')
        self.b_dfs1.active   = (self.algo == 'DFS1')
        self.b_dfs2.active   = (self.algo == 'DFS2')
        self.b_ids.active    = (self.algo == 'IDS')
        self.b_ucs.active    = (self.algo == 'UCS')
        self.b_greedy.active = (self.algo == 'GREEDY')
        self.b_astar.active  = (self.algo == 'A_STAR')

    def _sync_edit(self):
        self.b_wall.active = (self.edit == 'wall')
        self.b_dirt.active = (self.edit == 'dirt')
        self.b_vac.active  = (self.edit == 'vacuum')

    # ── Logging ─────────────────────────────────────────────────────────────
    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {msg}")
        if len(self.log) > 100:
            self.log.pop(0)

    # ── Grid hit-test ────────────────────────────────────────────────────────
    def _cell_at(self, px, py):
        c = (px - GRID_X) // CELL_PX
        r = (py - GRID_Y) // CELL_PX
        if 0 <= r < ROWS and 0 <= c < COLS:
            return r, c
        return None

    # ── AI ──────────────────────────────────────────────────────────────────
    def _plan(self):
        if   self.algo == 'BFS1':   fn = bfs1
        elif self.algo == 'BFS2':   fn = bfs2
        elif self.algo == 'DFS1':   fn = dfs1
        elif self.algo == 'DFS2':   fn = dfs2
        elif self.algo == 'IDS':    fn = ids
        elif self.algo == 'UCS':    fn = ucs
        elif self.algo == 'GREEDY': fn = greedy
        elif self.algo == 'A_STAR': fn = a_star
        else:                       fn = bfs1

        p, g = find_nearest(self.grid, self.vpos, fn)
        if p is None:
            self.done = True; self.running = False
            self._log("Hoàn thành! Hết bụi.")
            return
        self.path = p[1:]
        self._log(f"{self.algo}: {self.vpos}->{g} ({len(p)} bước)")
    def _step(self):
        if not self.path:
            r, c = self.vpos
            if self.grid.clean(r, c):
                self.n_clean += 1
                self.trail.add((r, c))
                self._log(f"Hút bụi ({r},{c})")
            self._plan()
            return
        nxt = self.path.pop(0)
        self.vpos = nxt
        self.n_steps += 1
        if self.grid.clean(*nxt):
            self.n_clean += 1
            self.trail.add(nxt)

    # ── Actions ─────────────────────────────────────────────────────────────
    def _start(self):
        if self.done: self._reset_sim()
        self.running = True; self.done = False
        self._log(f"Start [{self.algo}]")
        if not self.path: self._plan()

    def _reset(self):
        self.running = self.done = False
        self.path = []; self.trail = set()
        self.vpos = (0, 0); self.n_steps = self.n_clean = 0
        self.log = []
        if self._saved_grid is not None:
            self.grid.restore(self._saved_grid)   # ← khôi phục lưới ban đầu
            self._log("Reset về sơ đồ ban đầu")
        else:
            self.grid.reset()
            self._log("Reset lưới")

    def _reset_sim(self):
        self.path = []; self.trail = set()
        self.vpos = (0, 0); self.n_steps = self.n_clean = 0
        self.done = False

    def _randomize(self):
        self.running = self.done = False
        self.path = []; self.trail = set()
        self.vpos = (0, 0); self.n_steps = self.n_clean = 0
        self.grid.randomize()
        self._saved_grid = self.grid.snapshot()   # ← lưu lại
        self._log("Tạo lưới ngẫu nhiên")

    # ── Draw ────────────────────────────────────────────────────────────────
    def _draw_panel(self):
        # Nền panel
        pygame.draw.rect(screen, PANEL_BG, (0, 0, PANEL_W, WIN_H))
        pygame.draw.line(screen, BORDER, (PANEL_W, 0), (PANEL_W, WIN_H), 2)

        # Tiêu đề
        screen.blit(F_TITLE.render("Vacuum AI", True, (70, 120, 200)), (12, 14))
        screen.blit(F_SM.render("BFS & DFS Pathfinding", True, LGRAY), (14, 42))
        pygame.draw.line(screen, BORDER, (12, 62), (PANEL_W-12, 62), 1)
        screen.blit(F_SM.render("ALGORITHM", True, DGRAY), (12, 76))

        # Tất cả nút
        for b in self.all_btns:
            b.draw(screen)

        # Nhãn phần chỉnh sửa
        edit_label_y = self._edit_btn_bottom_y - 3*(self.BH + self.GAP) - 10
        screen.blit(F_SM.render("EDIT", True, DGRAY), (12, edit_label_y))

        # ── Speed slider ────────────────────────────────────────────────────
        sr = self.sl_rect
        sl_label_y = sr.top - 18
        screen.blit(F_SM.render(f"SPEED  {int(self.spd_pct*100)}%", True, LGRAY),
                    (12, sl_label_y))
        pygame.draw.rect(screen, (200, 215, 230), sr, border_radius=5)
        fw = max(1, int(self.spd_pct * sr.width))
        pygame.draw.rect(screen, P_TEAL_HI, (sr.x, sr.y, fw, sr.height), border_radius=5)
        pygame.draw.circle(screen, (60, 130, 180), (sr.x + fw, sr.centery), 7)

        # ── Stats box ───────────────────────────────────────────────────────
        st_y = sr.bottom + 14
        box_h = 86
        pygame.draw.rect(screen, (215, 228, 245), (12, st_y, PANEL_W-24, box_h), border_radius=8)
        pygame.draw.rect(screen, BORDER,          (12, st_y, PANEL_W-24, box_h), 1, border_radius=8)
        rows_data = [
            ("Step:",    str(self.n_steps),                (70, 130, 210)),
            ("Vacuumed:",     str(self.n_clean),                (60, 170, 100)),
            ("Left:",    str(len(self.grid.dirt_list())),  (200, 130,  40)),
            ("Algorithm:", self.algo,                        (70, 120, 200)),
        ]
        for i, (k, v, col) in enumerate(rows_data):
            screen.blit(F_SM.render(k, True, LGRAY),  (20, st_y + 8 + i*19))
            screen.blit(F_MED.render(v, True, col),   (112, st_y + 6 + i*19))

        # ── Status text ─────────────────────────────────────────────────────
        scol = (55, 170, 90) if self.running else ((180, 130, 40) if self.done else LGRAY)
        stxt = "RUNNING..." if self.running else ("COMPLETE!" if self.done else "READY!!!")
        status_y = st_y + box_h + 10
        if status_y + 20 < WIN_H:
            screen.blit(F_MED.render(stxt, True, scol), (14, status_y))

    def _draw_header(self):
        pygame.draw.rect(screen, PANEL_BG, (PANEL_W, 0, WIN_W - PANEL_W, GRID_Y - 8))
        pygame.draw.line(screen, BORDER, (PANEL_W, GRID_Y - 10), (WIN_W, GRID_Y - 10), 1)
        info = (f"Map: {COLS}x{ROWS}  |  Dusk: {len(self.grid.dirt_list())}  |  "
                f"Algo: {self.algo}  |  {'RUNNING' if self.running else 'STOP'}")
        screen.blit(F_MED.render(info, True, LGRAY), (GRID_X + 4, 12))
        screen.blit(F_SM.render("Click the box to edit (while in use)", True, DGRAY),
                    (GRID_X + 4, 34))

    def _draw_grid(self):
        # Viền ngoài lưới — pastel shadow
        outer = pygame.Rect(GRID_X - 3, GRID_Y - 3,
                            COLS * CELL_PX + 6, ROWS * CELL_PX + 6)
        pygame.draw.rect(screen, (175, 195, 220), outer, border_radius=8)

        path_set = set(self.path)

        for r in range(ROWS):
            for c in range(COLS):
                val  = self.grid.cells[r][c]
                px   = GRID_X + c * CELL_PX
                py   = GRID_Y + r * CELL_PX
                rect = pygame.Rect(px + 1, py + 1, CELL_PX - 2, CELL_PX - 2)

                # Màu nền ô
                if   val == WALL:           bg = CELL_WALL
                elif val == DIRTY:          bg = CELL_DIRTY
                elif (r, c) in self.trail:  bg = CELL_CLEAN
                else:                       bg = CELL_EMPTY
                pygame.draw.rect(screen, bg, rect, border_radius=3)

                # Tường: vạch kẻ chéo – tím vừa trên nền sáng
                if val == WALL:
                    for i in range(0, CELL_PX, 9):
                        pygame.draw.line(screen, (115, 75, 160),
                                         (px+2, py+2+i), (px+2+i, py+2), 1)
                        pygame.draw.line(screen, (115, 75, 160),
                                         (px+CELL_PX-3, py+2+i), (px+2+i, py+CELL_PX-3), 1)

                # Bụi
                if val == DIRTY:
                    cx, cy = rect.centerx, rect.centery
                    pygame.draw.circle(screen, GOLD,        (cx, cy), 11)
                    pygame.draw.circle(screen, GOLD_LIGHT,  (cx, cy),  7)
                    pygame.draw.circle(screen, GOLD_BRIGHT, (cx, cy),  3)

                # Đường đi dự kiến
                if (r, c) in path_set:
                    hl = pygame.Surface((CELL_PX-2, CELL_PX-2), pygame.SRCALPHA)
                    hl.fill((0, 140, 195, 50))
                    screen.blit(hl, rect.topleft)
                    pygame.draw.circle(screen, PATH_DOT, rect.center, 4)

                # Viền ô
                pygame.draw.rect(screen, BORDER, (px, py, CELL_PX, CELL_PX), 1)

        # Trail glow nhạt trên nền sáng
        for (r, c) in self.trail:
            cx = GRID_X + c * CELL_PX + CELL_PX // 2
            cy = GRID_Y + r * CELL_PX + CELL_PX // 2
            glow = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(glow, (80, 180, 120, 55), (9, 9), 9)
            screen.blit(glow, (cx - 9, cy - 9))

        # Robot
        vr, vc = self.vpos
        vx = GRID_X + vc * CELL_PX + CELL_PX // 2
        vy = GRID_Y + vr * CELL_PX + CELL_PX // 2
        ROB = (60, 140, 210)   # xanh dương đậm hơn để nổi trên nền sáng
        for rad, alpha in [(20, 30), (15, 65), (10, 110)]:
            g = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
            pygame.draw.circle(g, (*ROB, alpha), (rad, rad), rad)
            screen.blit(g, (vx - rad, vy - rad))
        pygame.draw.circle(screen, ROB,   (vx, vy), 13)
        pygame.draw.circle(screen, WHITE, (vx, vy),  8)
        pygame.draw.circle(screen, ROB,   (vx, vy),  3)
        pygame.draw.circle(screen, TXT_DARK, (vx-5, vy-3), 2)
        pygame.draw.circle(screen, TXT_DARK, (vx+5, vy-3), 2)

    def _draw_log(self):
        """Log hiển thị dưới lưới — chiều cao cố định, không bị cắt."""
        lx = GRID_X
        ly = GRID_Y + ROWS * CELL_PX + 8
        lw = COLS * CELL_PX
        lh = LOG_LINES * LOG_LINE_H + 12

        # Kiểm tra không vượt cửa sổ
        if ly + lh > WIN_H:
            lh = WIN_H - ly - 4

        pygame.draw.rect(screen, (215, 228, 245), (lx, ly, lw, lh), border_radius=5)
        pygame.draw.rect(screen, BORDER,           (lx, ly, lw, lh), 1, border_radius=5)

        # Tính chiều rộng tối đa (chars) cho text
        max_px = lw - 16
        shown = self.log[-LOG_LINES:]
        for i, msg in enumerate(shown):
            txt = msg
            rendered = F_MONO.render(txt, True, LGRAY)
            while rendered.get_width() > max_px and len(txt) > 4:
                txt = txt[:-2] + "~"
                rendered = F_MONO.render(txt, True, LGRAY)
            col = (60, 140, 200) if "Hoãn" in msg else ((60, 160, 90) if "Hút" in msg else LGRAY)
            rendered = F_MONO.render(txt, True, col)
            screen.blit(rendered, (lx + 8, ly + 6 + i * LOG_LINE_H))

    # ── Main loop ────────────────────────────────────────────────────────────
    def run(self):
        last = time.time()
        while True:
            dt   = time.time() - last
            last = time.time()
            mpos = pygame.mouse.get_pos()

            for b in self.all_btns:
                b.update_hover(mpos)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    if ev.key == pygame.K_SPACE:
                        if self.running: self.running = False
                        else: self._start()

                # Slider drag
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.sl_rect.collidepoint(ev.pos):
                        self.sl_drag = True
                if ev.type == pygame.MOUSEBUTTONUP:
                    self.sl_drag = False
                    self._last_painted = None
                if ev.type == pygame.MOUSEMOTION and self.sl_drag:
                    r = max(0., min(1., (ev.pos[0] - self.sl_rect.x) / self.sl_rect.width))
                    self.spd_pct = r
                    self.delay   = (1 - r) * 0.46 + 0.02   # 0.48s … 0.02s

                # Buttons
                # --- Nút Thuật toán ---
                if self.b_bfs1.is_clicked(ev):
                    self.algo = 'BFS1'; self._sync_algo(); self._log("Thuật toán: BFS 1")
                if self.b_bfs2.is_clicked(ev):
                    self.algo = 'BFS2'; self._sync_algo(); self._log("Thuật toán: BFS 2")
                if self.b_dfs1.is_clicked(ev):
                    self.algo = 'DFS1'; self._sync_algo(); self._log("Thuật toán: DFS 1")
                if self.b_dfs2.is_clicked(ev):
                    self.algo = 'DFS2'; self._sync_algo(); self._log("Thuật toán: DFS 2")
                if self.b_ids.is_clicked(ev):
                    self.algo = 'IDS'; self._sync_algo(); self._log("Thuật toán: IDS")
                if self.b_ucs.is_clicked(ev):
                    self.algo = 'UCS'; self._sync_algo(); self._log("Thuật toán: UCS")
                if self.b_greedy.is_clicked(ev):
                    self.algo = 'GREEDY'; self._sync_algo(); self._log("Thuật toán: Greedy")
                if self.b_astar.is_clicked(ev):
                    self.algo = 'A_STAR'; self._sync_algo(); self._log("Thuật toán: A*")

                # --- Nút Điều khiển ---
                if self.b_go.is_clicked(ev):
                    self._start()
                if self.b_stop.is_clicked(ev):
                    self.running = False; self._log("Đã dừng")
                if self.b_rst.is_clicked(ev):
                    self._reset()
                if self.b_rnd.is_clicked(ev):
                    self._randomize()

                # --- Nút Chỉnh sửa (Edit) ---
                if self.b_wall.is_clicked(ev):
                    self.edit = 'wall'; self._sync_edit(); self._log("Chế độ: Vẽ tường")
                if self.b_dirt.is_clicked(ev):
                    self.edit = 'dirt'; self._sync_edit(); self._log("Chế độ: Vẽ bụi")
                if self.b_vac.is_clicked(ev):
                    self.edit = 'vacuum'; self._sync_edit(); self._log("Chế độ: Đặt Robot")

                # Click lên ô (toggle khi nhấn)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    cell = self._cell_at(*ev.pos)
                    if cell and not self.running:
                        r, c = cell
                        if self.edit == 'wall':
                            self.grid.cells[r][c] = WALL if self.grid.cells[r][c] != WALL else EMPTY
                        elif self.edit == 'dirt':
                            self.grid.cells[r][c] = DIRTY if self.grid.cells[r][c] != DIRTY else EMPTY
                        elif self.edit == 'vacuum':
                            if self.grid.cells[r][c] != WALL: self.vpos = (r, c)
                        self._last_painted = cell

            # Kéo chuột để vẽ liên tục (không flip)
            if pygame.mouse.get_pressed()[0] and self.edit in ('wall', 'dirt') and not self.running:
                cell = self._cell_at(*mpos)
                if cell and cell != self._last_painted:
                    r, c = cell
                    tgt = WALL if self.edit == 'wall' else DIRTY
                    self.grid.cells[r][c] = tgt
                    self._last_painted = cell

            # Simulation tick
            if self.running and not self.done:
                self.stimer += dt
                if self.stimer >= self.delay:
                    self.stimer = 0.
                    self._step()

            # Draw
            screen.fill(BG)
            self._draw_header()
            self._draw_panel()
            self._draw_grid()
            self._draw_log()
            pygame.display.flip()
            clock.tick(60)


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    VacuumApp().run()
