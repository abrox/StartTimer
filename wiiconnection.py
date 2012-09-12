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
        TimeOn={}
        SLEEP_TIME=0.01
        while self.running:
            #######################################
            if ( self.state == self.NOT_CONNECTED):
                try:
                    wm = cwiid.Wiimote()
                    #enable button reporting
                    wm.rpt_mode = cwiid.RPT_BTN
                    self.queue.put(FOUND)
                    self.changeState(self.CONNECTED)
                except:
                    pass
                
            #######################################     
            elif ( self.state == self.CONNECTED): 
                
                #User must hold A button some while before we send stop message
                if(wm.state['buttons'] & cwiid.BTN_A):
                    TimeOn[cwiid.BTN_A]+=1
                    if (TimeOn[cwiid.BTN_A]*SLEEP_TIME >= 1.5):
                        TimeOn[cwiid.BTN_A] = 0
                        self.queue.put(STOP) 
                else:#reset counter when button released
                    TimeOn[cwiid.BTN_A] = 0
                       
                if(wm.state['buttons'] & cwiid.BTN_B):
                    if(TimeOn[cwiid.BTN_B]):
                        TimeOn[cwiid.BTN_B] = 1
                        self.queue.put( START )
                else:
                    TimeOn[cwiid.BTN_B] = 0  
                
                if(wm.state['buttons'] & cwiid.BTN_RIGHT ):
                    if(TimeOn[cwiid.BTN_RIGHT]==0):
                        TimeOn[cwiid.BTN_RIGHT] = 1
                        self.queue.put( SHOW_NEXT )
                else:
                    TimeOn[cwiid.BTN_RIGHT] = 0  

                if(wm.state['buttons'] & cwiid.BTN_LEFT ):
                    if(TimeOn[cwiid.BTN_LEFT]==0):
                        TimeOn[cwiid.BTN_LEFT] = 1
                        self.queue.put( SHOW_PREV )
                else:
                    TimeOn[cwiid.BTN_LEFT] = 0  
                                       
            #####################################        
            time.sleep(SLEEP_TIME)
            