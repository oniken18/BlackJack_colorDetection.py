class Player:

    def __init__(self, name, money):
        self.Hands = []
        self.Name = name
        self.Money = money

    def addMoney(self, bet):
        self.Money = self.Money + (bet * 2)

    def reduceMoney(self, bet):
        self.Money = self.Money - bet
