import sys, pygame
from pygame.locals import *
flags = WINDOWMAXIMIZED | DOUBLEBUF

class MyGame(object):

    def __init__(self, score = 0, levels = 0, hiscore = 0):
        pygame.init()

        # Window Info and allowed events for performance
        pygame.display.set_caption("Space Invaders")
        pygame.display.set_icon(pygame.image.load("images/invader1.png"))
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

        # If no new high score value is provided, instead read the saved hiscore
        if hiscore == 0:
            hiscoreFile = open("hiscore.txt","r")
            self._hiscore = int(hiscoreFile.readline())
            hiscoreFile.close()
        else: self._hiscore = hiscore
        self._newHS = False
        
        # Display info, background colour, font
        self._size = self._width, self._height = 960, 720
        self._bgColour = 0, 0, 0
        self._screen = pygame.display.set_mode(self._size, flags, 8)
        # Royalty free font from fontspace.com
        self._font = pygame.font.Font('fonts/quinque-five-font/Quinquefive-K7qep.ttf', 16)

        # Frame, score and time counters
        self._framecounter = 0
        self._endScreenCounter = 0
        self._lastShot = 0
        self._score = score

        # Setting up player - Sprite from pngegg.com
        self._playerview = pygame.transform.scale(pygame.image.load("images/cannon.png").convert_alpha(), (90, 70))
        self._playermodel = PlayerState(435, 630, self._width - 90, 2)

        # Setting up missiles and Enemies - Sprites from pngegg.com
        self._missileList = []
        self._enemyview = pygame.transform.scale(pygame.image.load("images/invader.png").convert_alpha(), (60, 60))
        self._enemylist = []
        self._enemyDirection = 1

        # Text to be displayed
        self._gameOverText = self._font.render(f"GAME OVER", False, (255, 255, 255))
        self._gameOverRect = self._gameOverText.get_rect()
        self._gameOverRect.center = (480, 320)
        self._winText = self._font.render(f"YOU WIN!", False, (255, 255, 255))
        self._winRect = self._winText.get_rect()
        self._winRect.center = (480, 320)
        self._restartText = self._font.render(f"- PRESS R TO RESTART -", False, (255, 255, 255))
        self._restartRect = self._restartText.get_rect()
        self._restartRect.center = (480, 360)
        self._hiScoreText = self._font.render(f"NEW HIGH SCORE!", False, (255, 255, 255))
        self._hiScoreRect = self._hiScoreText.get_rect()
        self._hiScoreRect.center = (480, 440)

        # Loading sounds
        # Royalty free sounds from pixabay.org
        self._shootSound = pygame.mixer.Sound("sfx/shoot.wav")
        self._dieSound = pygame.mixer.Sound("sfx/death.wav")
        self._killSound = pygame.mixer.Sound("sfx/explosion.wav")
        self._startSound = pygame.mixer.Sound("sfx/start.wav")
        self._winSound = pygame.mixer.Sound("sfx/win.wav")
        self._invaderSound = pygame.mixer.Sound("sfx/invader.wav")
        
        # Win and Lose conditions
        self._failed = False
        self._won = False

        # Spawning enemies (number is dependant on current level)
        for i in range(5+levels):
            for j in range(11):
                self._enemylist.append(Enemy(146 + (j * 60), 30 + (i * 60)))
            

    def rungame(self):
        pygame.mixer.Sound.play(self._startSound)
        # Game loop
        while True:
            # Fixed framerate and frame counter
            pygame.time.delay(8)
            self._framecounter += 1

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # On quit, overwrite saved hiscore with current value before exiting
                    hiscoreWrite = open("hiscore.txt","w")
                    hiscoreWrite.write(f"{self._hiscore}")
                    hiscoreWrite.close()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Fire missile if the last shot was more than 1 second ago
                        if self._framecounter - self._lastShot > 62.5 or self._lastShot == 0:
                            pygame.mixer.Sound.play(self._shootSound)
                            missile = Missile(self._playermodel.getXPos() + 43)
                            self._missileList.append(missile)
                            self._lastShot = self._framecounter

                    # Restart / continue game
                    if event.key == pygame.K_r:
                        if self._won:
                            # Add new level (as far as 3) if the game was won
                            levels = self._score//275 
                            if levels > 3: levels = 3
                            # Provide new high score if one has been set
                            if self._newHS: self.__init__(self._score, levels, self._hiscore)
                            else: self.__init__(self._score, levels)
                        else:
                            if self._newHS: self.__init__(hiscore = self._hiscore)
                            else: self.__init__()

                if event.type == pygame.KEYUP:
                    self._playermodel.handleStopMove()

            # Movement handling
            pressedkeys = pygame.key.get_pressed()  
            if pressedkeys[pygame.K_LEFT]:
                self._playermodel.handleMoveLeft()
            if pressedkeys[pygame.K_RIGHT]:
                self._playermodel.handleMoveRight()
            
            # Draw background
            self._screen.fill(self._bgColour)

            # Run end screen if the player fails or wins a level
            if self._failed or self._won:
                # Update high score
                if self._score > self._hiscore:
                    self._newHS = True
                    self._hiscore = self._score
                
                # Frame counting for text animation
                self._endScreenCounter += 1

                # Game over text and sound effect on loss
                if self._failed:    
                    self._screen.blit(self._gameOverText, self._gameOverRect)
                    pygame.mixer.Sound.play(self._dieSound)
                # Level complete text and sound on win
                elif self._won:     
                    self._screen.blit(self._winText, self._winRect)
                    self._restartText = self._font.render(f"- PRESS R TO CONTINUE -", False, (255, 255, 255))
                    pygame.mixer.Sound.play(self._winSound)

                # Flashing restart / Continue text
                if (self._endScreenCounter // 60 == 0) or (self._endScreenCounter//60%2 == 0):
                    self._screen.blit(self._restartText, self._restartRect)

                # Draw the remaining end screen text
                self._scoreText = self._font.render(f"SCORE: {self._score}", False, (255, 255, 255))
                self._scoreRect = self._scoreText.get_rect()
                self._scoreRect.center = (480, 400)
                self._screen.blit(self._scoreText, self._scoreRect)
                if self._newHS: self._screen.blit(self._hiScoreText, self._hiScoreRect)

                # Don't run the rest of the game on end screen
                pygame.display.flip()
                continue

            # Drawing player
            self._screen.blit(self._playerview, (self._playermodel.getXPos(), self._playermodel.getYPos()))
                
            # Enemy handling    
            for enemy in self._enemylist:
                Xoffset = enemy.getOffset()[0]
                Yoffset = enemy.getOffset()[1]
                
                # Enemy collision with player - Sets loss condition
                if ((enemy.getYPos() + enemy.getHeight()) > 630):
                    if ( self._playermodel.getXPos() + 90 > ((enemy.getXPos() + Yoffset) or (enemy.getXPos() + enemy.getWidth() - Xoffset)) 
                    > self._playermodel.getXPos() ):
                        self._failed = True

                # Switch directions and move down when reaching the side of the screen
                if ((enemy.getXPos() + enemy.getWidth() ) > 930) or (enemy.getXPos() < 30):
                    self._enemyDirection *= -1
                    for enemy in self._enemylist:
                        enemy.moveDown()
                        enemy.move(self._enemyDirection)
                # Move the enemies incrementally
                if (self._framecounter % 30 == 0):
                    enemy.move(self._enemyDirection)
                # Draw all enemies
                self._screen.blit(enemy.getIcon(), (enemy.getXPos(), enemy.getYPos()))

            # Missile handling
            for missile in self._missileList:
                # Move missile
                missile.moveMissile()
                # Delete missiles that have gone off screen
                if (missile.getYPos() + missile.getHeight()) < 0:
                    self._missileList.remove(missile)
                # Draw missiles
                self._screen.blit(missile.getIcon(), (missile.getXPos(), missile.getYPos()))
                # Missile collision handling with enemies - deletes both enemy and missile and increments score
                for enemy in self._enemylist:
                    Xoffset = enemy.getOffset()[0]
                    Yoffset = enemy.getOffset()[1]
                    if ( (enemy.getXPos() + Xoffset) < ((missile.getXPos() + missile.getWidth()) or missile.getXPos()) < (enemy.getXPos() + enemy.getWidth() - Xoffset)
                            and  (enemy.getYPos() + Yoffset) < (missile.getYPos()) < (enemy.getYPos() + enemy.getHeight() - Yoffset) ):
                                pygame.mixer.Sound.play(self._killSound)
                                self._enemylist.remove(enemy)
                                self._missileList.remove(missile)
                                self._score += 5

            # Win condition set when all enemies are killed
            if len(self._enemylist) == 0: self._won = True
            # Draw score and high score text
            self._screen.blit(self._font.render(f"SCORE: {self._score}", False, (255, 255, 255)), (4, 0))
            self._screen.blit(self._font.render(f"HI: {self._hiscore}", False, (255, 255, 255)), (4, 20))
            # Play sound each time enemies move
            if (self._framecounter % 30 == 0):
                pygame.mixer.Sound.play(self._invaderSound)

            pygame.display.flip()

# Classes

class Missile(object):
    def __init__(self, xpos):
        self._xPos = xpos
        self._yPos = 630
        self._width = 4
        self._height = 13
        self._icon = pygame.transform.scale(pygame.image.load("images/missile.png").convert(), (self._width, self._height))
        self._movespeed = 10

    def getXPos(self):
        return self._xPos

    def getYPos(self):
        return self._yPos

    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height

    def moveMissile(self):
            self._yPos -= self._movespeed

    def getIcon(self):
        return self._icon


class PlayerState(object):
    def __init__(self, xpos, ypos, maxxpos, change):
        self._xPos = xpos
        self._yPos = ypos
        self._maxXPos = maxxpos
        self._movespeed = change

    def getXPos(self):
        return self._xPos

    def getYPos(self):
        return self._yPos

    def handleMoveRight(self):
        if self._xPos + self._movespeed < self._maxXPos:
            self._xPos += self._movespeed

    def handleMoveLeft(self):
        if self._xPos - self._movespeed > 0:
            self._xPos -= self._movespeed

    def handleStopMove(self):
        self._xPos = self._xPos


class Enemy(object):
    def __init__(self, xpos, ypos):
        self._xPos = xpos
        self._yPos = ypos
        self._width = 60
        self._height = 60
        self._offsetX = 6
        self._offsetY = 13
        self._icon = pygame.transform.scale(pygame.image.load("images/invader.png"), (self._width, self._height))
        self._movespeed = 1.0

    def getXPos(self):
        return self._xPos

    def getYPos(self):
        return self._yPos

    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height

    def getOffset(self):
        return (self._offsetX, self._offsetY)

    def move(self, direction):
        self._xPos += 5*self._movespeed*direction

    def moveDown(self):
        self._yPos += 30
        # Make the enemies move faster every time they reach side of screen
        if self._movespeed * 1.35 < 3:
            self._movespeed *= 1.35
        else:
            self._movespeed = 5

    def getIcon(self):
        return self._icon

if __name__ == "__main__":
    mygame = MyGame()
    mygame.rungame()