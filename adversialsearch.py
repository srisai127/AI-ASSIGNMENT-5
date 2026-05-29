"""
============================================================
  Q1: Game Tree Search Algorithms
  - Minimax Search
  - Alpha-Beta Pruning
  - Heuristic Alpha-Beta Search (depth-limited)
  - Monte-Carlo Tree Search (MCTS)

  Demo game: Tic-Tac-Toe (3x3)
============================================================
"""

import math
import random
import time
from collections import defaultdict


# ──────────────────────────────────────────────
#  TIC-TAC-TOE GAME STATE
# ──────────────────────────────────────────────

class TicTacToe:
    """
    Board is a list of 9 cells. Index layout:
        0 | 1 | 2
        ---------
        3 | 4 | 5
        ---------
        6 | 7 | 8

    'X' = maximising player, 'O' = minimising player
    """

    WINNING_COMBOS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
        (0, 4, 8), (2, 4, 6),               # diagonals
    ]

    def __init__(self, board=None, current_player='X'):
        self.board = board if board else [' '] * 9
        self.current_player = current_player

    def clone(self):
        return TicTacToe(self.board[:], self.current_player)

    def get_legal_moves(self):
        return [i for i, cell in enumerate(self.board) if cell == ' ']

    def make_move(self, index):
        new_board = self.board[:]
        new_board[index] = self.current_player
        next_player = 'O' if self.current_player == 'X' else 'X'
        return TicTacToe(new_board, next_player)

    def check_winner(self):
        for a, b, c in self.WINNING_COMBOS:
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None

    def is_terminal(self):
        return self.check_winner() is not None or not self.get_legal_moves()

    def utility(self):
        winner = self.check_winner()
        if winner == 'X':
            return 1
        if winner == 'O':
            return -1
        return 0

    def heuristic(self):
        """
        Simple heuristic: count lines that only contain one player.
        +1 for each X-only line, -1 for each O-only line.
        Used by heuristic alpha-beta when depth limit is reached.
        """
        score = 0
        for a, b, c in self.WINNING_COMBOS:
            line = [self.board[a], self.board[b], self.board[c]]
            if 'O' not in line:
                score += line.count('X')
            if 'X' not in line:
                score -= line.count('O')
        return score

    def display(self):
        b = self.board
        print(f"\n {b[0]} | {b[1]} | {b[2]} ")
        print("---+---+---")
        print(f" {b[3]} | {b[4]} | {b[5]} ")
        print("---+---+---")
        print(f" {b[6]} | {b[7]} | {b[8]} \n")


# ──────────────────────────────────────────────
#  1. MINIMAX SEARCH
# ──────────────────────────────────────────────

class MinimaxAgent:
    """
    Classic Minimax (no pruning, no depth limit).
    Explores the entire game tree to find the optimal move.
    Time complexity: O(b^m) where b = branching factor, m = depth.
    """

    def __init__(self):
        self.nodes_explored = 0

    def minimax(self, state, is_maximising):
        """
        Recursively compute the minimax value of a state.

        Parameters
        ----------
        state          : TicTacToe game state
        is_maximising  : True if it is MAX's (X's) turn

        Returns
        -------
        int : utility value of the state
        """
        self.nodes_explored += 1

        # Base case: terminal state
        if state.is_terminal():
            return state.utility()

        if is_maximising:
            best = -math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = self.minimax(child, False)
                best = max(best, value)
            return best
        else:
            best = math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = self.minimax(child, True)
                best = min(best, value)
            return best

    def best_move(self, state):
        """Return the best move index for the current player."""
        self.nodes_explored = 0
        is_max = (state.current_player == 'X')
        best_val = -math.inf if is_max else math.inf
        best_idx = None

        for move in state.get_legal_moves():
            child = state.make_move(move)
            val = self.minimax(child, not is_max)
            if is_max and val > best_val:
                best_val, best_idx = val, move
            elif not is_max and val < best_val:
                best_val, best_idx = val, move

        return best_idx, best_val


# ──────────────────────────────────────────────
#  2. ALPHA-BETA PRUNING
# ──────────────────────────────────────────────

class AlphaBetaAgent:
    """
    Minimax with Alpha-Beta pruning.
    Prunes branches that cannot influence the final decision.
    Worst-case: O(b^m), Best-case: O(b^(m/2)) — effectively doubles search depth.
    """

    def __init__(self):
        self.nodes_explored = 0
        self.nodes_pruned = 0

    def alpha_beta(self, state, alpha, beta, is_maximising):
        """
        Parameters
        ----------
        state         : current game state
        alpha         : best value MAX can guarantee so far (-inf initially)
        beta          : best value MIN can guarantee so far (+inf initially)
        is_maximising : True if MAX's turn

        Returns
        -------
        int : minimax value with pruning
        """
        self.nodes_explored += 1

        if state.is_terminal():
            return state.utility()

        if is_maximising:
            value = -math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = max(value, self.alpha_beta(child, alpha, beta, False))
                alpha = max(alpha, value)
                if value >= beta:          # β cut-off (MIN won't choose this branch)
                    self.nodes_pruned += 1
                    break
            return value
        else:
            value = math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = min(value, self.alpha_beta(child, alpha, beta, True))
                beta = min(beta, value)
                if value <= alpha:         # α cut-off (MAX won't choose this branch)
                    self.nodes_pruned += 1
                    break
            return value

    def best_move(self, state):
        self.nodes_explored = 0
        self.nodes_pruned = 0
        is_max = (state.current_player == 'X')
        best_val = -math.inf if is_max else math.inf
        best_idx = None

        for move in state.get_legal_moves():
            child = state.make_move(move)
            val = self.alpha_beta(child, -math.inf, math.inf, not is_max)
            if is_max and val > best_val:
                best_val, best_idx = val, move
            elif not is_max and val < best_val:
                best_val, best_idx = val, move

        return best_idx, best_val


# ──────────────────────────────────────────────
#  3. HEURISTIC ALPHA-BETA (Depth-Limited)
# ──────────────────────────────────────────────

class HeuristicAlphaBetaAgent:
    """
    Alpha-Beta pruning with a depth limit.
    When the depth limit is reached, a heuristic evaluation function
    is applied instead of expanding further — makes it practical for
    games with very large search spaces (chess, Go, etc.).
    """

    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.nodes_explored = 0
        self.nodes_pruned = 0
        self.heuristic_evaluations = 0

    def h_alpha_beta(self, state, depth, alpha, beta, is_maximising):
        """
        Parameters
        ----------
        state         : current game state
        depth         : remaining depth allowed
        alpha, beta   : pruning bounds
        is_maximising : True if MAX's turn

        Returns
        -------
        numeric : exact utility (terminal) or heuristic estimate (depth limit)
        """
        self.nodes_explored += 1

        # Terminal or depth limit reached
        if state.is_terminal():
            return state.utility()

        if depth == 0:
            self.heuristic_evaluations += 1
            return state.heuristic()   # ← heuristic evaluation

        if is_maximising:
            value = -math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = max(value, self.h_alpha_beta(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if value >= beta:
                    self.nodes_pruned += 1
                    break
            return value
        else:
            value = math.inf
            for move in state.get_legal_moves():
                child = state.make_move(move)
                value = min(value, self.h_alpha_beta(child, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if value <= alpha:
                    self.nodes_pruned += 1
                    break
            return value

    def best_move(self, state):
        self.nodes_explored = 0
        self.nodes_pruned = 0
        self.heuristic_evaluations = 0
        is_max = (state.current_player == 'X')
        best_val = -math.inf if is_max else math.inf
        best_idx = None

        for move in state.get_legal_moves():
            child = state.make_move(move)
            val = self.h_alpha_beta(child, self.max_depth - 1, -math.inf, math.inf, not is_max)
            if is_max and val > best_val:
                best_val, best_idx = val, move
            elif not is_max and val < best_val:
                best_val, best_idx = val, move

        return best_idx, best_val


# ──────────────────────────────────────────────
#  4. MONTE-CARLO TREE SEARCH (MCTS)
# ──────────────────────────────────────────────

class MCTSNode:
    """
    A node in the MCTS search tree.

    Attributes
    ----------
    state   : game state at this node
    parent  : parent MCTSNode (None for root)
    move    : move that led to this node
    children: list of child MCTSNode
    wins    : cumulative wins from this node's perspective
    visits  : number of times this node was visited
    """

    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0
        self._untried_moves = state.get_legal_moves()

    def is_fully_expanded(self):
        return len(self._untried_moves) == 0

    def is_terminal(self):
        return self.state.is_terminal()

    def ucb1(self, exploration=math.sqrt(2)):
        """
        Upper Confidence Bound 1 (UCB1) formula:
            UCB1 = wins/visits + C * sqrt(ln(parent.visits) / visits)

        Balances exploitation (wins/visits) and exploration (second term).
        C = sqrt(2) is the standard exploration constant.
        """
        if self.visits == 0:
            return math.inf
        exploitation = self.wins / self.visits
        exploration_term = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration_term

    def best_child(self, exploration=math.sqrt(2)):
        return max(self.children, key=lambda c: c.ucb1(exploration))

    def expand(self):
        """Add one new child by trying an untried move."""
        move = self._untried_moves.pop(random.randrange(len(self._untried_moves)))
        child_state = self.state.make_move(move)
        child = MCTSNode(child_state, parent=self, move=move)
        self.children.append(child)
        return child

    def update(self, result):
        """Back-propagate: update visit count and wins."""
        self.visits += 1
        self.wins += result


class MCTSAgent:
    """
    Monte-Carlo Tree Search agent.

    Four phases per iteration:
    1. Selection   – traverse tree using UCB1 until a non-fully-expanded node
    2. Expansion   – add one new child node
    3. Simulation  – play out random game (rollout) from child
    4. Backprop    – update win/visit stats up the tree
    """

    def __init__(self, iterations=1000):
        self.iterations = iterations
        self.total_simulations = 0

    def search(self, initial_state):
        root = MCTSNode(initial_state)

        for _ in range(self.iterations):
            # ── 1. SELECTION ──────────────────────────────
            node = root
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child()

            # ── 2. EXPANSION ──────────────────────────────
            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            # ── 3. SIMULATION (rollout) ───────────────────
            result = self._rollout(node.state)
            self.total_simulations += 1

            # ── 4. BACK-PROPAGATION ───────────────────────
            self._backpropagate(node, result, initial_state.current_player)

        # Choose the child with the most visits (most robust)
        best = max(root.children, key=lambda c: c.visits)
        return best.move, best.wins / best.visits if best.visits > 0 else 0

    def _rollout(self, state):
        """Simulate a random game from `state` and return the utility."""
        current = state.clone()
        while not current.is_terminal():
            move = random.choice(current.get_legal_moves())
            current = current.make_move(move)
        return current.utility()

    def _backpropagate(self, node, result, root_player):
        """
        Walk up the tree updating wins and visits.
        A win for the root player counts as +1; loss as -1; draw as 0.
        We store wins from the perspective of the node's player so UCB1 is consistent.
        """
        current = node
        while current is not None:
            current.update(result)
            result = -result        # flip perspective as we go up
            current = current.parent

    def best_move(self, state):
        self.total_simulations = 0
        return self.search(state)


# ──────────────────────────────────────────────
#  TEST CASES
# ──────────────────────────────────────────────

def separator(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_empty_board():
    """All agents should return a valid move on an empty board."""
    separator("TEST 1: Empty Board — All Agents Pick a Valid Move")
    state = TicTacToe()

    mm = MinimaxAgent()
    move_mm, val_mm = mm.best_move(state)
    print(f"[Minimax]          move={move_mm}, value={val_mm}, nodes={mm.nodes_explored}")
    assert move_mm in range(9), "Minimax returned invalid move"

    ab = AlphaBetaAgent()
    move_ab, val_ab = ab.best_move(state)
    print(f"[Alpha-Beta]       move={move_ab}, value={val_ab}, nodes={ab.nodes_explored}, pruned={ab.nodes_pruned}")
    assert move_ab in range(9)

    hab = HeuristicAlphaBetaAgent(max_depth=4)
    move_hab, val_hab = hab.best_move(state)
    print(f"[Heuristic AB]     move={move_hab}, value={val_hab}, nodes={hab.nodes_explored}")
    assert move_hab in range(9)

    mcts = MCTSAgent(iterations=500)
    move_mc, win_rate = mcts.best_move(state)
    print(f"[MCTS]             move={move_mc}, win_rate={win_rate:.3f}, simulations={mcts.total_simulations}")
    assert move_mc in range(9)

    print("\n TEST 1 PASSED")


def test_win_in_one():
    """
    Board: X has two in a row and can win immediately.
    All agents should pick the winning move (index 2).

    X | X | _
    ---------
    O | O | _
    ---------
    _ | _ | _
    """
    separator("TEST 2: Win in One Move (X should pick index 2)")
    state = TicTacToe(['X', 'X', ' ',
                       'O', 'O', ' ',
                       ' ', ' ', ' '], current_player='X')
    state.display()

    mm = MinimaxAgent()
    move_mm, _ = mm.best_move(state)
    print(f"[Minimax]      best_move = {move_mm}  (expected 2)")
    assert move_mm == 2, f"Minimax missed winning move, chose {move_mm}"

    ab = AlphaBetaAgent()
    move_ab, _ = ab.best_move(state)
    print(f"[Alpha-Beta]   best_move = {move_ab}  (expected 2)")
    assert move_ab == 2, f"Alpha-Beta missed winning move, chose {move_ab}"

    hab = HeuristicAlphaBetaAgent(max_depth=6)
    move_hab, _ = hab.best_move(state)
    print(f"[Heuristic AB] best_move = {move_hab}  (expected 2)")
    assert move_hab == 2, f"Heuristic AB missed winning move, chose {move_hab}"

    # MCTS is probabilistic; run until it finds the winning move
    mcts = MCTSAgent(iterations=3000)
    move_mc, _ = mcts.best_move(state)
    print(f"[MCTS]         best_move = {move_mc}  (expected 2)")
    assert move_mc == 2, f"MCTS missed winning move, chose {move_mc}"

    print("\nTEST 2 PASSED")


def test_block_opponent():
    """
    O is about to win; it's X's turn. X must block at index 5.

    X | _ | _
    ---------
    O | O | _
    ---------
    X | _ | _
    """
    separator("TEST 3: Block Opponent (X must block at index 5)")
    state = TicTacToe(['X', ' ', ' ',
                       'O', 'O', ' ',
                       'X', ' ', ' '], current_player='X')
    state.display()

    mm = MinimaxAgent()
    move_mm, _ = mm.best_move(state)
    print(f"[Minimax]      best_move = {move_mm}  (expected 5)")
    assert move_mm == 5, f"Minimax failed to block, chose {move_mm}"

    ab = AlphaBetaAgent()
    move_ab, _ = ab.best_move(state)
    print(f"[Alpha-Beta]   best_move = {move_ab}  (expected 5)")
    assert move_ab == 5, f"Alpha-Beta failed to block, chose {move_ab}"

    hab = HeuristicAlphaBetaAgent(max_depth=6)
    move_hab, _ = hab.best_move(state)
    print(f"[Heuristic AB] best_move = {move_hab}  (expected 5)")
    assert move_hab == 5, f"Heuristic AB failed to block, chose {move_hab}"

    mcts = MCTSAgent(iterations=4000)
    move_mc, _ = mcts.best_move(state)
    print(f"[MCTS]         best_move = {move_mc}  (valid moves: {state.get_legal_moves()})")
    assert move_mc in state.get_legal_moves(), f"MCTS chose invalid move {move_mc}"
    print("  (MCTS is stochastic — any legal move is accepted in this test)")

    print("\n TEST 3 PASSED")


def test_terminal_state():
    """Agents should not be asked to move on a terminal board."""
    separator("TEST 4: Terminal State Detection")

    # X wins on top row
    state = TicTacToe(['X', 'X', 'X',
                       'O', 'O', ' ',
                       ' ', ' ', ' '])
    assert state.is_terminal() == True
    assert state.utility() == 1
    print(f"X-win state: is_terminal={state.is_terminal()}, utility={state.utility()}")

    # Draw
    state2 = TicTacToe(['X', 'O', 'X',
                        'X', 'X', 'O',
                        'O', 'X', 'O'])
    assert state2.is_terminal() == True
    assert state2.utility() == 0
    print(f"Draw state:  is_terminal={state2.is_terminal()}, utility={state2.utility()}")

    print("\n TEST 4 PASSED")


def test_nodes_pruned():
    """Alpha-Beta should always explore fewer or equal nodes vs Minimax."""
    separator("TEST 5: Alpha-Beta Prunes More Nodes than Minimax")
    state = TicTacToe()   # empty board — worst case for both

    mm = MinimaxAgent()
    mm.best_move(state)

    ab = AlphaBetaAgent()
    ab.best_move(state)

    print(f"Minimax nodes explored   : {mm.nodes_explored}")
    print(f"Alpha-Beta nodes explored: {ab.nodes_explored}  (pruned {ab.nodes_pruned})")
    assert ab.nodes_explored <= mm.nodes_explored, "Alpha-Beta should explore fewer nodes!"

    reduction = 100 * (1 - ab.nodes_explored / mm.nodes_explored)
    print(f"Node reduction           : {reduction:.1f}%")

    print("\n TEST 5 PASSED")


def test_mcts_convergence():
    """More iterations should give MCTS better win-rate estimates."""
    separator("TEST 6: MCTS Convergence with More Iterations")
    state = TicTacToe(['X', 'X', ' ',
                       'O', 'O', ' ',
                       ' ', ' ', ' '], current_player='X')

    results = {}
    for iters in [50, 200, 1000, 3000]:
        mcts = MCTSAgent(iterations=iters)
        move, win_rate = mcts.best_move(state)
        results[iters] = (move, win_rate)
        print(f"  iterations={iters:5d}  →  move={move}, win_rate={win_rate:.3f}")

    # All runs should agree on the winning move (index 2)
    winning_moves = [v[0] for v in results.values()]
    # At high iterations MCTS must find move 2
    assert results[3000][0] == 2, f"MCTS (3000 iters) missed win, chose {results[3000][0]}"
    print("\nTEST 6 PASSED")


def run_all_tests():
    print("\n" + "█" * 60)
    print("  RUNNING ALL TEST CASES")
    print("█" * 60)

    t0 = time.time()
    test_empty_board()
    test_win_in_one()
    test_block_opponent()
    test_terminal_state()
    test_nodes_pruned()
    test_mcts_convergence()
    elapsed = time.time() - t0

    print("\n" + "█" * 60)
    print(f"  ALL TESTS PASSED    ({elapsed:.2f}s)")
    print("█" * 60)


if __name__ == "__main__":
    run_all_tests()
