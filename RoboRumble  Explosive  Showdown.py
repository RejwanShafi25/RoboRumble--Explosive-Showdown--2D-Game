from turtle import window_height
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import random

# Window Title
Title = b"RoboRumble Explosive Showdown"

# Window Size and FPS
W_Width, W_Height = 1000, 700
mouse_x, mouse_y = 0, 0
FPS = 120
last_key_pressed = None

# Global Variables
terrain = None
chunk_size = 5

bullets = []
explosions = []
bullet_types = ["Simple", "Explosive", "Sniper", "Burst"]
selected_bullet_type = "Simple"

current_turn = 1

paused = False
lost = False

# Players
robots = []


class Robot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 20
        self.h = 20
        self.r = 6
        self.tilt = 0
        self.jump_velocity = 0
        self.on_ground = True
        self.last_key_pressed=False
        self.health = 100
        self.energy = 100

class Bullet:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.r = 2
        self.type = "Simple"
        self.damage = 20

    def UpdatePosition(self):
        self.x = self.x + self.vx
        self.y = self.y + self.vy

        if self.type in ["Sniper"]:
            self.vy -= 0
        elif self.type in ["Simple", "Explosive", "Burst"]:
            self.vy -= 1

class Explosion:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.r = 1
        self.r_max = 20

def RestartGame():
    global paused, lost, current_turn
    paused = False
    lost = False
    current_turn = 1

    GenerateRandomTerrain()

    global bullets
    bullets = []

    global robots
    robots = []

    global explosions
    explosions = []

    robot1 = Robot()
    robot1.x = 100
    robot1.y = terrain[robot1.x]  
    robots.append(robot1)

    robot2 = Robot()
    robot2.x = W_Width - 100
    robot2.y = terrain[robot2.x]
    robots.append(robot2)

def GenerateRandomTerrain():
    global W_Width, W_Height, terrain
    
    terrain = []
    y = random.randint(200, 300)

    for i in range(W_Width):
        decision = random.randint(1, 10)
        if decision == 1:
            y += 1
        elif decision == 2:
            y -= 1
        else:
            pass
        terrain.append(y)

def ModifyTerrain(r, cx, cy):
    global terrain,robots

    x, y, d = 0, r, 1 - r
    
    while x <= y:
        tx = cx + x
        if tx>=0 and tx<W_Width:
            ty = terrain[tx]
            ny = cy - y
            terrain[tx] = max(100, min(ty, ny))

        tx = cx + y
        if tx>=0 and tx<W_Width:
            ty = terrain[tx]
            ny = cy - x
            terrain[tx] = max(100, min(ty, ny))

        tx = cx - x
        if tx>=0 and tx<W_Width:
            ty = terrain[tx]
            ny = cy - y
            terrain[tx] = max(100, min(ty, ny))

        tx = cx - y
        if tx>=0 and tx<W_Width:
            ty = terrain[tx]
            ny = cy - x
            terrain[tx] = max(100, min(ty, ny))

        x = x + 1
        if d < 0:
            d = d + 2 * x + 3
        else:
            y = y - 1
            d = d + 2 * x - 2 * y + 5
        robots[0].on_ground=False
        robots[1].on_ground=False

def SmoothTerrain(x1, y1, x2, y2):
    global terrain

    zone = FindZone(x1, y1, x2, y2)
    x1, y1 = ConvertToZoneZero(x1, y1, zone)
    x2, y2 = ConvertToZoneZero(x2, y2, zone)
    dx = x2 - x1
    dy = y2 - y1
    d = dy + dy - dx
    incE = dy + dy 
    incNE = dy - dx
    incNE += incNE
    y = y1

    for x in range(x1, x2 + 1):
        x3, y3 = ConvertFromZoneZero(x, y, zone)
        terrain[x] = min(terrain[x], y3)
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE

def DrawTerrain():
    global terrain, W_Width, chunk_size

    # Only Using GL_POINTS
    #glColor3ub(242, 157, 38)
    #glBegin(GL_POINTS)
    #for x in range(W_Width):
    #    y = terrain[x]
    #    while y >= 0:
    #        glVertex2i(x, y)
    #        y -= 1
    #glEnd()

    # Only Using GL_LINES
    glColor3ub(242, 157, 38)

    for x in range(W_Width):
         glBegin(GL_LINES)
         glVertex2i(x, terrain[x])
         glVertex2i(x, 100)
         glEnd()
    

    #for chunk_x in range(0, len(terrain), chunk_size):
    #    chunk = terrain[chunk_x:(chunk_x + chunk_size)]
    #    min_y = min(chunk)

    #    # Rough Part
    #    glColor3ub(242, 157, 38)
    #    glBegin(GL_POINTS)
    #    for i in range(chunk_size):
    #        x = chunk_x + i
    #        y = chunk[i]
    #        while y >= min_y:
    #            glVertex2i(x, y)
    #            y -= 1
    #    glEnd()

    #    # Using GL_POLYGON (for optimization)
    #    # Fixed Part
    #    #glColor3ub(100, 0, 0)
    #    glColor3ub(242, 157, 38)
    #    glBegin(GL_POLYGON)
    #    glVertex2i(chunk_x, 100)
    #    glVertex2i(chunk_x, min_y)
    #    glVertex2i(chunk_x + chunk_size, min_y)
    #    glVertex2i(chunk_x + chunk_size, 100)
    #    glEnd()

def AllPointsInLine(x1, y1, x2, y2):
    points = []
    zone = FindZone(x1, y1, x2, y2)
    x1, y1 = ConvertToZoneZero(x1, y1, zone)
    x2, y2 = ConvertToZoneZero(x2, y2, zone)
    dx = x2 - x1
    dy = y2 - y1
    d = dy + dy - dx
    incE = dy + dy  # incE = 2 * dy
    incNE = dy - dx
    incNE += incNE  # incNE = 2 * (dy - dx)
    y = y1
    for x in range(int(x1), int(x2) + 1):
        x3, y3 = ConvertFromZoneZero(x, y, zone)
        points.append((x3, y3))
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE
    return points

# Midpoint Line Drawing Algorithm
def DrawLine(x1, y1, x2, y2):
    zone = FindZone(x1, y1, x2, y2)
    x1, y1 = ConvertToZoneZero(x1, y1, zone)
    x2, y2 = ConvertToZoneZero(x2, y2, zone)
    dx = x2 - x1
    dy = y2 - y1
    d = dy + dy - dx
    incE = dy + dy  # incE = 2 * dy
    incNE = dy - dx
    incNE += incNE  # incNE = 2 * (dy - dx)
    y = y1
    glBegin(GL_POINTS)
    for x in range(int(x1), int(x2) + 1):
        x3, y3 = ConvertFromZoneZero(x, y, zone)
        glVertex2f(x3, y3)
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE
    glEnd()

def FindZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    zone = 0
    if abs(dx) >= abs(dy):
        if dx > 0 and dy >= 0:
            zone = 0
        elif dx < 0 and dy >= 0:
            zone = 3
        elif dx < 0 and dy < 0:
            zone = 4
        elif dx > 0 and dy < 0:
            zone = 7
    else:
        if dx >= 0 and dy > 0:
            zone = 1
        elif dx < 0 and dy > 0:
            zone = 2
        elif dx < 0 and dy < 0:
            zone = 5
        elif dx >= 0 and dy < 0:
            zone = 6
    return zone

def ConvertToZoneZero(x, y, zone):
    if zone == 0:
        return (x, y)
    elif zone == 1:
        return (y, x)
    elif zone == 2:
        return (y, -x)
    elif zone == 3:
        return (-x, y)
    elif zone == 4:
        return (-x, -y)
    elif zone == 5:
        return (-y, -x)
    elif zone == 6:
        return (-y, x)
    elif zone == 7:
        return (x, -y)

def ConvertFromZoneZero(x, y, zone):
    if zone == 0:
        return (x, y)
    elif zone == 1:
        return (y, x)
    elif zone == 2:
        return (-y, x)
    elif zone == 3:
        return (-x, y)
    elif zone == 4:
        return (-x, -y)
    elif zone == 5:
        return (-y, -x)
    elif zone == 6:
        return (y, -x)
    elif zone == 7:
        return (x, -y)
# End Midpoint Line Drawing Algorithm

# Midpoint Circle Drawing Algorithm
def DrawCircle(r, cx = 0, cy = 0):
    x, y, d = 0, r, 1 - r
    glPointSize(2)
    glBegin(GL_POINTS)
    while x <= y:
        glVertex2f(cx + x, cy + y)
        glVertex2f(cx + y, cy + x)
        glVertex2f(cx - x, cy + y)
        glVertex2f(cx - y, cy + x)
        glVertex2f(cx + x, cy - y)
        glVertex2f(cx + y, cy - x)
        glVertex2f(cx - x, cy - y)
        glVertex2f(cx - y, cy - x)
        x = x + 1
        if d < 0:
            d = d + 2 * x + 3
        else:
            y = y - 1
            d = d + 2 * x - 2 * y + 5
    glEnd()
# End Midpoint Circle Drawing Algorithm

def specialKeyListener(key, x, y):
    global terrain, robots, W_Width, paused, current_turn, last_key_pressed

    robot = robots[current_turn]

    if not paused and robot.on_ground and len(bullets) == 0:
        if key in [GLUT_KEY_RIGHT, GLUT_KEY_LEFT]:
            robot.last_key_pressed = key

        if key == GLUT_KEY_RIGHT and robot.energy >= 1:
            MoveRobotRight(robot, terrain)
            robot.energy -= 1
        if key == GLUT_KEY_LEFT and robot.energy >= 1:
            MoveRobotLeft(robot, terrain)
            robot.energy -= 1

        if key == GLUT_KEY_UP and robot.energy >= 20:
            robot.jump_velocity = 12
            robot.on_ground = False
            robot.tilt = 0
            robot.energy -= 20

def update_robot_position(robot):
    global W_Width, terrain

    if not robot.on_ground:
        robot.jump_velocity -= 1

    robot.y += robot.jump_velocity  # Update Y position based on jump velocity

    # Update X position based on direction last pressed
    if robot.last_key_pressed == GLUT_KEY_RIGHT:
        robot.x += 2
    elif robot.last_key_pressed == GLUT_KEY_LEFT:
        robot.x -= 2

    # Ensure robot.x is within the window's boundaries
    robot.x = max(0, min(robot.x, W_Width - 1 - robot.w))

    # Check for collision with terrain, ensuring robot_x_index is within bounds
    if robot.y <= terrain[robot.x]:
        robot.y = terrain[robot.x]
        robot.jump_velocity = 0
        robot.on_ground = True
        robot.last_key_pressed = None

def keyboardListener(key, x, y):
    global paused, current_turn
    if key == b' ':
        paused = not paused
        
def FireBullet(robot, angle):
    global bullets, selected_bullet_type

    bx = robot.x + (robot.w // 2)
    by = robot.y + robot.h + robot.r

    if selected_bullet_type == "Burst":
        for sway in range(-5, 6):
            bullet = Bullet()
            bullet.type = selected_bullet_type
            bullet.x = bx
            bullet.y = by
            bullet.vx = math.cos(angle + sway * 0.03) * 20
            bullet.vy = math.sin(angle + sway * 0.03) * 20
            bullet.damage = 5
            bullets.append(bullet)
    else:
        bullet = Bullet()
        bullet.type = selected_bullet_type
        bullet.x = bx
        bullet.y = by

        speed = 0
        damage = 0

        if selected_bullet_type == "Simple":
            speed = 30
            damage = 20
        elif selected_bullet_type == "Explosive":
            speed = 20
            damage = 20
        elif selected_bullet_type == "Sniper":
            speed = 50
            damage = 30

        bullet.vx = math.cos(angle) * speed
        bullet.vy = math.sin(angle) * speed
        bullet.damage = damage
        bullets.append(bullet)
    
def MoveRobotRight(robot, terrain):
    global W_Width
    if not paused:
        for i in range(10):
            robot.x += 1
            if robot.x + robot.w >= W_Width:
                robot.x -= 1
                break
            new_y = terrain[robot.x]
            new_tilt = terrain[robot.x + robot.w] - terrain[robot.x]
            max_yl = max(terrain[robot.x:(robot.x + robot.w // 2)])
            max_yr = max(terrain[(robot.x + robot.w // 2):(robot.x + robot.w)])
            if abs(new_tilt) > 5 or abs(max_yl - new_y) > 5 or abs(max_yr - new_y - new_tilt) > 5:
                robot.x -= 1
            else:
                robot.y = new_y
                robot.tilt = new_tilt
                SmoothTerrain(robot.x, robot.y + 1, robot.x + robot.w, robot.y + robot.tilt + 1)

def MoveRobotLeft(robot, terrain):
    if not paused:
        for i in range(2):
            robot.x -= 1
            if robot.x <= 0:
                robot.x += 1
                break
            new_y = terrain[robot.x]
            new_tilt = terrain[robot.x + robot.w] - terrain[robot.x]
            max_yl = max(terrain[robot.x:(robot.x + robot.w // 2)])
            max_yr = max(terrain[(robot.x + robot.w // 2):(robot.x + robot.w)])
            if abs(new_tilt) > 5 or abs(max_yl - new_y) > 5 or abs(max_yr - new_y - new_tilt) > 5:
                robot.x += 1
            else:
                robot.y = new_y
                robot.tilt = new_tilt
                SmoothTerrain(robot.x, robot.y + 1, robot.x + robot.w, robot.y + robot.tilt + 1)

def mouseListener(button, state, x, y):
    global paused
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mx, my = x, W_Height - y
            buttonSize = 100
            # Restart Button
            bx1, bx2 = 0, buttonSize
            by1, by2 = W_Height - buttonSize, W_Height

            if bx1 <= mx and by1 <= my and mx <= bx2 and my <= by2:
                print("Game restarted.")
                RestartGame()

            # Pause Button
            bx1, bx2 = W_Width // 2 - buttonSize // 2,  W_Width // 2 + buttonSize // 2
            by1, by2 = W_Height - buttonSize, W_Height

            if bx1 <= mx and by1 <= my and mx <= bx2 and my <= by2:
                global paused
                paused = not paused
                if paused:
                    print("Game paused.")
                else:
                    print("Game unpaused.")

            # Exit Button
            bx1, bx2 = W_Width - buttonSize, W_Width
            by1, by2 = W_Height - buttonSize, W_Height

            if bx1 <= mx and by1 <= my and mx <= bx2 and my <= by2:
                print("Terminating the game")
                glutLeaveMainLoop()

    if not paused and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mx, my = x, W_Height - y

        if my < W_Height - 100 and len(bullets) == 0:
            global current_turn, robots
            player = robots[current_turn]

            # Calculate angle between player and mouse click position
            angle = math.atan2(my - (player.y + player.h + player.r), mx - (player.x + player.w // 2))

            FireBullet(player, angle)

            player.energy = 100

            global selected_bullet_type
            from random import choice
            selected_bullet_type = choice(bullet_types)

            current_turn = (current_turn+1)%2



    # if button == GLUT_MIDDLE_BUTTON:
    glutPostRedisplay()

def mouseMove(x, y):
    if not paused and not lost:
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = W_Height - y

        glutPostRedisplay()

def display():
    global bullets, robots, current_turn

    ClearColor()
    DrawTerrain()

    # Menu Lines
    glColor3ub(255, 255, 255)
    DrawLine(0, 100, W_Width, 100)
    DrawLine(0, W_Height - 100, W_Width, W_Height - 100)

    #Healthbar
    DrawHealthBar(0, 10, 60)
    DrawHealthBar(1, W_Width - 210, 60)

    #Energybar
    DrawEnergyBar(0, 10, 20)
    DrawEnergyBar(1, W_Width - 210, 20)
    
    # Bullets
    glColor3ub(255, 255, 255)
    for bullet in bullets:
        DrawCircle(bullet.r, bullet.x, bullet.y)
        DrawCircle(bullet.r - 1, bullet.x, bullet.y)

    # Aim Angle
    global mouse_x, mouse_y
    glColor3ub(255, 255, 255)
    player = robots[current_turn]
    x1, y1, x2, y2 = player.x + player.w // 2, player.y + player.h + player.r, mouse_x, mouse_y
    angle = math.atan2(y2 - y1, x2 - x1)
    x3 = x1 + math.cos(angle) * 50
    y3 = y1 + math.sin(angle) * 50
    DrawLine(x1, y1, x3, y3)

    # Draw Robots
    for i, robot in enumerate(robots):
        if i==0:
            glColor3ub(3, 227, 252) #player 1 blue color
        if i==1:
            glColor3ub(54, 172, 41) #player 2 green color

        DrawRobot(robot)

    # Turn Indicator
    cx = W_Width // 2

    glColor3ub(255, 255, 255)
    DrawText(cx - 70, 80, f"Turn : Player {current_turn + 1}")

    if current_turn == 0:
        glColor3ub(3, 227, 252) # Blue
    if current_turn == 1:
        glColor3ub(54, 172, 41) # Green
    temp_robot = Robot()
    temp_robot.x = cx - temp_robot.w // 2
    temp_robot.y = 30
    DrawRobot(temp_robot)

    # Selected Weapon Indicator
    global selected_bullet_type
    glColor3ub(255, 255, 255)
    DrawText(120, W_Height - 20, f"Weapon : {selected_bullet_type}")

    glColor3ub(255, 255, 255)
    DrawLine(cx - 25, 20, cx + 25, 20)
    DrawLine(cx + 25, 20, cx + 25, 70)
    DrawLine(cx + 25, 70, cx - 25, 70)
    DrawLine(cx - 25, 70, cx - 25, 20)

    # Win Condition
    if robots[current_turn].health <= 0:
        DrawText(120, W_Height - 40, f"Player {2 - current_turn} Won")

    # Explosions
    glColor3ub(252, 44, 3)
    for explosion in explosions:
        DrawCircle(explosion.r, explosion.x, explosion.y)

    # Restart Button
    glColor3ub(3, 227, 252)
    DrawLine(20, W_Height - 50, 50, W_Height - 20)
    DrawLine(20, W_Height - 50, 80, W_Height - 50)
    DrawLine(20, W_Height - 50, 50, W_Height - 80)

    global paused
    glColor3ub(242, 157, 38)
    if paused:
        # Play Button
        DrawLine(W_Width // 2 - 30, W_Height - 20, W_Width // 2 + 30, W_Height - 50)
        DrawLine(W_Width // 2 + 30, W_Height - 50, W_Width // 2 - 30, W_Height - 80)
        DrawLine(W_Width // 2 - 30, W_Height - 80, W_Width // 2 - 30, W_Height - 20)
    else:
        # Pause Button
        DrawLine(W_Width // 2 - 20, W_Height - 20, W_Width // 2 - 20, W_Height - 80)
        DrawLine(W_Width // 2 + 20, W_Height - 20, W_Width // 2 + 20, W_Height - 80)

    # Exit Button
    glColor3ub(252, 44, 3)
    DrawLine(W_Width - 80, W_Height - 20, W_Width - 20, W_Height - 80)
    DrawLine(W_Width - 20, W_Height - 20, W_Width - 80, W_Height - 80)

    glutSwapBuffers()

def draw():
    glutPostRedisplay()


def DrawRobot(robot):
    x1, y1 = robot.x, robot.y
    x2, y2 = robot.x + robot.w, robot.y + robot.tilt

    for i in range(robot.h):
        DrawLine(x1, y1 + i, x2, y2 + i)
        
    cx = robot.x+(robot.w//2)
    cy = robot.y + robot.r + robot.h
    for r in range(1, robot.r + 1):
        DrawCircle(r, cx, cy)

def DrawHealthBar(robot_index, x, y):
    global robots
    robot = robots[robot_index]

    max_width = 200
    health_width = int(robot.health * 2)

    glColor3ub(255, 255, 255)
    DrawText(x, y + 20, f"Player {robot_index + 1} Health:")

    # Using GL_POINTS
    #glBegin(GL_POINTS)
    #for i in range(max_width):
    #    if i <= health_width:
    #        glColor3ub(54, 172, 41) # Green
    #    else:
    #        glColor3ub(255, 255, 255) # White
    #    for j in range(10):
    #        glVertex2i(x + i, y + j)
    #glEnd()

    # Using GL_POLYGON
    glColor3ub(54, 172, 41)
    glBegin(GL_POLYGON)
    glVertex2i(x, y)
    glVertex2i(x, y + 10)
    glVertex2i(x + health_width, y + 10)
    glVertex2i(x + health_width, y)
    glEnd()

    glColor3ub(255, 255, 255)
    glBegin(GL_POLYGON)
    glVertex2i(x + health_width, y)
    glVertex2i(x + health_width, y + 10)
    glVertex2i(x + max_width, y + 10)
    glVertex2i(x + max_width, y)
    glEnd()

def DrawEnergyBar(robot_index, x, y):
    global robots
    robot = robots[robot_index]

    max_width = 200
    energy_width = int(robot.energy * 2)

    glColor3ub(255, 255, 255)
    DrawText(x, y + 20, f"Player {robot_index + 1} Energy:")

    # Using GL_POINTS
    #glBegin(GL_POINTS)
    #for i in range(max_width):
    #    if i <= energy_width:
    #        glColor3ub(3, 227, 252) # Blue
    #    else:
    #        glColor3ub(255, 255, 255) # White
    #    for j in range(10):
    #        glVertex2i(x + i, y + j)
    #glEnd()

    # Using GL_POLYGON
    glColor3ub(3, 227, 252) # Blue
    glBegin(GL_POLYGON)
    glVertex2i(x, y)
    glVertex2i(x, y + 10)
    glVertex2i(x + energy_width, y + 10)
    glVertex2i(x + energy_width, y)
    glEnd()

    glColor3ub(255, 255, 255) # White
    glBegin(GL_POLYGON)
    glVertex2i(x + energy_width, y)
    glVertex2i(x + energy_width, y + 10)
    glVertex2i(x + max_width, y + 10)
    glVertex2i(x + max_width, y)
    glEnd()


def EndGame():
    global lost, paused, current_turn
    lost = True
    paused = True  # Stop the game
    winning_player_index = 1 - current_turn
    losing_player_index = current_turn
    print(f"Robot {losing_player_index + 1} has been destroyed! \nRobot {winning_player_index + 1} has win.\n To Play Again restart the Game")
    

def animate(t):
    # Stop Animation if Game Lost of Paused
    global paused, lost,robots,robots, current_turn, bullets, explosions
    if paused:
        glutTimerFunc(1000 // FPS, animate, t);
        return
    
    if lost:
        robots[0].on_ground=True
        robots[1].on_ground=True
        paused=True
        return
    
    for robot in robots:
        if not robot.on_ground:
            update_robot_position(robot)
                
        if robot.health <= 0:
            EndGame()
            break  # Exit the loop as the game is over
    
    for explosion in explosions:
        if explosion.r < explosion.r_max:
            explosion.r += 1
            ModifyTerrain(explosion.r, explosion.x, explosion.y)
        else:
            explosions.remove(explosion)

    if not lost:
        for bullet in bullets:
            points = AllPointsInLine(int(bullet.x), int(bullet.y), int(bullet.x + bullet.vx), int(bullet.y + bullet.vy))
                
            for point in points:
                (cx, cy) = point
                robot = robots[current_turn] # Oppornent Robot

                # Check for collision with the opponent
                if (cx>=robot.x) and (cy>=robot.y) and (cx<=robot.x+robot.w) and (cy<=robot.y+robot.h+robot.r*2):
                    ActivateBullet(bullet, cx, cy)
                    robot.health -= bullet.damage  # Apply damage to the robot
                    if robot.health < 0:
                        robot.health = 0
                    break

                # Check if bullet is out of bounds   
                if cx < 0 or cx >= W_Width or cy >= W_Height - 100 or cy <= 100: 
                    bullets.remove(bullet)
                    break

                # Check if bullet has hit the terrain
                elif cy <= terrain[int(cx)]:
                    ActivateBullet(bullet, cx, cy) 
                    break

            bullet.UpdatePosition()
                    
    glutTimerFunc(1000 // FPS, animate, t + 1)
    
def ActivateBullet(bullet, cx, cy):
    if bullet.type == "Simple":
        ActivateExplosion(10, cx, cy)
    if bullet.type == "Explosive":
        ActivateExplosion(30, cx, cy)
    if bullet.type == "Sniper":
        ActivateExplosion(6, cx, cy)
    if bullet.type == "Burst":
        ActivateExplosion(6, cx, cy)

    global bullets
    bullets.remove(bullet)

def ActivateExplosion(r_max, cx, cy):
    global explosions
    explosion = Explosion()
    explosion.x = cx
    explosion.y = cy
    explosion.r = 2
    explosion.r_max = r_max
    explosions.append(explosion)

def init():
    global Title, W_Width, W_Height

    glutInit()
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_RGB)

    wind = glutCreateWindow(Title)

    AdjustWindow()
    ClearColor()

    RestartGame()

    glutDisplayFunc(display)
    glutIdleFunc(draw)

    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutPassiveMotionFunc(mouseMove)

    glutTimerFunc(1000 // FPS, animate, 0);
    glutMainLoop()

def ClearColor():
    # Resets Background Color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)

def AdjustWindow():
    # Resize Window
    glViewport(0, 0, W_Width, W_Height)

    # Convert to Projection Mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Adjust Aspect Ratio
    glOrtho(0.0, W_Width, 0.0, W_Height, 0.0, 1.0)

    # Back to Model View
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    
def DrawText(x, y, text):
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(character))

init()

