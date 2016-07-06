rotations = [-90, 0, 90]

dir_move = {'up': [0, 1],
            'right': [1, 0],
            'down': [0, -1],
            'left': [-1, 0]}

dir_reverse = {'up': 'down',
               'right': 'left',
               'down': 'up',
               'left': 'right'}

dir_rotation = {'up': ['left', 'up', 'right'],
                'right': ['up', 'right', 'down'],
                'down': ['right', 'down', 'left'],
                'left': ['down', 'left', 'up']}


class Robot(object):
    def __init__(self, maze_dim):
        """
        Sets up attributes that a robot will use to learn and navigate the
        maze. Some initial attributes are provided based on common information,
        including the size of the maze the robot is placed in.
        """

        self.start = [0, 0]
        self.goal = [maze_dim / 2 - 1, maze_dim / 2]

        self.maze = Maze(maze_dim, [0, 0])
        self.policy = [[None for _ in range(maze_dim)] for _ in range(maze_dim)]

        self.heading = 'up'
        self.location = [self.start[0], self.start[1]]
        self.sensors = None
        self.rotation = None
        self.movement = None

    def reset(self):
        """
        Resets the robot to the initial state.
        """

        self.heading = 'up'
        self.location = [self.start[0], self.start[1]]
        self.sensors = None
        self.rotation = None
        self.movement = None

    def next_move(self, sensors):
        """
        Determines the next move the robot should make, based on the input
        from the sensors after its previous move. Sensor inputs are a list
        of three distances from the robot's left, front, and right-facing
        sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returning the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        """

        self.update_state()

        self.sensors = sensors

        self.update_maze()

        self.policy = self.calc_policy(self.goal)

        self.rotation, self.movement = self.next_action()

        return rotations[self.rotation], self.movement

    def next_action(self):
        """
        Chooses next rotation and movement, based on optimal policy, current
        heading and location of the robot.
        """

        x, y = self.location
        heading = self.policy[x][y]

        if not heading:
            return 0, 0

        if self.heading == dir_reverse[heading]:
            heading = self.heading
            movement = -1
        else:
            movement = 1

        rotation = dir_rotation[self.heading].index(heading)

        return rotation, movement

    def update_state(self):
        """
        Updates robot heading and location, based on rotation, movement and
        current sensors values. Localization is skipped if no pending action.
        """

        if not self.sensors:
            return

        # update heading
        self.heading = dir_rotation[self.heading][self.rotation]

        # check for wall
        movement = min(self.sensors[self.rotation], self.movement)

        # update position
        move = dir_move[self.heading]
        self.location[0] += movement * move[0]
        self.location[1] += movement * move[1]

    def update_maze(self):
        """
        Updates information about known walls.
        """

        for s in range(len(self.sensors)):
            heading = dir_rotation[self.heading][s]
            x, y = self.location
            move = dir_move[heading]
            for i in range(self.sensors[s]):
                self.maze.set_wall(x, y, heading, False)
                x += move[0]
                y += move[1]
            self.maze.set_wall(x, y, heading, True)

    def calc_policy(self, goal):
        """
        Build optimal policy to reach the goal, based on known walls.
        """

        value = [[999 for _ in range(self.maze.dim)] for _ in range(self.maze.dim)]
        value[goal[0]][goal[1]] = 0

        policy = [[None for _ in range(self.maze.dim)] for _ in range(self.maze.dim)]

        open = [(goal[0], goal[1])]
        while len(open) > 0:
            next = open.pop()
            x = next[0]
            y = next[1]
            step = value[x][y]
            for dir, move in dir_move.iteritems():
                if not self.maze.has_wall(x, y, dir):
                    x2 = x + move[0]
                    y2 = y + move[1]
                    step2 = step + 1
                    if step2 < value[x2][y2]:
                        open.append((x2, y2))
                        value[x2][y2] = step2
                        policy[x2][y2] = dir_reverse[dir]

        return policy


class Maze(object):
    """
    Internal robot's representation of the maze.
    Holds information about borders and spotted walls.
    """

    def __init__(self, dim, start):
        self.dim = dim
        self.walls = {}

    def set_wall(self, x, y, dir, is_wall):
        move = dir_move[dir]
        x_ = 2 * x + move[0]
        y_ = 2 * y + move[1]
        self.walls[x_, y_] = is_wall

    def has_wall(self, x, y, dir):
        move = dir_move[dir]
        x_ = 2 * x + move[0]
        y_ = 2 * y + move[1]
        return self.is_border(x_, y_) or self.walls.get((x_, y_), None)

    def is_border(self, x, y):
        return x < 0 or x > 2 * (self.dim - 1) or y < 0 or y > 2 * (self.dim - 1)
