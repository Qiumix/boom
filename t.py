Line = 10
All = [False, [[], ["?"] * Line] * Line]
Count = [[], [[], [0] * Line] * Line]
judge_edge = [0, 0]
for i in range(1, Line + 1):
    for j in range(1, Line + 1):
        judge_edge[0] = 1 if i == 1 else (2 if i == Line else 0)
        judge_edge[1] = 1 if j == 1 else (2 if j == Line else 0)
        all_edge = set((i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j - 1),
                       (i - 1, j - 1), (i + 1, j - 1), (i + 1, j),
                       (i + 1, j + 1))
        up_edge = set((i - 1, j - 1), (i - 1, j), (i - 1, j + 1)(i, j - 1))
        down_edge = set((i + 1, j - 1), (i + 1, j), (i + 1, j + 1))
        left_edge = set((i - 1, j - 1), (i, j - 1), (i + 1, j - 1))
        right_edge = set((i - 1, j - 1), (i, j), (i + 1, j + 1))
        if judge_edge[0] == 1:
            all_edge -= up_edge
        elif judge_edge[0] == 2:
            all_edge -= down_edge
        if judge_edge[1] == 1:
            all_edge -= left_edge
        elif judge_edge[1] == 2:
            all_edge -= right_edge
        Count[i][j] = len([x for x in all_edge if is_boom(x, All)])


def is_boom(pos, All):
    if All[pos[0]][pos[1]] == "*":
        return True
