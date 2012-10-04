import time
import threading
import cwiid

#definations for  messages
LOST = 0
FOUND = 1
START_COUNTDOWN = 2
STOP_RACETIMER = 3
SHOW_NEXT =  4
SHOW_PREV =  5
SHOW_TIME = 6
HIDE_TIME = 7
RESET_RACETIMER = 8
INTERMEDIATE = 9
SHOW_HELP = 10
HIDE_HELP =11

class Server:
    NOT_CONNECTED=0
    CONNECTED = 1
    def rumble(self, state):
        self.wm.rumble = state
    def leds(self,no):
        
        ledsTolit=0    
        if no == 1: 
            ledsTolit=1
        elif no == 2: 
            ledsTolit=3
        elif no == 3: 
            ledsTolit=7
        elif no == 4: 
            ledsTolit=15
        else: 
            ledsTolit =15
            
        self.wm.led =ledsTolit
        
    def changeState(self,newState):
        self.state = newState

    def __init__(self, queue):
        self.running = 0
        self.queue = queue
        self.thread1 = None
        self.state = None
        self.wm = None 
        
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
        
        TimeOn={}
        SLEEP_TIME=0.01
        
        while self.running:
            #######################################
            if ( self.state == self.NOT_CONNECTED):
                try:
                    self.wm = cwiid.Wiimote()
                    #enable button reporting
                    self.wm.rpt_mode = cwiid.RPT_BTN
                    self.queue.put(FOUND)
                    self.changeState(self.CONNECTED)
                    TimeOn[cwiid.BTN_1] = 0
                    TimeOn[cwiid.BTN_HOME] = 0
                except:
                    pass
                
            #######################################     
            elif ( self.state == self.CONNECTED): 
                
                #User must hold A button some while before we send stop message
                if(self.wm.state['buttons'] & cwiid.BTN_A):
                    TimeOn[cwiid.BTN_A]+=1
                    if (TimeOn[cwiid.BTN_A]==1 and self.wm.state['buttons'] & cwiid.BTN_B):
                        self.queue.put(INTERMEDIATE)
                    elif (TimeOn[cwiid.BTN_A]==150):
                        self.queue.put(STOP_RACETIMER) 
                    elif (TimeOn[cwiid.BTN_A]==300):
                        self.queue.put(RESET_RACETIMER)
                else:#reset counter when button released
                    TimeOn[cwiid.BTN_A] = 0
                       
                if(self.wm.state['buttons'] & cwiid.BTN_B):
                    if not(TimeOn[cwiid.BTN_B]):
                        TimeOn[cwiid.BTN_B] = 1
                        self.queue.put( START_COUNTDOWN )
                else:
                    TimeOn[cwiid.BTN_B] = 0  
                
                if(self.wm.state['buttons'] & cwiid.BTN_RIGHT ):
                    if not (TimeOn[cwiid.BTN_RIGHT]):
                        TimeOn[cwiid.BTN_RIGHT] = 1
                        self.queue.put( SHOW_NEXT )
                else:
                    TimeOn[cwiid.BTN_RIGHT] = 0  

                if(self.wm.state['buttons'] & cwiid.BTN_LEFT ):
                    if not (TimeOn[cwiid.BTN_LEFT]):
                        TimeOn[cwiid.BTN_LEFT] = 1
                        self.queue.put( SHOW_PREV )
                else:
                    TimeOn[cwiid.BTN_LEFT] = 0  
            
                if(self.wm.state['buttons'] & cwiid.BTN_1 ):
                    if not (TimeOn[cwiid.BTN_1]):
                        TimeOn[cwiid.BTN_1] = 1
                        self.queue.put( SHOW_TIME )
                else:
                    if(TimeOn[cwiid.BTN_1] == 1):
                        TimeOn[cwiid.BTN_1] = 0  
                        self.queue.put( HIDE_TIME )
                        
                if(self.wm.state['buttons'] & cwiid.BTN_HOME ):
                    if not (TimeOn[cwiid.BTN_HOME]):
                        TimeOn[cwiid.BTN_HOME] = 1
                        self.queue.put( SHOW_HELP )
                else:
                    if(TimeOn[cwiid.BTN_HOME] == 1):
                        TimeOn[cwiid.BTN_HOME] = 0  
                        self.queue.put( HIDE_HELP )               
            #####################################
            
            time.sleep(SLEEP_TIME)