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
import Tkinter
import time
import Queue
import wiiconnection as wii


 
class GuiPart:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        frame = Tkinter.Frame(master)
        frame.pack()
        self.lText = Tkinter.StringVar()
        self.label = Tkinter.Label(frame, textvariable = self.lText)
        self.label.pack(side=Tkinter.TOP)
        self.button = Tkinter.Button(frame, text='Done', command=endCommand)
        self.button.pack(side = Tkinter.BOTTOM )
        # Add more GUI stuff here


    def handleWiiLost(self):
        self.lText.set('No connection to WII press 1&2 to detct remote....')

    def handleWiiFound(self):
        self.lText.set('Remote found')

    def handleStart(self):
        print 'Start'


    def handleStopTimer(self):
        print 'STop'


    def handleShowNext(self):
        print 'SHow Next'


    def handleShowPrev(self):
        print 'SHow prev'

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if (msg == wii.LOST):
                    self.handleWiiLost()
                elif (msg == wii.FOUND):
                    self.handleWiiFound()
                elif (msg == wii.START):
                    self.handleStart()
                elif (msg == wii.STOP):
                    self.handleStopTimer()
                elif (msg == wii.SHOW_NEXT):
                    self.handleShowNext()
                elif (msg == wii.SHOW_PREV):
                    self.handleShowPrev()
                else:
                    print msg
            except Queue.Empty:
                pass

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

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.wiiServer.isRunning():
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)
               
    def endApplication(self):
        self.wiiServer.stop()
        
if __name__ == "__main__":
    root = Tkinter.Tk()
    client = ThreadedClient(root)
    root.mainloop()
## end of http://code.activestate.com/recipes/82965/ }}}
