import requests
import pprint
import json
import time
import datetime
import pprint
import sys
import urllib
import urllib2
import json
import time
import datetime
import hmac, hashlib
import datetime
import time
import re
import os.path
import math
import copy
import random
from math import radians, cos, sin, asin, sqrt

global inf
inf = 999999999.9
global EliteFamily

#global firstTime
#firstTime = 0


def smallestDistance(targetLocation, unitLocations):
    shortestDistance = None
    for i in range(0, len(unitLocations)):
        if shortestDistance == None or shortestDistance > distance(targetLocation, unitLocations[i]):
            shortestDistance =  distance(targetLocation, unitLocations[i])
    return (shortestDistance)


'''class NavyUnit():
    def __init__(self, location, range):
        self.Location = location
        self.Range = range'''

class ServiceTypeUnit():
    def __init__(self, location, range, type, name, munitions):
        self.Locations = location
        self.Range = range
        self.Type = type #1 air force  #2 army  #3 navy
        self.Name = name
        self.Munitions = munitions

        self.Alive = True
        self.Dead = False

    def printt(self):
        print "   Unit: " + str(self.Name)
        for i in range(0, len(self.Locations) ):
            self.Locations[i].printt()
        print "        Range: " + str(self.Range)
        print ""



class Location():
    def __init__(self,latt,long):
        self.Latt = float(latt)
        self.Long = float(long)

    '''def __init__(self, location):
        self.latt = location.latt
        self.long = location.long'''

    def printt(self):
        print "      Lattitude: " + str(self.Latt) + " Longitude: " + str(self.Long)


class MunitionType():
    def __init__(self, name, platform, cost, range, cep, reliability, quantity, af, cdm, ct, fd, h, mrbm, rb, sr, ss, ssb, tc):
        self.Name = name
        self.Platform   = platform
        self.Cost = cost
        self.Range = range
        self.Cep = cep
        self.Reliability = reliability
        self.Quantity = quantity

        #MER Blast Radius for Each Type of Target
        self.AirField = af
        self.CoastalDefenseMissile = cdm
        self.CommunicationTower = ct
        self.FuelDepot = fd  #not used
        self.House = h   #Not used
        self.MRBM = mrbm
        self.RocketBattery = rb
        self.SAMRadar = sr
        self.SAMSite = ss
        self.StorageSiteBuilding  = ssb
        self.TroopCivilian = tc
        self.TerroristTrainingCamp = tc




class Target():
    def __init__(self, name, location, mobile, targetType, radius, popDens):

        self.Name = name

        self.Location = Location(location.Latt, location.Long)
        self.Mobile = mobile
        self.TargetType = targetType
        self.Radius = float(radius)

        self.Area = math.pow(radius, 2)*3.141

        self.Destroyed = False
        self.PopDensity = float(popDens)
        self.whoAssigned = None
        self.ServicesAssigned = []
        self.Assigned = False
        self.inRangeof = []


        #for quantifying effectiveness
        #operational Effectiveness
        self.NumAirCraftLost = 0.0
        self.MunitionsUsed = []

             #Cost of Stategy
        self.MunitionCost = 0.0
        self.DownedAirCraftCost = 0.0

        #Collateral Damage
        self.NumOfCasulties = 0.0



    def printt(self):
        print "Target: " + self.Name + " @ Location: " + str(self.Location.Latt) + " " + str(self.Location.Long)
        #self.Location.printt()
        print "   Assigned to Target: " + str( self.whoAssigned.Name )
        print "   Destroyed: " + str(self.Destroyed)
        print "   In Range of: "
        for i in range(0, len(self.inRangeof)):
            print "      " + str( self.inRangeof[i].Name)
        print "   Num Munitions Used: " + str( len(self.MunitionsUsed) )
        sys.stdout.write("      ")
        for i in range(0, len( self.MunitionsUsed)) :
            sys.stdout.write(" " + str(self.MunitionsUsed[i].Name))
        sys.stdout.write("\n")
        print "   Munition Cost " + str ( self.MunitionCost )
        print "   Downed Air Craft Cost: " + str( self.DownedAirCraftCost )
        print "   Number Of Casualties: " + str( int( self.NumOfCasulties) )


class Solution():
    def __init__(self, targets, cTargets):
        #array of destroyed targets
        self.Targets = targets
        self.CleanTargets = cTargets

        # ------------- Totals -------
        #Ops Effectivness
        self.TotNumAirCraftLost = 0.0
        self.TotMunitionsUsed = []
        #Cost
        self.TotMunitionCost = 0.0
        self.TotDownedAirCraftCost = 0.0
        #Collateral Damage
        self.TotNumOfCasualties = 0.0

        #------------- Scores -------------------
        self.OperationalEffectivenessScore = 0.0
        self.CostScore = 0.0
        self.CollateralDamageScore = 0.0
        self.TotalScore = 0.0
        self.WeightedScore = 0.0

    def printSolution(self):
        print "Solution: "
        print "   Assignments:"
        for i in range(0, len(self.Targets)):
            print self.Targets[i].printt()
        print "Total Score: " + str( self.TotalScore )
        print "Total Cost: " + str(  self.TotMunitionCost)

    def calculateScore(self):
        for t in range(0, len(self.Targets)):
            self.TotNumAirCraftLost = self.TotNumAirCraftLost + self.Targets[t].NumAirCraftLost
            self.TotMunitionsUsed = self.TotMunitionsUsed + self.Targets[t].MunitionsUsed
            self.TotMunitionCost += self.Targets[t].MunitionCost
            self.TotDownedAirCraftCost += self.Targets[t].DownedAirCraftCost
            self.TotNumOfCasualties += self.Targets[t].NumOfCasulties

        #Building Scores
        # I think we also need to assign weighting to the factors which make up a MOM
        #Right now it weights the use of 1 munition the same as the loss of an aircraft
        self.OperationalEffectivenessScore = self.TotNumAirCraftLost + len( self.TotMunitionsUsed )
        self.CostScore = self.TotMunitionCost + self.TotDownedAirCraftCost
        self.CollateralDamageScore = self.TotNumOfCasualties

        #TODO: make low cost better the score simple subtraction right now
        self.TotalScore = self.OperationalEffectivenessScore*float(.55) - self.CostScore*float(.1) + self.CollateralDamageScore*float(.35)
        self.WeightedScore = self.TotalScore/len(self.Targets)

        #print "Total Cost: " + str(self.TotMunitionCost)
        #print "Total Score: " + str(self.TotalScore)
        #print str(self.TotalScore)




class Family():
    def __init__(self):
        self.children = []
        self.HighestScore = -inf
        self.Child = 0
        self.SolutionNumber = 0
        self.HighestSolution = None


class Scenario():
    def __init__(self, targets, units, munitions, age):
        self.Targets = targets
        self.CleanTargets = None
        self.Units = units
        self.ServiceTypeUnit = units
        self.Munitions = munitions
        self.Solution = None
        self.SolutionSets = []
        self.Age = age
        self.PreviousCleanTargetState = None

    def printTopScenarioAssignments(self,num):
        top = -9999999
        location = 0

        for i in range(0, len(self.SolutionSets)):
            if top == -9999999:
                top = self.SolutionSets[i].TotalScore
                location = 0
            if top < self.SolutionSets[i].TotalScore:
                top = self.SolutionSets[i].TotalScore
                location = i

        ##### Not printing for space consumption
        #self.SolutionSets[location].printSolution()
        return self.SolutionSets[location]




    def findRandomAirForceUnitLocation(self):
        found = False
        iter = 0
        while found == False:
            iter = iter +1
            randAFUnit = random.randint(0,len(self.Units)-1)
            if self.Units[randAFUnit].Type == 1 and self.Units[randAFUnit].Dead == False :
                return randAFUnit
            if iter > 99999:
                print "Stuck in Finding Air Force Loop"

        #find for assignment
    def findRandomUnitLocation(self):
        found = False
        iter = 0
        while found == False:
            iter = iter +1
            randUnit = random.randint(0,len(self.Units)-1)
            if self.Units[randUnit].Dead == False :
                return randUnit
            if iter > 99999:
                print "Stuck in Finding a Unit"


    def firstTimeRandomAssignments(self):
        #for all targets
        for t in range(0, len(self.Targets)):

            #for all units in range of this target
            for i in range(0, len( self.Targets[t].inRangeof )):

                #if Mobile Target then Assign Random Air Force Unit
                if self.Targets[t].Mobile == True and self.Targets[t].Assigned == False :
                    self.Targets[t].whoAssigned = self.Units[self.findRandomAirForceUnitLocation()]
                    self.Targets[t].Assigned = True

                #assign random Unit to  target
                if self.Targets[t].Assigned == False:
                    self.Targets[t].whoAssigned = self.Units[self.findRandomUnitLocation()]
                    #self.Targets[t].ServicesAssigned =
                    self.Targets[t].Assigned = True

        #setting Previous state for clean targets with assignemnts
        self.PreviousCleanTargetState = copy.deepcopy(self.Targets)

        #for t in range(0, len(self.Targets)):
            #print self.Targets[t].printt()




    def AFAttack(self,t):
        #This is where we can perform complex math to figure probabilities for attacking this
        #target at this specific location

        DamageDone = 0.0
        airPlaneTrips = 0
        while self.Targets[t].Area > DamageDone:
            airPlaneTrips += 1
            randInt = random.randint(0,len( self.Targets[t].whoAssigned.Munitions  )-1)
            randMunition = self.Targets[t].whoAssigned.Munitions[randInt]
            #self.Targets[t].MunitionsUsed.append( randMunition )

            #Random Air Force shot Down:


            if self.Targets[t].TargetType == "AirField":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.AirField #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CoastalDefenseMissile":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CoastalDefenseMissile #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CommunicationTower":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CommunicationTower #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "FuelDepot":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.FuelDepot #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "House":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.House #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "MRBM":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.MRBM #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "RocketBattery":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.RocketBattery #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMRadar #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMSite":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMSite #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "StorageSiteBuilding":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.StorageSiteBuilding #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.TroopCivilian
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TroopCivilian #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "TerroristTrainingCamp":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TerroristTrainingCamp #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

        #It will end with target being destroyed

        ''' More Random Variance
        airPlaneTrips =  airPlaneTrips/4.0 #because 4-8 munitions per load
        planesDowned = random.randint(0, int(airPlaneTrips))
        self.Targets[t].NumAirCraftLost = planesDowned
        self.Targets[t].DownedAirCraftCost = 42360000.0*planesDowned
        '''

        #
        self.Targets[t].DownedAirCraftCost = airPlaneTrips*200




        self.Targets[t].Destroyed = True

    def ArmyAttack(self,t):
        #This is where we can perform complex math to figure probabilities for attacking this
        #target at this specific location

        DamageDone = 0.0
        while self.Targets[t].Area > DamageDone:
            randInt = random.randint(0,len( self.Targets[t].whoAssigned.Munitions  )-1)
            randMunition = self.Targets[t].whoAssigned.Munitions[randInt]
            #self.Targets[t].MunitionsUsed.append( randMunition )

            if self.Targets[t].TargetType == "AirField":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.AirField #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CoastalDefenseMissile":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CoastalDefenseMissile #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CommunicationTower":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CommunicationTower #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "FuelDepot":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.FuelDepot #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "House":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.House #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "MRBM":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.MRBM #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "RocketBattery":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.RocketBattery #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMRadar #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMSite":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMSite #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "StorageSiteBuilding":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.StorageSiteBuilding #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.TroopCivilian
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TroopCivilian #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "TerroristTrainingCamp":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TerroristTrainingCamp #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

        self.Targets[t].Destroyed = True

    def NavyAttack(self,t):
        #This is where we can perform complex math to figure probabilities for attacking this
        #target at this specific location

        DamageDone = 0.0
        while self.Targets[t].Area > DamageDone:
            randInt = random.randint(0,len( self.Targets[t].whoAssigned.Munitions  )-1)
            randMunition = self.Targets[t].whoAssigned.Munitions[randInt]
            #self.Targets[t].MunitionsUsed.append( randMunition )

            if self.Targets[t].TargetType == "AirField":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.AirField #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CoastalDefenseMissile":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CoastalDefenseMissile #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "CommunicationTower":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.CommunicationTower #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "FuelDepot":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.FuelDepot #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "House":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.House #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "MRBM":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.MRBM #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "RocketBattery":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.RocketBattery #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.CoastalDefenseMissile
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMRadar #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMSite":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.SAMSite #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

            if self.Targets[t].TargetType == "StorageSiteBuilding":
                DamageDone += randMunition.AirField
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.StorageSiteBuilding #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "SAMRadar":
                DamageDone += randMunition.TroopCivilian
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TroopCivilian #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition
            if self.Targets[t].TargetType == "TerroristTrainingCamp":
                DamageDone += randMunition.CommunicationTower
                self.Targets[t].MunitionsUsed.append(randMunition)
                self.Targets[t].MunitionCost += randMunition.Cost
                self.Targets[t].NumOfCasulties += self.Targets[t].PopDensity*.001*randMunition.TerroristTrainingCamp #change here
                self.Targets[t].whoAssigned.Munitions[randInt] = randMunition

        self.Targets[t].Destroyed = True


    def simulateAttacks(self):
        # for all targets
        for t in range(0, len(self.Targets)):
            #attack modeld by type of uint
            if ( self.Targets[t].whoAssigned.Type == 1 ):
                self.AFAttack(t)
            if (self.Targets[t].whoAssigned.Type == 2):
                self.ArmyAttack(t)
            if ( self.Targets[t].whoAssigned.Type == 3 ):
                self.NavyAttack(t)


    def checkAndCalculateScore(self):
        AssignedAndDestroyed = True
        count = 0
        solution1 = Solution(self.Targets, self.CleanTargets)
        for t in range(0, len(self.Targets)):
            if ( self.Targets[t].Assigned == False or self.Targets[t].Destroyed == False  ):
                AssignedAndDestroyed = False
                count += 1

        if ( AssignedAndDestroyed == True  ) :
            solution1.calculateScore()
            self.Solution = copy.deepcopy(solution1)
            self.SolutionSets.append(copy.deepcopy(self.Solution))
        else:
            print "Not All Targets are Assigned or Destoryed: " + str(count ) + " Not Assigned or Destroyed"


    def setFeasibleTargest(self):
        # update all targets with units they can be hit by with respect to unit Grand Range
        for t in range(0, len(self.Targets)):

            for i in range(0, len(self.Units)):
                distance2 = distance(self.Targets[t].Location, self.Units[i].Locations[0])
                #if distance(self.Targets[t].Location, self.Units[i].Locations[0]) <   self.Units[i].Range:
                    #self.Targets[t].inRangeof.append(self.Units[i])
                if smallestDistance(self.Targets[t].Location, self.Units[i].Locations ) < self.Units[i].Range:
                    self.Targets[t].inRangeof.append(self.Units[i])

            # print self.Targets[t].printt()


    def modifyAssignments(self):
        #Randomly change an assignment

        randTarget = random.randint(0, len(self.Targets) - 1)

        # for all units in range of this target
        for i in range(0, len(self.Targets[randTarget].inRangeof)):

            # assign random Unit to  target
            if self.Targets[randTarget].Assigned == True:
                self.Targets[randTarget].whoAssigned = self.Units[self.findRandomUnitLocation()]
                self.Targets[randTarget].Assigned = True


    def RandomMunitionAssignment(self, mutationRate):
        # for all targets
        for t in range(0, len(self.Targets)):

            # for all Service Units in range of this target
            for i in range(0, len(self.Targets[t].inRangeof)):

                # assign adequate random Munition to target
                if self.Targets[t].Assigned == False:
                    pass

                    self.Targets[t].whoAssigned = self.Units[self.findRandomUnitLocation()]
                    self.Targets[t].Assigned = True

        # setting Previous state for clean targets with assignemnts
        self.PreviousCleanTargetState = copy.deepcopy(self.Targets)

        for t in range(0, len(self.Targets)):
            print self.Targets[t].printt()

    '''
    def firstTimeRandomMunitionAssignments(self):
        for t in range(0, len(self.Targets)):
            for m in range(0, len( self.Targets.WhoAssigned )):
                airForce = False
                Army = False
                Navy = False
                if 1 == self.Targets.WhoAssigned[m].Type:
                    #air Force assigned pick random munition assignments
                    damagedArea = 0
                    while damagedArea < self.Targets[t].Area:
                        self.Targets[t].MunitionsAssigned = random.choice(self.Targets[t].  )
    '''


    def resetToPreviousCleanState(self):
        self.Targets = copy.deepcopy(self.PreviousCleanTargetState)
        self.Solution = None

    def setCleanState(self):
        self.CleanTargets = copy.deepcopy(self.Targets)

    def resetToHighestScore(self):
        highestScore = -99999999
        for i in range(0, len(self.SolutionSets)):
            if highestScore == -99999999 :
                highestScore = self.SolutionSets[i].TotalScore
                self.Targets = copy.deepcopy(self.SolutionSets[i].CleanTargets)
                self.CleanTargets = copy.deepcopy(self.SolutionSets[i].CleanTargets)
            if highestScore < self.SolutionSets[i].TotalScore:
                highestScore = self.SolutionSets[i].TotalScore
                self.Targets = copy.deepcopy(self.SolutionSets[i].CleanTargets)
                self.CleanTargets = copy.deepcopy(self.SolutionSets[i].CleanTargets)




    def runSim(self):

        #sets Targets based on Grand Ranges
        self.setFeasibleTargest()

        #first time - Random assignment
        self.firstTimeRandomAssignments()
        self.setCleanState()

        #first time - Random Munition Assignments
        #self.firstTimeRandomMunitionAssignments()

        #mutate the munitions and number assigned to a target
        #self.RandomMunitionAssignment(1)

        #setting previous State
        #self.PreviousState = copy.deepcopy(self.Targets)

        #Simulate Attacks
        self.simulateAttacks()

        #Calculate Score after attacks
        self.checkAndCalculateScore()

        for i in range(0, self.Age):
            #Load Previous State
            self.resetToHighestScore()
            #self.resetToPreviousCleanState()

            #Modify Assignments
            self.modifyAssignments()

            # Simulate Attacks
            self.simulateAttacks()

            # Calculate Score after attacks
            self.checkAndCalculateScore()


        #for i in range(0, len(self.SolutionSets)):
        #   print str(i) + " " + str( self.SolutionSets[i].TotalScore/10000.0 )
        return self.printTopScenarioAssignments(1) #used for returning now







def distance(Location1, Location2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1 = float(0.00)
    lat1 = float(0.00)
    lon2 = float(0.00)
    lat2 = float(0.00)
    lon1 = Location1.Long
    lat1 = Location1.Latt
    lon2 = Location2.Long
    lat2 = Location2.Latt
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # 6371 km is the radius of the Earth
    km = 6371 * c
    return km

def readInMunitions():
    pass

    # Read in from files
    #f = open('Munitions.csv', 'a', 0)



def main():
    global inf
    global EliteFamily
    #Read in from files
    #f = open('OfficialRates2.csv', 'a', 0)



    ###### Targets #####
    #Dallas Targets self, ( name, location, mobile, targetType, radius, popDens):
    loc4 = Location(32.7584072, -96.7359924)
    loc5 = Location(33.7584072, -95.7359924)
    loc6 = Location(31.7584072, -97.7359924)
    tloc1 = Location(33.24787, -110.65429)
    tloc2 = Location( 37.73726, -101.201)
    tloc3 = Location( 29.71335, -98.62278)
    tloc4 = Location(37.26374, -92.23175 )
    tloc5 = Location(34.54732, -94.29676)
    tloc6 = Location(39.12406, -98.09335)
    tloc7 = Location(38.20143, -92.79644)
    tloc8 = Location(33.54278, -109.14501)

    target1 = Target(" Houston Air Force ", loc4, False, "TerroristTrainingCamp", 5, 555 )
    target2 = Target(" Cost Def MIssle Galveston ", loc5, False, "TerroristTrainingCamp", 14, 333)
    target3 = Target("Station Prison", loc6, False, "TerroristTrainingCamp", 10, 8888 )
    target4 = Target("Air Field 2 ", tloc1, False, "TerroristTrainingCamp", 8, 8888)
    target5 = Target("West  Christi", tloc2, False, "TerroristTrainingCamp", 4.3, 299995)
    target6 = Target("Corpus Christi", tloc3, False, "TerroristTrainingCamp", 12, 222)
    target7 = Target("North East", tloc4, False, "TerroristTrainingCamp", 15, 1222)
    target8 = Target("North East", tloc5, False, "TerroristTrainingCamp", 10, 1222)
    target9 = Target("North East", tloc6, False, "TerroristTrainingCamp", 4, 1222)
    target10 = Target("North East", tloc7, False, "TerroristTrainingCamp", 2, 1222)
    target11 = Target("North East", tloc8, False, "TerroristTrainingCamp", 4, 1222)




    ###### Munitions #####
    #Distance all in km and and blast radius in meters
    # (name, platform, cost, range, cep, reliability, quantity, af, cdm, ct, fd, h, mrbm, rb, sr, ss, ssb, tc)
    #mun1 = MunitionType("GBU-10", 1, 23000.0, inf, 9, .95, inf, 50.0, 93.,90.0,59.0,169.0,93.0,93.0,109.0,80.0,60.0,102.0)
    #mun12 = MunitionType("GBU-99", 1, 555.0, inf, 9, .95, inf, 50.0, 93.,90.0,59.0,169.0,93.0,93.0,109.0,80.0,60.0,102.0)
    #mun2 = MunitionType("ATACM Block IVA",2, 820000.0, 300.0, 4.0, .92,96, 5.0,93.86641816,90.0,59.0,169.0,93.0,93.0,109.0,80.0,60.0,102.0)
    #mun3 = MunitionType("USN DDG",3,500000.0,1111.2,12.2,.85,inf, 5.0, 93.,90.0,59.0,169.0,93.0,93.0,109.0,80.0,60.0,102.0)

    mun1 = MunitionType("ATACM Block IVA", 2, 820, 300, 3, 0.92, 96, 5.546560304, 93.86641816, 90.29146012, 59.63519672, 169.0604774, 93.86641816, 93.86641816, 109.0290676, 80.94938263, 60.09769117, 102.9630445 )
    mun2 = MunitionType("ATACM Block IVB", 2, 1300, 500, 3, 0.98, 96, 3.69770687, 62.57761211, 60.19430675, 39.75679781, 112.7069849, 62.57761211, 62.57761211, 72.68604506, 53.96625508, 40.06512745, 68.64202967)
    mun3 = MunitionType("GBU - 10", 1, 23.7,inf, 9, 0.95, inf, 2.099217937, 197.1555717, 188.5025668, 84.75725198, 171.2385191, 197.1555717, 197.1555717, 148.7837769, 182.3141446, 60.87194239, 417.6536451  )
    mun4 = MunitionType("GBU - 39 - SDB - I", 1, 40,inf, 7, 0.95, inf, 1.8, 46.47001389, 44.43048108, 19.97747588, 40.36130603, 46.47001389, 46.47001389, 35.06867253, 42.97185599, 14.34765442, 98.44190822  )
    mun5 = MunitionType("AGM - 158 JASSM", 1, 830, 370, 3, 0.98, 330, 1.0549777, 136.4779279, 85.25398384, 104.0518977, 110.6252169, 146.0826712, 145.2161891, 92.47901463, 114.3967936, 26.82675292, 291.5775505  )
    mun6 = MunitionType("AGM - 158 B JASSM - ER", 1, 1280, 1000, 3, 0.98, 94, 1.0549777, 136.4779279, 85.25398384, 104.0518977, 110.6252169, 146.0826712, 145.2161891, 92.47901463, 114.3967936, 26.82675292, 291.5775505  )
    mun7 = MunitionType("BGM - 109 Tomahawk", 3, 500, 1111.2, 12.2, 0.85, inf, 1.167750321, 131.5298499, 91.60166623, 101.1379605, 114.0097601, 131.5298499, 131.5298499, 88.30884733, 111.1088541, 31.24932979, 241.7452417   )
    mun8 = MunitionType("BGM - 108 Tomahawk", 3, 1000, 1111.2, 4.6, 0.9, inf, 1.167750321, 131.5298499, 91.60166623, 101.1379605, 114.0097601, 131.5298499, 131.5298499, 88.30884733, 111.1088541, 31.24932979, 241.7452417  )
    mun9 = MunitionType("AGM - 84 E Harpoon / SLAM", 3, 475, 111.12, 6.7, 0.8, inf, 0.957420581, 96.793559, 91.60166623, 61.9139031, 86.61771886, 96.793559, 96.793559, 72.90993911, 99.04084853, 27.76991371, 190.5345095  )
    mun10 = MunitionType("AGM - 84 E Harpoon / SLAM - ER", 3, 575, 277.8, 6.7, 0.9, inf, 0.957420581, 96.793559, 91.60166623, 61.9139031, 86.61771886, 96.793559, 96.793559, 72.90993911, 99.04084853, 27.76991371, 190.5345095  )






    # Service Assignments
    # 1 - air force , 2 is army , 3 is navy

    ###### UNITS ##### (location, range, type, name, munitions):
    # Colorado SPrings
    loc1 = Location(38.8058, -104.7008)
    unit1 = ServiceTypeUnit([loc1], inf, 1, "AIR FORCE", [mun3, mun4, mun5, mun6])

    # Alabama Area
    loc2 = Location(32.31507, -91.59368)
    loc21 = Location(34.31507, -88.59368)
    loc22 = Location(31.31507, -90.59368)
    unit2 = ServiceTypeUnit([loc2, loc21, loc22], 800.0, 2, "ARMY", [mun1, mun2])

    # Gulf Coast
    loc3 = Location(28.11787, -95.37432)
    unit3 = ServiceTypeUnit([loc3], 1126.0, 3, "Navy", [mun7,mun8,mun9,mun10])


    #TODO: Handle the case switching assignments in the case of no muni8tions left to be used by that unit



    #Initialize and Load Scenario from files
    grandFamily = Family()
    numKids = 100
    childAge = 100

    #build the number of Children in the family
    for i in range(0, numKids):
        child = Scenario([target1, target2,target3, target4, target5, target6, target7, target8, target9,target10,target11], [unit1, unit2, unit3], [mun1, mun2, mun3], childAge)
        grandFamily.children.append(copy.deepcopy(child))

    #Run evolution of each child
    # seperate thread so it can be multithreaded as needed
    for i in range(0, len(grandFamily.children )):
        currentChildTopSolution = grandFamily.children[i].runSim()
        if currentChildTopSolution.TotalScore > grandFamily.HighestScore:
            grandFamily.HighestSolution = currentChildTopSolution
            grandFamily.HighestScore = currentChildTopSolution.TotalScore
        print "##################  End Scenario " + str(i)
        print ""
    print "Family Top Score: " + str(grandFamily.HighestScore)
    print "Family Top Solution:  "
    print grandFamily.HighestSolution.printSolution()


    '''
    for i in range(0, children):
        world =  Scenario([target1, target2,target3], [unit1, unit2, unit3], [mun1, mun2, mun3])

    #One Child and Grows
    world.runSim()
    '''





if __name__ == '__main__':
    main()