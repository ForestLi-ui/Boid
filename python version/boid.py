import arcade
import random
import math
from arcade import Texture
from matplotlib import pyplot as plt


WIDTH = 1000
HEIGHT = 1000
N = 100
SCALE = 0.08
MAX_SPEED = 5
MAX_ACC = 0.05

sprites_list = arcade.SpriteList()

PRIMARY_BOID = 1
VIEW_DISTANCE = 100
VIEW_ANGLE = 180


class Boid(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 1, image_x: float = 0, image_y: float = 0,
                 image_width: float = 0, image_height: float = 0, center_x: float = 0, center_y: float = 0,
                 repeat_count_x: int = 1, repeat_count_y: int = 1, flipped_horizontally: bool = False,
                 flipped_vertically: bool = False, flipped_diagonally: bool = False, hit_box_algorithm: str = "Simple",
                 hit_box_detail: float = 4.5, texture: Texture = None, angle: float = 0):
        super().__init__(filename, scale, image_x, image_y, image_width, image_height, center_x, center_y,
                         repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically, flipped_diagonally,
                         hit_box_algorithm, hit_box_detail, texture, angle)
        self.acceleration = [0.0, 0.0]
        self.velocity = [random.uniform(-1 * MAX_SPEED, MAX_SPEED), random.uniform(-1 * MAX_SPEED, MAX_SPEED)]
        self.in_view = []

    def update(self):
        self.clamp()
        self.center_x += self.velocity[0]
        self.center_y += self.velocity[1]
        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]
        self.clamp()

        # set the colour
        if self.angle < 0:
            angle = 360 + self.angle
        else:
            angle = self.angle
        angle = angle / 180 * math.pi
        self.color = (128*(math.cos(angle)+1), 128*(math.cos(angle + 2/3 * math.pi)+1), 128*(math.cos(angle - 2/3 * math.pi)+1))

        # getting boids in its view
        self.in_view = self.view()

        # align
        average = [0.0, 0.0]
        for b in self.in_view:
            average[0] += b.velocity[0]
            average[1] += b.velocity[1]
        if len(self.in_view) > 0 and math.hypot(average[0], average[1]) != 0:
            average[0] = average[0] / len(self.in_view) / math.hypot(average[0], average[1]) * MAX_SPEED
            average[1] = average[1] / len(self.in_view) / math.hypot(average[0], average[1]) * MAX_SPEED
            self.acceleration[0] += average[0] - self.velocity[0]
            self.acceleration[1] += average[1] - self.velocity[1]

        # cohesion
        total = [self.center_x, self.center_y]
        for b in self.in_view:
            total[0] += b.center_x
            total[1] += b.center_y
        if len(self.in_view) > 0:
            total[0] /= (len(self.in_view) + 1)
            total[1] /= (len(self.in_view) + 1)
            dir = [total[0] - self.center_x - self.velocity[0], total[1] - self.center_y - self.velocity[1]]
            if math.hypot(dir[0], dir[1]) != 0:
                dir[0] = dir[0] / math.hypot(dir[0], dir[1]) * MAX_ACC
                dir[1] = dir[1] / math.hypot(dir[0], dir[1]) * MAX_ACC
                self.acceleration[0] += dir[0]
                self.acceleration[1] += dir[1]

        # separation
        average = [0.0, 0.0]
        for b in self.in_view:
            diff = [self.center_x - b.center_x, self.center_y - b.center_y]
            distance = math.hypot(self.center_x - b.center_x, self.center_y - b.center_y)
            diff = [diff[0] / math.hypot(diff[0], diff[1]), diff[1] / math.hypot(diff[1], diff[0])]
            diff = [diff[0] / distance, diff[1] / distance]

            #plt.plot(distance, math.hypot(diff[0], diff[1]), "bo-")

            average = [average[0] + diff[0], average[1] + diff[1]]
        if len(self.in_view) > 0:
            average = [average[0] / len(self.in_view), average[1] / len(self.in_view)]
            delta = [average[0] - self.velocity[0], average[1] - self.velocity[1]]
            if math.hypot(delta[0], delta[1]) != 0:
                delta[0] = delta[0] / math.hypot(delta[0], delta[1]) * MAX_ACC
                delta[1] = delta[1] / math.hypot(delta[0], delta[1]) * MAX_ACC
                self.acceleration[0] += delta[0]
                self.acceleration[1] += delta[1]

        # edge detection
        angle = angle / math.pi * 180
        if self.center_x > WIDTH - VIEW_DISTANCE:
            if angle + VIEW_ANGLE / 2 > 90:
                self.acceleration[0] -= 1 / abs(WIDTH - self.center_x)

    def clamp(self):
        if math.hypot(self.velocity[0], self.velocity[1]) > MAX_SPEED:
            self.velocity[0] = self.velocity[0] / math.hypot(self.velocity[0], self.velocity[1]) * MAX_SPEED
            self.velocity[1] = self.velocity[1] / math.hypot(self.velocity[0], self.velocity[1]) * MAX_SPEED
        if self.acceleration[0] < -1 * MAX_ACC:
            self.acceleration[0] = -1 * MAX_ACC
        if self.acceleration[0] > MAX_ACC:
            self.acceleration[0] = MAX_ACC
        if self.acceleration[1] < -1 * MAX_ACC:
            self.acceleration[1] = -1 * MAX_ACC
        if self.acceleration[1] > MAX_ACC:
            self.acceleration[1] = MAX_ACC
        self.angle = self.t()
        self.edge_detection()

    def t(self):
        if self.velocity[0] == 0:
            if self.velocity[1] >= 0:
                return 0
            return 180
        angle = math.degrees(math.atan(self.velocity[1] / self.velocity[0]))
        if self.velocity[0] < 0:
            return 90 + angle
        if self.velocity[0] > 0:
            return -90 + angle

    def edge_detection(self):
        if self.center_x > WIDTH + 2:
            self.center_x = -2
        elif self.center_x < -2:
            self.center_x = WIDTH + 2
        if self.center_y > HEIGHT + 2:
            self.center_y = -2
        elif self.center_y < -2:
            self.center_y = HEIGHT + 2

    def view(self):
        viewed = []
        for b in sprites_list:
            if b == self:
                continue
            if math.hypot(b.center_x - self.center_x, b.center_y - self.center_y) <= VIEW_DISTANCE:
                if b.center_y == self.center_y or b.center_x == self.center_x:
                    continue
                x_difference = b.center_x - self.center_x
                y_difference = b.center_y - self.center_y
                angle = math.degrees(math.atan(y_difference / x_difference))
                if x_difference < 0:
                    absolute_angle = 90 + angle
                else:
                    absolute_angle = -90 + angle
                if self.angle - VIEW_ANGLE / 2 <= absolute_angle <= self.angle + VIEW_ANGLE / 2:
                    viewed.append(b)
        return viewed


class Application(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        global sprites_list
        for i in range(N):
            boid = Boid("E:\computing\programming canford\school\\boid\Drawing.png", SCALE)
            boid.center_x = random.uniform(0, WIDTH)
            boid.center_y = random.uniform(0, HEIGHT)
            sprites_list.append(boid)

    def on_draw(self):
        arcade.start_render()
        sprites_list.update()
        sprites_list.draw()


window = Application(WIDTH, HEIGHT)
window.setup()
# plt.clf()
# plt.xlabel('distance')
# plt.ylabel('acceleration')
arcade.run()
# plt.show()