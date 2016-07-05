import random
from robot import Robot


class RobotRandom(Robot):
    """
    The dummy implementation of the Robot class that takes random moves.
    """

    def __init__(self, maze_dim):
        super(RobotRandom, self).__init__(maze_dim)

    def next_action(self, sensors):
        rotation = random.choice([0, 1, 2])
        movement = random.choice(range(0, 3))
        self.update_state((rotation, movement))
        return rotation, movement
