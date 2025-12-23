"""Visual feedback UI - Siri-like animated sphere overlay."""

import tkinter as tk
import math
import threading
import time
from pathlib import Path

class SiriUI:
    """Siri-like animated sphere overlay for voice feedback."""
    
    def __init__(self):
        """Initialize the UI overlay."""
        self.root = None
        self.canvas = None
        self.is_listening = False
        self.is_processing = False
        self.animation_thread = None
        self.running = False
        self.phase = 0
        
    def start(self):
        """Start the UI in a separate thread."""
        if not self.running:
            self.running = True
            ui_thread = threading.Thread(target=self._create_window, daemon=True)
            ui_thread.start()
            time.sleep(0.5)  # Wait for window to initialize
    
    def _create_window(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("Voice Assistant")
        
        # Window configuration
        window_size = 120
        self.root.geometry(f"{window_size}x{window_size}")
        
        # Position at top-right corner
        screen_width = self.root.winfo_screenwidth()
        x_position = screen_width - window_size - 20
        y_position = 20
        self.root.geometry(f"+{x_position}+{y_position}")
        
        # Make window transparent and always on top
        self.root.attributes('-alpha', 0.9)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=window_size,
            height=window_size,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Start animation
        self._animate()
        
        self.root.mainloop()
    
    def _animate(self):
        """Animate the sphere."""
        if not self.canvas or not self.running:
            return
        
        self.canvas.delete("all")
        center_x, center_y = 60, 60
        
        if self.is_listening:
            # Pulsing circles when listening
            self.phase += 0.1
            for i in range(3):
                radius = 20 + i * 15 + math.sin(self.phase + i) * 10
                alpha = int(255 * (1 - i / 3) * (0.5 + 0.5 * math.sin(self.phase)))
                color = f'#{alpha:02x}{alpha//2:02x}{255:02x}'  # Blue gradient
                
                self.canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline=color,
                    width=3,
                    fill=''
                )
        
        elif self.is_processing:
            # Spinning arc when processing
            self.phase += 0.15
            for i in range(4):
                angle = (self.phase + i * 90) % 360
                color = f'#00{int(200 + 55 * math.sin(self.phase + i)):02x}ff'
                
                self.canvas.create_arc(
                    20, 20, 100, 100,
                    start=angle,
                    extent=60,
                    outline=color,
                    width=4,
                    style=tk.ARC
                )
        
        else:
            # Idle state - small pulsing dot
            self.phase += 0.05
            radius = 8 + math.sin(self.phase) * 3
            brightness = int(100 + 100 * math.sin(self.phase))
            color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
            
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color,
                outline=''
            )
        
        # Schedule next frame
        if self.root:
            self.root.after(33, self._animate)  # ~30 FPS
    
    def set_listening(self, listening=True):
        """Set listening state."""
        self.is_listening = listening
        self.is_processing = False
    
    def set_processing(self, processing=True):
        """Set processing state."""
        self.is_processing = processing
        self.is_listening = False
    
    def set_idle(self):
        """Set idle state."""
        self.is_listening = False
        self.is_processing = False
    
    def stop(self):
        """Stop the UI."""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
