class Hand:

    def __init__(self,cards):
        self.isBJ = False
        self.Winner = ''
        self.cards = cards
        self.isDouble = False

    def addCard(self, card):
        self.cards.append(card)

    def removeCard(self, card):
        self.cards.remove(card)

    def getSum(self):
        sumC = 0
        for i in range(len(self.cards)):
            cardVal = self.cards[i][0]
            if cardVal > 10:
                cardVal = 10
            sumC = sumC + cardVal

        for i in range(len(self.cards)):
            cardVal = self.cards[i][0]
            if cardVal == 1 and sumC +10 <=21:
                sumC = sumC + 10

        return sumC
