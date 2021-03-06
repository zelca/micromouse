import sys
from maze import Maze
from robot import Robot
from simulator import Simulator
from policy import estimate_score

# global dictionaries for robot movement and sensing
dir_sensors = {'up': ['left', 'up', 'right'], 'right': ['up', 'right', 'down'],
               'down': ['right', 'down', 'left'], 'left': ['down', 'left', 'up']}
dir_move = {'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'up': 'down', 'right': 'left', 'down': 'up', 'left': 'right'}

# test and score parameters
max_time = 1000
train_score_ratio = 1 / 30.

if __name__ == '__main__':
    '''
    This script tests a robot based on the code in robot.py on a maze given
    as an argument when running the script.
    '''

    # create a maze based on input argument on command line.
    testmaze = Maze(str(sys.argv[1]))
    init = [0, 0]
    goal_bounds = [testmaze.dim / 2 - 1, testmaze.dim / 2]

    # initialize a robot; robot receives info about maze dimensions.
    testrobot = Robot(testmaze.dim, init, goal_bounds)

    # create a simulator to display maze and robot movements.
    # set delay to None to disable simulator.
    delay = None
    if len(sys.argv) > 2:
        delay = int(sys.argv[2])
    show_maze = False
    if len(sys.argv) > 3:
        show_maze = bool(sys.argv[3])
    simulator = Simulator(testmaze, testrobot, delay=delay, show_maze=show_maze, show_policy=False)

    # print estimated score
    best_score, worst_score = estimate_score(testmaze, init, goal_bounds, train_score_ratio)
    print "Estimated score is between {:4.3f} and {:4.3f}".format(best_score, worst_score)

    # record robot performance over two runs.
    runtimes = []
    total_time = 0
    for run in range(2):
        print 'Starting run {}.'.format(run)

        # set the robot in the start position. Note that robot position
        # parameters are independent of the robot itself.
        robot_pos = {'location': [init[0], init[1]], 'heading': 'up'}

        run_active = True
        hit_goal = False
        while run_active:
            # check for end of time
            total_time += 1
            if total_time > max_time:
                run_active = False
                print 'Allotted time exceeded.'
                break

            # provide robot with sensor information, get actions
            sensing = [testmaze.dist_to_wall(robot_pos['location'], heading)
                       for heading in dir_sensors[robot_pos['heading']]]
            rotation, movement = testrobot.next_move(sensing)

            # render simulator
            simulator.render()

            # check for a reset
            if (rotation, movement) == ('Reset', 'Reset'):
                if run == 0 and hit_goal:
                    run_active = False
                    runtimes.append(total_time)
                    print 'Ending first run. Starting next run.'
                    break
                elif run == 0 and not hit_goal:
                    print 'Cannot reset - robot has not hit goal yet.'
                    continue
                else:
                    print 'Cannot reset on runs after the first.'
                    continue

            # perform rotation
            if rotation == -90:
                robot_pos['heading'] = dir_sensors[robot_pos['heading']][0]
            elif rotation == 90:
                robot_pos['heading'] = dir_sensors[robot_pos['heading']][2]
            elif rotation == 0:
                pass
            else:
                print 'Invalid rotation value, no rotation performed.'

            # perform movement
            if abs(movement) > 3:
                print 'Movement limited to three squares in a turn.'
            movement = max(min(int(movement), 3), -3)  # fix to range [-3, 3]
            while movement:
                if movement > 0:
                    if testmaze.is_permissible(robot_pos['location'], robot_pos['heading']):
                        robot_pos['location'][0] += dir_move[robot_pos['heading']][0]
                        robot_pos['location'][1] += dir_move[robot_pos['heading']][1]
                        movement -= 1
                    else:
                        print 'Movement stopped by wall.'
                        movement = 0
                else:
                    rev_heading = dir_reverse[robot_pos['heading']]
                    if testmaze.is_permissible(robot_pos['location'], rev_heading):
                        robot_pos['location'][0] += dir_move[rev_heading][0]
                        robot_pos['location'][1] += dir_move[rev_heading][1]
                        movement += 1
                    else:
                        print 'Movement stopped by wall.'
                        movement = 0

            # check for goal entered
            if robot_pos['location'][0] in goal_bounds and robot_pos['location'][1] in goal_bounds:
                hit_goal = True
                if run != 0:
                    runtimes.append(total_time - sum(runtimes))
                    run_active = False
                    print 'Goal found; run {} completed!'.format(run)

    # report score if robot is successful.
    if len(runtimes) == 2:
        print 'Task complete! Score: {:4.3f}'.format(runtimes[1] + train_score_ratio * runtimes[0])
