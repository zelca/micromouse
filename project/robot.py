import random


class Robot(object):
    rotations = [-90, 0, 90]

    dir_move = {'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}

    dir_reverse = {'up': 'down', 'right': 'left', 'down': 'up', 'left': 'right'}

    dir_rotation = {'up': ['left', 'up', 'right'], 'right': ['up', 'right', 'down'],
                    'down': ['right', 'down', 'left'], 'left': ['down', 'left', 'up']}

    def __init__(self, maze_dim):
        """
        Sets up attributes that a robot will use to learn and navigate the
        maze. Some initial attributes are provided based on common information,
        including the size of the maze the robot is placed in.
        """

        self.heading = 'up'
        self.location = [0, 0]

        self.action = None
        self.sensors = None

        self.maze_dim = maze_dim
        self.goal = [maze_dim / 2 - 1, maze_dim / 2]
        self.walls = [[{} for _ in range(maze_dim)] for _ in range(maze_dim)]
        self.policy = [[None for _ in range(maze_dim)] for _ in range(maze_dim)]

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

        self.update_walls()

        self.update_policy()

        rotation, movement = self.next_action()

        self.action = rotation, movement

        return self.rotations[rotation], movement

    def update_state(self):
        """
        Updates robot heading and location, based on rotation, movement and
        current sensors values. Localization is skipped if no pending action.
        """

        if not self.action:
            return

        rotation, movement = self.action

        # update heading
        self.heading = self.dir_rotation[self.heading][rotation]

        # check for wall
        sensor = self.sensors[rotation]
        if sensor < movement:
            movement = sensor

        # update position
        move = self.dir_move[self.heading]
        self.location[0] += movement * move[0]
        self.location[1] += movement * move[1]

        return movement

    def update_walls(self):
        """
        Updates information about known walls.
        """

        for s in range(len(self.sensors)):
            heading = self.dir_rotation[self.heading][s]
            x, y = self.location
            move = self.dir_move[heading]
            for i in range(self.sensors[s]):
                self.walls[x][y][heading] = False
                x += move[0]
                y += move[1]
            self.walls[x][y][heading] = True

    def update_policy(self):
        self.policy = [[None for _ in range(self.maze_dim)] for _ in range(self.maze_dim)]

        value = [[999 for _ in range(self.maze_dim)] for _ in range(self.maze_dim)]
        value[self.goal[0]][self.goal[1]] = 0

        open = [[self.goal[0], self.goal[1]]]
        while len(open) > 0:
            next = open.pop()
            x = next[0]
            y = next[1]
            step = value[x][y]
            for dir, move in self.dir_move.iteritems():
                x2 = x + move[0]
                y2 = y + move[1]
                step2 = step + 1
                if self.is_valid_move(dir, x, y, x2, y2) and step2 < value[x2][y2]:
                    open.append([x2, y2])
                    value[x2][y2] = step2
                    self.policy[x2][y2] = self.dir_reverse[dir]

    def is_valid_move(self, dir, x, y, x2, y2):
        return 0 <= x2 < self.maze_dim and 0 <= y2 < self.maze_dim

    def next_action(self):
        rotation = random.choice([0, 1, 2])
        movement = 1  # random.choice(range(0, 3))

        return rotation, movement
