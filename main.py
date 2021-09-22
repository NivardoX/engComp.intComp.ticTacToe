import functools
import timeit
from copy import deepcopy

import math
from functools import wraps

inf = float(math.inf)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        start = timeit.default_timer()
        result = f(*args, **kw)
        end = timeit.default_timer()
        print(f'{f.__name__} took: %2.4f sec' % (end - start))
        return result

    return wrap


class Board(list):
    def format_board(self):
        def get_symbol(f):
            value = '__'
            if f == 1:
                value = 'X'
            elif f == 0:
                value = 'O'
            return value

        def format_line(line):
            return "\t".join([get_symbol(i) for i in line])

        return "\n".join(format_line(line) for line in self)

    @property
    def open_fields(self):
        fields = []
        for line in range(len(self)):
            for column in range(len(self[line])):
                if self[line][column] is None:
                    fields.append((line, column))
        return fields

    @property
    def qnt_zeros(self):
        return sum(x.count(0) for x in self)

    @property
    def qnt_ones(self):
        return sum(x.count(1) for x in self)

    @property
    def possible_movements(self):
        boards = []
        value_of_move =  0 if self.qnt_ones > self.qnt_zeros else 1

        for x, y in self.open_fields:
            possible_board = deepcopy(self)
            possible_board[x][y] = value_of_move
            boards.append(possible_board)

        return boards

    @property
    def score(self):
        secondary_diagonal_1 = 0
        secondary_diagonal_0 = 0

        primary_diagonal_1 = 0
        primary_diagonal_0 = 0

        for i, line in enumerate(self):
            if line.count(1) == 3:
                return 10
            if line.count(0) == 3:
                return -10
            line_1 = 0
            line_0 = 0

            for column in self:
                if column[i] == 1:
                    line_1 += 1
                elif column[i] == 0:
                    line_0 += 1
            if line_1 == 3:
                return 10
            if line_0 == 3:
                return -10

            # right to left
            if self[i][i] == 1:
                secondary_diagonal_1 += 1
            if self[i][i] == 0:
                secondary_diagonal_0 += 1
            if secondary_diagonal_1 == 3:
                return 10
            if secondary_diagonal_0 == 3:
                return -10

            # left to right
            if self[i][2 - i] == 1:
                primary_diagonal_1 += 1
            if self[i][2 - i] == 0:
                primary_diagonal_0 += 1
            if primary_diagonal_1 == 3:
                return 10
            if primary_diagonal_0 == 3:
                return -10

        return 0

    @property
    def should_finish(self):
        result = self.score
        if result == 10:
            print("Game over! Max Won!!!")
            return True
        if result == -10:
            print("Game over! Min Won!!!")
            return True
        if self.is_finished:
            print("Draw!")
            return True

        return False

    def __hash__(self):
        return hash(self.format_board())
    @property
    def is_finished(self):
        for _ in self:
            for f in _:
                if f is None:
                    return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"""Game\n{self.format_board()}\n"""


class TicTacToe:
    def __init__(self, board_size=3):
        self.board = Board([[None] * board_size for _ in range(board_size)])
        print(self.board)

    @timing
    def move(self, *args, **kwargs):
        return self.minimax(*args, **kwargs)

    @staticmethod
    def read_movement(board):
        while True:
            k = eval(input("Enter your move (1...9): "))
            k -= 1
            x, y = int(k / 3), k % 3
            if 0 <= k <= 8 and board[x][y] is None:
                break

            print("Position not allowed! Choose another one!")

        return x, y

    @functools.lru_cache(maxsize=None)
    def minimax(self, actual_board, player=1, alfa=-inf, beta=inf):
        actual_board = deepcopy(actual_board)
        possible_movements = actual_board.possible_movements
        scores = []

        if player == 1:
            for possible_movement in possible_movements:
                result = possible_movement.score
                if result == 10 or result == -10 or possible_movement.is_finished:
                    scores.append(result)
                else:
                    best_score, best_score_board = self.minimax(possible_movement, 1 - player, alfa, beta)
                    if best_score >= beta:
                        return best_score, best_score_board
                    alfa = max(alfa, best_score)
                    scores.append(best_score)

            best_score = max(scores)
        else:
            for possible_movement in possible_movements:
                result = possible_movement.score
                if result == 10 or result == -10 or possible_movement.is_finished:
                    scores.append(result)
                else:
                    best_score, best_score_board = self.minimax(possible_movement, 1 - player, alfa, beta)
                    if best_score <= alfa:
                        return best_score, best_score_board
                    beta = min(beta, best_score)
                    scores.append(best_score)

            best_score = min(scores)

        best_score_index = scores.index(best_score)
        return best_score, possible_movements[best_score_index]

    def start(self):
        while True:
            _, updated_board = self.move(self.board)
            print(updated_board)

            if updated_board.should_finish:
                return

            x, y = TicTacToe.read_movement(updated_board)
            updated_board[x][y] = 0
            print(updated_board)

            if updated_board.should_finish:
                return

            self.board = updated_board


if __name__ == "__main__":
    TicTacToe().start()
