import random


class Robot(object):
    rotations = [-90, 0, 90]

    dir_move = {'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}

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

        self.goal = [maze_dim / 2 - 1, maze_dim / 2]
        self.maze_dim = maze_dim
        self.info = [[' ' for _ in range(maze_dim)] for _ in range(maze_dim)]
        self.visited = [[None for _ in range(maze_dim)] for _ in range(maze_dim)]

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

        self.localize()

        self.sensors = sensors

        rotation, movement = self.next_action()

        self.action = rotation, movement

        return self.rotations[rotation], movement

    def localize(self):
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
        x, y = self.location
        x += movement * move[0]
        y += movement * move[1]
        self.location = [x, y]
        self.visited[x][y] = True

        return movement

    def next_action(self):
        rotation = random.choice([0, 1, 2])
        movement = 1  # random.choice(range(0, 3))

        return rotation, movement
