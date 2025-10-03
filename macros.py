from pynput import keyboard, mouse
import argparse
import os
import threading
import time
import pyautogui

write_lock = threading.RLock() #thread safe recording
nullTime = 0 #zero time for macro recording and playback
keysOnTime = {} #when a key is pressed, the key is added to the array,
                            #when a key is released, this key is searched in the array with the initial time,
                            #then the time the key is held in milliseconds is calculated
kController = keyboard.Controller() #create 2 controllers
mController = mouse.Controller() #in the sense of 2 objects
#pre-declared global variables
args = None
file = None
file_handler = None 
#global flags
ctrlActive: bool = False 
pressed: bool = False 
threadFlag: bool = True
execute: bool = False
writer: bool = False

#KEYBOARD DETECT FUNCTIONS
def onPress(key):
    with write_lock: #thread safe recording
        if key not in keysOnTime: #protection against repeated reactions when pressing a key
            keysOnTime[key] = time.perf_counter()  #start of counting
            print(f"Press{key}") #debug
            global file_handler #accesing a global variable to write to file
            file_handler.write(f"[KEYBOARD:PRESS:{key}:{time.perf_counter() - nullTime:.3f}]") #write to file
            file_handler.flush() #for reliability
            
def onRelease(key):
    with write_lock:
        if key in keysOnTime:
            print(f"Release {key} through {(time.perf_counter()-keysOnTime[key])*1000:.1f}ms") #debug
            file_handler.write(f"[KEYBOARD:RELEASE:{key}:{time.perf_counter() - nullTime:.3f}]") #recording a key to a file with the time it was held
            file_handler.flush()
            del keysOnTime[key] #clear a key in the buffer
#END KEYBOARD DETECT FUNCTIONS

#MOUSE DETECT FUNCTIONS
def onMove(x, y):
    with write_lock:
        global file_handler
        file_handler.write(f"[MOUSE:MOVE:{x},{y}:{time.perf_counter() - nullTime:.3f}]")
        file_handler.flush()
        print(f"Mouse move on {x}, {y}, on time:{time.perf_counter() - nullTime:.3f}") #debug
        
def onClick(x, y, key, pressed):
    with write_lock:
        global file_handler
        if pressed: #The library in relation to the mouse does not have "press" and "release" functions,
            if key not in keysOnTime:                       #but passes to "on_click" whether the key is pressed
                keysOnTime[key] = time.perf_counter()
                file_handler.write(f"[MOUSE:PRESS:{key}:{time.perf_counter() - nullTime:.3f}]")
                file_handler.flush()
                print(f"{key} press on {x},{y}") #debug
        else:
            if key in keysOnTime:
                file_handler.write(f"[MOUSE:RELEASE:{key}:{time.perf_counter() - nullTime:.3f}]")
                file_handler.flush()
                print(f"{key} release on {x},{y} for {(time.perf_counter()-keysOnTime[key])*1000:.1f}ms") #debug
                del keysOnTime[key]
                
def onScroll(x, y, dx, dy, key):
    with write_lock:
        global file_handler
        file_handler.write(f"[MOUSE:SCROLL:{'DOWN' if dy < 0 else 'UP'}:{time.perf_counter() - nullTime:.3f}]")
        file_handler.flush()
        print(f"Scroll {'down' if dy < 0 else 'up'} at {x},{y} ") #debug
#END MOUSE DETECT FUNCTIONS

def createMacros():
    global writer, file_handler, threadFlag, nullTime
    if not writer:
        print("Start writing macros") #debug
        writer = True
        threadFlag = True
        nullTime = time.perf_counter()
        kListener = keyboard.Listener(on_press=onPress, on_release=onRelease) #create 2 listeners
        mListener = mouse.Listener(on_move=onMove, on_click=onClick, on_scroll=onScroll) #in the sense of 2 objects
        try:
            if args.temp:
                file_handler = open(file, "x", encoding="utf-8")
            else:
                file_handler = open(file, "w", encoding="utf-8")
            print(file_handler, "open") #debug
            kListener.start()
            print(kListener, "start") #debug
            mListener.start()
            print(mListener, "start") #debug
            while True:
                #Threads working
                if not threadFlag:
                    break
                time.sleep(0.1)
        except FileExistsError:
            os.remove("temp.txt")
            print(FileExistsError, " fixed. Try again") #debug
            writer = False
            return
        finally:
            kListener.stop()
            print(kListener, "stop") #debug
            mListener.stop()
            print(mListener, "stop") #debug
            file_handler.close()
            print(file_handler, "close") #debug
            postProces()
            writer = False
    else: 
        print("Writing stop")
        writer = False
        threadFlag = False
        
        
def convertToKey(key):
    global pressed
    if key.startswith("'") and key.endswith("'"):
        content = key[1:-1]
        
        if content.startswith("\\x"):
            try:
                charCode = int(content[2:], 16)
                print(pressed)
                if ctrlActive:
                    if not pressed:
                        if charCode == 0x16:  # Ctrl+V
                            executeHotkey("v")
                            return None
                        elif charCode == 0x03:  # Ctrl+C
                            executeHotkey("c")
                            return None
                        elif charCode == 0x18:  # Ctrl+X
                            executeHotkey("x")
                            return None
                        elif charCode == 0x01: # Ctrl+A
                            executeHotkey("a")
                            return None
                        elif charCode == 0x1a: # Ctrl+Z
                            executeHotkey("z")
                            return None
                    else: pressed = False
                else:
                    return chr(charCode)
            except:
                return content
        else:
            return content
   
    elif key == "Key.esc": return keyboard.Key.esc
    elif key == "Key.f1": return keyboard.Key.f1
    elif key == "Key.f2": return keyboard.Key.f2
    elif key == "Key.f3": return keyboard.Key.f3
    elif key == "Key.f4": return keyboard.Key.f4
    elif key == "Key.f5": return keyboard.Key.f5
    elif key == "Key.f6": return keyboard.Key.f6
    elif key == "Key.f7": return keyboard.Key.f7
    elif key == "Key.f8": return keyboard.Key.f8
    elif key == "Key.f9": return keyboard.Key.f9
    elif key == "Key.f10": return keyboard.Key.f10
    elif key == "Key.f11": return keyboard.Key.f11
    elif key == "Key.f12": return keyboard.Key.f12
    elif key == "Key.f13": return keyboard.Key.f13
    elif key == "Key.f14": return keyboard.Key.f14
    elif key == "Key.f15": return keyboard.Key.f15
    elif key == "Key.f16": return keyboard.Key.f16
    elif key == "Key.f17": return keyboard.Key.f17
    elif key == "Key.f18": return keyboard.Key.f18
    elif key == "Key.f19": return keyboard.Key.f19
    elif key == "Key.f20": return keyboard.Key.f20
    elif key == "Key.print_screen": return keyboard.Key.print_screen
    elif key == "Key.scroll_lock": return keyboard.Key.scroll_lock
    elif key == "Key.pause": return keyboard.Key.pause
    elif key == "Key.insert": return keyboard.Key.insert
    elif key == "Key.delete": return keyboard.Key.delete
    elif key == "Key.home": return keyboard.Key.home
    elif key == "Key.end": return keyboard.Key.end
    elif key == "Key.page_up": return keyboard.Key.page_up
    elif key == "Key.page_down": return keyboard.Key.page_down
    elif key == "Key.up": return keyboard.Key.up
    elif key == "Key.down": return keyboard.Key.down
    elif key == "Key.left": return keyboard.Key.left
    elif key == "Key.right": return keyboard.Key.right
    elif key == "Key.backspace": return keyboard.Key.backspace
    elif key == "Key.enter": return keyboard.Key.enter
    elif key == "Key.tab": return keyboard.Key.tab
    elif key == "Key.caps_lock": return keyboard.Key.caps_lock
    elif key == "Key.num_lock": return keyboard.Key.num_lock
    elif key == "Key.space": return keyboard.Key.space
    elif key == "Key.menu": return keyboard.Key.menu
    elif key == "Key.shift": return keyboard.Key.shift
    elif key == "Key.shift_l": return keyboard.Key.shift_l
    elif key == "Key.shift_r": return keyboard.Key.shift_r
    elif key == "Key.ctrl": return keyboard.Key.ctrl
    elif key == "Key.ctrl_l": return keyboard.Key.ctrl_l
    elif key == "Key.ctrl_r": return keyboard.Key.ctrl_r
    elif key == "Key.alt": return keyboard.Key.alt
    elif key == "Key.alt_l": return keyboard.Key.alt_l
    elif key == "Key.alt_r": return keyboard.Key.alt_r
    elif key == "Key.alt_gr": return keyboard.Key.alt_gr
    elif key == "Key.cmd": return keyboard.Key.cmd
    elif key == "Key.cmd_l": return keyboard.Key.cmd_l
    elif key == "Key.cmd_r": return keyboard.Key.cmd_r
    elif key == "Key.media_play_pause": return keyboard.Key.media_play_pause
    elif key == "Key.media_volume_mute": return keyboard.Key.media_volume_mute
    elif key == "Key.media_volume_down": return keyboard.Key.media_volume_down
    elif key == "Key.media_volume_up": return keyboard.Key.media_volume_up
    elif key == "Key.media_previous": return keyboard.Key.media_previous
    elif key == "Key.media_next": return keyboard.Key.media_next
    
    elif key == "Key.num0": return keyboard.Key.num0
    elif key == "Key.num1": return keyboard.Key.num1
    elif key == "Key.num2": return keyboard.Key.num2
    elif key == "Key.num3": return keyboard.Key.num3
    elif key == "Key.num4": return keyboard.Key.num4
    elif key == "Key.num5": return keyboard.Key.num5
    elif key == "Key.num6": return keyboard.Key.num6
    elif key == "Key.num7": return keyboard.Key.num7
    elif key == "Key.num8": return keyboard.Key.num8
    elif key == "Key.num9": return keyboard.Key.num9
    elif key == "Key.num_add": return keyboard.Key.num_add
    elif key == "Key.num_subtract": return keyboard.Key.num_subtract
    elif key == "Key.num_multiply": return keyboard.Key.num_multiply
    elif key == "Key.num_divide": return keyboard.Key.num_divide
    elif key == "Key.num_enter": return keyboard.Key.num_enter
    elif key == "Key.num_decimal": return keyboard.Key.num_decimal
    
    elif key == "Button.left": return mouse.Button.left
    elif key == "Button.right": return mouse.Button.right
    elif key == "Button.middle": return mouse.Button.middle
    elif key == "Button.x1": return mouse.Button.x1
    elif key == "Button.x2": return mouse.Button.x2
    
    elif key.startswith("<") and key.endswith(">"): return None
    else:
        return key

def executeHotkey(key): #hotkeys 
    global pressed
    if key == "v":
        pyautogui.hotkey("ctrl", "v")
        pressed = True
        print("Ctrl+V execute")
    elif key == "c":
        pyautogui.hotkey("ctrl", "c")
        pressed = True
        print("Ctrl+C execute")
    elif key == "x":
        pyautogui.hotkey("ctrl", "x")
        pressed = True
        print("Ctrl+X execute")
    elif key == "a":
        pyautogui.hotkey("ctrl", "a")
        pressed = True
        print("Ctrl+A execute")
    elif key == "z":
        pyautogui.hotkey("ctrl", "z")
        pressed = True
        print("Ctrl+Z execute")

def postProces(): #delete last 3 instruction because they press but do not release the keys
    print("Post processing")
    try: 
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        counter = 0
        while counter < 3 and text:
            if text[-1] == "]":
                lastLabel = text.rfind("[")
                if lastLabel != -1:
                    text = text[:lastLabel]
                    counter += 1
                else: break
            else: text = text[:-1]
        with open(file, "w", encoding="utf-8") as f:
            f.write(text)
        print("Post processing complete")
    except Exception as e:
        print(f"{e} need to fix")

def parseText(text): #read in blocks from [ to ]
    global execute
    instructionArray = [] #one complete instruction
    word = "" #a word is some meaning between :
    instructionFlag: bool = False
    for i in text:
        if execute:
            if i == "[": 
                instructionFlag = True
                continue
            elif i == "]": 
                instructionFlag = False
                if word:
                    instructionArray.append(word)
                word = ""
                parseInstr(instructionArray) #complete instruction
                instructionArray = [] #clean instruction
            elif instructionFlag:
                if not i == ":" and not i == ",":
                    word += i
                else: 
                    if word:
                        instructionArray.append(word)
                        word = ""
        else: return False
    print("Execute macros complete") #debug

def parseInstr(instructionArray):
    if execute:
        print(instructionArray) #debug
        global kController, mController, ctrlActive 
        fileRelativeTime = float(instructionArray[-1])
        currentRelativeTime = time.perf_counter() - nullTime
        sleepTime = round(fileRelativeTime - currentRelativeTime, 3)
        if sleepTime > 0:
                time.sleep(sleepTime)
        if instructionArray[0] == "KEYBOARD":
            convertedKey = convertToKey(instructionArray[2])
            if instructionArray[1] == "PRESS":
                if convertedKey is not None:
                    if instructionArray[2] == "Key.ctrl_l":
                        ctrlActive = True
                        print(ctrlActive) #debug
                    kController.press(convertedKey)   
            elif instructionArray[1] == "RELEASE":
                if convertedKey is not None:
                    if instructionArray[2] == "Key.ctrl_l":
                        ctrlActive = False
                        print(ctrlActive) #debug
                    kController.release(convertedKey)
        elif instructionArray[0] == "MOUSE":
            if instructionArray[1] == "MOVE":
                mController.position = (instructionArray[2], instructionArray[3])
            elif instructionArray[1] == "SCROLL":
                if instructionArray[2] == "UP":
                    mController.scroll(0, 1)
                elif instructionArray[2] == "DOWN":
                    mController.scroll(0, -1)
            elif instructionArray[1] == "PRESS":
                mController.press(convertToKey(instructionArray[2]))
            elif instructionArray[1] == "RELEASE":
                mController.release(convertToKey(instructionArray[2]))

def executeMacros():
    global execute, nullTime
    if not execute:
        execute = True
        print("Start execute macros") #debug
        nullTime = time.perf_counter()
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            parseText(content)
        execute = False
    else: 
        print("Execute stop") #debug
        execute = False
        
def safeExit():
    try:
        global threadFlag, writer, execute
        threadFlag = False
        writer = False
        execute = False
        
        if args and args.temp and os.path.exists("temp.txt"):
            os.remove("temp.txt")
    except Exception as e:
        print(f"Cleanup error: {e}")
    finally:
        print("Exit") #debug
        exit()
    
def main():
    global args, file
    parser = argparse.ArgumentParser(prog="Macrosos",
                                                            description="Utility for create and execute macros",
                                                            epilog="""
To start record macro press CTRL+ALT+W(rite)
To start execute recorded macro press CTRL+ALT+E(xecute)
To exit from script press CTRL+L(eave)
""", formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", type=str, help="Specify the file in which the macro will be written/read")
    group.add_argument("-t", "--temp", action="store_true", help="Temporary file for creating and using a macro (it will be deleted after the program is turned off)")
    
    args = parser.parse_args()
    if args.file:
        file = args.file
    elif args.temp:
        file = "temp.txt"
    
    with keyboard.GlobalHotKeys({
    "<ctrl>+<alt>+w": lambda: threading.Thread(target=createMacros, daemon=True).start(),
    "<ctrl>+<alt>+e": lambda: threading.Thread(target=executeMacros, daemon=True).start(),
    "<ctrl>+l": lambda: safeExit()}) as hotkey:
        hotkey.join()

if __name__ == "__main__":
    print("Launch script, waiting for hotkeys")
    main()