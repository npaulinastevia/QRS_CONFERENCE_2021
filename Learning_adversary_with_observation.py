
import os, sys, random, operator
import numpy as np
import statistics
import pandas as pd
import random
from csv import writer,reader
import csv
import matplotlib.pyplot as plt
from pysmt.shortcuts import Symbol, LE, GE, Int, And, Equals, Plus, Solver
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, And, Not, is_sat, GE, Int, TRUE, Equals, Or, FALSE, is_valid, Times, LE, Bool


class Environment:

    def __init__(self, Ny=6, Nx=6):

        self.Ny = Ny
        self.Nx = Nx
        self.state_dim = (Ny, Nx)
        self.state = (0, 0)
        self.stateA = (0, 0)

        self.action_dim = (4,)
        self.action_dict = {"up": 0, "right": 1, "down": 2, "left": 3}

        self.action_coords = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        self.R = self._build_rewards()

        self.obs_dict = {0:(0,0),1:(0,1), 2:(0,2), 3:(0,3),4:(0,4),5:(0,5),
                          6:(1, 0),  7:(1, 1),  8:(1, 2),  9:(1, 3),  10:(1, 4),  11:(1, 5),
                          12:(2, 0), 13:(2, 1),  14:(2, 2),  15:(2, 3),  16:(2, 4),  17:(2, 5),
                          18:(3, 0),  19:(3, 1),  20:(3, 2),  21:(3, 3),  22:(3, 4),  23:(3, 5),
                          24:(4, 0),  25:(4, 1),  26:(4, 2),  27:(4, 3),  28:(4, 4),  29:(4, 5),
                          30:(5, 0),  31:(5, 1),  32:(5, 2),  33:(5, 3),  34:(5, 4),  35:(5, 5),
                         }
        self.rew_dict = {(0, 0):0.3, (0, 1):0.4, (0, 2):0.4, (0, 3):0.4, (0, 4):0.5, (0, 5):0.3,
                         (1, 0):0.4, (1, 1):0.5, (1, 2):0.5, (1, 3):0.4, (1, 4):0.5, (1, 5):0.4,
                         (2, 0):0.3, (2, 1):0.5, (2, 2):0.5, (2, 3):0.5, (2, 4):0.5, (2, 5):0.4,
                         (3, 0):0.3, (3, 1):0.4, (3, 2):0.5, (3, 3):0.5, (3, 4):0.5, (3, 5):0.4,
                         (4, 0):0.4, (4, 1):0.5, (4, 2):0.5, (4, 3):0.4, (4, 4):0.4, (4, 5):0.5,
                         (5, 0):0.3, (5, 1):0.3, (5, 2):0.4, (5, 3):0.5, (5, 4):0.5, (5, 5):0.1,
                         }
        self.obs_dictIn = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4, (0, 5): 5,
                           (1, 0): 6, (1, 1): 7, (1, 2): 8, (1, 3): 9, (1, 4): 10, (1, 5): 11,
                           (2, 0): 12, (2, 1): 13, (2, 2): 14, (2, 3): 15, (2, 4): 16, (2, 5): 17,
                           (3, 0): 18, (3, 1): 19, (3, 2): 20, (3, 3): 21, (3, 4): 22, (3, 5): 23,
                           (4, 0): 24, (4, 1): 25, (4, 2): 26, (4, 3): 27, (4, 4): 28, (4, 5): 29,
                           (5, 0): 30, (5, 1): 31, (5, 2): 32, (5, 3): 33, (5, 4): 34, (5, 5): 35,
                           }


    def reset(self):

        self.state = (0, 0)
        return self.state

    def resetA(self):

        self.stateA = (0, 0)
        return self.stateA

    def step(self, action,actionA):

        state_next = (self.state[0] + self.action_coords[action][0],
                      self.state[1] + self.action_coords[action][1])
        state_nextA = (self.stateA[0] + self.action_coords[actionA][0],
                       self.stateA[1] + self.action_coords[actionA][1])

        self.R = self._build_rewards()



        reward = self.R[self.state + (action,)]


        rewA = 0


        self.state = state_next
        self.stateA=state_nextA
        done = (state_next[0] == self.Ny - 1) and (state_next[1] == self.Nx - 1)
        return state_next,state_nextA, reward, done,rewA,self.stateA



    def allowed_actions(self):

        actions_allowed = []
        actions_allowedA=[]
        y, x = self.state[0], self.state[1]
        w,z=self.stateA[0], self.stateA[1]
        if (w > 0):
            actions_allowedA.append(self.action_dict["up"])
        if (w < self.Ny - 1):
            actions_allowedA.append(self.action_dict["down"])
        if (z > 0):
            actions_allowedA.append(self.action_dict["left"])
        if (z < self.Nx - 1):
            actions_allowedA.append(self.action_dict["right"])


        if (y > 0):
            actions_allowed.append(self.action_dict["up"])
        if (y < self.Ny - 1):
            actions_allowed.append(self.action_dict["down"])
        if (x > 0):
            actions_allowed.append(self.action_dict["left"])
        if (x < self.Nx - 1):
            actions_allowed.append(self.action_dict["right"])

        actions_allowed = np.array(actions_allowed, dtype=int)
        actions_allowedA = np.array(actions_allowedA, dtype=int)
        return actions_allowed,actions_allowedA

    def _build_rewards(self):

        r_goal = 100  # reward for arriving at terminal state (bottom-right corner)
        r_nongoal = -1  # penalty for not reaching terminal state


        R = r_nongoal * np.ones(self.state_dim + self.action_dim, dtype=float)  # R[s,a]

        R[self.Ny - 2, self.Nx - 1, self.action_dict["down"]] = 100 # arrive from above

        R[self.Ny - 1, self.Nx - 2, self.action_dict["right"]] = 100 # arrive from the left


        return R


class Agent:

    def __init__(self, env):

        self.state_dim = env.state_dim
        self.action_dim = env.action_dim

        self.epsilon = 1
        self.epsilon_decay = 0.3
        self.beta = 0.01
        self.gamma = 0.95
        self.Q = np.zeros(self.state_dim + self.action_dim, dtype=float)
        self.QObs = np.zeros(self.state_dim + self.action_dim, dtype=float)
        self.QObsA = np.zeros(self.state_dim + self.action_dim, dtype=float)
        self.QA = np.zeros(self.state_dim + self.action_dim, dtype=float)


    def get_action(self, env):

        x,y=env.allowed_actions()
        state = env.state
        stateA = env.stateA
        obs=0
        ran=0
        obsA=0
        ranA=0
        stateA = env.stateA
        if random.uniform(0, 1) < self.epsilon:
            # explore
            actA = np.random.choice(y)
            ranA=1
        else:

            actions_allowedA = y
            Q_sA = self.QA[stateA[0], stateA[1], actions_allowedA]
            actions_greedyA = actions_allowedA[np.flatnonzero(Q_sA == np.max(Q_sA))]
            actA = np.random.choice(actions_greedyA)


        if random.uniform(0, 1) < self.epsilon:
            # explore
            act=np.random.choice(x)
            actP=act

            ran=1

        else:

            actions_allowed = x

            Q_s = self.Q[state[0], state[1], actions_allowed]
            actions_greedy = actions_allowed[np.flatnonzero(Q_s == np.max(Q_s))]
            act=np.random.choice(actions_greedy)
            actP=act




        if (state[0] + env.action_coords[act][0] == stateA[0] + env.action_coords[actA][0] and state[1] +
                        env.action_coords[act][1] == stateA[1] + env.action_coords[actA][1] and ran==0):
                    saa = state + (act,)

                    saaN = (state[0] + env.action_coords[act][0], state[1] + env.action_coords[act][1])
                    saaAd = (stateA[0] + env.action_coords[actA][0], stateA[1] + env.action_coords[actA][1])
                    self.QObs[saa] += self.beta * (
                            -100 + self.gamma * np.max(self.QObs[saaN]) - self.QObs[saa])

                    obs = 1


        if (stateA[0] + env.action_coords[actA][0] == state[0] + env.action_coords[actP][0] and stateA[1] +
                        env.action_coords[actA][1] == state[1] + env.action_coords[actP][1] and ranA==0):
                    saad = stateA + (actA,)

                    saaNd = (stateA[0] + env.action_coords[actA][0], stateA[1] + env.action_coords[actA][1])
                    self.QObsA[saad] += self.beta * (
                            100 + self.gamma * np.max(self.QObsA[saaNd]) - self.QObs[saad])

                    obsA = 1
        if obs == 1 and ran==0:
            Q_s = self.QObs[state[0], state[1], actions_allowed]
            actions_greedy = actions_allowed[np.flatnonzero(Q_s == np.max(Q_s))]
            act = np.random.choice(actions_greedy)
        if obsA == 1 and ranA==0:
            Q_sA = self.QObsA[stateA[0], stateA[1], actions_allowedA]
            actions_greedyA = actions_allowedA[np.flatnonzero(Q_sA == np.max(Q_sA))]
            actA = np.random.choice(actions_greedyA)

        return act,actA



    def train(self, memory):

        (state, action, state_next, reward, done,stateA,actionA,state_nextA,rewA) = memory
        sa = state + (action,)
        sad=stateA + (actionA,)


        self.Q[sa] += self.beta * (reward + self.gamma * np.max(self.Q[state_next]) - self.Q[sa])
        self.QObs[sa] += self.beta * (reward + self.gamma * np.max(self.QObs[state_next]) - self.QObs[sa])
        self.QA[sad] += self.beta * (rewA + self.gamma * np.max(self.QA[state_nextA]) - self.QA[sad])
        self.QObsA[sad] += self.beta * (rewA + self.gamma * np.max(self.QObsA[state_nextA]) - self.QObsA[sad])

        return state,stateA




    def display_greedy_policy(self):
        # greedy policy = argmax[a'] Q[s,a']
        greedy_policy = np.zeros((self.state_dim[0], self.state_dim[1]), dtype=int)
        greedy_policyA = np.zeros((self.state_dim[0], self.state_dim[1]), dtype=int)
        for x in range(self.state_dim[0]):
            for y in range(self.state_dim[1]):
                greedy_policy[y, x] = np.argmax(self.Q[y, x, :])
        for x in range(self.state_dim[0]):
            for y in range(self.state_dim[1]):
                greedy_policyA[y, x] = np.argmax(self.QA[y, x, :])

        print(greedy_policy)
        print('attacker')
        print(greedy_policyA)



# Settings
class Learn:
    def debut(self):
        env = Environment(Ny=6, Nx=6)

        agent = Agent(env)
        action_coords = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.obs_dict = {0: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3), 4: (0, 4), 5: (0, 5),
                         6: (1, 0), 7: (1, 1), 8: (1, 2), 9: (1, 3), 10: (1, 4), 11: (1, 5),
                         12: (2, 0), 13: (2, 1), 14: (2, 2), 15: (2, 3), 16: (2, 4), 17: (2, 5),
                         18: (3, 0), 19: (3, 1), 20: (3, 2), 21: (3, 3), 22: (3, 4), 23: (3, 5),
                         24: (4, 0), 25: (4, 1), 26: (4, 2), 27: (4, 3), 28: (4, 4), 29: (4, 5),
                         30: (5, 0), 31: (5, 1), 32: (5, 2), 33: (5, 3), 34: (5, 4), 35: (5, 5),
                         }
        self.obs_dictIn = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4, (0, 5): 5,
                           (1, 0): 6, (1, 1): 7, (1, 2): 8, (1, 3): 9, (1, 4): 10, (1, 5): 11,
                           (2, 0): 12, (2, 1): 13, (2, 2): 14, (2, 3): 15, (2, 4): 16, (2, 5): 17,
                           (3, 0): 18, (3, 1): 19, (3, 2): 20, (3, 3): 21, (3, 4): 22, (3, 5): 23,
                           (4, 0): 24, (4, 1): 25, (4, 2): 26, (4, 3): 27, (4, 4): 28, (4, 5): 29,
                           (5, 0): 30, (5, 1): 31, (5, 2): 32, (5, 3): 33, (5, 4): 34, (5, 5): 35,
                           }

        # Train agent
        print("\nTraining agent...\n")

        #df = pd.DataFrame(list())
        #df.to_csv('statProb.csv')
        #List = ['episode Number', 'ProbCollision', 'observation', 'adversaryPosition','collision per episode']
        List = ['episode Number', 'collision per episode']

        # Open our existing CSV file in append mode
        # Create a file object for this file
        file = open('statProb1.csv', 'w', newline='')
        with file:
            # identifying header
            header = ['episode Number','Cumulative reward per episode', 'collision per episode','Cumulative reward per episode of adv']
            writer = csv.DictWriter(file, fieldnames=header)

            # writing data row-wise into the csv file
            writer.writeheader()
        #with open('statProb.csv', 'a+') as f_object1:

            # Pass this file object to csv.writer()
            # and get a writer object
            #writer_object1 = writer(f_object1)

            # Pass the list as an argument into
            # the writerow()
            #writer_object1.writerow(List)

            # Close the file object
            #f_object1.close()
        N_episodes = 2000
        A = []
        E = []
        R = []

        ES = []
        cumR = []
        cumRA = []
        num = 0
        nbColl = []

        nj=0
        h=0


        InitAPos=(5,4)
        self.MylistofProb = np.zeros((6, 6))
        self.MylistofColl = np.zeros((6, 6))
        self.MylistofNonColl = np.zeros((6, 6))

        listAdv = [(5, 4), (4, 4), (4, 5)]
        advPos = listAdv[0]
        cumReward=0
        cumRewardA = 0
        elf=0
        for episode in range(N_episodes):

            # Generate an episode

            x=episode%50000
            ob = []


            #if x==0:
                #print(episode,j)
                #A.append(j)
            iter_episode, reward_episode = 0, 0
            reward_episodeA = 0
            state = env.reset()  # starting state
            #state = env.state
            #stateA = env.state
            #env.R = env._build_rewards()
            stateA = env.resetA()


            E.append(episode + num)
            ES.append(1)
            j=0
            while True:

                #for elt in range(4):

                    #if (state[0]+action_coords[elt][0]==stateA[0] and state[1]+action_coords[elt][1]==stateA[1]):
                        #env.R[state[0], state[1], elt] = -100

                # evolve state by action
                #r = reader(open('statProb.csv'))  # Here your csv file
                #lines = list(r)

                #saa=state+(action,)
                #print(state,stateA,saa)
                #print(agent.Q)
                action, actionA = agent.get_action(env)
                # A.append(actionA)

                state_next, state_nextA, reward, done, rewA, stateAdv = env.step(action, actionA)
                state = state_next

                stateA = state_nextA
                if state == stateA and state!=(0,0):

                    reward = -100

                    rewA = 100

                # train agent
                # print(state_next, reward)
                # print(self.MylistofNonColl,'coll',self.MylistofColl)
                agent.train((state, action, state_next, reward, done, stateA, actionA, state_nextA, rewA))
                if state == stateA and state!=(0,0):

                    j=j+1

                    self.MylistofColl[state[0]][state[1]]+=1

                    for z in range(6):
                        for w in range(6):

                            if self.MylistofColl[z][w] == 0 and self.MylistofNonColl[z][w] == 0:
                                self.MylistofProb[z][w] = 0

                            elif self.MylistofColl[z][w] > self.MylistofNonColl[z][w]:

                                self.MylistofProb[z][w] = 1

                            elif self.MylistofNonColl[z][w] == 0:

                                self.MylistofProb[z][w] = 1

                            elif self.MylistofColl[z][w] < self.MylistofNonColl[z][w]:

                                self.MylistofProb[z][w] = self.MylistofColl[z][w] / self.MylistofNonColl[z][w]

                            else:

                                self.MylistofProb[z][w] = self.MylistofColl[z][w] / self.MylistofNonColl[z][w]








                else:
                    self.MylistofNonColl[state[0]][state[1]] += 1
                    for z in range(6):
                        for w in range(6):

                            if self.MylistofColl[z][w] == 0 and self.MylistofNonColl[z][w] == 0:
                                self.MylistofProb[z][w] = 0

                            elif self.MylistofColl[z][w] > self.MylistofNonColl[z][w]:

                                self.MylistofProb[z][w] = 1

                            elif self.MylistofNonColl[z][w] == 0:

                                self.MylistofProb[z][w] = 1

                            elif self.MylistofColl[z][w] < self.MylistofNonColl[z][w]:

                                self.MylistofProb[z][w] = self.MylistofColl[z][w] / self.MylistofNonColl[z][w]

                            else:

                                self.MylistofProb[z][w] = self.MylistofColl[z][w] / self.MylistofNonColl[z][w]

                    #print(episode,self.MylistofProb)
                    nj = nj + 1



                # train agent


                #R.append(rewA)
                # R.append(reward_episodeA)


                iter_episode += 1

                reward_episode += reward
                cumReward += reward
                cumRewardA += rewA
                reward_episodeA += rewA

                if j>0:

                    break
                if (iter_episode > 100):
                    break
                if done:

                    break
                #if state_nextA == state_next:

                    # env.state=(0,0)






            Lst= [episode,reward_episode, int(j), reward_episodeA]
            #nbColl.append(j)

            file = open('statProb10.csv', 'a+', newline='')

            # writing the data into the file
            with file:
                write = csv.writer(file)
                write.writerow(Lst)


            h += 1
            if h<3:
                advPos= listAdv[h]

            if h==3:
                temp=listAdv[0]
                listAdv[0]=listAdv[2]
                listAdv[2]=temp
                h=0
            if agent.epsilon >= 0.001:
                agent.epsilon *= agent.epsilon_decay


Start=Learn()
Start.debut()


