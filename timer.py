
""" print ' print '%sTime to start:%s'%(timeString,self.getTimeString(self.timerTickCount))%sTime to start:%s'%(timeString,self.getTimeString(self.timerTickCount))
Simple sail boat race start application.
Thus mouse is bit problematic in this case :-) control is done with wii remote.
 
"""
import Tkinter as tk
import Queue
import wiiconnection as wii
import tkFont
from time import  strftime
from datetime import timedelta
import string

class GuiPart:
    INIT =0
    TIMER_STOPPED = 1
    COUNTDOWN = 2
    RACE = 3
    
    def __init__(self, master, tClient):
        self.queue = tClient.queue
        self.parent = master
        self.tClient = tClient
        
        self._textFont = tkFont.Font(name="TextFont")
        self._textFont.configure(**tkFont.nametofont("TkDefaultFont").configure())
        
        self._sbFont = tkFont.Font(name="StatusBarFont")
        self._sbFont.configure(**tkFont.nametofont("TkDefaultFont").configure())
        
        self.statusBar = tk.Frame(master, borderwidth=0)
        container = tk.Frame(master, borderwidth=1, relief="sunken", 
                             width=600, height=600)
        container.grid_propagate(False)
        self.statusBar.pack(side="bottom", fill="x")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.lText = tk.StringVar()
        text = tk.Label(container, font="TextFont", textvariable=self.lText, justify='left')
        text.grid(row=0, column=0, sticky="nsew")
        
        self.statBarText = tk.StringVar()
        self.lStatus = tk.Label(self.statusBar, font='StatusBarFont', textvariable=self.statBarText )
        self.lStatus.pack(side='left')
       
        container.bind("<Configure>", self.resize)
        master.protocol("WM_DELETE_WINDOW", tClient.endApplication)

        self.availableTimers=[60,120,180,240,300,360,600]
        self.selectedTimer = 4 #5 min is default
        self.state = self.TIMER_STOPPED
        self.timerTickCount=self.availableTimers[self.selectedTimer]
        self.hideRacetimer = False
        self.showHelp()

    def ScaleFont(self, tLen):
        """
        Scale timer text as big it can be.
        todo: Check is there better way than hardcoded scaling factors ?
        """
        if tLen == 0:
            return
        width= self.parent.winfo_width()
        height = self.parent.winfo_height()
        font = tkFont.nametofont("TextFont")
        size = int(height * 0.7)
        size2 = int((width / tLen) * 1.3)
        if size2 < size:
            size = size2
        font.configure(size=size)

    def resize(self,event):
        """
        Resize of the window will scale font as big as possible. 
        """
        textLen = self.getLongestLine(self.lText.get())
        self.ScaleFont(textLen)
        
    def changeState(self,newState):
        self.state = newState

    def handleWiiLost(self):
        """
        Inform user that we do not have connection to wiimote
        using red background to highlight missing connection.
        """
        self.statusBar.config(background='red')
        self.statBarText.set('No connection to WII press 1&2 to detect remote....')
        self.statusBar.config(background='red')
        self.lStatus.config(background='red',foreground='white')

    def handleWiiFound(self):
        """
        Inform user that connection to wiimote is established. 
        """
        self.statBarText.set('Press home for help')
        self.tClient.rumble()
        self.statusBar.config(background='grey')
        self.lStatus.config(background='grey',foreground='black')
        self.showRaceTimer()
        
    def startRaceTimer(self):
        """
        Inform user that countdown is started and change state machine state.
        """
        self.tClient.rumble()
        self.tClient.leds(self.timerTickCount/60)
        self.changeState(self.COUNTDOWN)

    def stopRaceTimer(self):
        if (self.state != self.TIMER_STOPPED):
            self.changeState(self.TIMER_STOPPED)
            self.tClient.rumble()
            
    def resetRaceTimer(self):
        self.timerTickCount = self.availableTimers[self.selectedTimer]
        self.showRaceTimer()

    def selectNextTimer(self):
        """
        Select and show next available timer.
        """
        if self.selectedTimer < len(self.availableTimers)-1:
            self.selectedTimer += 1
            self.timerTickCount = self.availableTimers[self.selectedTimer]
        self.showRaceTimer()

    def selectPreviousTimer(self):
        """
        Select and show previous available timer.
        """
        if self.selectedTimer > 0:
            self.selectedTimer -= 1
            self.timerTickCount = self.availableTimers[self.selectedTimer]
        self.showRaceTimer()
            

    def getTimeString(self,ticks):
        """
        Construct time to correct format.
        todo: is there some library function/ class for this 
        """
        hour = ticks / 3600
        timeLeft = ticks % 3600
        mins = timeLeft / 60
        secs = timeLeft % 60
        timeString = ''
        if hour:
            timeString = '%d:' % hour
        if hour or mins:
            timeString += '%d:' % mins
        timeString += '%02d' % secs
        return timeString

    def showRaceTimer(self):
        #when show time or help dont let racetimer overrun. 
        if self.hideRacetimer:
            return
        
        timeString = self.getTimeString(self.timerTickCount) 
        self.displayAndScaleText(timeString)
    
    def getLongestLine(self, theSring):
        """
        Utility function to
        get longest line from multiline string.
        """
        sLen = 0
        for line in theSring.split('\n'):
            aLen = len(line)
            if aLen > sLen:
                sLen = aLen    
        return sLen

    def displayAndScaleText(self, stringToShow):        
        
        prevLen = self.getLongestLine(self.lText.get())
        sLen = self.getLongestLine(stringToShow)
        
        self.lText.set(stringToShow)
        
        if sLen != prevLen:
            self.ScaleFont(sLen)

    def showClock(self):
        timeString = strftime("%H:%M:%S")
        self.displayAndScaleText(timeString)
        
    def showHelp(self):
        helpText ='Detect wii:    Press 1&2 together\n'
        helpText+='Select timer:  Use Right and Left arrows\n'
        helpText+='Start timer:   Press B\n'
        helpText+='Stop timer:    Press A for few seconds\n'
        helpText+='Reset timer:   Press A for about 3 seconds\n'
        helpText+='Show Time:     Press 1\n'
        helpText+='Show help:     Press home\n'
        helpText+='Intermediate time: Press first B and then A at same time\n'
    
        self.displayAndScaleText(helpText)
        
    def informWhileCountDown(self,timeLeft):
        """
        Giving some feedback to user,with leds and rumbling wii remote
        """
        #rumble once every minute
        if not (timeLeft % 60): 
            self.tClient.rumble()
            self.tClient.leds(timeLeft / 60)
        #last minute rumble every 10 sec
        if (timeLeft < 60 and not timeLeft % 10):
            self.tClient.rumble()
            self.tClient.leds(timeLeft / 10) 
        #last 10 sec rubmle every sec
        if (timeLeft < 10):
            self.tClient.rumble()
            self.tClient.leds(timeLeft)

    def processIncoming(self,msg):
        """
        Handle incoming messages.
        """ 
        ###########Any state################################
        if ( msg == wii.SHOW_TIME):
            self.hideRacetimer = True
            self.showClock()
        elif (msg == wii.HIDE_TIME):
            self.hideRacetimer = False
            self.showRaceTimer()
        elif (msg == wii.STOP_RACETIMER):
            self.stopRaceTimer()
        elif (msg == wii.SHOW_HELP):
            self.hideRacetimer = False
            self.showHelp()
        elif( msg == wii.HIDE_HELP): 
            self.hideRacetimer = False
            self.showRaceTimer()
        ##########Timer Stopped##############################
        if self.state == self.TIMER_STOPPED:
            if (msg == wii.LOST):
                self.handleWiiLost()
            elif (msg == wii.FOUND):
                self.handleWiiFound()
            elif (msg == wii.START_COUNTDOWN):
                self.startRaceTimer()
            elif (msg == wii.SHOW_NEXT):
                self.selectNextTimer()
            elif (msg == wii.SHOW_PREV):
                self.selectPreviousTimer()
            elif (msg == wii.RESET_RACETIMER):
                self.resetRaceTimer()
        ##########Countdown#################################
        elif self.state == self.COUNTDOWN:
            if (msg == 'ONE_SEC_TIMER'):
                self.timerTickCount-=1
                self.informWhileCountDown(self.timerTickCount)
                self.showRaceTimer()
                if (self.timerTickCount == 0):
                    timeString = strftime("%H:%M:%S")
                    print '%s\tSTART....'%(timeString)
                    self.changeState(self.RACE)
            elif (msg == wii.INTERMEDIATE):
                timeString = strftime("%H:%M:%S")
                print '%s\tTime to start:\t%s'%(timeString,timedelta(seconds=self.timerTickCount))
        ###############Race#################################    
        elif self.state == self.RACE:
            if (msg == 'ONE_SEC_TIMER'):
                self.timerTickCount+=1
                self.showRaceTimer()
            elif (msg == wii.INTERMEDIATE):
                timeString = strftime("%H:%M:%S")
                print '%s\tRace is on:\t%s'%(timeString,timedelta(seconds=self.timerTickCount))
        ####################################################
class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.wiiServer = wii.Server(self.queue)
        self.wiiServer.start()    
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()
        self.master.after(1000, self.oneSecTimer)
        
    def oneSecTimer(self):
        self.gui.processIncoming('ONE_SEC_TIMER')
        self.master.after(1000, self.oneSecTimer)
    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.gui.processIncoming(msg)
            except Queue.Empty:
                pass

        if not self.wiiServer.isRunning():
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)
               
    def endApplication(self):
        self.wiiServer.stop()

    def rumble(self):
        """
        Rumble wii for a while
        """
        self.wiiServer.rumble(1)
        self.master.after(100, self.stopRumble)
        
    def stopRumble(self):
        self.wiiServer.rumble(0)
    def leds(self,leds):
        """
        Lif Leds so that user sees how long there is time to start.
        """
        self.wiiServer.leds(leds) 
             
if __name__ == "__main__":
    root = tk.Tk()
    client = ThreadedClient(root)
    root.mainloop()
