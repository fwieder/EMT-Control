Target = {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 0, 'FA_b3': 0}
#Control strategies using percolation
cs = [{'TGFB': 1, ('FA_b1', 'FA_b2'): 0},
 {'TGFBR': 1, ('FA_b1', 'FA_b2'): 0},
 {'ROS': 1, ('FA_b1', 'FA_b2'): 0},
 {'PAK': 0, ('ROS', 'ROS'): 1},
 {'PAK': 0, 'ROS': 1},
 {('FA_b1', 'FA_b2'): 0, ('ROS', 'ROS'): 1},
 {('FA_b1', 'FA_b2'): 0, ('TGFB', 'TGFB'): 1},
 {'FAK_SRC_b1': 0, ('TGFB', 'TGFB'): 1},
 {'FAK_SRC_b1': 0, 'TGFBR': 1},
 {'FAK_SRC_b1': 0, 'TGFB': 1}]
