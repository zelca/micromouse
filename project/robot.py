from policy import *


class Robot(object):
    def __init__(self, maze_dim, init, finish):
        """
        Sets up attributes that a robot will use to learn and navigate the
        maze. Some initial attributes are provided based on common information,
        including the size of the maze the robot is placed in.
        """

        self.init = init
        self.goal = finish

        self.solution = []
        self.maze = Maze(maze_dim)
        self.policy = [[None for _ in range(maze_dim)] for _ in range(maze_dim)]

        # start exploring
        self.mode = 'exploring'
        self.heading = 'up'
        self.location = [self.init[0], self.init[1]]

    def start_testing(self):
        """
        Resets to initial position for testing run.
        """

        self.mode = 'testing'
        self.heading = 'up'
        self.location = [self.init[0], self.init[1]]

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

        if self.mode == 'exploring' and self.location == self.goal:
            self.mode = 'connecting'

        if self.update_maze(sensors):
            solution_policy = compute_policy(self.maze, self.goal)
            self.solution = compute_path(solution_policy, self.init)
            if self.mode == 'connecting':
                unknown = self.first_unknown(self.solution)
                if unknown:
                    self.policy = compute_policy(self.maze, unknown)
                else:
                    self.policy = solution_policy
                    self.start_testing()
                    return 'Reset', 'Reset'
            else:
                self.policy = solution_policy

        rotation, movement = self.next_action()

        self.update_state(sensors, rotation, movement)

        return rotations[rotation], movement

    def first_unknown(self, solution):
        for cell in reversed(solution):
            if not self.maze.is_known(cell):
                return cell

        return None

    def next_action(self):
        """
        Chooses next rotation and movement, based on optimal policy, current
        heading and location of the robot.
        """

        x, y = self.location
        heading, movement, _ = self.policy[x][y]

        if self.mode == "exploring":
            movement = 1

        if self.heading == heading_reverse[heading]:
            movement *= -1
            heading = self.heading

        rotation = heading_rotation[self.heading].index(heading)

        return rotation, movement

    def update_state(self, sensors, rotation, movement):
        """
        Updates robot heading and location, based on rotation, movement and
        current sensors values. Localization is skipped if no pending action.
        """

        # update heading
        self.heading = heading_rotation[self.heading][rotation]

        # check for wall
        movement = min(sensors[rotation], movement)

        # update position
        move = heading_move[self.heading]
        self.location[0] += movement * move[0]
        self.location[1] += movement * move[1]

    def update_maze(self, sensors):
        """
        Updates information about known walls.
        Returns true if maze data was updated.
        """
        updated = False
        for s in range(len(sensors)):
            heading = heading_rotation[self.heading][s]
            x, y = self.location
            move = heading_move[heading]
            for i in range(sensors[s]):
                updated |= self.maze.set_wall([x, y], heading, False)
                x += move[0]
                y += move[1]
            updated |= self.maze.set_wall([x, y], heading, True)

        return updated


class Maze(object):
    """
    Internal robot's representation of the maze.
    Holds information about borders and spotted walls.
    """

    def __init__(self, dim):
        self.dim = dim
        self.walls = {}
        self.walls_dim = 2 * (dim - 1)

    def set_wall(self, cell, heading, is_wall):
        updated = False
        move = heading_move[heading]
        x_ = 2 * cell[0] + move[0]
        y_ = 2 * cell[1] + move[1]
        if not (x_, y_) in self.walls:
            self.walls[x_, y_] = is_wall
            updated = True

        return updated

    def is_known(self, cell):
        for heading in heading_move:
            move = heading_move[heading]
            x_ = 2 * cell[0] + move[0]
            y_ = 2 * cell[1] + move[1]
            if self.in_bound(x_, y_) and not (x_, y_) in self.walls:
                return False

        return True

    def is_permissible(self, cell, heading):
        move = heading_move[heading]
        x_ = 2 * cell[0] + move[0]
        y_ = 2 * cell[1] + move[1]
        return self.in_bound(x_, y_) and not self.walls.get((x_, y_), None)

    def in_bound(self, x, y):
        return 0 <= x <= self.walls_dim and 0 <= y <= self.walls_dim
