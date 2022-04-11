import cvxpy as cp
import numpy as np

from canonicOp import CanonicMonome, simplify
import itertools

def reduce_monome_list(monomeList, playersOperators, monomeSize=None):
    print("Before simplify {} monomes: {}.".format(len(monomeList), monomeList))
    monomeList = set(map(lambda x: tuple(simplify(x, playersOperators, monomeSize)), monomeList))
    monomeList = list(map(lambda x: list(x), monomeList))
    monomeList.sort()
    print("after simplify {} monomes: {}".format(len(monomeList), monomeList))

    return monomeList


class Hierarchie:
    """
    Class for the implementation of the modified NPA's hierarchy.
    """

    def __init__(self, game, operatorsPlayers, level = 1, other_monomes=None):
        self.game = game
        self.level = level
        # Creation of the list of monomials.
        self.operatorsPlayers = operatorsPlayers
        monomeList = [list(s) for s in itertools.product(*operatorsPlayers)] # 1 + AB + AC + BC + ABC
        self.monomeList = reduce_monome_list(monomeList, operatorsPlayers)

        if level == 2:
            for player in range(self.game.nbPlayers):
                assert(self.game.nbPlayers == 3) # changer pour 5 joueurs
                self.monomeList += [list(s) for s in itertools.product(operatorsPlayers[player], operatorsPlayers[player], [0])] # AA'
            self.monomeList = reduce_monome_list(self.monomeList, operatorsPlayers)

        if level == 3:
            monomes = [list(s) for s in itertools.product(list(range(2 * self.game.nbPlayers + 1)), repeat=self.game.nbPlayers)] #0....2*nbPlayer
            self.monomeList = reduce_monome_list(monomes, operatorsPlayers)

        if level == 6:
            #Add lvl 3 monomes
            monomes = [list(s) for s in itertools.product(list(range(2 * self.game.nbPlayers + 1)), repeat=self.game.nbPlayers)] #0....2*nbPlayer

            #Add lvl 6
            ops = itertools.chain(*zip(operatorsPlayers, operatorsPlayers)) # [ops1, ops1, ops2, ops2, ops3, ops3....] => AA'BB'CC'
            monomes += [list(s) for s in itertools.product(*ops)]
            self.monomeList = reduce_monome_list(monomes, operatorsPlayers, monomeSize=6)

        if other_monomes != None:
            assert(type(other_monomes) == list)
            size = max(map(lambda mon: len(mon), other_monomes))
            self.monomeList += other_monomes
            self.monomeList = reduce_monome_list(self.monomeList, operatorsPlayers, monomeSize=size)


        self.n = len(self.monomeList)
        print(self.n)
        # Dict for reducing the numbers of SDP variables.
        self.variableDict = {}
        self.variablePosition = {}

        # Constraints and SDP variables.
        self.constraints = []
        self.X = cp.bmat(self.init_variables())
        self.constraints += [self.X >> 0] #SDP
        self.constraints += [self.X[0][0] == 1] #Normalization

        # Objectif function and cvxpy problem.
        self.objectifFunc = self.objectifFunctions(game)
        self.prob = cp.Problem(cp.Maximize(cp.sum(self.X[0] @ cp.bmat(self.objectifFunc))), self.constraints)


    def updateProb(self):
        """
        Function which update the cvxpy problem.
        """
        self.prob = cp.Problem(cp.Maximize(cp.sum(self.X[0] @ cp.bmat(self.objectifFunc))), self.constraints)

    def projectorConstraints(self):
        '''
        Create the matrix filled with the canonic representation of each element of the moment matrix.
        '''
        matrix = np.zeros((self.n, self.n))
        variableId = 0

        for i, Si in enumerate(self.monomeList):
            for j, Sj in enumerate(self.monomeList):
                var = CanonicMonome(self.monomeList, i, j, self.operatorsPlayers)

                if var not in self.variableDict:
                    # If no other element as the same canonic representation has *var*, a new SDP variable will be created.
                    self.variableDict[var] = variableId
                    self.variablePosition[variableId] = (i, j)
                    variableId += 1

                matrix[i][j] = self.variableDict[var]

        return matrix

    def init_variables(self):
        """
        Initialise the cvxpy variables.
        """
        matrix = self.projectorConstraints()
        variablesDict = {}
        variable = [[None for i in range(self.n)] for j in range(self.n)]

        for line in range(self.n):
            for column in range(self.n):

                varId = matrix[line][column]
                if varId not in variablesDict:
                    # One variable for each canonic element of the matrix of moments.
                    variablesDict[varId] = cp.Variable()

                variable[line][column] = variablesDict[varId]

        return variable


    def setNashEqConstraints(self):
        '''
        Creation of the set of Nash Equilibrium constraint.
        '''
        for playerId in range(self.game.nbPlayers):

            payoutVec = []  # Payout if he follow advice
            for question in self.game.questions():
                for validAnswer in self.game.validAnswerIt(question):
                    payoutVec.append(self.genVecPlayerPayoutWin(validAnswer, question, playerId))

            payoutVec = self.game.questionDistribution * np.array(payoutVec).transpose()

            # Payout for strat which diverge from advice
            for type in ['0', '1']:
                for noti in ['0', '1']:
                    payoutVecNot = []
                    for question in self.game.questions():
                        #Answers where the player doesn't defect from its advice
                        untouchedAnswers = lambda answer: question[playerId] != type or answer[playerId] != noti

                        #Answers where the player defect from its advice
                        notAnswers = lambda answer: question[playerId] == type and answer[playerId] == noti

                        # if he is not involved, the set of accepted answer is the same
                        if playerId not in self.game.involvedPlayers(question):
                            #The player is not involved, the set of accepted question stay the same
                            for validAnswer in filter(untouchedAnswers, self.game.validAnswerIt(question)):
                                payoutVecNot.append(self.genVecPlayerPayoutWin(validAnswer, question, playerId))

                            for validAnswer in filter(notAnswers, self.game.validAnswerIt(question)):
                                payoutVecNot.append(self.genVecPlayerNotPayoutWin(validAnswer, question, playerId))

                        #The player is involved. He loose on the accepted answer where he defect. But some rejected answers
                        #are now accepted.
                        else:
                            for validAnswer in filter(untouchedAnswers, self.game.validAnswerIt(question)):
                                payoutVecNot.append(self.genVecPlayerPayoutWin(validAnswer, question, playerId))

                            for validAnswer in filter(notAnswers, self.game.wrongAnswerIt(question)):
                                payoutVecNot.append(self.genVecPlayerNotPayoutWin(validAnswer, question, playerId))

                    payoutVecNot = self.game.questionDistribution * np.array(payoutVecNot).transpose()
                    self.constraints.append(cp.sum(self.X[0] @ cp.bmat((payoutVec - payoutVecNot))) >= 0)

        self.updateProb()


    def genVec(self, answer, question):
        '''
        Generate the encoding vector to get the probability of the answer given the question.
        '''
        assert(len(answer) == len(question) == self.game.nbPlayers)

        vec = [0] * len(self.monomeList)

        operator = []
        for p in range(self.game.nbPlayers):
            #the flag is negative if the player answer 1, positive otherwise.
            flag = -2 * (answer[p] == "1") + 1

            if question[p] == "1":
                operator.append(flag * (p + 1) * 2)
            else:
                operator.append(flag * (p * 2 + 1))

        op_size = len(self.monomeList[0])
        while len(operator) != op_size:
            operator.append(0)

        def recursiveFunc(operator, coef):
            #The operator is in the matrix
            operator = simplify(operator, self.operatorsPlayers)
            if operator in self.monomeList:
                vec[self.monomeList.index(operator)] = coef

            #There is a negative number as operator (the player answer 1)
            else:
                #We find the negative operator
                negIdx = next(idx for idx, x in enumerate(operator) if x < 0)

                opId = operator.copy()
                opId[negIdx] = 0
                op2 = operator.copy()
                op2[negIdx] = - op2[negIdx]

                #P(101|111) = P(I01|111) - P(OO1|111)
                recursiveFunc(opId, coef)
                recursiveFunc(op2, -coef)

        recursiveFunc(operator, 1)
        return vec

    def genVecPlayerPayoutWin(self, answer, question, playerdId):
        """
        Return the vector with which to multiply the first row of X to have the payout of a player.
        """
        coef = self.game.playerPayoutWin(answer, playerdId)
        return list(map(lambda x: x * coef, self.genVec(answer, question)))

    def genVecPlayerNotPayoutWin(self, answer, question, playerdId):
        """
        Payout of a player, if he defect from its advice.
        """
        coef = self.game.notPlayerPayoutWin(answer, playerdId)
        return list(map(lambda x: x * coef, self.genVec(answer, question)))

    def genVecWelfareWin(self, answer, question):
        """
        Mean payout of all player.
        """
        coef = self.game.answerPayoutWin(answer)
        return list(map(lambda x: x * coef, self.genVec(answer, question)))

    def objectifFunctions(self, game):
        """
        The objectif function is the social welfare.
        """
        objectifFunctionPayout = []

        for question in game.questions():
            for validAnswer in game.validAnswerIt(question):
                objectifFunctionPayout.append(self.genVecWelfareWin(validAnswer, question))

        objectifFunction = self.game.questionDistribution * np.array(objectifFunctionPayout).transpose()

        return objectifFunction

    def optimize(self, verbose, warmStart, solver):
        """
        Optimize on a given solver.
        """
        assert(solver == "SCS" or solver == "MOSEK")
        if solver == "SCS":
            self.prob.solve(solver=cp.SCS, verbose=verbose, warm_start=warmStart)
        else:
            self.prob.solve(solver=cp.MOSEK, verbose=verbose, warm_start=warmStart)
        return self.prob.value
