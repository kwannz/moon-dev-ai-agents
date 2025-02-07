"""
Coordinate Finder Tool
Helps find screen coordinates for automation scripts
"""

import os
import sys
import time
from pathlib import Path
import pyautogui
import keyboard
from termcolor import cprint

def get_mouse_position():
    """Get current mouse position"""
    x, y = pyautogui.position()
    return x, y

def main():
    """Main function for coordinate finding"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\nCoordinate Finder Tool")
    print("Press 'p' to print coordinates")
    print("Press 'q' to quit\n")
    
    try:
        while True:
            if keyboard.is_pressed('p'):
                x, y = get_mouse_position()
                print(f"Current position: ({x}, {y})")
                time.sleep(0.5)
            elif keyboard.is_pressed('q'):
                print("\nExiting coordinate finder...")
                break
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting coordinate finder...")

if __name__ == "__main__":
    main()
