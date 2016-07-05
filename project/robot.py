class Robot(object):
    rotations = [-90, 0, 90]

    dir_move = {'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}

    dir_rotation = {'up': ['left', 'up', 'right'], 'right': ['up', 'right', 'down'],
                    'down': ['right', 'down', 'left'], 'left': ['down', 'left', 'up']}

    def __init__(self, maze_dim):
        """
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        """

        self.heading = 'up'
        self.sensors = None
        self.location = [0, 0]

        self.goal = [maze_dim / 2 - 1, maze_dim / 2]
        self.maze_dim = maze_dim
        self.info = [[' ' for _ in range(maze_dim)] for _ in range(maze_dim)]
        self.visited = [[None for _ in range(maze_dim)] for _ in range(maze_dim)]

    def next_move(self, sensors):
        """
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

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

        x, y = self.location
        self.visited[x][y] = True
        self.sensors = sensors
        rotation, movement = self.next_action(sensors)
        return self.rotations[rotation], movement

    def next_action(self, sensors):
        raise NotImplementedError()

    def update_state(self, action):
        rotation, movement = action
        sensor = self.sensors[rotation]

        # update heading
        self.heading = self.dir_rotation[self.heading][rotation]

        # check for wall
        if sensor < movement:
            movement = sensor

        # update position
        move = self.dir_move[self.heading]
        self.location[0] += movement * move[0]
        self.location[1] += movement * move[1]

        return movement
