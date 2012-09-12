import time
import threading
import cwiid

#definations for  messages
LOST = 0
FOUND = 1
START =2
STOP = 3
SHOW_NEXT= 4
SHOW_PREV= 5

class Server:
    NOT_CONNECTED=0
    CONNECTED = 1
    

    def changeState(self,newState):
        self.state = newState

    def __init__(self, queue):
        self.running = 0
        self.queue = queue
        self.thread1 = None
        self.state = None
        
        
    def start(self):
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()
        
    def stop(self):
        self.running = 0
    
    def isRunning(self):
        return (self.running == 1)
        
    def workerThread1(self):
        self.changeState(self.NOT_CONNECTED)
        self.queue.put(LOST)
        wm = None
        while self.running:
            #######################################
            if ( self.state == self.NOT_CONNECTED):
                wm = cwiid.Wiimote()
                #enable button reporting
                wm.rpt_mode = cwiid.RPT_BTN
                self.queue.put(FOUND)
                self.changeState(self.CONNECTED)
               
            #######################################     
            elif ( self.state == self.CONNECTED): 
                msg = ''
                if(wm.state['buttons'] & cwiid.BTN_A):
                    msg = STOP
                if(wm.state['buttons'] & cwiid.BTN_B):
                    msg = START
                    
                #send only when change     
                if not (msg =='' ):
                    self.queue.put(msg)                    
            #####################################        
            time.sleep(0.01)