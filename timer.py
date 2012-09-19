
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
    STOPPED = 1
    WAIT_RACE_BEGIN = 2
    RACE = 3
    
    def __init__(self, master, tClient):
        self.queue = tClient.queue
        self.parent = master
        self.tClient = tClient
        
        self._textFont = tkFont.Font(name="TextFont")
        self._textFont.configure(**tkFont.nametofont("TkDefaultFont").configure())
        
        self._sbFont = tkFont.Font(name="StatusBarFont")
        self._sbFont.configure(**tkFont.nametofont("TkDefaultFont").configure())
        
        toolbar = tk.Frame(master, borderwidth=0)
        container = tk.Frame(master, borderwidth=1, relief="sunken", 
                             width=600, height=600)
        container.grid_propagate(False)
        toolbar.pack(side="bottom", fill="x")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.lText = tk.StringVar()
        text = tk.Label(container, font="TextFont", textvariable=self.lText)
        text.grid(row=0, column=0, sticky="nsew")
        
        self.statBarText = tk.StringVar()
        lStatus = tk.Label(toolbar, font='StatusBarFont', textvariable=self.statBarText )
        lStatus.pack(side='left')
       
        container.bind("<Configure>", self.resize)
        master.protocol("WM_DELETE_WINDOW", tClient.endApplication)

        self.Timers=[60,120,180,240,300,600]
        self.usedTimer = 4 #5 min is default
        self.state = self.STOPPED
        self.timerTick=self.Timers[self.usedTimer]
        self.showTime =0
        self.showRaceTimer()
        # Add more UI stuff here

    def ScaleFont(self, tLen):
        """
        Scale timer text as big it can be.
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
        self.ScaleFont(len(self.lText.get()))
        
    def changeState(self,newState):
        self.state = newState

    def handleWiiLost(self):
        self.statBarText.set('No connection to WII press 1&2 to detct remote....')

    def handleWiiFound(self):
        self.statBarText.set('Remote found')
        self.tClient.rumble()
        
    def handleStart(self):
        self.timerTick = self.Timers[self.usedTimer]
        self.tClient.rumble()
        self.tClient.leds(self.timerTick/60)
        print 'Start'

    def handleStopTimer(self):
        self.timerTick = self.Timers[self.usedTimer]
        self.showRaceTimer()
        self.tClient.rumble()
        print 'STop'

    def handleShowNext(self):
        try:
            self.timerTick = self.Timers[self.usedTimer+1]
            self.usedTimer+=1
        except IndexError:
            self.timerTick = self.Timers[self.usedTimer]
        
        self.showRaceTimer()
        print 'SHow Next %d'%self.usedTimer

    def handleShowPrev(self):
        if self.usedTimer > 0:
            self.usedTimer-=1
            self.timerTick = self.Timers[self.usedTimer]
        self.showRaceTimer()
        
        print 'SHow prev%d'%self.usedTimer
    def showRaceTimer(self):
        #when show time do not override it with race timer
        if self.showTime:
            return
        
        hour = self.timerTick/3600
        timeLeft = self.timerTick%3600
        
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
        

    def informUserWhileWaitStart(self,timeLeft):
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
        if ( msg == wii.SHOW_TIME):
            self.showTime =1
            self.showDateTime()
        
        if (msg == wii.HIDE_TIME):
            self.showTime =0
            self.showRaceTimer()
        ###################################################
        if self.state == self.STOPPED:
            if (msg == wii.LOST):
                self.handleWiiLost()
            elif (msg == wii.FOUND):
                self.handleWiiFound()
            elif (msg == wii.START):
                self.handleStart()
                self.changeState(self.WAIT_RACE_BEGIN)
            elif (msg == wii.SHOW_NEXT):
                self.handleShowNext()
            elif (msg == wii.SHOW_PREV):
                self.handleShowPrev()
        ####################################################
        elif self.state == self.WAIT_RACE_BEGIN:
            if (msg == 'ONE_SEC_TIMER'):
                self.timerTick-=1
                self.informUserWhileWaitStart(self.timerTick)
                self.showRaceTimer()
                if (self.timerTick ==0):
                    self.changeState(self.RACE)
            elif (msg == wii.STOP):
                self.handleStopTimer()
                self.changeState(self.STOPPED)
        ####################################################    
        elif self.state == self.RACE:
            if (msg == wii.STOP):
                self.handleStopTimer()
                self.changeState(self.STOPPED)
            if (msg == 'ONE_SEC_TIMER'):
                self.timerTick+=1
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
