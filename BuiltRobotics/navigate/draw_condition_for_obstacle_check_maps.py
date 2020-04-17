


def _draw_condition(obstacle_check, obstacle_snapshot, start_wp, goal_wp):
    obstacle_map = obstacle_map_module.ObstacleMap()

    import matplotlib.pyplot as plt
    no_plan_map = obstacle_snapshot.guidelines.cells.astype(int)
    x, y, yaw_region = obstacle_check._car_shapes_to_cell_func(start_wp)
    obstacle_map_position = np.array(obstacle_map.to_obstacle_map_position(start_wp)).astype(int)

    def add_car_shape_to_map(position, val):
        car_shape_in_map = np.zeros(obstacle_snapshot.guidelines.cells.shape)
        car_mask = obstacle_check._get_mask_to_check(yaw_region)
        car_shape_in_map[position[0] - int(car_mask.shape[0] / 2):position[0] +
                         int(car_mask.shape[0] / 2), position[1] - int(car_mask.shape[1] / 2):position[1] +
                         int(car_mask.shape[1] / 2)] = car_mask.astype(int) * val
        return car_shape_in_map

    start_car_shape = add_car_shape_to_map(obstacle_map_position, -10)
    goal_car_shape = add_car_shape_to_map(np.array(obstacle_map.to_obstacle_map_position(goal_wp)).astype(int), -20)

    plt.imshow(start_car_shape + no_plan_map + goal_car_shape)
    plt.show()





def _plot_path(path):
    import matplotlib.pyplot as plt
    plot_points = []
    l = 0.25
    for wp in path:
        plot_points.append([wp[0], wp[1], math.cos(wp[2])*l, math.sin(wp[2])*l])
        plt.arrow(*plot_points[-1])
    plot_points = np.array(plot_points)
    plt.plot(plot_points[:, 0], plot_points[:, 1], 'rx')
    plt.axis('equal')   
    plt.show()