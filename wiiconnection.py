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
    #These are quick and nasty hacks...FIX
    def rumble(self):
        self.rumbleState=15
    def leds(self,no):
        if no == 0: 
            self.ledsTolit=0    
        elif no == 1: 
            self.ledsTolit=1
        elif no == 2: 
            self.ledsTolit=3
        elif no == 3: 
            self.ledsTolit=7
        elif no == 4: 
            self.ledsTolit=15
        else: 
            self.ledsTolit =15
            
        print no
        self.setLed =1;
        
    def changeState(self,newState):
        self.state = newState

    def __init__(self, queue):
        self.running = 0
        self.queue = queue
        self.thread1 = None
        self.state = None
        self.rumbleState=0
        self.ledsTolit = 0
        self.setLed =0 
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
                    if not(TimeOn[cwiid.BTN_B]):
                        TimeOn[cwiid.BTN_B] = 1
                        self.queue.put( START )
                else:
                    TimeOn[cwiid.BTN_B] = 0  
                
                if(wm.state['buttons'] & cwiid.BTN_RIGHT ):
                    if not (TimeOn[cwiid.BTN_RIGHT]):
                        TimeOn[cwiid.BTN_RIGHT] = 1
                        self.queue.put( SHOW_NEXT )
                else:
                    TimeOn[cwiid.BTN_RIGHT] = 0  

                if(wm.state['buttons'] & cwiid.BTN_LEFT ):
                    if not (TimeOn[cwiid.BTN_LEFT]):
                        TimeOn[cwiid.BTN_LEFT] = 1
                        self.queue.put( SHOW_PREV )
                else:
                    TimeOn[cwiid.BTN_LEFT] = 0  
                                       
            #####################################
            if (self.rumbleState):
                wm.rumble=1
                self.rumbleState -= 1
                if not self.rumbleState:
                    wm.rumble =0
            
            
            
            if self.setLed:
                self.setLed =0
                wm.led =  self.ledsTolit
                          
            time.sleep(SLEEP_TIME)
            
            
            
            
            
            