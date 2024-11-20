# encoding: utf-8
import os.path
import sys

import cv2


class Mazer:
    # 默认从左上角开始向右走，遇到边界或者墙就右转，遇到空地就左转
    # 左手扶墙走，没走一步检查左边是否有墙，左边没有强视为空地
    def __init__(self, file_name):
        self.file_name = file_name
        image = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
        # 透明转白色
        if image.shape[2] == 4:
            a_mask = (image[:, :, 3] == 0)
            image[a_mask] = [255, 255, 255, 255]
            self.org_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        else:
            self.org_img = image
        self.width = self.org_img.shape[0]
        self.height = self.org_img.shape[1]

        # ↓1 ←2 ↑3 →4  左转减一，右转加一，如果是0就改成4，如果是5就改成1
        self.dir = 4
        # self.org_img[row, col, cell], 但是这里是反过来的 (col, row)
        self.pos = [0, (int)(self.height/2)]

        self.start_touch = False

    def move(self):
        # ↓1
        if self.dir == 1:
            # 如果前方是红色的，可能是遇到死角掉头了，继续向前
            if (self.get_color((self.pos[0], self.pos[1]+1)) == (0, 0, 255)).all():
                self.pos[1] = self.pos[1] + 1
            elif self.pos[1] == self.height - 1:
                # 遇到边界右转
                self.turn_right()
            elif not self.check_pos_empty((self.pos[0], self.pos[1]+1)):
                # 如果前方不为空就右转
                self.turn_right()
            else:
                self.pos[1] = self.pos[1] + 1
        # ←2
        elif self.dir == 2:
            # 如果前方是红色的，可能是遇到死角掉头了，继续向前
            if (self.get_color((self.pos[0]-1, self.pos[1])) == (0, 0, 255)).all():
                self.pos[0] = self.pos[0] - 1
            elif self.pos[0] == 0:
                self.turn_right()
            elif not self.check_pos_empty((self.pos[0]-1, self.pos[1])):
                # 如果前方不为空就右转
                self.turn_right()
            else:
                self.pos[0] = self.pos[0] - 1
        # ↑3
        elif self.dir == 3:
            # 如果前方是红色的，可能是遇到死角掉头了，继续向前
            if (self.get_color((self.pos[0], self.pos[1]-1)) == (0, 0, 255)).all():
                self.pos[1] = self.pos[1] - 1
            elif self.pos[1] == 0:
                self.turn_right()
            elif not self.check_pos_empty((self.pos[0], self.pos[1]-1)):
                # 如果前方不为空就右转
                self.turn_right()
            else:
                self.pos[1] = self.pos[1] - 1
        # →4
        elif self.dir == 4:
            # 如果前方是红色的，可能是遇到死角掉头了，继续向前
            if (self.get_color((self.pos[0]+1, self.pos[1])) == (0, 0, 255)).all():
                self.pos[0] = self.pos[0] + 1
            elif self.pos[0] >= self.width - 1:
                self.turn_right()
            elif not self.check_pos_empty((self.pos[0]+1, self.pos[1])):
                # 如果前方不为空就右转
                self.turn_right()
            else:
                self.pos[0] = self.pos[0] + 1

    def run(self):
        step = 1
        while True:
            # print(step, self.pos, self.dir)
            # 把当前位置涂红
            self.org_img[self.pos[1], self.pos[0]] = [0, 0, 255]
            if self.check_empty_left():
                # 一开始左侧为空，但是还没碰到迷宫的墙
                if self.start_touch:
                    # print("empty left")
                    self.turn_left()
                else:
                    if not self.check_pos_empty((self.pos[0]+1, self.pos[1])):
                        self.start_touch = True
            self.move()
            self.org_img[self.pos[1], self.pos[0]] = [0, 0, 255]
            if self.check_flag_left():
                # self.show()
                split_name = os.path.splitext(self.file_name)
                # black_mask = (self.org_img[:, :, 0] == 0) & (self.org_img[:, :, 1] == 0) & (self.org_img[:, :, 2] == 0)
                # self.org_img[black_mask] = (255, 255, 255)
                cv2.imwrite(split_name[0] + "-r.jpg", self.org_img)
                break

            step = step + 1
            # if step % 10000 == 0:
            #     self.show()

    def show(self):
        img = self.org_img.copy()
        img = cv2.resize(img, (1024, 1024))
        cv2.imshow("img", img)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            quit()
        cv2.destroyAllWindows()

    # 检查左侧是否标记了红色，红色表示已经找到出路了
    def check_flag_left(self):
        # ↓1
        if self.dir == 1:
            v = self.org_img[self.pos[1], self.pos[0]+1]
            if v[0] == 0 and v[1] == 0 and v[2] == 255:
                return True
        # ←2
        elif self.dir == 2:
            v = self.org_img[self.pos[1]+1, self.pos[0]]
            if v[0] == 0 and v[1] == 0 and v[2] == 255:
                return True
        # ↑3
        elif self.dir == 3:
            v = self.org_img[self.pos[1], self.pos[0]-1]
            if v[0] == 0 and v[1] == 0 and v[2] == 255:
                return True
        # →4
        elif self.dir == 4:
            v = self.org_img[self.pos[1]-1, self.pos[0]]
            if v[0] == 0 and v[1] == 0 and v[2] == 255:
                return True

        return False

    # 检查左侧是否为空，墙和界外False，空地True
    def check_empty_left(self):
        # ↓1
        if self.dir == 1:
            if self.pos[0] >= self.width-1:
                return False
            return self.check_pos_empty((self.pos[0]+1, self.pos[1]))
        # ←2
        elif self.dir == 2:
            if self.pos[1] >= self.height-1:
                return False
            return self.check_pos_empty((self.pos[0], self.pos[1]+1))
        # ↑3
        elif self.dir == 3:
            if self.pos[0] <= 0:
                return False
            return self.check_pos_empty((self.pos[0]-1, self.pos[1]))
        # →4
        elif self.dir == 4:
            if self.pos[1] <= 0:
                return False
            return self.check_pos_empty((self.pos[0], self.pos[1]-1))

    # 检查位置是否为空
    def check_pos_empty(self, pos):
        v = self.org_img[pos[1], pos[0]]
        if v[0] == 255 and v[1] == 255 and v[2] == 255:
            return True
        else:
            return False

    def turn_left(self):
        self.dir = self.dir - 1
        if self.dir == 0:
            self.dir = 4

    def turn_right(self):
        self.dir = self.dir + 1
        if self.dir == 5:
            self.dir = 1

    def get_color(self, pos):
        return self.org_img[pos[1], pos[0]]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mazer = Mazer(sys.argv[1])
        mazer.run()
    else:
        dir = "resource"
        for root, dirs, files in os.walk(dir):
            for file in files:
                if not file.endswith(".png"):
                    continue
                # print(file)
                mazer = Mazer(dir + "/" + file)
                mazer.run()
