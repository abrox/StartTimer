## {{{ http://code.activestate.com/recipes/82965/ (r1)
"""
This recipe describes how to handle asynchronous I/O in an environment where
you are running Tkinter as the graphical user interface. Tkinter is safe
to use as long as all the graphics commands are handled in a single thread.
Since it is more efficient to make I/O channels to block and wait for something
to happen rather than poll at regular intervals, we want I/O to be handled
in separate threads. These can communicate in a threasafe way with the main,
GUI-oriented process through one or several queues. In this solution the GUI
still has to make a poll at a reasonable interval, to check if there is
something in the queue that needs processing. Other solutions are possible,
but they add a lot of complexity to the application.
Created by Jacob Hallen, AB Strakt, Sweden.2001-10-17
"""
import Tkinter as tk
import Queue
import wiiconnection as wii
import tkFont

 
class GuiPart:
    INIT =0
    STOPPED = 1
    WAIT_RACE_BEGIN = 2
    RACE = 3
    
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        self.parent = master
        # Set upthe GUI
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
        master.protocol("WM_DELETE_WINDOW", endCommand)

        self.state = self.STOPPED
        self.timerTick=66
        self.apu = 0
        self.showRaceTimer()
        # Add more UI stuff here

    def ScaleFont(self, height, width,tLen):
        if not tLen:
            return
        #print 'h:%d, w%d, l%d'%(height, width,tLen)
        font = tkFont.nametofont("TextFont")
        size = int(height * 0.7)
        size2 = int((width / tLen) * 1.3)
        if size2 < size:
            size = size2
        font.configure(size=size)

    def resize(self,event):
        self.ScaleFont(event.height,event.width,len(self.lText.get()))
        
    def changeState(self,newState):
        self.state = newState

    def handleWiiLost(self):
        self.statBarText.set('No connection to WII press 1&2 to detct remote....')
        pass
    def handleWiiFound(self):
        self.statBarText.set('Remote found')
        pass
    def handleStart(self):
        self.timerTick = 66
        print 'Start'

    def handleStopTimer(self):
        self.timerTick = 300
        self.showRaceTimer()
        print 'STop'

    def handleShowNext(self):
        print 'SHow Next'

    def handleShowPrev(self):
        print 'SHow prev'
    def showRaceTimer(self):
        hour = self.timerTick/360
        timeLeft = self.timerTick%360
        
        mins = timeLeft/60
        secs = timeLeft%60
        timeString=''
        if hour:
            timeString = '%02d:'%hour
        if hour or mins:
            timeString += '%02d:'%mins 
                   
        timeString += '%02d'%secs    
        self.lText.set(timeString)
        sLen = len(timeString)
        
        if not (sLen == 0 or sLen == self.apu):
            self.apu = sLen
            width= self.parent.winfo_width()
            height = self.parent.winfo_height()
            self.ScaleFont(height, width,sLen)
            
    def processIncoming(self,msg):
        """
        
        """
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
        self.gui = GuiPart(master, self.queue, self.endApplication)

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
        
if __name__ == "__main__":
    root = tk.Tk()
    client = ThreadedClient(root)
    root.mainloop()
