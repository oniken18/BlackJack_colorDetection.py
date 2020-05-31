import os
import random
import threading
import time

import cv2
import imutils
import numpy as np
import pygame
from PIL import Image, ImageDraw

from Hand import Hand
from Player import Player


class Game2:
    DealerTurn = False
    CardsDeck = []
    Bet = 0
    tempBet = 0

    def __init__(self):
        self.Player = Player('Eitan', 5000)
        self.Dealer = Player('Dealer', 1)
        self.ShuffleNewDeck()
        pygame.init()
        self.currHandNum = 0
        self.isSplitEn = False
        self.isDoubleEn = False
        self.cap = cv2.VideoCapture(0)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.centerX = int(self.width / 2)
        self.heightY = int(height)
        self.betPos = (self.centerX + 230, 300)

        self.win = pygame.display.set_mode((self.width, height))
        self.surf = pygame.Surface((self.width, height))
        self.isCheckAction = False
        self.setUI((0, 0), 0, 1, 0)

        self.cx = 0
        self.cy = 0
        self.finger = (0, 0)

        self.myAction = ''
        self.requestedAction = 'bet'

        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

        img = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\backCard1.png'))
        self.DeckImage = pygame.transform.scale(img, (50, 80))
        self.animCard = pygame.transform.scale(img, (50, 80))

        arrowIMG = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\arrowBlue.png'))
        self.ArrowImg = pygame.transform.scale(arrowIMG, (10, 20))

        HImg1 = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\hearts.png'))
        self.HImg = pygame.transform.scale(HImg1, (30, 30))

        DImg1 = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\diamondsC.png'))
        self.DImg = pygame.transform.scale(DImg1, (30, 30))

        CImg1 = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\cloversC.png'))
        self.CImg = pygame.transform.scale(CImg1, (30, 30))

        SImg1 = pygame.image.load(os.path.join(THIS_FOLDER, r'Graphics\spadesC.png'))
        self.SImg = pygame.transform.scale(SImg1, (30, 30))

        DARK_BLUE = (118, 111, 111)

        pil_size = 300
        pil_image = Image.new("RGBA", (pil_size, pil_size))
        pil_draw = ImageDraw.Draw(pil_image)
        shape = [(40, 40), (100, 100)]
        pil_draw.pieslice(shape, 270, 270, fill=DARK_BLUE)
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        self.cirResult = pygame.image.fromstring(data, size, mode)
        self.image_rectResult = self.cirResult.get_rect(center=self.win.get_rect().center)

    def drawTimer(self, circleCenter, circleSize, circleFull):

        pil_size = 300
        pil_image = Image.new("RGBA", (pil_size, pil_size))
        pil_draw = ImageDraw.Draw(pil_image)

        PerFull = circleFull * 100 / 2
        toFill = PerFull * 360 / 100 + 270

        DARK_BLUE = (118, 111, 111)

        shape = [(0, 0), (circleSize, circleSize)]

        pil_draw.pieslice(shape, 270, toFill, fill=DARK_BLUE)
        # - convert into PyGame image -

        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        cir = pygame.image.fromstring(data, size, mode)
        image_rect = cir.get_rect(center=circleCenter)

        return cir, image_rect

    def setUI(self, fingerPos, isActionEn, isBetEn, isSplitEn):
        RED = pygame.Color('red')
        WHITE = pygame.Color('white')
        YELLOW = pygame.Color('yellow')
        BLUE = pygame.Color('blue')
        ORANGE = pygame.Color('orange')
        PINK = pygame.Color('pink')
        BLACK_FONT = (0, 0, 0)
        WHITE_FONT = (255, 255, 255)

        pygame.font.init()
        myFont = pygame.font.SysFont("monospace", 15)

        self.surf.fill((0, 128, 0))

        # Stand  /Hit / double action

        if isActionEn:
            # stand action
            pygame.draw.circle(self.surf, RED, (self.centerX + 200, self.heightY - 50), 40, 0)
            lbl = myFont.render("STAND", 4, WHITE_FONT, 0)
            self.surf.blit(lbl, (self.centerX + 179, self.heightY - 57))

            # hit action
            pygame.draw.circle(self.surf, YELLOW, (self.centerX + 100, self.heightY - 50), 40, 0)
            lbl = myFont.render("HIT", 4, BLACK_FONT, 0)
            self.surf.blit(lbl, (self.centerX + 85, self.heightY - 57))

            if len(self.Player.Hands[self.currHandNum].cards) == 2:
                # double action
                pygame.draw.circle(self.surf, PINK, (self.centerX - 100, self.heightY - 50), 40, 0)
                lbl = myFont.render("DOUBLE", 4, WHITE_FONT, 0)
                self.surf.blit(lbl, (self.centerX - 130, self.heightY - 57))

        # Bet action
        if isBetEn:

            pygame.draw.circle(self.surf, BLUE, (self.centerX + 250, 40), 30, 0)
            lbl = myFont.render("BET", 4, BLACK_FONT, 0)
            self.surf.blit(lbl, (self.centerX + 236, 30))

            pygame.draw.line(self.surf, BLUE, (self.centerX + 250, 100), (self.centerX + 250, 300), 2)
            pygame.draw.rect(self.surf, WHITE, (self.betPos[0], self.betPos[1] - 10, 41, 20), 0)

            bet = int((300 - self.betPos[1]) / 200 * self.Player.Money)
            lbl = myFont.render(str(bet), 4, WHITE_FONT, 0)
            self.surf.blit(lbl, (self.centerX + 236, 70))

        else:
            self.surf.blit(self.DeckImage, (10, 10))
            if not self.DealerTurn:
                self.surf.blit(self.ArrowImg, (((self.currHandNum + 1) * 80) + 30, 360))
            else:
                self.surf.blit(self.ArrowImg, (self.centerX - 10, 120))

            countHand = 0
            for hand in self.Player.Hands:
                countHand = countHand + 1
                countCards = 0

                handSum = str(hand.getSum())
                lblSum = myFont.render(handSum, 4, BLACK_FONT, 3)
                self.surf.blit(lblSum, (countHand * 80 + 30, 380))

                if hand.Winner != '':
                    lblWinner = myFont.render(hand.Winner, 4, BLACK_FONT, 3)
                    self.surf.blit(lblWinner, (countHand * 80 + 30, 390))

                for c in hand.cards:
                    countCards = countCards + 1
                    txt = str(c[0])
                    cardType = c[1]
                    Pos = (countHand * 80 + countCards * 20, 300 - countCards * 20)
                    pygame.draw.rect(self.surf, WHITE, (Pos, (40, 70)), 0)
                    pygame.draw.rect(self.surf, BLUE, (Pos, (40, 70)), 1)
                    lbl = myFont.render(txt, 4, BLACK_FONT, 3)
                    self.surf.blit(lbl, Pos)

                    SignPos = (Pos[0] + 5, Pos[1] + 20)

                    tempSign = self.HImg

                    if cardType == 'Hearts':
                        tempSign = self.HImg
                    elif cardType == 'Diamonds':
                        tempSign = self.DImg
                    elif cardType == 'Spades':
                        tempSign = self.SImg
                    elif cardType == 'Clovers':
                        tempSign = self.CImg

                    self.surf.blit(tempSign, SignPos)

            for hand in self.Dealer.Hands:
                countCards = 0
                if self.DealerTurn:
                    handSum = str(hand.getSum())
                    lblSum = myFont.render(handSum, 4, BLACK_FONT, 3)
                    self.surf.blit(lblSum, (self.centerX - 10, 140))

                for c in hand.cards:
                    countCards = countCards + 1
                    txt = str(c[0])
                    cardType = c[1]
                    Pos = (self.centerX - 100 + countCards * 50, 40)
                    pygame.draw.rect(self.surf, WHITE, (Pos, (40, 70)), 0)
                    pygame.draw.rect(self.surf, BLUE, (Pos, (40, 70)), 1)
                    if self.DealerTurn or countCards == 1:
                        lbl = myFont.render(txt, 4, BLACK_FONT, 3)
                        self.surf.blit(lbl, Pos)

                        SignPos = (Pos[0] + 5, Pos[1] + 20)

                        tempSign = self.HImg

                        if cardType == 'Hearts':
                            tempSign = self.HImg
                        elif cardType == 'Diamonds':
                            tempSign = self.DImg
                        elif cardType == 'Spades':
                            tempSign = self.SImg
                        elif cardType == 'Clovers':
                            tempSign = self.CImg

                        self.surf.blit(tempSign, SignPos)

        # split action
        if isSplitEn:
            pygame.draw.circle(self.surf, ORANGE, (self.centerX, self.heightY - 50), 40, 0)
            lbl = myFont.render("SPLIT", 4, BLACK_FONT, 0)
            self.surf.blit(lbl, (self.centerX - 25, self.heightY - 57))

        if self.isCheckAction:
            self.surf.blit(self.cirResult, self.image_rectResult)

        lblMoney = myFont.render(str(self.Player.Money), 10, BLACK_FONT, 0)
        self.surf.blit(lblMoney, (50, self.heightY - 30))

        pygame.draw.circle(self.surf, WHITE, fingerPos, 5, 1)
        self.win.blit(self.surf, (0, 0))
        pygame.display.update()

    def setAnimationUI(self, animPos):
        RED = pygame.Color('red')
        WHITE = pygame.Color('white')
        YELLOW = pygame.Color('yellow')
        BLUE = pygame.Color('blue')
        ORANGE = pygame.Color('orange')
        PINK = pygame.Color('pink')

        BLACK_FONT = (0, 0, 0)
        WHITE_FONT = (255, 255, 255)

        pygame.font.init()
        myFont = pygame.font.SysFont("monospace", 15)

        self.surf.fill((0, 128, 0))
        self.surf.blit(self.animCard, (10, 10))
        self.surf.blit(self.DeckImage, animPos)

        if not self.DealerTurn:
            self.surf.blit(self.ArrowImg, (((self.currHandNum + 1) * 80) + 30, 360))
        else:
            self.surf.blit(self.ArrowImg, (self.centerX - 10, 120))

        countHand = 0
        for hand in self.Player.Hands:
            countHand = countHand + 1
            countCards = 0

            handSum = str(hand.getSum())
            lblSum = myFont.render(handSum, 4, BLACK_FONT, 3)
            self.surf.blit(lblSum, (countHand * 80 + 30, 380))

            for c in hand.cards:
                cardType = c[1]
                countCards = countCards + 1
                txt = str(c[0])
                Pos = (countHand * 80 + countCards * 20, 300 - countCards * 20)
                pygame.draw.rect(self.surf, WHITE, (Pos, (40, 70)), 0)
                pygame.draw.rect(self.surf, BLUE, (Pos, (40, 70)), 1)
                lbl = myFont.render(txt, 4, BLACK_FONT, 3)
                self.surf.blit(lbl, Pos)
                SignPos = (Pos[0] + 5, Pos[1] + 20)

                tempSign = self.HImg

                if cardType == 'Hearts':
                    tempSign = self.HImg
                elif cardType == 'Diamonds':
                    tempSign = self.DImg
                elif cardType == 'Spades':
                    tempSign = self.SImg
                elif cardType == 'Clovers':
                    tempSign = self.CImg

                self.surf.blit(tempSign, SignPos)

        for hand in self.Dealer.Hands:
            countCards = 0
            if self.DealerTurn:
                handSum = str(hand.getSum())
                lblSum = myFont.render(handSum, 4, BLACK_FONT, 3)
                self.surf.blit(lblSum, (self.centerX - 10, 140))

            for c in hand.cards:
                countCards = countCards + 1
                txt = str(c[0])
                cardType = c[1]
                Pos = (self.centerX - 100 + countCards * 50, 40)
                pygame.draw.rect(self.surf, WHITE, (Pos, (40, 70)), 0)
                pygame.draw.rect(self.surf, BLUE, (Pos, (40, 70)), 1)
                if self.DealerTurn or countCards == 1:
                    lbl = myFont.render(txt, 4, BLACK_FONT, 3)
                    self.surf.blit(lbl, Pos)
                    SignPos = (Pos[0] + 5, Pos[1] + 20)

                    tempSign = self.HImg

                    if cardType == 'Hearts':
                        tempSign = self.HImg
                    elif cardType == 'Diamonds':
                        tempSign = self.DImg
                    elif cardType == 'Spades':
                        tempSign = self.SImg
                    elif cardType == 'Clovers':
                        tempSign = self.CImg

                    self.surf.blit(tempSign, SignPos)

        lblMoney = myFont.render(str(self.Player.Money), 10, BLACK_FONT, 0)
        self.surf.blit(lblMoney, (50, self.heightY - 30))

        self.win.blit(self.surf, (0, 0))
        pygame.display.update()

    def ShuffleNewDeck(self):
        self.CardsDeck.clear()

        for i in range(4):

            if i == 0:
                sign = "Hearts"
            elif i == 1:
                sign = "Diamonds"
            elif i == 2:
                sign = "Spades"
            else:
                sign = "Clovers"

            for j in range(13):
                self.CardsDeck.append((j + 1, sign))
        self.CardsDeck = self.CardsDeck * 4

    def ClearGame(self):
        self.Bet = 0
        self.DealerTurn = False
        self.Player.Hands.clear()
        self.Dealer.Hands.clear()

        self.cx = 0
        self.cy = 0
        self.finger = (0, 0)

        self.isCheckAction = False
        self.myAction = ''
        self.requestedAction = 'bet'

        self.setUI((0, 0), 0, 1, 0)

    def Split(self, nmHand):
        nmRan = random.randint(0, len(self.CardsDeck) - 1)
        splitCard = self.Player.Hands[nmHand].cards[1]
        self.Player.Hands[nmHand].removeCard(splitCard)
        self.Player.Hands[nmHand].addCard(self.CardsDeck[nmRan])
        self.CardsDeck.remove(self.CardsDeck[nmRan])

        tempCards = []

        nmRan = random.randint(1, len(self.CardsDeck))
        tempCards.append(splitCard)
        tempCards.append(self.CardsDeck[nmRan])
        self.CardsDeck.remove(self.CardsDeck[nmRan])

        h = Hand(tempCards)
        self.Player.Hands.append(h)
        self.Player.reduceMoney(self.Bet)

    def setBet(self):
        bet = int((300 - self.betPos[1]) / 200 * self.Player.Money)
        self.Bet = bet
        self.Player.reduceMoney(self.Bet)


    def CheckDealerHand(self):
        currSum = self.Dealer.Hands[0].getSum()
        if currSum <= 16:
            self.Hit(0)
            return False
        else:
            return True

    def Hit(self, nmHand):

        animPos = (10, 10)

        if not self.DealerTurn:
            finalX = (self.currHandNum * 80) + 80
            nextX = 10

            for i in range(300):
                if animPos[0] < finalX:
                    nextX = animPos[0] + 1

                animPos = (nextX, animPos[1] + 1)
                self.setAnimationUI(animPos)

        else:
            for i in range(200):
                animPos = (animPos[0] + 1, animPos[1])
                self.setAnimationUI(animPos)

        nmRan = random.randint(0, len(self.CardsDeck) - 1)
        if self.DealerTurn:
            self.Dealer.Hands[0].addCard(self.CardsDeck[nmRan])
        else:
            self.Player.Hands[nmHand].addCard(self.CardsDeck[nmRan])

        self.CardsDeck.remove(self.CardsDeck[nmRan])

    def DealCards(self):
        tempCards = []
        for i in range(2):
            nmRan = random.randint(1, len(self.CardsDeck)) - 1
            tempCards.append(self.CardsDeck[nmRan])
            self.CardsDeck.remove(self.CardsDeck[nmRan])

        h = Hand(tempCards)
        self.Player.Hands.append(h)

        tempCards = []
        for i in range(2):
            nmRan = random.randint(1, len(self.CardsDeck)) - 1
            tempCards.append(self.CardsDeck[nmRan])
            self.CardsDeck.remove(self.CardsDeck[nmRan])

        h = Hand(tempCards)
        self.Dealer.Hands.append(h)

    def tryStand(self):
        start_time = time.time()
        while time.time() - start_time < 2:

            t = time.time() - start_time
            butPos = (self.centerX + 310, self.heightY + 60)
            self.cirResult, self.image_rectResult = self.drawTimer(butPos, 80, t)

            if not ((80 <= self.cx <= 160) and (390 <= self.cy <= 470)):
                self.isCheckAction = False
                return
        self.myAction = 'stand'

    def trySplit(self):
        start_time = time.time()
        while time.time() - start_time < 2:
            t = time.time() - start_time
            butPos = (self.centerX + 110, self.heightY + 60)
            self.cirResult, self.image_rectResult = self.drawTimer(butPos, 80, t)

            if not ((280 <= self.cx <= 360) and (390 <= self.cy <= 470)):
                self.isCheckAction = False
                return
        self.myAction = 'split'

    def tryHit(self):
        start_time = time.time()

        while time.time() - start_time < 2:

            t = time.time() - start_time

            butPos = (self.centerX + 210, self.heightY + 60)
            self.cirResult, self.image_rectResult = self.drawTimer(butPos, 80, t)

            if not ((170 <= self.cx <= 270) and (380 <= self.cy <= 480)):
                self.isCheckAction = False
                return
        self.myAction = 'hit'

    def tryDouble(self):
        start_time = time.time()

        while time.time() - start_time < 2:
            t = time.time() - start_time

            butPos = (self.centerX + 10, self.heightY + 60)
            self.cirResult, self.image_rectResult = self.drawTimer(butPos, 80, t)

            if not ((370 <= self.cx <= 470) and (380 <= self.cy <= 480)):
                self.isCheckAction = False
                return

        self.myAction = 'double'

    def tryBet(self):
        start_time = time.time()
        while time.time() - start_time < 2:

            t = time.time() - start_time
            butPos = (self.centerX + 370, 160)

            self.cirResult, self.image_rectResult = self.drawTimer(butPos, 60, t)

            if not ((self.centerX - 265 <= self.cx <= self.centerX - 235) and (20 <= self.cy <= 60)):
                self.isCheckAction = False
                return

        self.requestedAction = 'Deal'
        self.myAction = 'Deal'
        self.isCheckAction = False

    def CheckPlayerHand(self, nmHand):
        currCards = self.Player.Hands[nmHand].cards
        currSum = self.Player.Hands[nmHand].getSum()
        if currSum > 21:
            self.Player.Hands[nmHand].Winner = 'Dealer'
            return 'lose'
        elif currSum == 21:
            if len(currCards) == 2:
                self.Player.Hands[nmHand].isBJ = True
            return 'stand'
        elif self.Player.Hands[nmHand].isDouble:
            return 'stand'
        else:
            return ''

    def run(self):
        # t2 = threading.Thread(target=self.startCam)
        # t2.start()

        run = True

        while run:
            _, frame = self.cap.read()
            self.finger = (0, 0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            if self.DealerTurn:
                self.isCheckAction = False
                isCheckWins = False

                while not isCheckWins:
                    isCheckWins = self.CheckDealerHand()
                    self.setUI((0, 0), False, False, False)

                d = self.Dealer.Hands[0].getSum()
                for i in range(len(self.Player.Hands)):
                    self.checkWins(i, d)
                    self.setUI((0, 0), False, False, False)

                # reset and start new Game
                time.sleep(2)
                self.ClearGame()
            else:

                if self.requestedAction == 'action':
                    autoAction = self.CheckPlayerHand(self.currHandNum)

                    if autoAction == '':
                        self.requestedAction = 'action'
                    elif self.currHandNum < len(self.Player.Hands) - 1:
                        self.currHandNum = self.currHandNum + 1
                        self.requestedAction = 'action'
                        self.myAction = ''
                    else:
                        self.currHandNum = 0
                        self.DealerTurn = True
                        self.requestedAction = 'DealerTurn'

                if self.myAction == 'Deal':
                    self.DealCards()
                    self.requestedAction = 'action'
                    self.isCheckAction = False
                elif self.myAction == 'stand':
                    if self.currHandNum < len(self.Player.Hands) - 1:
                        self.currHandNum = self.currHandNum + 1
                        self.requestedAction = 'action'
                    else:
                        self.currHandNum = 0
                        self.DealerTurn = True
                        self.requestedAction = 'DealerTurn'

                    self.isCheckAction = False
                elif self.myAction == 'hit':
                    self.Hit(self.currHandNum)
                    self.requestedAction = 'action'
                    self.isCheckAction = False
                elif self.myAction == 'split':
                    self.Split(self.currHandNum)
                    self.isSplitEn = False
                    self.isCheckAction = False
                elif self.myAction == 'double':
                    self.Hit(self.currHandNum)
                    self.requestedAction = 'action'
                    self.isCheckAction = False
                    self.Player.Hands[self.currHandNum].isDouble = True
                    self.Player.reduceMoney(self.Bet)

                self.myAction = ''

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                finger_low = np.array([31, 43, 153])
                finger_high = np.array([80, 137, 224])

                finger_mask = cv2.inRange(hsv, finger_low, finger_high)

                cnt1 = cv2.findContours(finger_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cnt1 = imutils.grab_contours(cnt1)

                for c in cnt1:
                    finger_area = cv2.contourArea(c)

                    if finger_area > 50:
                        # cv2.drawContours(frame, [c], -1, (0, 0, 0), 1)
                        M = cv2.moments(c)

                        self.cx = int(M["m10"] / M["m00"])
                        self.cy = int(M["m01"] / M["m00"])
                        self.finger = (self.width - self.cx, self.cy)

                        isActionEn = (self.requestedAction == 'action')
                        isBetEn = (self.requestedAction == 'bet')
                        SplitEn = False

                        if len(self.Player.Hands) > 0:
                            tempCards = self.Player.Hands[self.currHandNum].cards
                            if len(tempCards) == 2:
                                if tempCards[0][0] == tempCards[1][0]:
                                    SplitEn = True

                        self.isSplitEn = SplitEn
                        self.setUI(self.finger, isActionEn, isBetEn, SplitEn)

                    if not self.isCheckAction and not self.DealerTurn and self.requestedAction == 'bet':
                        # Click Bet
                        if (self.centerX - 265 <= self.cx <= self.centerX - 235) and (20 <= self.cy <= 60):
                            bet = int((300 - self.betPos[1]) / 200 * self.Player.Money)
                            if bet > 0:
                                self.isCheckAction = True
                                threading.Thread(target=self.tryBet).start()

                        # move bet Slider
                        if 100 < self.cy < 300:
                            if (self.betPos[0] - 500 <= self.cx <= self.betPos[0] - 459) and (
                                    self.betPos[1] - 10 <= self.cy <= self.betPos[1] + 10):
                                self.betPos = (self.betPos[0], self.cy)

                    if not self.isCheckAction and not self.DealerTurn and self.requestedAction == 'action':
                        # Click Stand
                        if (80 <= self.cx <= 160) and (390 <= self.cy <= 470):
                            self.isCheckAction = True
                            threading.Thread(target=self.tryStand).start()

                        # Click Hit
                        if (170 <= self.cx <= 270) and (380 <= self.cy <= 480):
                            self.isCheckAction = True
                            threading.Thread(target=self.tryHit).start()

                        if len(self.Player.Hands[self.currHandNum].cards) == 2:
                            if (370 <= self.cx <= 470) and (380 <= self.cy <= 480):
                                self.isCheckAction = True
                                threading.Thread(target=self.tryDouble).start()

                        # Click Split
                        if self.isSplitEn:
                            if (280 <= self.cx <= 360) and (390 <= self.cy <= 470):
                                self.isCheckAction = True
                                threading.Thread(target=self.trySplit).start()

            frame = cv2.flip(frame, 1)

            cv2.imshow("result", frame)

        self.cap.release()
        cv2.destroyAllWindows()

    def checkWins(self, nmHand, dealerSum):

        playerSum = self.Player.Hands[nmHand].getSum()
        self.Player.Hands[nmHand].Winner = 'Hand Lost!'
        if not playerSum > 21:
            if playerSum == 21 and len(self.Player.Hands[nmHand].cards) == 2 and dealerSum != 21:

                self.Player.addMoney(self.Bet * 2)
                self.Player.Hands[nmHand].Winner = 'Win!'
                return
            elif dealerSum > 21:
                if self.Player.Hands[nmHand].isDouble:
                    self.Player.addMoney(self.Bet * 4)
                else:
                    self.Player.addMoney(self.Bet)

                self.Player.Hands[nmHand].Winner = 'Win!'
                return
            elif dealerSum == playerSum:
                if self.Player.Hands[nmHand].isDouble:
                    self.Player.addMoney(self.Bet)
                else:
                    self.Player.addMoney(self.Bet / 2)

                self.Player.Hands[nmHand].Winner = 'Tie!'
                return
            elif dealerSum < playerSum:

                if self.Player.Hands[nmHand].isDouble:
                    self.Player.addMoney(self.Bet * 4)
                else:
                    self.Player.addMoney(self.Bet)
                self.Player.Hands[nmHand].Winner = 'Win!'
        return


g = Game2()
g.run()
