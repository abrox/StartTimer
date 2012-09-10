import time
import threading
import cwiid

#definations for used messages
WII_LOST = 0
WII_FOUND = 1
START =2
STOP = 3
SHOW_NEXT= 4
SHOW_PREV= 5

class WiiServer:

    def __init__(self, queue):
        self.running = 0
        self.queue = queue
        self.thread1 = None

    def start(self):
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()
        
    def stop(self):
        self.running = 0
    
    def isRunning(self):
        return (self.running == 1)
        
    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        self.queue.put(WII_LOST)
        wm = cwiid.Wiimote()
        self.queue.put(WII_FOUND)
        #enable button reporting
        wm.rpt_mode = cwiid.RPT_BTN
        prevMsg=''
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            time.sleep(0.01)
            msg = ''
            if(wm.state['buttons'] & cwiid.BTN_A):
                msg += 'BTN_A'
            
            if(wm.state['buttons'] & cwiid.BTN_B):
                msg += 'BTN_B'
                
            #send only when change     
            if not (msg ==''or msg == prevMsg ):
                prevMsg = msg
                self.queue.put(msg)
