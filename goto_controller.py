from ursina import *
import numpy as np

from car import Car


def rotation_by_angle(vector_to_rotate: Vec3, angle: float) -> Vec3:
    """
    Rotate a vector by a given angle around the y-axis

    Args:
        vector_to_rotate (Vec3): Vector to rotate
        angle (float): Angle to rotate around the y-axis

    Returns:
        Vec3: Rotated vector
    """
    # print(vector_to_rotate)
    # print(angle)
    # print(Vec3(vector_to_rotate[0] * cos(angle) - vector_to_rotate[2] * sin(angle),
    #            vector_to_rotate[1],
    #            vector_to_rotate[0] * sin(angle) + vector_to_rotate[2] * cos(angle)))
    return Vec3(vector_to_rotate[0] * cos(angle) - vector_to_rotate[2] * sin(angle),
                vector_to_rotate[1],
                vector_to_rotate[0] * sin(angle) + vector_to_rotate[2] * cos(angle))


def ursina_dot_product(vector1: Vec3, vector2: Vec3) -> float:
    """
    Calculate the dot product between two vectors

    Args:
        vector1 (Vec3): First vector
        vector2 (Vec3): Second vector

    Returns:
        float: Dot product between the two vectors
    """
    return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]


def ursina_vector_norm(vector: Vec3) -> float:
    """
    Calculate the norm of a vector

    Args:
        vector (Vec3): Vector

    Returns:
        float: Norm of the vector
    """
    return sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


def ursina_cosine_similarity(vector1: Vec3, vector2: Vec3) -> float:
    """
    Calculate the cosine similarity between two vectors

    Args:
        vector1 (Vec3): First vector
        vector2 (Vec3): Second vector

    Returns:
        float: Cosine similarity between the two vectors
    """
    return ursina_dot_product(vector1, vector2) / (ursina_vector_norm(vector1) * ursina_vector_norm(vector2))


def go_to_waypoint(player: Car, point_of_interest: Entity, held_keys: dict, nr_rays=15, check_collision=False):
    arrived = False

    direction_to_point_of_interest = point_of_interest.position - player.position

    angles = np.linspace(-pi, pi, nr_rays)[:-1]  # The last element will be the same as the first (back of the car)
    # TO TEST: Do we rotate around the y-axis through z or x? We may need to invert the angles based on that
    rays = []
    ray_directions = []
    for angle in angles:

        # player_forward = player.forward
        # player_forward[1] = 0
        ray_direction = rotation_by_angle(player.forward, angle)
        # ray_direction = ray_direction / ursina_vector_norm(ray_direction)

        ray_directions.append(ray_direction)  # max(5*ursina_cosine_similarity(ray_direction, player_forward), 1)
        rays.append(raycast(player.position, ray_direction,
                            distance=max(5 * ursina_cosine_similarity(ray_direction, player.forward), 1),
                            ignore=[player, point_of_interest], debug=False))  # we need to test the distance
        if angle == 0:
            new_ray_direction = Vec3(ray_direction[0], ray_direction[1], ray_direction[2])
            new_ray_direction[1] += 1
            ray_directions.append(new_ray_direction)
            rays.append(raycast(player.position, new_ray_direction,
                                distance=max(5 * ursina_cosine_similarity(new_ray_direction, player.forward), 1),
                                ignore=[player, point_of_interest], debug=False))  # we need to test the distance
            # ray_directions

    cosine_similarities = [max(0., ursina_cosine_similarity(direction_to_point_of_interest, ray_direction)) for
                           ray_direction in
                           ray_directions]

    # accumulation_of_directions = [cosine_similarity * ray_direction for cosine_similarity, ray_direction in
    #                    zip(cosine_similarities, ray_directions)]

    # print(cosine_similarities)
    if check_collision:
        for i, ray in enumerate(rays):
            if ray.hit:
                # print(angles[i], "hit", ray.entity)
                cosine_similarities[i] = 0
    # print(cosine_similarities)
    smart_direction = Vec3((0, 0, 0))
    for cosine_similarity, ray_direction in zip(cosine_similarities, ray_directions):
        smart_direction += cosine_similarity * ray_direction
    smart_direction /= np.linalg.norm(smart_direction)

    angle_sign = player.forward[0] * smart_direction[2] - player.forward[2] * smart_direction[0]

    if np.sum(cosine_similarities) == 0:
        held_keys['s'] = 1
    elif ursina_vector_norm(direction_to_point_of_interest) > 5:
        if angle_sign >= 0.3:
            # print("Turning left")
            held_keys['a'] = 1
        elif angle_sign < -0.3:
            # print("Turning right")
            held_keys['d'] = 1
        if ursina_cosine_similarity(player.forward, smart_direction) > 0.3:
            # print("Going forward")
            held_keys['w'] = 1
        # elif ursina_cosine_similarity(player.forward, smart_direction) < 0 and abs(angle_sign) < 0.2:
        #     print("This is the spammed action")
        #     held_keys['s'] = 1
        #     held_keys['a'] = 1
        elif ursina_cosine_similarity(player.forward, smart_direction) < 0.3:
            # print("Going back")
            held_keys['s'] = 1

    elif ursina_vector_norm(direction_to_point_of_interest) <= 5 and abs(player.speed > 1):
        if ursina_cosine_similarity(player.forward, smart_direction) > 0.2:
            # print("Braking")
            held_keys['s'] = 1
        elif ursina_cosine_similarity(player.forward, smart_direction) < 0.2:
            # print("Braking reverse")
            held_keys['w'] = 1
        # print("Arrived at waypoint")
        arrived = True

    return held_keys, arrived
