Target = {'AJ_b1': 1, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 1, 'FA_b3': 0}
#Control strategies using percolation
cs = [{('ECad', 'AJ_b1'): 1, ('FAK_SRC_b1', 'FA_b3'): 0, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('FAK_SRC_b1', 'RAP1'): 0, ('ROS', 'ROS'): 1},
 {('ECM', 'ECM'): 0, ('ECad', 'AJ_b1'): 1, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('PAK', 'FA_b3'): 0, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('FA_b2', 'FA_b3'): 0, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('FA_b1', 'FA_b3'): 0, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('RAP1', 'ITG_AB'): 0, ('ROS', 'ROS'): 1},
 {('ECM', 'ITG_AB'): 0, ('ECad', 'AJ_b1'): 1, ('ROS', 'ROS'): 1},
 {('ECad', 'AJ_b1'): 1, ('ITG_AB', 'FA_b3'): 0, ('ROS', 'ROS'): 1}]
