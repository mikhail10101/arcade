import pygame
import math
import random
from physics import *

class Player:
    def __init__(self):
        #draw
        self.size = 30

        #movement
        self.pos = [300,300]
        self.speed = 4
        self.accel = 0.2
        self.deccel = 0.05
        self.curr_vel = [0,0]

        #shot in milliseconds
        self.last_shot = -1000
        self.shot_interval = 333
        

    def draw(self, window, offset=(0,0)):
        pygame.draw.circle(window, (255,255,255), (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])), self.size)

    def update(self, inputs, bullets, map, offset=(0,0)):
        current_time = pygame.time.get_ticks()

        #MOVEMENT
        target_vel = [0,0]

        if not (inputs["left"] and inputs["right"]):
            if inputs["left"]:
                target_vel[0] = -self.speed
            if inputs["right"]:
                target_vel[0] = self.speed
        if not (inputs["up"] and inputs["down"]):
            if inputs["up"]:
                target_vel[1] = -self.speed
            if inputs["down"]:
                target_vel[1] = self.speed
        
        phys_helper(self.curr_vel, target_vel, self.accel, self.deccel)

        self.move([self.pos[0] + self.curr_vel[0], self.pos[1] + self.curr_vel[1]], map)

        #SHOOT
        if inputs["click"]:
            if current_time > self.last_shot + self.shot_interval:
                mx, my = inputs["click_pos"]

                mx += offset[0]
                my += offset[1]

                dx = mx - self.pos[0]
                dy = my - self.pos[1]

                rads = math.atan2(dy,dx)

                bullets.append(Bullet(self.pos, 10, rads, True, 7))

                self.last_shot = current_time

    def move(self, new_pos, map):
        i = int(self.pos[0] // map.tile_size)
        j = int(self.pos[1] // map.tile_size)
        newI = int(new_pos[0] // map.tile_size)
        newJ = int(new_pos[1] // map.tile_size)

        if 0 <= newI < len(map.map_values) and 0 <= newJ < len(map.map_values[0]):
            if (map.map_values[newI][newJ] == 1):
                if abs(i - newI) == 1 and abs(j - newJ) == 1:
                    if map.map_values[i][newJ] == 0:
                        self.pos[1] = new_pos[1]
                    elif map.map_values[newI][j] == 0:
                        self.pos[0] = new_pos[0]
                    else:
                        pass
                elif abs(j - newJ) == 1:
                    self.pos[0] = new_pos[0]
                else:
                    self.pos[1] = new_pos[1]
            else:
                self.pos[0] = new_pos[0]
                self.pos[1] = new_pos[1]
        else:
            pass



class Bullet:
    def __init__(self, pos, speed, angle, target_shapes, radius=10):
        self.pos = list(pos)
        self.speed = speed
        self.angle = float(angle)
        self.radius = radius

        self.active = True

        self.target_shapes = target_shapes
        
        self.active = True

    def update(self):
        self.pos[0] += self.speed * math.cos(self.angle)
        self.pos[1] += self.speed * math.sin(self.angle)

    def draw(self, window, offset=(0,0)):
        pygame.draw.circle(window, (255,255,255), (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])), self.radius)

    #bullet collisions with an ordered set of points (any polygon)
    def collision(self, points):
        n = len(points)
        p1 = 0
        for i in range(1, n+1):
            p2 = i%n
            if intersect_circle(points[p1],points[p2],self.pos,self.radius):
                return True
            p1 = p2
        return point_in_polygon(self.pos, points)
    




class Triangle(ForceObject):
    def __init__(self, pos, speed, size, health=3):
        super().__init__()

        self.pos = list(pos)
        self.speed = speed
        self.size = size

        self.health = health

        self.angle_accel = 0.2
        self.curr_angle = 0

        top = (self.pos[0] + self.size * math.cos(self.curr_angle), self.pos[1] + self.size * math.sin(self.curr_angle))
        b1 = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi*2/3), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi*2/3))
        b2 = (self.pos[0] + self.size * math.cos(self.curr_angle - math.pi*2/3), self.pos[1] + self.size * math.sin(self.curr_angle - math.pi*2/3))

        self.points = [top, b1, b2]

        self.active = True

    def update(self, players):
        super().update()

        closest = players[0]
        for i in range(1,len(players)):
            if dist(players[i].pos, self.pos) < dist(closest.pos, self.pos):
                closest = players[i]

        target_angle = math.atan2(closest.pos[1] - self.pos[1], closest.pos[0] - self.pos[0])

        #implement angle matching
        self.curr_angle = target_angle

        self.points[0] = (self.pos[0] + self.size * math.cos(self.curr_angle), self.pos[1] + self.size * math.sin(self.curr_angle))
        self.points[1] = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi*2/3), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi*2/3))
        self.points[2] = (self.pos[0] + self.size * math.cos(self.curr_angle - math.pi*2/3), self.pos[1] + self.size * math.sin(self.curr_angle - math.pi*2/3))

        self.pos[0] += self.speed * math.cos(self.curr_angle) + self.fx
        self.pos[1] += self.speed * math.sin(self.curr_angle) + self.fy

    def draw(self, window, offset):
        drawpoints = [ [int(pair[0] - offset[0]), int(pair[1] - offset[1])] for pair in self.points]

        pygame.draw.polygon(window, (255,255,255), drawpoints)
        #pygame.draw.circle(window, (255,255,255), (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])), self.size)




class Square(ForceObject):
    def __init__(self, pos, speed, size, health=4):
        super().__init__()
        self.pos = list(pos)
        self.speed = speed
        self.size = size

        self.health = health

        self.angle_accel = 0.2
        self.curr_angle = 0

        a = (self.pos[0] + self.size * math.cos(self.curr_angle), self.pos[1] + self.size * math.sin(self.curr_angle))
        b = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi/2))
        c = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi))
        d = (self.pos[0] + self.size * math.cos(self.curr_angle + 3*math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + 3*math.pi/2))

        self.points = [a,b,c,d]

        self.active = True

    def update(self, players):
        super().update()
        closest = players[0]
        for i in range(1,len(players)):
            if dist(players[i].pos, self.pos) < dist(closest.pos, self.pos):
                closest = players[i]

        target_angle = math.atan2(closest.pos[1] - self.pos[1], closest.pos[0] - self.pos[0])

        #implement angle matching
        self.curr_angle = target_angle

        self.points[0] = (self.pos[0] + self.size * math.cos(self.curr_angle), self.pos[1] + self.size * math.sin(self.curr_angle))
        self.points[1] = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi/2))
        self.points[2] = (self.pos[0] + self.size * math.cos(self.curr_angle + math.pi), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi))
        self.points[3] = (self.pos[0] + self.size * math.cos(self.curr_angle + 3*math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + 3*math.pi/2))

        self.pos[0] += self.speed * math.cos(self.curr_angle) + self.fx
        self.pos[1] += self.speed * math.sin(self.curr_angle) + self.fy

    def draw(self,window,offset):
        drawpoints = [ [int(pair[0] - offset[0]), int(pair[1] - offset[1])] for pair in self.points]

        pygame.draw.polygon(window, (255,255,255), drawpoints)



class Squarelet(ForceObject):
    def __init__(self, pos, speed, size, health=1):
        super().__init__()

        self.pos = list(pos)
        self.speed = speed
        self.size = size

        self.health = 1

        self.angle_accel = 0.2
        self.curr_angle = 0

        self.active = True

        a = (self.pos[0] + self.size/2 * math.cos(self.curr_angle), self.pos[1] + self.size * math.sin(self.curr_angle))
        b = (self.pos[0] + self.size/2 * math.cos(self.curr_angle + math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi/2))
        c = (self.pos[0] + self.size/2 * math.cos(self.curr_angle + math.pi), self.pos[1] + self.size * math.sin(self.curr_angle + math.pi))
        d = (self.pos[0] + self.size/2 * math.cos(self.curr_angle + 3*math.pi/2), self.pos[1] + self.size * math.sin(self.curr_angle + 3*math.pi/2))

        self.points = [a,b,c,d]

        #shot in milliseconds
        self.last_shot = -1000
        self.shot_interval = 333

        #vel
        self.curr_speed = 0
        self.accel = 0.1
        self.deccel = 0.05


    def update(self, players, bullets):
        super().update()

        current_time = pygame.time.get_ticks()

        closest = players[0]
        for i in range(1,len(players)):
            if dist(players[i].pos, self.pos) < dist(closest.pos, self.pos):
                closest = players[i]

        target_angle = math.atan2(closest.pos[1] - self.pos[1], closest.pos[0] - self.pos[0])

        #implement angle matching
        self.curr_angle = target_angle

        a = (self.pos[0] + self.size * 0.7 * math.cos(self.curr_angle), self.pos[1] + self.size * 0.7 * math.sin(self.curr_angle))
        b = (self.pos[0] + self.size * 0.7 * math.cos(self.curr_angle + math.pi/2), self.pos[1] + self.size * 0.7 * math.sin(self.curr_angle + math.pi/2))
        c = (self.pos[0] + self.size * 0.7 * math.cos(self.curr_angle + math.pi), self.pos[1] + self.size * 0.7 * math.sin(self.curr_angle + math.pi))
        d = (self.pos[0] + self.size * 0.7 * math.cos(self.curr_angle + 3*math.pi/2), self.pos[1] + self.size * 0.7 * math.sin(self.curr_angle + 3*math.pi/2))

        self.points = [a,b,c,d]

        #control distance
        d = dist(closest.pos, self.pos)
        target_speed = 0
        if d > 350:
            target_speed = self.speed
        else:
            target_speed = -self.speed

        self.curr_speed = phys_single_helper(self.curr_speed, target_speed, self.accel, self.deccel)
        self.pos[0] += self.curr_speed * math.cos(self.curr_angle) + self.fx 
        self.pos[1] += self.curr_speed * math.sin(self.curr_angle) + self.fy

        if current_time > self.last_shot + self.shot_interval:
            dx = closest.pos[0] - self.pos[0]
            dy = closest.pos[1] - self.pos[1]
            rads = math.atan2(dy,dx)
            bullets.append(Bullet(self.pos, 13, rads, False, 5))
            self.last_shot = current_time

    def draw(self,window,offset):
        drawpoints = [ [int(pair[0] - offset[0]), int(pair[1] - offset[1])] for pair in self.points]

        pygame.draw.polygon(window, (255,255,255), drawpoints)




class Pentagon(ForceObject):
    def __init__(self, pos, size, health=5):
        super().__init__()

        self.pos = list(pos)
        self.size = size

        self.health = health

        self.angle_pos = 0

        p1 = (self.pos[0], self.pos[1])
        p2 = (self.pos[0] + self.size * math.cos(self.angle_pos + math.pi/4), self.pos[1] + self.size * math.sin(self.angle_pos + math.pi/4))
        p3 = (self.pos[0] + self.size * math.cos(self.angle_pos + math.pi/3), self.pos[1] + self.size * math.sin(self.angle_pos + math.pi/3))
        p4 = (self.pos[0] + self.size * math.cos(self.angle_pos - math.pi/3), self.pos[1] + self.size * math.sin(self.angle_pos - math.pi/3))
        p5 = (self.pos[0] + self.size * math.cos(self.angle_pos - math.pi/4), self.pos[1] + self.size * math.sin(self.angle_pos - math.pi/4))

        self.points = [p1,p2,p3,p4,p5]

        self.active = True


        self.mode = 0
        #0 normal
        #1 shooting

        #laser details
        self.pause_duration = 1000
        self.laser_interval = 6000
        self.last_laser = 0
        self.laser_duration = 2000
        self.lasers = []
        self.bounds = [0,0]

        self.laser_warning = []
    
    def update(self,players,map):
        super().update()
        current_time = pygame.time.get_ticks()

        if self.mode == 0:
            if len(self.lasers) > 0:
                self.bounds[0] = 0
                self.bounds[1] = 0

            closest = players[0]
            for i in range(1,len(players)):
                if dist(players[i].pos, self.pos) < dist(closest.pos, self.pos):
                    closest = players[i]

            target_angle = math.atan2(closest.pos[1] - self.pos[1], closest.pos[0] - self.pos[0])
            #implement angle matching
            
            self.angle_pos = target_angle

            if current_time > self.laser_interval + self.last_laser:
                self.mode = 1
                self.last_laser = current_time
        
        if self.mode == 1:
            if len(self.laser_warning) == 0:
                self.laser_warning.append((self.pos,map.raycast(self.pos,self.angle_pos,10000)))
        
            if current_time > + self.pause_duration + self.last_laser:
                self.mode = 2
                self.shoot_laser(map)
                
        if self.mode == 2:
            if len(self.laser_warning) > 0:
                self.laser_warning = []

            #shooting laser mode
            laser_time = self.laser_duration + current_time - (self.laser_duration + self.pause_duration + self.last_laser)
            
            #ratio goes from 0 to 1
            time_ratio = min(laser_time/self.laser_duration,1)
            w_ratio = 0
            if time_ratio < 0.1:
                w_ratio = time_ratio**2 * 10**2
            elif time_ratio >= 0.9:
                time_ratio -= 0.9
                w_ratio = (0.1 - time_ratio)/0.1
            else:
                if current_time%7 == 0:
                    w_ratio = 1
                else:
                    w_ratio = 0.9

            self.bounds[0], self.bounds[1] = middle_bounds(len(self.lasers), w_ratio)

            if current_time > self.laser_duration + self.pause_duration + self.last_laser:
                self.mode = 0

        

        self.points[0] = (self.pos[0], self.pos[1])
        self.points[1] = (self.pos[0] + self.size * math.cos(self.angle_pos + math.pi/3), self.pos[1] + self.size * math.sin(self.angle_pos + math.pi/3))
        self.points[2] = (self.pos[0] + self.size * math.cos(self.angle_pos + math.pi*2/3), self.pos[1] + self.size * math.sin(self.angle_pos + math.pi*2/3))
        self.points[3] = (self.pos[0] + self.size * math.cos(self.angle_pos - math.pi*2/3), self.pos[1] + self.size * math.sin(self.angle_pos - math.pi*2/3))
        self.points[4] = (self.pos[0] + self.size * math.cos(self.angle_pos - math.pi/3), self.pos[1] + self.size * math.sin(self.angle_pos - math.pi/3))



    def draw(self, window, offset):
        drawpoints = [ [int(pair[0] - offset[0]), int(pair[1] - offset[1])] for pair in self.points]

        pygame.draw.polygon(window, (255,255,255), drawpoints)

        for i in range(self.bounds[0],self.bounds[1]):
            laser = self.lasers[i]
            pygame.draw.line(window, (255,255,255), 
                (laser[0][0] - offset[0], laser[0][1] - offset[1]), 
                (laser[1][0] - offset[0], laser[1][1] - offset[1]), 
            2)

        for warn in self.laser_warning:
            pygame.draw.line(window, (255,0,0), 
                (warn[0][0] - offset[0], warn[0][1] - offset[1]), 
                (warn[1][0] - offset[0], warn[1][1] - offset[1]), 
            2)

    
    def shoot_laser(self, map):
        self.lasers = []
        s = int(self.size//4)
        for i in range(-s,s+1,1):
            p1 = (
                self.pos[0] - i * math.cos(self.angle_pos + math.pi/2),
                self.pos[1] - i * math.sin(self.angle_pos + math.pi/2)
            )
            p2 = map.raycast(p1, self.angle_pos, 10000)
            self.lasers.append((p1,p2))
        print(len(self.lasers))

        

    


