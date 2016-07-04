import random
from robot import Robot


class RobotRandom(Robot):
    """
    The dummy implementation of the Robot class that takes random moves.
    """

    def __init__(self, maze_dim):
        super(RobotRandom, self).__init__(maze_dim)

    def next_move(self, sensors):
        self.sensors = sensors

        rotation = random.choice([-90, 0, 90])
        movement = random.choice(range(-3, 3))

        return rotation, movement
