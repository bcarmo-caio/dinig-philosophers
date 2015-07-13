#!/usr/bin/env python3

import threading
from random import *
import time
import sys

eatingTime = .1

# monitor defs
IN_USE = 0
CONDITION = 1
QUEUE_SIZE = 2

class Monitor: 
    def __init__(self, numberOfPhilosophers, ration):
        self.lock = threading.Lock()
        self.ration = ration
        self.chopsticks = ([], [], [])
        for i in range(numberOfPhilosophers):
            self.chopsticks[IN_USE].append(False)
            self.chopsticks[CONDITION].append(threading.Condition())
            self.chopsticks[QUEUE_SIZE].append(0)

    def GetChopstick(self, chopstick):
        self.lock.acquire(True)
        if (self.chopsticks[IN_USE])[chopstick] == False:
            (self.chopsticks[IN_USE])[chopstick] = True
            self.lock.release()
        else:
            self.wait(chopstick)

    def wait(self, cs):
        self.chopsticks[CONDITION][cs].acquire(True)
        self.chopsticks[QUEUE_SIZE][cs] += 1
        self.lock.release()
        self.chopsticks[CONDITION][cs].wait()
        self.chopsticks[CONDITION][cs].release()

    def PutChopstick(self, chopstick):
        self.lock.acquire(True)
        if self.chopsticks[QUEUE_SIZE][chopstick] == 0:
            self.chopsticks[IN_USE][chopstick] = False
        else:
            self.signal(chopstick)
        self.lock.release()

    def signal(self, cs):
        self.chopsticks[CONDITION][cs].acquire(True)
        self.chopsticks[QUEUE_SIZE][cs] -= 1
        self.chopsticks[CONDITION][cs].notify()
        self.chopsticks[CONDITION][cs].release()

    def MayEat(self):
        self.lock.acquire(True)
        if self.ration > 0:
            self.ration -= 1
            self.lock.release()
            return True
        else:
            self.lock.release()
            return False

    def HasFood(self):
        self.lock.acquire(True)
        rationsLeft = self.ration
        self.lock.release()
        return rationsLeft


class Philosopher:
    def __init__(self, _id, weight, rationsToEat):
        self._id = _id
        self.weight = weight
        self.rationsEaten = 0
        self.rationsToEat = rationsToEat
        
        if self._id % 2:
            self.firstChopstick  = _id
            self.secondChopstick = ((_id + 1) % numberOfPhilosophers)
        else:
            self.firstChopstick  = ((_id + 1) % numberOfPhilosophers)
            self.secondChopstick = _id

        threads.append(threading.Thread(target = self.PhilThread))
        threads[-1].start()

    def PhilThread(self):
        while True:
            if simulationMode == 'P':
                if self.rationsToEat == self.rationsEaten:
                    if philophersGoHome == True:
                        rationsPerPhilosopher[self._id] = self.rationsEaten
                        break
                    else:
                        time.sleep(.005)
                        continue
            self.Think()
            monitor.GetChopstick(self.firstChopstick)
            monitor.GetChopstick(self.secondChopstick)
            if monitor.MayEat() == True:
                print("Filosofo ", "{:0>5d} ".format(self._id),
                        "comecou a comer em   ", time.time() - start_time)
                self.Eat()
                print("Filosofo ", "{:0>5d} ".format(self._id),
                        "terminou de comer em ", time.time() - start_time)
                self.rationsEaten += 1
            monitor.PutChopstick(self.firstChopstick)
            monitor.PutChopstick(self.secondChopstick)
            if philophersGoHome == True:
                rationsPerPhilosopher[self._id] = self.rationsEaten
                break
        return

    def Think(self):
        sleeping = random()
        if sleeping > 0.1:
            sleeping -= 0.1
        time.sleep(sleeping)

    def Eat(self):
        time.sleep(eatingTime)

def main():
    global simulationMode, monitor, numberOfPhilosophers, philophersGoHome
    global rationsPerPhilosopher, simulationMode, threads
    fp = open(sys.argv[1], 'r')
    ration = int(sys.argv[2])
    numberOfPhilosophers = int(fp.readline()[:-1])
    weight = fp.readline()[:-1].split()
    fp.close()
    simulationMode = sys.argv[3]

    monitor = Monitor(numberOfPhilosophers, ration)
    philosophers = []
    philophersGoHome = False
    rationsPerPhilosopher = [None] * numberOfPhilosophers

    totalWeight = 0
    for i in range(numberOfPhilosophers):
        totalWeight += int(weight[i])

    rationsToBeEatenPerPhilosopher = []
    for i in range(numberOfPhilosophers):
        rationsToBeEatenPerPhilosopher.append(int(ration * (int(weight[i]) / totalWeight)))

    #some rations may be left. Redistributing them
    totalDistributed = 0
    for i in range(numberOfPhilosophers):
        totalDistributed += rationsToBeEatenPerPhilosopher[i]

    rationsLeftToDistribute = ration - totalDistributed
    for i in range(rationsLeftToDistribute):
        rationsToBeEatenPerPhilosopher[i] += 1

    threads = []
    for i in range(numberOfPhilosophers):
        philosophers.append(Philosopher(i, int(weight[i]),
            rationsToBeEatenPerPhilosopher[i]))

    while philophersGoHome == False:
        time.sleep(1)
        if not monitor.HasFood():
            philophersGoHome = True
            for i in range(numberOfPhilosophers):
                threads[i].join()

    for i in range(numberOfPhilosophers):
        print("Filosofo ", "{:0>5d}".format(i), "comeu ", "{:0>5d} ".format(rationsPerPhilosopher[i]), "porcoes")

    del threads, philosophers, monitor, weight, rationsPerPhilosopher

if __name__ == '__main__':
    global start_time
    start_time = time.time()
    main()
    quit(0)
