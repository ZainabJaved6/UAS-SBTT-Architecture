import csv
import json
import re
import socket
import subprocess

import os
import filecmp
import time
from pathlib import Path
from subprocess import Popen
from psutil import process_iter
from signal import SIGTERM # or SIGKILL
from subprocess import STDOUT
from uav.apcmds import getVehicle, arm, disarm, takeoff_simple, takeoff_complex, loiter, return_to_launch, \
    land, move_forward, move_backward, move_down, move_up, turn_left, turn_right, \
    hold_position, hold_altitude, stop_sitl, resetEnvParamValues, \
    reset_sitl, reset_mode, goto_location, restartSim, setParamValuesInEnv, setNextState, setResFile, getResFile, \
    setcurrentState, getTotalDistAvg, cleardist, setformationprocess, getDist, settcfailurefitness, gettcfailurefitness

from utils.py2j import Py2JavaCommunicator
testSeq = []
nextState = ""
global ListVeh
rootPath = Path(__file__).parent.parent
rootPath = str(rootPath)
ListVeh = getVehicle()
executionresultfile = open(rootPath+'\\results\\resfile1.txt', 'a+')



def readfile():
    #global listIndex
    pathFile = open(rootPath+'\\PathCoverage\\pathsSelected.txt', "r")
    pathFile2 = open(rootPath+'\\PathCoverage\\pathsSelected.txt', "r")
    SMPathCoveredFile = open(rootPath+'\\PathCoverage\\SMpathsCovered.txt','a+')  #Opened to keep track of executed paths
    
    global executionresultfile
   
    #listIndex = 0
    listStates = []
    listActions = []

    # Get Test case
    global battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude, heading
    

    #code to restart path execution after the path last executed in case of unexpected shutdown
    file1 = rootPath+'\\PathCoverage\\pathsSelected.txt' #commented for formation
    file2 = rootPath+'\\PathCoverage\\SMpathsCovered.txt'
    file6 = rootPath+'\\PathCoverage\\TestData.csv'
    pathFile6 = open(rootPath+'\\PathCoverage\\TestData.csv', "r")
    
    with open(file6, 'r') as readobj:
        csvreader = csv.reader(readobj)
        itr = 0
        for row in csvreader:
            if inco==itr:
                TD = str(row).split("\\t")
                break
            else:
                itr += 1

        # for val in pathFile6:
        #     TD = val.split(",")

        battery = TD[0]
        battery = battery[2:]
        vibLevel = TD[1]
        gCSConn = TD[2]
        gPSConn = TD[3]
        rCConn = TD[4]
        windSpeed = TD[5]
        windDirec = TD[6]
        speed = TD[7]
        altitude = TD[8]
        heading = TD[9]
        heading = heading[:-2]
       
    if not (os.stat(file2).st_size == 0) and not filecmp.cmp(file1,file2):  
        with open(file2, 'r') as f:
            try:
                sec_last_line = f.readlines()[-1]
            except OSError:
                print("-1 location not available")
        print("sec_last_line:", sec_last_line)
        ind2 = 1 


    else:
        counterfile = open(rootPath+'\\PathCoverage\\gaEvaluationCounter.txt',
                           'r')
        for c in counterfile:
            if len(c) > 0:
                i = int(c)
        counterfile.close()
        ind2 = 0
        executionresultfile.write("\n\n\n\n-----------------------New GA Solution Evaluation " + str(i)+"-----------------------\n\n")
        executionresultfile.flush()
        print("Received Test Data: ", battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed,
              altitude)
     
        executionresultfile.write(
            "Test Data: " + "Battery-" + battery + ", VibrationLevel-" + vibLevel + ", GPSConn-" + gPSConn + ", GCSConn-" + gCSConn + ", WindSpeed-" + windSpeed + ", WindDirec-" + windDirec +
            ", rcConn-" + rCConn + ", groundSpeed" + speed + ", altitude-" + altitude + ", Heading-" + heading + "\n")
        executionresultfile.flush()
        count = 0
    

    found = False
    countp1 = 1
    for x in pathFile:
        if ind2 == 1:
            if x == sec_last_line: 
                found = True

            for x2 in pathFile:
                x = x2
                countp1 += 1
                if found:
                    break
                if x2 == sec_last_line:
                    found = True
        if not 'pathCount' in x: #last line has path count
            if len(x) > 2: #  checking if x contains a path
                x1 = str(x)
                stateaction = x1.split(",")
                i = 0
                for sa in stateaction:
                    if "\n" in sa:
                        sa = sa[:-1]
                    if (i % 2 == 0):
                        listStates.append(sa)
                    else:
                        listActions.append(sa)
                    i += 1
                print (listStates)
                print (listActions)

                if ind2 == 1:
                    count = countp1 
                else :
                    count += 1 
               
                testcaseFile = open(rootPath+'\\PathCoverage\\testcasenumber.txt', "r")

                for val in testcaseFile:
                    if len(val) > 0:
                        tc = int(val)
                tc += 1
                testcaseFile.close
                   

                executionresultfile.write("\n\n\n----------------New Path--------------\n\n")
                executionresultfile.write("Test Case Number:" + str(tc) + "\n")
                executionresultfile.flush()

                executionresultfile.write("Test Sequence Number: "+ str(count)+" ")
                executionresultfile.flush()
                executionresultfile.write(str(x))
                executionresultfile.flush()
                executionresultfile.write("\n")
                executionresultfile.flush()

                print("Path Selected for Execution")

                stateInd = 0
                flag2=False
                for action in listActions: 
                    if flag2 == True:
                       break
                    for state in listStates[stateInd:]:
                        #global nextState
                        if stateInd<=(len(listStates)-3):
                            currstate = listStates[stateInd+1]
                            nextState = listStates[stateInd+2]
                            print("State:", currstate, "Next State:", nextState)
                            setNextState(getStateID(nextState)) #for constraint evaluation, setting in apcmds
                            setcurrentState(getStateID(currstate))
                        else:
                            setNextState(-1)
                            setcurrentState(-1)
                        setResFile(executionresultfile) #sending updated res file to the apcmd for editing

                        isDisarmed = perform_action(action)

                        executionresultfile = getResFile() # getting updated resfile

                        
                        if not isDisarmed:
                            print("Not Disarmed")
                            
                            stateInd += 1
                            break
                        else:
                            print("Disarmed!!!...")
                            flag2 = True
                            break

                FailedCountInCurrentEpisode = 0
                PassedCountInCurrentEpisode = 0
                
                distance, failed2 = getTotalDistAvg()  

                if not (len(failed2["failed"]) == 0):  
                    failedConsStr = str(failed2["failed"])
                    x4 = failedConsStr.split("!@!")
                    print("x: ", x4)
                    print("len x: ", len(x4))
                    FailedCountInCurrentEpisode = FailedCountInCurrentEpisode + len(
                        x4) - 1;  

                if not (len(failed2["passed"]) == 0):  
                    passedConsStr = str(failed2["passed"])
                    w = passedConsStr.split("!@!")
                    print("w: ", w)
                    print("len w: ", len(w))
                    PassedCountInCurrentEpisode = PassedCountInCurrentEpisode + len(
                        w) - 1;  # total number of constraints passed in this episode
                print("FailedCountInCurrentEpisode: ", FailedCountInCurrentEpisode)
                print("PassedCountInCurrentEpisode: ", PassedCountInCurrentEpisode)

                calculatefitnessofInd(FailedCountInCurrentEpisode,
                                          distance)  # combining dist calculated for other paths and calculating avg
                #executionresultfile.write("\n\nFailed Constraints: "+failed2["failed"]+"\n")
                #executionresultfile.flush()
                ind2 = 0 # setting ind2 to 0 to restart nowmal path execution after once restarted
                executionresultfile.write("\nTotal Failed count: " + str(FailedCountInCurrentEpisode))
                executionresultfile.flush()
                #executionresultfile.write("\n\nPassed constraints: "+failed2["passed"]+"\n")
                #executionresultfile.flush()
                executionresultfile.write("\nTotal Passed count: " + str(PassedCountInCurrentEpisode)+"\n")
                executionresultfile.flush()
                t = FailedCountInCurrentEpisode+PassedCountInCurrentEpisode
                executionresultfile.write("\nTotal Constraints Evaluated: " + str(t)+ "\n")
                executionresultfile.flush()

                if FailedCountInCurrentEpisode>0:
                    executionresultfile.write("Test case Result:"+"Failed"+"\n")
                elif FailedCountInCurrentEpisode==0:
                    executionresultfile.write("Test case Result:"+"Passed"+"\n")

                # writing test case to file
                testcaseFile = open(rootPath+'\\PathCoverage\\testcasenumber.txt', "w")
                testcaseFile.write(str(tc))
                testcaseFile.flush()
                testcaseFile.close

                executionresultfile.write("\n")
                executionresultfile.flush()
                #executionresultfile.close()

                SMPathCoveredFile.write(str(x))
                SMPathCoveredFile.flush()

                #listMission.clear()
                listStates.clear()
                listActions.clear()
                cleardist()
                #testSeq.clear()
                resetEnvParamValues()
                stop_sitl()
                restartSim()
                reset_mode()
                reset_sitl()

                
            else:
                listStates.clear()
                listActions.clear()
       
failed2 = {"count": "0", "failed": "", "passed": "", "distance": ""}
total_dist = 0
listdist = []


def getStateID(TState):
    #global TargetState
    if (TState == "Landing" or TState=="LAND"):
        return 0
    elif (TState == "ReturnToLaunch" or TState=="RTL"):
        return 1
    elif (TState == "FlyingStraight"):
        return 2
    elif (TState == "PositionHold" or TState=="POSHOLD"):
        return 3
    else:
        return -1

def perform_action(action):
    global battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude, heading
    isDisarmed = False
    #global is_loiter
    if action == "Arm":
        
        arm() #commented due to formation

        # setParamValuesInEnv(battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude)
    elif action == "Disarm":
        # for veh in ListVeh:
        isDisarmed = disarm()
    elif action == "GotoLocation":
        # for veh in ListVeh:
        isDisarmed = goto_location()
        if not isDisarmed:
            executionresultfile.write("((State Flying))\n")
            executionresultfile.flush()
            setParamValuesInEnv(battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude,
                            heading)  # setting environment values when UAV is in flying state
    elif action == "Takeoff":
        
        isDisarmed = takeoff_complex()
    elif action == "MoveForward":
        # for veh in ListVeh:
        isDisarmed = move_forward()
    elif action == "MoveBackward":
        # for veh in ListVeh:
        isDisarmed = move_backward()
    elif action == "IncreaseAltitude":
        isDisarmed = move_up()
    elif action == "DecreaseAltitude":
        isDisarmed = move_down()
    elif action == "TurnLeft":
        # for veh in ListVeh:
        isDisarmed = turn_left()
    elif action == "TurnRight":
        # for veh in ListVeh:
        isDisarmed = turn_right()
    elif action == "HoldPosition":
        isDisarmed = hold_position()
    elif action == "Wait":
        isDisarmed = hold_position()
        if not isDisarmed:
            executionresultfile.write("((State HoldPosition))\n")
            executionresultfile.flush()
            setParamValuesInEnv(battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude,
                            heading) # we set all values and revaluate the holdpos same constraints every time, to check if any variable setting makes the constraints false
    elif action == "HoldAltitude":
        isDisarmed = hold_altitude()
    elif action == "StartTaxi":
        pass
    elif action == "EndTaxi":
        pass
    elif action == "Loiter":
        isDisarmed = loiter()
       # is_loiter = True
    elif action == "ReturnToLaunch":
        return_to_launch()
    elif action == "RTL":
        isDisarmed = return_to_launch()
    elif action == "Land":
        # for veh in ListVeh:
        isDisarmed = land()

    return isDisarmed

def getTestData():
    global battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed \
        , altitude, heading, lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4, lat5, lon5, lat6, lon6, lat7, lon7, lat8, lon8, wpcount

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 2004))

    datagramFromServer = client_socket.recv(1024)
    print(datagramFromServer)
    x = str(datagramFromServer).split(",", -1)

    print(x)
    i = -1
    # l = len(x)
    for var in x:
        i = i + 1
        
        if i == 0:
            var1 = var.split("[", -1)
            vibLevel = var1[1]
            print("Vibration:" + vibLevel)
        
        elif i == 1:
            gPSConn = var
            print("gps: " + gPSConn)
        elif i == 2:
            rCConn = var
            print("RC: " + rCConn)
        elif i == 3:
            windSpeed = var
            print("wind speed: " + windSpeed)
        elif i == 4:
            lat1 = var
            print("lat1: " + lat1)
        elif i == 5:
            lon1 = var
            print("lon1: " + lon1)
        elif i == 6:
            lat2 = var
            print("lat2: " + lat2)
        elif i == 7:
            lon2 = var
            print("lon2: " + lon2)
        elif i == 8:
            lat3 = var
            print("lat3: " + lat3)
        elif i == 9:
            lon3 = var
            print("lon3: " + lon3)
        elif i == 10:
            lat4 = var
            print("lat4: " + lat4)
        elif i == 11:
            lon4 = var
            print("lon4: " + lon4)
        elif i == 12:
            lat5 = var
            print("lat5: " + lat5)
        elif i == 13:
            lon5 = var
            print("lon5: " + lon5)
        elif i == 14:
            lat6 = var
            print("lat6: " + lat6)
        elif i == 15:
            lon6 = var
            print("lon6: " + lon6)
        elif i == 16:
            lat7 = var
            print("lat7: " + lat7)
        elif i == 17:
            lon7 = var
            print("lon7: " + lon7)
        elif i == 18:
            lat8 = var
            print("lat8: " + lat8)
        elif i == 19:
            lon8 = var
            print("lon8: " + lon8)
        # elif i == 8:
        #     altitude = var
        #     altitude = altitude
        #     print("alt" + altitude)
        elif i == 20:
            wpcount = var[:-1]
            wpcount = wpcount[:-1]
            print ("wpcount" + wpcount)
            
    print("test data received")
    executionresultfile.write(
        "Test Data: " + ", VibrationLevel-" + vibLevel + ", GPSConn-" + gPSConn + ", WindSpeed-" + windSpeed +
        ", rcConn-" + rCConn + ", Lat1-" + lat1 + ", lon1-" + lon1 + ", Lat2-" + lat2 + ", lon2-" + lon2 + ", Lat3-" + lat3 + ", lon3-" + lon3 + ", Lat4-" + lat4 + ", lon4-" + lon4 + ", Lat5-" + lat5 + ", lon5-" + lon5 + ", Lat6-" + lat6 + ", lon6-" + lon6 + ", Lat7-" + lat7 + ", lon7-" + lon7 + ", Lat8-" + lat8 + ", lon8-" + lon8 + ", WpCount-" + wpcount + "\n")
    executionresultfile.flush()


def calculatefitnessofInd(passcons, failedcons, dist):
    PathOfpathFile = rootPath+"\\PathCoverage\\distanceFile.txt"

    if os.path.exists(PathOfpathFile) and os.stat(PathOfpathFile).st_size == 0:
        passconsAllPathsCount = passcons
        failedconsAllPathsCount = failedcons
        distAllPath = dist
    else:
        distFileR = open(rootPath+'\\PathCoverage\\distanceFile.txt',
                         'r')

        for val in distFileR:
            if "," in val:
                countDist = val.split(",")
                passconsAllPathsCount = int(round(float(countDist[0]), 0))
                failedconsAllPathsCount = int(round(float(countDist[1]), 0))
                passconsAllPathsCount += passcons
                failedconsAllPathsCount += failedcons
                # distAllPath = int(round(float(countDist[1]), 0))
                distAllPath = float(countDist[2])
                distAllPath = max(dist,distAllPath)
                # distAllPath =
                # distAllPath += dist

        distFileR.close()
    distFile = open(rootPath+'\\PathCoverage\\distanceFile.txt',
                    'w')
    distFile.write(str(passconsAllPathsCount) + "," + str(failedconsAllPathsCount) + "," + str(distAllPath) + "\n") #writing failed constraints and total distance cal after each test case evaluation
    distFile.flush()
    distFile.close()
def sendTestDataEvaluationRes2(fitness):
    print("Dist Received for sending", fitness, "\n")
    # print(failed[count], "\n")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5000))
    # client_socket.connect(("localhost", 2004))
    var = str(fitness)
    print("var: ", var)
    # user_encode_data = json.dumps(failedcons, indent=2).encode('utf-8') #{"c": 0, "b": 0, "a": 0}
    user_encode_data = json.dumps(var, indent=2).encode('utf-8')
    client_socket.send(user_encode_data)
    client_socket.close()


def sendTestDataEvaluationRes():  # method added by zainab

    distFileR = open(rootPath+'\\PathCoverage\\distanceFile.txt',
                     'r')
    with open(rootPath+'\\PathCoverage\\pathsSelected.txt', 'r') as f:
        last_line = f.readlines()[-1]
        print ("last line:",last_line)
        if 'pathCount' in last_line:
            pathC = last_line.split(":")
            numofPaths = int(pathC[1])

    for val in distFileR:
        if "," in val:
            countDist = val.split(",")
            passconsAllPathsCount = int(round(float(countDist[0]), 0))
            distAllPath = int(round(float(countDist[1]), 0))

    avg = round(float(distAllPath/passconsAllPathsCount),2)
    print("----Sending Test data Evaluation Result----")
    print("Failed cons count received for sending", passconsAllPathsCount, "\n")
    print("Dist Received for sending", avg, "\n")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5000))
    var = str(passconsAllPathsCount) + "-" + str(avg)
    print("var: ", var)
    user_encode_data = json.dumps(var, indent=2).encode('utf-8')
    client_socket.send(user_encode_data)
    client_socket.close()


def main():
    resetEnvParamValues()
    
    PathOfpathFile1 = rootPath+"\\PathCoverage\\gaEvaluationCounter.txt"
    global i
    if os.path.exists(PathOfpathFile1) and os.stat(PathOfpathFile1).st_size == 0:
        i = 0
        counterfile1 = open(rootPath+'\\PathCoverage\\gaEvaluationCounter.txt',
                           'w')
        counterfile1.write(str(i))
        counterfile1.flush()
        counterfile1.close()
    else:
        counterfile = open(rootPath+'\\PathCoverage\\gaEvaluationCounter.txt',
                           'r')
        for c in counterfile:
            if len(c) > 0:
                i = int(c)
        counterfile.close()
        print ("GA counter: ", i)
        if i > 0:
            i += 1

    PathOfpathFile8 = rootPath+"\\PathCoverage\\SMpathsCovered.txt"
   
    global executionresultfile
    executionresultfile = open(rootPath + '\\results\\resfile1.txt', 'a+')
    while i < 1000: 
        global inco
        print("\n\n-----value of i: ",i)
        inco = i
        

        try:
           
            print("killing port")
            for proc in process_iter():
                for conns in proc.connections(kind='inet'):
                    if conns.laddr.port == 10002:
                        proc.send_signal(SIGTERM)  # or SIGKILL
        except:
            print("no file")
            
        testcaseFile = open(rootPath + '\\PathCoverage\\testcasenumber.txt', "r")

        for val in testcaseFile:
            if len(val) > 0:
                tc = int(val)

        executionresultfile.write("\n\n\n----------------New Test Case--------------\n\n")
        executionresultfile.write("Test Case Number:" + str(tc) + "\n")
        #time.sleep(300)
        getTestData()
        # gettestdata()
        checkvalidwps()
        generatemissionstr()
        startformation()
        # time.sleep(300)
        settcfailurefitness() 
        setparamsandobserve()
        executioncompleted()
        resetting()

        
        fitness = saveevares()
        sendTestDataEvaluationRes2(fitness)
        distFile = open(rootPath+'\\PathCoverage\\distanceFile.txt',
                        'w')
        distFile.truncate(0) 
        distFile.flush()
        distFile.close()
       

        counterfile = open(rootPath+'\\PathCoverage\\gaEvaluationCounter.txt',
                           'w')
        counterfile.write(str(i))
        counterfile.flush()
        counterfile.close()
        i += 1
        # ii = i-1
        if i % 10 == 0:
            #getting GA gen counter
            gencounterfile = open(rootPath + '\\results\\genCounter.txt', 'r')
            for c in gencounterfile:
                counter = int(c)
            gencounterfile.close()
            print("Gencounter: ", counter)
          
            executionresultfile.write("\n\n\n----------------Next Generation--------------\n\n")

            uniquefailbeh1 = open(rootPath + '\\results\\behaviorsFailedInaGen.txt', 'w')
            # uniquefailbeh1.write("Generation "+str(counter)+" unique behaviors failed are:"+"\n")
            uniquefailbeh1.truncate(0)
            uniquefailbeh1.flush()
            uniquefailbeh1.close()
            
            fitnessfile = open(rootPath + '\\PathCoverage\\GAEvaResult.txt',
                               'r')
            fitnessList = []
            listRes = []
            for v in fitnessfile:
                listRes.append(v)
            for a in reversed(listRes):
                if "--Next Generation--" in a:
                    print("\n.....Nextgen - break...\n")
                    break;
                else:
                    try:
                        print(float(a))
                        fitnessList.append(float(a))
                    except:
                        print("not a float")
            
            maxfitness = max(fitnessList)
            minfitness = min(fitnessList)
            avgfitness = round(sum(fitnessList)/len(fitnessList),3)
            fitnessfile.close()
            
            genfitnessfile = open(rootPath + '\\results\\GenFitness.txt', 'a+')
            genfitnessfile.write(str(counter)+','+str(maxfitness)+','+str(minfitness)+','+str(avgfitness)+"\n")
            genfitnessfile.flush()
            genfitnessfile.close()

            filee = open(rootPath + '\\PathCoverage\\GAEvaresult.txt', "a+")
            filee.write("\n--Next Generation--\n")
            filee.flush()
            filee.close()
            
            bb = open(rootPath + '\\results\\genCounter.txt',
                                 'w')
            bb.write(str(counter+1))
            bb.flush()
            bb.close()

def checkvalidwps():
    global validwpcount
    validwpcount =0
    global wp1isvalid
    global wp2isvalid
    global wp3isvalid
    global wp4isvalid
    global wp5isvalid
    global wp6isvalid
    global wp7isvalid
    global wp8isvalid

    wp1isvalid=False
    wp2isvalid=False
    wp3isvalid=False
    wp4isvalid=False
    wp5isvalid=False
    wp6isvalid=False
    wp7isvalid=False
    wp8isvalid=False
    dist1 = getDist(-35.363262,149.165237,float(lat1),float(lon1))
    dist2 = getDist(-35.363262, 149.165237, float(lat2), float(lon2))
    dist3 = getDist(-35.363262, 149.165237, float(lat3), float(lon3))
    dist4 = getDist(-35.363262, 149.165237, float(lat4), float(lon4))
    dist5 = getDist(-35.363262, 149.165237, float(lat5), float(lon5))
    dist6 = getDist(-35.363262, 149.165237, float(lat6), float(lon6))
    dist7 = getDist(-35.363262, 149.165237, float(lat7), float(lon7))
    dist8 = getDist(-35.363262, 149.165237, float(lat8), float(lon8))
    if(dist1<=380):
        validwpcount += 1
        wp1isvalid=True
    if(dist2<=380):
        validwpcount += 1
        wp2isvalid=True
    if dist3<=380:
        validwpcount += 1
        wp3isvalid=True
    if dist4<=380:
        validwpcount += 1
        wp4isvalid=True
    if dist5<=380:
        validwpcount += 1
        wp5isvalid=True
    if dist6<=380:
        validwpcount += 1
        wp6isvalid=True
    if dist7<=380:
        validwpcount += 1
        wp7isvalid=True
    if dist8<=380:
        validwpcount += 1
        wp8isvalid=True
def generatemissionstr():
    numofwps = int(round(float(wpcount), 0))
    
    global mission
    if numofwps == 1:
        if wp1isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1
        else:
            mission = "-35.363262,149.165237:" + "-35.36162911,149.1647715"
        # mission = lat1+","+lon1
    elif numofwps == 2:
        if wp1isvalid and wp2isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2
        # elif wp1isvalid and not wp2isvalid:
        #     mission = "-35.363262,149.165237:" + lat1 + "," + lon1 + ":" + "-35.36162911,149.1647715"
        # elif not wp1isvalid and wp2isvalid:
        #     mission = "-35.363262,149.165237:" + "-35.36162911,149.1647715" + ":" + lat2 + "," + lon2
        else: #not wp1isvalid and not wp2isvalid:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36162911,149.1647715"
    elif numofwps == 3:
        if wp1isvalid and wp2isvalid and wp3isvalid:
            mission = "-35.363262,149.165237:" + lat1 + "," + lon1 + ":" + lat2 + "," + lon2 + ":" + lat3 + "," + lon3
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501"
        # mission = lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3
    elif numofwps == 4:
        if wp1isvalid and wp2isvalid and wp3isvalid and wp4isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3+":"+lat4+","+lon4
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36162911,149.1647715"
        # mission = lat1 + "," + lon1 + ":" + lat2 + "," + lon2 + ":" + lat3 + "," + lon3 + ":" + lat4 + ":" + lon4
    elif numofwps == 5:
        if wp1isvalid and wp2isvalid and wp3isvalid and wp4isvalid and wp5isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3+":"+lat4+","+lon4+":"+lat5+","+lon5
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.36162911,149.1647715"

    elif numofwps == 6:
        if wp1isvalid and wp2isvalid and wp3isvalid and wp4isvalid and wp5isvalid and wp6isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3+":"+lat4+","+lon4+":"+lat5+","+lon5+":"+lat6+","+lon6
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299"
    elif numofwps == 7:
        if wp1isvalid and wp2isvalid and wp3isvalid and wp4isvalid and wp5isvalid and wp6isvalid and wp7isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3+":"+lat4+","+lon4+":"+lat5+","+lon5+":"+lat6+","+lon6+":"+lat7+","+lon7
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.3647725,149.1654501"
    elif numofwps == 8:
        if wp1isvalid and wp2isvalid and wp3isvalid and wp4isvalid and wp5isvalid and wp6isvalid and wp7isvalid and wp8isvalid:
            mission = "-35.363262,149.165237:"+lat1+","+lon1+":"+lat2+","+lon2+":"+lat3+","+lon3+":"+lat4+","+lon4+":"+lat5+","+lon5+":"+lat6+","+lon6+":"+lat7+","+lon7+":"+lat8+","+lon8
        else:
            mission = "-35.363262,149.165237:-35.36162911,149.1647715:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299:-35.3647725,149.1654501:-35.36389702,149.1661299"
    print("Mission String: "+mission)
def resetting():
    cleardist()
    # testSeq.clear()
    resetEnvParamValues()
    stop_sitl()
    restartSim()
    reset_mode()
    reset_sitl()
    g2 = Popen(rootPath+'\\utils\\killformationmav.bat', stdin=subprocess.PIPE,
             stdout=subprocess.PIPE)
    g2.stdin.close()
    process.kill()
def executioncompleted():
    FailedCountInCurrentEpisode = 0
    PassedCountInCurrentEpisode = 0

    
    distance, failed2 = getTotalDistAvg()  #

    if not (len(failed2["failed"]) == 0):  # code added by zainab getting number of failed constraints

        failedConsStr = str(failed2["failed"])
        x4 = failedConsStr.split("!@!")
        print("x: ", x4)
        print("len x: ", len(x4))
        FailedCountInCurrentEpisode = FailedCountInCurrentEpisode + len(
            x4) - 1;  # total number of constraints failed in this episode

    if not (len(failed2["passed"]) == 0):  # code added by zainab getting number of failed constraints
        # if not failed2["passed"] == "":
        passedConsStr = str(failed2["passed"])
        w = passedConsStr.split("!@!")
        print("w: ", w)
        print("len w: ", len(w))
        PassedCountInCurrentEpisode = PassedCountInCurrentEpisode + len(
            w) - 1;  # total number of constraints passed in this episode
    print("FailedCountInCurrentEpisode: ", FailedCountInCurrentEpisode)
    print("PassedCountInCurrentEpisode: ", PassedCountInCurrentEpisode)
    calculatefitnessofInd(PassedCountInCurrentEpisode, FailedCountInCurrentEpisode,
                          distance)
    
    ind2 = 0  
    executionresultfile.write("\nTotal Failed count: " + str(FailedCountInCurrentEpisode))
    executionresultfile.flush()
    
    executionresultfile.write("\nTotal Passed count: " + str(PassedCountInCurrentEpisode) + "\n")
    executionresultfile.flush()
    t = FailedCountInCurrentEpisode + PassedCountInCurrentEpisode
    executionresultfile.write("\nTotal Constraints Evaluated: " + str(t) + "\n")
    executionresultfile.flush()

    if FailedCountInCurrentEpisode > 0:
        executionresultfile.write("Test case Result:" + "Failed" + "\n")
    elif FailedCountInCurrentEpisode == 0:
        executionresultfile.write("Test case Result:" + "Passed" + "\n")

    
    testcaseFile = open(rootPath + '\\PathCoverage\\testcasenumber.txt', "r")

    for val in testcaseFile:
        if len(val) > 0:
            tc = int(val)
    tc += 1
    testcaseFile.close

    #writing test case to file
    testcaseFile = open(rootPath+'\\PathCoverage\\testcasenumber.txt', "w")
    testcaseFile.write(str(tc))
    testcaseFile.flush()
    testcaseFile.close

    executionresultfile.write("\n")
    executionresultfile.flush()
    # executionresultfile.close()
def gettestdata():
    global battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed\
        , altitude, heading, lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4, lat5,lon5, lat6, lon6, lat7, lon7, lat8, lon8, wpcount


    file6 = rootPath + '\\PathCoverage\\TestData.csv'
    pathFile6 = open(rootPath + '\\PathCoverage\\TestData.csv', "r")
    
    with open(file6, 'r') as readobj:
        csvreader = csv.reader(readobj)
        itr = 0
        for row in csvreader:
            if inco == itr:
                TD = str(row).split("\\t")
                break
            else:
                itr += 1

        
        vibLevel = TD[0]
        vibLevel = vibLevel[2:]
        
        gPSConn = TD[1]
        rCConn = TD[2]
        windSpeed = TD[3]
        
        lat1 = TD[4]
        lon1 = TD[5]
        lat2 = TD[6]
        lon2 = TD[7]
        lat3 = TD[8]
        lon3 = TD[9]
        lat4 = TD[10]
        lon4 = TD[11]
        lat5 = TD[12]
        lon5 = TD[13]
        lat6 = TD[14]
        lon6 = TD[15]
        lat7 = TD[16]
        lon7 = TD[17]
        lat8 = TD[18]
        lon8 = TD[19]
        
    print("test data received")
    executionresultfile.write(
        "Test Data: " + ", VibrationLevel-" + vibLevel + ", GPSConn-" + gPSConn + ", WindSpeed-" + windSpeed +
        ", rcConn-" + rCConn + ", Lat1-"+ lat1 + ", lon1-"+ lon1+ ", Lat2-"+ lat2 + ", lon2-"+ lon2+ ", Lat3-"+ lat3 + ", lon3-"+ lon3+ ", Lat4-"+ lat4 + ", lon4-"+ lon4 + ", Lat5-"+ lat5 + ", lon5-"+ lon5+ ", Lat6-"+ lat6 + ", lon6-"+ lon6+ ", Lat7-"+ lat7 + ", lon7-"+ lon7+ ", Lat8-"+ lat8 + ", lon8-"+ lon8 +", WpCount-"+ wpcount + "\n")
    executionresultfile.flush()

def setparamsandobserve():
    # Get Test data for all paths to be executed

    setResFile(executionresultfile)
    # setParamValuesInEnv(battery, vibLevel, gCSConn, gPSConn, rCConn, windSpeed, windDirec, speed, altitude,
    #                     heading, lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4)
    setParamValuesInEnv(vibLevel, gPSConn, rCConn, windSpeed, lat2, lon2)

def startformation():
    
    g = Popen(rootPath+"\\utils\\startformation.bat", stdin=subprocess.PIPE,
               stdout=subprocess.PIPE)
    
    time.sleep(2)
    

    arm()
    
    s = mission
    args = [rootPath+'\\utils\\formationAlgo2.jar', s]  # Any number of args to be passed to the jar file

    # result = jarWrapper(*args)
    jarWrapper(*args)
    print("formation started")
    # print(result)
    time.sleep(10) #waiting for the UAVs to start executing the mission

def jarWrapper(*args):
    global process
    process = Popen(['java', '-jar'] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    setformationprocess(process)
   
def saveevares():
    filee = open(rootPath + '\\PathCoverage\\GAEvaresult.txt', "a+")
    distFileR = open(rootPath + '\\PathCoverage\\distanceFile.txt',
                     'r')

    
    uniquefailurefound=gettcfailurefitness()
    for val in distFileR:
        if "," in val:
            countDist = val.split(",")
            passConsAllPathsCount = int(round(float(countDist[0]), 0))
            failedConsAllPathsCount = int(round(float(countDist[1]), 0))# countdist[2] has the max branch dist
            
            failedConsAllPathsCount = failedConsAllPathsCount -  uniquefailurefound # this gives the number of common  behaviors failed by the test case
            normalizedFailedcount = (failedConsAllPathsCount - 0)/ (10 - 0) #10 is set as max as the total number of constraints is 10
            uniquefailurefound = uniquefailurefound/10
            # normalizedFailedcount = normalizedFailedcount/10 # done so we don't end up getting a negative fitness, because we will subtract the normalized number of constraints failed from the branch distance, and subtract 0.1 if a unique constraint is failed
            if validwpcount==8:
                if uniquefailurefound == 0:
                    distAllPath = round(float(countDist[2])-normalizedFailedcount, 2)
                    print("\n\n-----unique failure not found---"+str(distAllPath))
                else:
                    distAllPath = round(float(countDist[2])-normalizedFailedcount-uniquefailurefound-0.4, 2) #subtracting 0.2 from fitness if unique failure identified
                    print("\n\n-----unique failure found---"+str(distAllPath))
            elif validwpcount<8:
                # if not uniquefailurefound:
                if uniquefailurefound > 0:
                    distAllPath = round(float(countDist[2])+0.2-normalizedFailedcount,2)  #adding max branch dist and number of cons passed, adding a 0.2 to the fitness val if the mission gen was invalid as fitness value
                    print("\n\n-----unique failure not found with incorrect mission---"+str(distAllPath))
                else:
                    distAllPath = round(float(countDist[2]) + 0.2-normalizedFailedcount-uniquefailurefound-0.4, 2) # subtracting the number of unique faults identified and 0.2
                    print("\n\n-----unique failure found with incorrect mission---"+str(distAllPath))

            
    try:        
        if distAllPath<0:
            avg=0
        else:
            avg=distAllPath
    except:
        print("\n\ndividion by zero")
        avg = 0
    print("----Saving Test data Evaluation Result----")
    print("passed cons count received for sending", passConsAllPathsCount, "\n")
    print("Dist Received for sending", avg, "\n")
    filee.write(str(avg))
    filee.flush()
    filee.write("\n")
    filee.flush()
    filee.close()
    return avg

if __name__ == "__main__":
    main()