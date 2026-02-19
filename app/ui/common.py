import customtkinter as ctk

class HorizontalScrollWrapper(ctk.CTkFrame):
    """
    A wrapper that provides horizontal scrolling for its contents.
    Ensures the inner content stretches to full width if possible.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Use canvas for horizontal scroll
        bg_color = master._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.canvas = ctk.CTkCanvas(self, height=kwargs.get("height", 400), 
                                   bg=bg_color,
                                   highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        # Inner frame to hold content
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Handle canvas resizing - Stretch inner frame to match canvas width"""
        self.canvas.itemconfigure(self.canvas_window, height=event.height)
        
        # Crucial: Always set the window width to at least the canvas width
        # This makes the table "Full" width.
        # If the content inside (table) is even wider, _on_frame_configure will expand scrollregion.
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
