import graphics
import gameplay
import data

class Skeleton(object):

    def __init__(self, world, pos, side=0):
        self.world = world

        self.animation = graphics.AnimationInfo()
        self.sprite = graphics.Sprite(0, "skeleton.png", pos)

        self.xVel, self.yVel = (0, 0)

        self.sprite.xScale = side if side else cmp(self.world.player.sprite.x, self.sprite.x)
        if self.sprite.xScale == 0: self.sprite.xScale = -1

        self.health = 3

        self.state = "idle"
        self.dir = 0

        self.invincibility = 0
        self.dead = False

        self.soundTimer = 0
        self.sound = "bone-rattle1.ogg"

    @property
    def leftBox(self): return 32 if self.sprite.xScale == 1 else 56

    @property
    def rightBox(self): return 56 if self.sprite.xScale == 1 else 32

    def draw(self, display, offset=(0, 0)):
        if self.playerClose() and self.state != "attacking":
            side = cmp(self.world.player.sprite.x, self.sprite.x)
            distance = abs(self.world.player.sprite.x - self.sprite.x)

            if self.sprite.xScale != side and distance > 38:
                self.sprite.x += 30 * side
                self.sprite.xScale = side

        if self.state == "knockback":
            self.animation.index = lambda: 32

        if self.state == "attacking":
            self.animation.index = lambda: 8 + (self.animation.timer / 16) % 2 if self.animation.timer < 32 \
            else 16 + (self.animation.timer / 8) % 4

        if self.state == "walking":
            self.animation.index = lambda: 1 + (self.animation.timer / 8) % 4

        if self.state == "idle":
            self.animation.index = lambda: (self.animation.timer / 16) % 2

        self.animation.animate(self.sprite)
        self.sprite.draw(display, offset)

    def playerClose(self):
        return abs(self.sprite.x - self.world.player.sprite.x) < 360 \
        and abs(self.sprite.y - self.world.player.sprite.y) < 128

    def stuck(self):
        self.sprite.x += self.dir
        stuck = self.collided()
        self.sprite.x -= self.dir

        return stuck

    def move(self):
        if self.onSurface() and self.dir != 0 and self.state == "idle":

            if self.xVel == 0 and self.stuck():
                if self.dir != self.sprite.xScale and \
                abs(self.sprite.x - self.world.player.sprite.x) > 128:
                    self.dir *= -1
                else: return

            self.state = "walking"
            self.xVel = max(-2, min(self.xVel + self.dir * 0.2, 2))

    def attack(self):
        self.state = "attacking"
        self.animation.timer = 0

    def knockBack(self, origin):
        self.animation.timer = 0
        self.state = "knockback"
        self.xVel = 8 * cmp(self.sprite.x, origin.sprite.x)

    def getHurt(self, origin):
        if self.invincibility > 0 or \
        (self.state == "attacking" and self.animation.timer >= 32):
            return

        self.knockBack(origin)
        self.health -= origin.damage()

        self.invincibility = origin.weapon.pos - origin.weapon.pre
        data.playSound("bone-smash.ogg")

        if self.health <= 0: self.summonBones()

    def summonBones(self):
        self.world.particles.append(gameplay.entity.Bone(40, (self.sprite.x + 4 * self.sprite.xScale, self.sprite.y - 24), self.sprite.xScale))
        self.world.particles.append(gameplay.entity.Bone(42, (self.sprite.x + 18 * self.sprite.xScale, self.sprite.y + 16), self.sprite.xScale))
        self.world.particles.append(gameplay.entity.Bone(43, (self.sprite.x + 4 * self.sprite.xScale, self.sprite.y + 44), self.sprite.xScale))
        self.world.particles.append(gameplay.entity.Bone(44, (self.sprite.x - 24 * self.sprite.xScale, self.sprite.y + 44), self.sprite.xScale))

        for i in range(4):
            self.world.particles.append(gameplay.entity.Bone(43, (self.sprite.x, self.sprite.y), self.sprite.xScale))
            self.world.particles.append(gameplay.entity.Bone(44, (self.sprite.x, self.sprite.y), self.sprite.xScale))

        self.world.particles.append(gameplay.entity.Bone(41, (self.sprite.x - 14 * self.sprite.xScale, self.sprite.y + 8), self.sprite.xScale))

    def damage(self):
        return 2 if self.state == "attacking" and 32 <= self.animation.timer < 64 else 0

    def update(self):
        self.animation.timer += 1

        self.sprite.x += self.xVel

        if self.collided():
            if self.xVel >= 0: self.sprite.x -= (self.sprite.x + self.sprite.xCenter - self.rightBox) % gameplay.tile.size
            else: self.sprite.x += gameplay.tile.size - (self.sprite.x - self.sprite.xCenter + self.leftBox) % gameplay.tile.size

            self.xVel = 0

        self.sprite.y += self.yVel

        if self.collided():
            if self.yVel >= 0: self.sprite.y -= (self.sprite.y + self.sprite.yCenter) % gameplay.tile.size
            else: self.sprite.y += gameplay.tile.size - (self.sprite.y - self.sprite.yCenter) % gameplay.tile.size

            self.yVel = 0

        self.applyGravity()

        self.invincibility -= 1

        if self.health <= 0:
            pos = self.sprite.x, self.sprite.y

            for i in range(8):
                newOrb = gameplay.entity.Orb(self.world, pos)
                self.world.entities.append(newOrb)

            self.dead = True

        if self.state == "walking":
            if self.soundTimer <= 0:
                data.playSound(self.sound)
                self.soundTimer = 24

                if self.sound == "bone-rattle1.ogg":
                    self.sound = "bone-rattle2.ogg"
                else: self.sound = "bone-rattle1.ogg"
        self.soundTimer -= 1


        if self.state != "attacking" or self.animation.timer >= 64:
            if self.state != "knockback" or (self.invincibility <= 0 and self.onSurface()):
                self.state = "idle"

            if self.playerClose() and self.world.player.health > 0:
                distance = abs(self.sprite.x - self.world.player.sprite.x)

                if distance < 256:
                    if distance > 192:
                        self.dir = self.sprite.xScale
                    if distance < 128:
                        if self.animation.timer > 96: self.attack()
                        self.dir = -self.sprite.xScale

                else: self.dir = self.sprite.xScale

            else: self.dir = 0
            self.move()

        elif self.animation.timer == 32:
            self.xVel = 16 * self.sprite.xScale
            data.playSound("slash.ogg")


    def collided(self):
        l = int(self.sprite.x - self.sprite.xCenter + self.leftBox) / gameplay.tile.size
        r = int(self.sprite.x + self.sprite.xCenter - 1 - self.rightBox) / gameplay.tile.size

        t = int(self.sprite.y - self.sprite.yCenter) / gameplay.tile.size
        b = int(self.sprite.y + self.sprite.yCenter - 1) / gameplay.tile.size

        for x in range(l, r + 1):
            for y in range(t, b + 1):
                if self.world.map[y][x].isColidable():
                    return True

        return False

    def collidedWith(self, entity):
        if isinstance(entity, gameplay.entity.Player):
            if entity.invincibility <= 0:
                if self.health > 0 and self.invincibility <= 0:
                    if self.sprite.collidesWith(entity.sprite):
                        entity.getHurt(self)

    def onSurface(self):
        self.sprite.y += 1
        check = self.collided()
        self.sprite.y -= 1
        return check

    def applyGravity(self):
        if self.onSurface() and self.state != "walking": self.xVel *= 0.8
        else:  self.yVel = min(self.yVel + 0.5, gameplay.tile.size - 1)
