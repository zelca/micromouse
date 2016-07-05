import random
from robot import Robot


class RobotML(Robot):
    """
    The implementation of the Robot class based on Reinforcement learning.
    """

    moves = [1, 2, 3]

    actions = []
    for r in range(len(Robot.rotations)):
        for m in moves:
            actions.append((r, m))

    states = []
    for i in range(4):
        for j in range(4):
            for k in range(4):
                states.append((i, j, k))

    def __init__(self, maze_dim):
        super(RobotML, self).__init__(maze_dim)
        self.state = None
        self.action = None
        self.reward = None
        self.q = self.init_q()

    def next_action(self, sensors):
        # get new state
        new_state = self.get_state(sensors)

        # update Q
        if self.state:
            self.update_q(self.state, self.action, self.reward, new_state)

        # update state
        self.state = new_state

        # select action according to the policy
        self.action, _ = self.get_action(self.state)

        # execute action and get reward
        self.reward = self.act(self.action, sensors)

        return self.action

    def init_q(self):
        q = {}
        init_q = .1
        for state in self.states:
            init_actions = {}
            for action in self.actions:
                init_actions[action] = init_q
            q[state] = init_actions
        return q

    def update_q(self, state, action, reward, new_state):
        learning_rate = .3
        discount_factor = .5
        q = self.q[state][action]
        _, max_q = self.get_action(new_state)
        new_q = q + learning_rate * (reward + discount_factor * max_q - q)
        # print "{} old q {} new q {}".format(state, q, new_q)
        self.q[state][action] = new_q

    def get_state(self, sensors):
        normalized = map(normalize, sensors)
        return normalized[0], normalized[1], normalized[2]

    def get_action(self, state):
        max_q = None
        max_action = None
        for action, q in self.q[state].iteritems():
            if q > max_q:
                max_q = q
                max_action = action
        # print "action - {} ({})".format(max_action, max_q)
        return max_action, max_q

    def act(self, action, sensors):
        goal_reward = 100
        move_reward = 1
        wall_reward = -6

        total_reward = 0

        moved = self.update_state(action)

        # check for wall
        if moved < action[1]:
            total_reward += wall_reward

        # reward for correct move
        if not self.visited[self.location[0]][self.location[1]]:
            total_reward += moved * move_reward
        else:
            total_reward += -move_reward

        # reward for goal
        if self.location == self.goal:
            total_reward += goal_reward

        return total_reward


def normalize(sensor):
    return sensor if sensor <= 3 else 3
