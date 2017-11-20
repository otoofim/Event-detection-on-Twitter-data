
class BurstDetection(object):
    
    def __init__(self,numOfWind,sourceDire = "clusters.sortedby.time.csv"):
        self.windows = {}
        self.invertedIndexes = {}
        self.numOfWind = numOfWind
        self.sourceDire = sourceDire
        self.countEvents = 0
        
    def readingTwitts(self):
        #windows intervals start from 5 min to 640 min
        TIMES = [300000,600000,1200000,2400000,4800000,9600000,19200000,38400000]
        #windows start times are initialized to zero 
        TimeStart = []
        #twitts are read one by one
        with open(self.sourceDire, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',',dialect=csv.excel_tab)
            for i,row in enumerate(spamreader):
                if i==0:
                    for k in range(0,self.numOfWind):
                        #First twitt time stamp is used for the start time of windows. This happens only the first time.
                        TimeStart.append(long(row[3]))
                        
                #Creating inverted indexes
                if row[1] in self.invertedIndexes:
                    #if a cluster name entity has alreadty been added 
                    #then the current twitt's data is appended to the list of twitts correspond to that entity cluster names.            
                    self.invertedIndexes[row[1]].append("{0},{1},{2},{3},{4},{5}".format(row[0],row[2],row[3],row[4],row[5],row[6]))   
                else:
                    #If a cluster name entity is not exist then a pair of key and value will be created for that.
                    self.invertedIndexes[row[1]] = ["{0},{1},{2},{3},{4},{5}".format(row[0],row[2],row[3],row[4],row[5],row[6])]   

                #Each window is checked if it is over
                for j in range(0, self.numOfWind):
                    if(long(row[3]) - TimeStart[j] >= TIMES[j]):
                        #Statr time of the window is updated to the last twitt time stamp
                        TimeStart[j] = long(row[3])
                        #Any possible bursting entity in this window is checked
                        self.DetectBursting()
                        #Window parameters (S0, S1, and S2) get updated
                        self.UpdateWindows("wind{0}".format(j+1))
                        #If this window is the largest window then set invertedIndexes dictionary to empty
                        if j == (self.numOfWind-1):
                            self.invertedIndexes = {}
                    
                    
    #This method updates a window parameters based on the current frequency of the twitts in invertedIndexs.
    def UpdateWindows(self, windId):
        for entity in self.invertedIndexes.keys():
            if (entity in self.windows) and (windId in self.windows[entity]):
                    #Computing S0, S1, and S2
                    s0 = self.windows[entity][windId]["s0"] + 1
                    s1 = self.windows[entity][windId]["s1"] + len(self.invertedIndexes[entity])
                    s2 = self.windows[entity][windId]["s2"] + np.power(len(self.invertedIndexes[entity]),2) 
                    self.windows[entity][windId]["s0"] = s0
                    self.windows[entity][windId]["s1"] = s1
                    self.windows[entity][windId]["s2"] = s2
            else:
                #Computing S0, S1, and S2
                self.windows[entity] = {windId:{"s0":0,"s1":0,"s2":0}}
                s0 = 0 + 1
                s1 = 0 + len(self.invertedIndexes[entity])
                s2 = 0 + np.power(len(self.invertedIndexes[entity]),2) 
                self.windows[entity][windId]["s0"] = s0
                self.windows[entity][windId]["s1"] = s1
                self.windows[entity][windId]["s2"] = s2
                
    #This method checks for any possible bursting entities in invertedIndexes
    def DetectBursting(self):
        for entity in self.invertedIndexes:
            #Checks if an entity exists in a window. Otherwise, it means it hasn't happened before and so it is not bursting.
            if entity in self.windows:
                for window in self.windows[entity].keys():
                    #Computing mean and standard deviation for a window
                    mu = self.windows[entity][window]["s1"] / self.windows[entity][window]["s0"]
                    sd = np.sqrt(abs((self.windows[entity][window]["s2"] - np.power(self.windows[entity][window]["s1"],2))) / self.windows[entity][window]["s0"])
                    #If the frequency of the entity in invertedIndexes is greater than 10 and 3 times SD plus mean
                    #then it will be considered as an event.
                    if (len(self.invertedIndexes[entity]) >= round(3*sd + mu)) and (len(self.invertedIndexes[entity]) > 10):
                        self.saveToFile(entity)



                    
    #This method saves detected events to a file for the future evaluation with eval.py
    def saveToFile(self, entity):
        with open('{0}wind.csv'.format(self.numOfWind), 'a+') as csvfile:
            self.countEvents = self.countEvents + 1
            for twitts in self.invertedIndexes[entity]:
                tokens = twitts.split(",")
                csvfile.write("{0},{1},{2},{3},{4},{5},{6}\n".format(self.countEvents,entity,tokens[1],tokens[2],tokens[3],tokens[4],tokens[5]))   
                
                



if __name__ == "__main__":

    import csv
    import math
    import numpy as np
    import sys
    
    print("Event detection has started with {0} windows.".format(sys.argv[1]))
    if len(sys.argv) > 2:
        t = BurstDetection(int(sys.argv[1]),sys.argv[2])
        t.readingTwitts()
        print("Event detection is over. See the result in {0}wind.csv file.".format(sys.argv[1]))
    elif len(sys.argv) > 1:
        t = BurstDetection(int(sys.argv[1]))
        t.readingTwitts()
        print("Event detection is over. See the result in {0}wind.csv file.".format(sys.argv[1]))
    else:
        print("Please provide number of windows.")


