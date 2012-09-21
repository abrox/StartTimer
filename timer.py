
"""
Simple sail boat race start application.
Thus mouse is bit problematic in this case :-) control is done with wii remote.
 
"""
import Tkinter as tk
import Queue
import wiiconnection as wii
import tkFont
from datetime import datetime
 
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
        text = tk.Label(container, font="TextFont", textvariable=self.lText)
        text.grid(row=0, column=0, sticky="nsew")
        
        self.statBarText = tk.StringVar()
        self.lStatus = tk.Label(self.statusBar, font='StatusBarFont', textvariable=self.statBarText )
        self.lStatus.pack(side='left')
       
        container.bind("<Configure>", self.resize)
        master.protocol("WM_DELETE_WINDOW", tClient.endApplication)

        self.availableTimers=[60,120,180,240,300,600]
        self.selectedTimer = 4 #5 min is default
        self.state = self.TIMER_STOPPED
        self.timerTickCount=self.availableTimers[self.selectedTimer]
        self.showTime =0
        self.showRaceTimer()

    def ScaleFont(self, tLen):
        """
        Scale timer text as big it can be.
        todo: Check is there better way than hardcode scaling factors ?
        """
        if not tLen:
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
        self.ScaleFont(len(self.lText.get()))
        
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
        self.statBarText.set('Remote found')
        self.tClient.rumble()
        self.statusBar.config(background='grey')
        self.lStatus.config(background='grey',foreground='black')
        
    def startRaceTimer(self):
        """
        Inform user that countdown is started and change state machine state.
        """
        self.tClient.rumble()
        self.tClient.leds(self.timerTickCount/60)
        self.changeState(self.COUNTDOWN)
        print 'Start'

    def stopRaceTimer(self):
        if (self.state != self.TIMER_STOPPED):
            self.changeState(self.TIMER_STOPPED)
            self.tClient.rumble()
            print 'STop'
            
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
        print 'SHow Next %d'%self.selectedTimer

    def selectPreviousTimer(self):
        """
        Select and show previous available timer.
        """
        if self.selectedTimer > 0:
            self.selectedTimer -= 1
            self.timerTickCount = self.availableTimers[self.selectedTimer]
        self.showRaceTimer()
        
        print 'SHow prev%d'%self.selectedTimer
            
    def showRaceTimer(self):
        #when show time do not override it with race timer
        if self.showTime:
            return
        
        hour = self.timerTickCount/3600
        timeLeft = self.timerTickCount%3600
        
        mins = timeLeft/60
        secs = timeLeft%60
        timeString=''
        if hour:
            timeString = '%d:'%hour
        if hour or mins:
            timeString += '%d:'%mins 
                   
        timeString += '%02d'%secs 
        self.displayAndScaleText(timeString)
    

    def displayAndScaleText(self, timeString):
        prevLen = len(self.lText.get())
        self.lText.set(timeString)
        sLen = len(timeString)
        if sLen != prevLen:
            self.ScaleFont(sLen)

    def showDateTime(self):
        d= datetime.now()
        timeString = datetime.strftime(d,"%H:%M:%S")
        self.displayAndScaleText(timeString)
        

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
            self.showTime =1
            self.showDateTime()
        elif (msg == wii.HIDE_TIME):
            self.showTime =0
            self.showRaceTimer()
        elif (msg == wii.STOP_RACETIMER):
            self.stopRaceTimer()
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
                    self.changeState(self.RACE)
        ###############Race#################################    
        elif self.state == self.RACE:
            if (msg == 'ONE_SEC_TIMER'):
                self.timerTickCount+=1
                self.showRaceTimer()
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
    
    #These are quick and nasty hacks...FIX
    def rumble(self): 
        self.wiiServer.rumble(1)
        self.master.after(100, self.stopRumble)
    def stopRumble(self):
        self.wiiServer.rumble(0)
    def leds(self,leds):
        self.wiiServer.leds(leds) 
             
if __name__ == "__main__":
    root = tk.Tk()
    client = ThreadedClient(root)
    root.mainloop()
