# Line = 10
# All = [False, [[], ["?"] * Line] * Line]
# Count = [[], [[], [0] * Line] * Line]
# judge_edge = [0, 0]

# def cal_count(Count, All):
#     Line = len(All) - 1
#     for i in range(1, Line + 1):
#         for j in range(1, Line + 1):
#             all_edge = {(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
#                         (i + 1, j - 1), (i + 1, j), (i + 1, j + 1), (i, j - 1),
#                         (i, j + 1)}

#             positions = []
#             for r, c in all_edge:
#                 if 1 <= r <= Line:
#                     if r < len(All) and 1 <= c < len(All[r]):
#                         positions.append((r, c))

#             Count[i][j] = sum(1 for pos in positions if is_boom(pos, All))

#     return Count

# def is_boom(pos, All):
#     if All[pos[0]][pos[1]] == "*":
#         return True

# import main

# main.print_all(Line, All)
import os

print(os.environ.get("SHELL"))
