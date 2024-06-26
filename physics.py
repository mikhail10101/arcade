import math
import pygame

class ForceObject:
    def __init__(self):
        self.forces = []
        self.fx = 0
        self.fy = 0

    def update(self, currtime):
        fx = 0
        fy = 0

        #remove dead forces
        self.forces[:] = [f for f in self.forces if f[5]]

        for force in self.forces:
            target_vel = force[0]
            duration = force[1]
            accel_time = force[2]
            deccel_time = force[3]
            time_created = force[4]

            force_lifetime = currtime - time_created

            if force_lifetime > accel_time + duration + deccel_time:
                force[5] = False
                continue

            curr_vel = [0,0]

            if force_lifetime < accel_time:
                curr_vel[0] = pygame.math.lerp(0, target_vel[0], force_lifetime/accel_time)
                curr_vel[1] = pygame.math.lerp(0, target_vel[1], force_lifetime/accel_time)
            elif force_lifetime < accel_time + duration:
                curr_vel = target_vel
            elif force_lifetime < accel_time + duration + deccel_time:
                curr_vel[0] = pygame.math.lerp(target_vel[0], 0, (force_lifetime - accel_time - duration)/deccel_time)
                curr_vel[1] = pygame.math.lerp(target_vel[1], 0, (force_lifetime - accel_time - duration)/deccel_time)
            else:
                pass
            
            fx += curr_vel[0]
            fy += curr_vel[1]

        self.fx = fx
        self.fy = fy
    
    def add_force(self, target_vel, accel_time, duration, deccel_time, currtime):
        #0 at the end is passed time in milliseconds
        #True shows that the force is still valid
        self.forces.append([target_vel, duration, accel_time, deccel_time, currtime, True])        


class Shape(ForceObject):
    def __init__(self, id):
        super().__init__()
        self.size = 1
        self.pos = [0,0]
        self.angle_pos = 0
        self.points = []
        self.last_hit = -1000
        self.monocolor = 160

        self.id = id
    
    def draw(self, window, offset, time):
        drawpoints = [ [int(pair[0] - offset[0]), int(pair[1] - offset[1])] for pair in self.points]

        #ANTI ALIASING
        # surf = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)
        # draw_points = points_creator((self.size*2, self.size*2),len(self.points),self.size*2,self.angle_pos)
        # if pygame.time.get_ticks() < self.last_hit + 75:
        #     pygame.draw.polygon(surf, (255,0,0), draw_points, 6)
        #     for p in draw_points:
        #         pygame.draw.circle(surf, (255,0,0), p, 2.5)
        # else:
        #     pygame.draw.polygon(surf, (self.monocolor,self.monocolor,self.monocolor), draw_points, 6)
        #     for p in draw_points:
        #         pygame.draw.circle(surf, (self.monocolor,self.monocolor,self.monocolor), p, 2.5)
        # scaled_surf = pygame.transform.smoothscale_by(surf, 0.5)
        # scaled_surf.set_colorkey((0,0,0))

        # window.blit(scaled_surf, (int(self.pos[0] - offset[0] - self.size), int(self.pos[1] - offset[1] - self.size)), special_flags = pygame.BLEND_PREMULTIPLIED)

        if time < self.last_hit + 75:
            pygame.draw.polygon(window, (self.monocolor,0,0), drawpoints, 3)
            for p in drawpoints:
                pygame.draw.circle(window, (self.monocolor,0,0), p, 0.8)
        else:
            pygame.draw.polygon(window, (self.monocolor,self.monocolor,self.monocolor), drawpoints, 3)
            for p in drawpoints:
                pygame.draw.circle(window, (self.monocolor,self.monocolor,self.monocolor), p, 0.8)


def phys_helper(curr_vel, target_vel, accel, deccel):
    if (target_vel[0] != 0):
        if (abs(curr_vel[0] - target_vel[0]) < accel):
            curr_vel[0] = target_vel[0]
        elif (curr_vel[0] < target_vel[0]):
            curr_vel[0] += accel
        else:
            curr_vel[0] -= accel
    else:
        if (abs(curr_vel[0] - target_vel[0]) < deccel):
            curr_vel[0] = target_vel[0]
        elif (curr_vel[0] < target_vel[0]):
            curr_vel[0] += deccel
        else:
            curr_vel[0] -= deccel

    if (target_vel[1] != 0):
        if (abs(curr_vel[1] - target_vel[1]) < accel):
            curr_vel[1] = target_vel[1]
        elif (curr_vel[1] < target_vel[1]):
            curr_vel[1] += accel
        else:
            curr_vel[1] -= accel
    else:
        if (abs(curr_vel[1] - target_vel[1]) < deccel):
            curr_vel[1] = target_vel[1]
        elif (curr_vel[1] < target_vel[1]):
            curr_vel[1] += deccel
        else:
            curr_vel[1] -= deccel

def phys_single_helper(curr_vel, target_vel, accel, deccel):
    if (target_vel != 0):
        if (abs(curr_vel - target_vel) < accel):
            curr_vel = target_vel
        elif (curr_vel < target_vel):
            curr_vel += accel
        else:
            curr_vel -= accel
    else:
        if (abs(curr_vel - target_vel) < deccel):
            curr_vel = target_vel
        elif (curr_vel < target_vel):
            curr_vel += deccel
        else:
            curr_vel -= deccel
    return curr_vel


def dist(pos, pos2):
    return math.sqrt((pos[0] - pos2[0])**2 + (pos[1] - pos2[1])**2) 

def point_in_polygon(point, polygon):
    num_vertices = len(polygon)
    x, y = point[0], point[1]
    inside = False
 
    p1 = polygon[0]
 
    for i in range(1, num_vertices + 1):
        p2 = polygon[i % num_vertices]
 
        if y > min(p1[1], p2[1]):
            if y <= max(p1[1], p2[1]):
                if x <= max(p1[0], p2[0]):
                    x_intersection = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                    if p1[0] == p2[0] or x <= x_intersection:
                        inside = not inside
        p1 = p2
    return inside

def intersect_circle(pointA, pointB, center, radius):
    d = pygame.math.Vector2(pointB[0]-pointA[0], pointB[1]-pointA[1])
    f = pygame.math.Vector2(pointA[0]-center[0], pointA[1]-center[1])

    a = d.dot(d)
    b = 2*f.dot(d)
    c = f.dot(f) - radius*radius

    discriminant = b*b - 4*a*c

    if a == 0:
        return False

    if discriminant < 0:
        return False
    
    discriminant = math.sqrt(discriminant)

    t1 = (-b - discriminant)/(2*a)
    t2 = (-b + discriminant)/(2*a)

    if t1 >= 0 and t1 <= 1:
        return True
    if t2 >= 0 and t2 <= 1:
        return True
    return False

def middle_bounds(size,w):
    if w==1:
        return (0,size)
    if w==0:
        return (0, 0)
    
    amount = int(size*w)
    
    if size%2 == 0:
        if amount%2 == 1:
            amount += 1
        return (max(0,size//2 - amount//2), min(size//2 + amount//2,size))

    if size%2 == 1:
        if amount%2 == 0:
            amount += 1
        return (max(0,size//2 - amount//2), min(size//2 + amount//2 + 1,size))


def signed_angle(angle, target_angle):
    a = target_angle - angle
    return (a + math.pi) % (2*math.pi) - math.pi

def move_angle(angle, target_angle, angle_vel):
    diff = signed_angle(angle, target_angle)
    if abs(diff) < angle_vel:
        return target_angle
    
    if diff < 0:
        return angle - angle_vel
    else:
        return angle + angle_vel

# def calc_collision(m1, p1, v1, m2, p2, v2):
#     if p2 > p1:
#         return calc_collision(m2, p2, v2, m1, p1, v1)[::-1]

#     x = None
#     y = None
#     #assume p1 is less than p2
#     if v1[0] < 0 and v2[0] > 0:
#         x = [0, 0]
#     elif v1[0] < 0 and v2[0] < 0:
#         x = [1, -1]
#     elif v1[0] > 0 and v2[0] > 0:
#         x = [-1, 1]
#     else:
#         x = [-1, -1]

#     if v1[1] < 0 and v2[1] > 0:
#         y = [0, 0]
#     elif v1[1] < 0 and v2[1] < 0:
#         y = [1, -1]
#     elif v1[1] > 0 and v2[1] > 0:
#         y = [-1, 1]
#     else:
#         y = [-1, -1]

#     return (
#         (x[0] * m2 / m1 * v2[0], y[0] * m2 / m1 * v2[1]),
#         (x[1] * m1 / m2 * v1[0], y[1] * m1 / m2 * v1[1])
#     )

def points_modifier(points_array, center, n, size, angle):
    for i in range(n):
        points_array[i] = (center[0] + size * math.cos(angle + 2*i*math.pi/n), center[1] + size * math.sin(angle + 2*i*math.pi/n))

def points_creator(center, n, size, angle):
    res = []
    for i in range(n):
        res.append([center[0] + size * math.cos(angle + 2*i*math.pi/n), center[1] + size * math.sin(angle + 2*i*math.pi/n)])
    return res

