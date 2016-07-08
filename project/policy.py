max_movement = 3

rotations = [-90, 0, 90]

heading_move = {'up': [0, 1],
                'right': [1, 0],
                'down': [0, -1],
                'left': [-1, 0]}

heading_reverse = {'up': 'down',
                   'right': 'left',
                   'down': 'up',
                   'left': 'right'}

heading_rotation = {'up': ['left', 'up', 'right'],
                    'right': ['up', 'right', 'down'],
                    'down': ['right', 'down', 'left'],
                    'left': ['down', 'left', 'up']}


def compute_policy(maze, goal):
    """
    Computes optimal policy to reach the goal, based on current maze data.
    """

    value = [[999 for _ in range(maze.dim)] for _ in range(maze.dim)]
    value[goal[0]][goal[1]] = 0

    policy = [[None for _ in range(maze.dim)] for _ in range(maze.dim)]

    rest = [(goal[0], goal[1])]
    while len(rest) > 0:
        cell = rest.pop()
        x = cell[0]
        y = cell[1]
        time = value[x][y]
        # check every direction for the cell
        for heading, move in heading_move.iteritems():
            i = 1
            x2 = x
            y2 = y
            # move as much as possible before wall is spotted
            while i <= max_movement and maze.is_permissible((x2, y2), heading):
                x2 += move[0]
                y2 += move[1]
                time2 = time + 1
                if time2 < value[x2][y2]:
                    rest.append((x2, y2))
                    value[x2][y2] = time2
                    policy[x2][y2] = (heading_reverse[heading], i, time2)
                i += 1

    return policy


def compute_path(policy, init):
    """
    Computes optimal path to reach the goal starting at init point.
    """

    path = []

    x, y = init
    while policy[x][y]:
        path.append((x, y))
        heading, movement, _ = policy[x][y]
        move = heading_move[heading]
        x += movement * move[0]
        y += movement * move[1]

    return path


def last_unvisited(maze, path):
    """
    Finds the last unvisited cell from the path.

    Returns None if all cells are visited or path is empty.
    """

    for cell in reversed(path):
        if maze.is_unvisited(cell):
            return cell

    return None


def estimate_score(maze, init, goal, train_score_ratio):
    """
    Estimates score for given maze, inti and goal points.

    Best score is calculated based on assumption that a robots takes
    optimal path to reach the goal in both runs. And equals

        optimal path time + optimal path time / train_score_ratio

    Worst score - a robot visits all cells during exploration and
    uses optimal path on second run. So equals

        optimal path time + number of cells / train_score_ratio
    """

    policy = compute_policy(maze, goal)

    _, _, optimal_time = policy[init[0]][init[1]]

    best_score = optimal_time + float(optimal_time) * train_score_ratio
    worst_score = optimal_time + float(maze.dim ** 2) * train_score_ratio

    return best_score, worst_score
