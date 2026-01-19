#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import img2pdf
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

class ImageToPdfApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to PDF Tool")
        self.root.geometry("650x550")
        # Set background color
        self.root.config(bg="#f0f8ff")
        
        # Define color scheme
        self.bg_color = "#f0f8ff"  # AliceBlue - light and fresh
        self.frame_bg = "#ffffff"  # White for frames
        self.button_bg = "#4a90e2"  # Soft blue for buttons
        self.button_hover = "#357abd"  # Darker blue for hover
        self.button_active = "#2a6496"  # Even darker for active
        self.text_color = "#333333"  # Dark gray for text
        self.included_color = "#e6ffe6"  # Light green for included
        self.excluded_color = "#ffe6e6"  # Light red for excluded
        self.border_color = "#dddddd"  # Light gray for borders
        
        # Variables
        self.image_folder = ""
        self.pdf_save_path = ""
        self.image_files = []
        self.dragged_item = None
        self.image_status = {}  # Dictionary to track image status: True for included, False for excluded
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Set up main frame with padding
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Image to PDF Tool", font=("Arial", 18, "bold"), 
                               bg=self.bg_color, fg=self.text_color)
        title_label.pack(pady=15)
        
        # Select image folder
        folder_frame = tk.Frame(main_frame, bg=self.bg_color)
        folder_frame.pack(pady=10, fill=tk.X)
        
        folder_label = tk.Label(folder_frame, text="Image Folder:", font=("Arial", 10, "bold"), 
                               bg=self.bg_color, fg=self.text_color)
        folder_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.folder_var = tk.StringVar()
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_var, width=50, 
                               font=("Arial", 10), bd=1, relief=tk.SOLID, bg="white")
        folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        folder_button = tk.Button(folder_frame, text="Browse", command=self.select_image_folder, 
                                 font=("Arial", 10), bg=self.button_bg, fg="white", 
                                 bd=1, relief=tk.SOLID)
        folder_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Select PDF save path
        save_frame = tk.Frame(main_frame, bg=self.bg_color)
        save_frame.pack(pady=10, fill=tk.X)
        
        save_label = tk.Label(save_frame, text="PDF Save Path:", font=("Arial", 10, "bold"), 
                             bg=self.bg_color, fg=self.text_color)
        save_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_var = tk.StringVar()
        save_entry = tk.Entry(save_frame, textvariable=self.save_var, width=50, 
                             font=("Arial", 10), bd=1, relief=tk.SOLID, bg="white")
        save_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        save_button = tk.Button(save_frame, text="Browse", command=self.select_pdf_save_path, 
                               font=("Arial", 10), bg=self.button_bg, fg="white", 
                               bd=1, relief=tk.SOLID)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Image listbox for reordering and exclusion
        listbox_frame = tk.Frame(main_frame, bg=self.bg_color)
        listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        listbox_label = tk.Label(listbox_frame, text="Image List (Drag to Reorder, Select to Exclude):", 
                                font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.text_color)
        listbox_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Create listbox with drag and drop functionality
        self.image_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=10, 
                                       font=("Arial", 10), bd=1, relief=tk.SOLID, 
                                       highlightthickness=1, selectbackground="#d4e6fc")
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to listbox
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind mouse events for drag and drop
        self.image_listbox.bind('<Button-1>', self.on_listbox_click)
        self.image_listbox.bind('<B1-Motion>', self.on_listbox_drag)
        self.image_listbox.bind('<ButtonRelease-1>', self.on_listbox_release)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Image count display
        self.image_count_var = tk.StringVar()
        self.image_count_var.set("Images detected: 0")
        image_count_label = tk.Label(main_frame, textvariable=self.image_count_var, 
                                   font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.text_color)
        image_count_label.pack(pady=10)
        
        # Create button frame for exclude and generate buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10, fill=tk.X)
        
        # Create delete button (left side, red)
        self.delete_button = tk.Button(button_frame, text="Exclude Selected Image", command=self.exclude_image, 
                                      font=("Arial", 10), bg="#e74c3c", fg="white", 
                                      bd=1, relief=tk.SOLID, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create generate button (right side, green)
        generate_button = tk.Button(button_frame, text="Generate PDF", command=self.generate_pdf, 
                                   font=("Arial", 12, "bold"), bg="#27ae60", fg="white", 
                                   bd=1, relief=tk.SOLID, width=20)
        generate_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def select_image_folder(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if folder_path:
            self.image_folder = folder_path
            self.folder_var.set(folder_path)
            self.load_images()
    
    def select_pdf_save_path(self):
        file_path = filedialog.asksaveasfilename(title="Select PDF Save Path", 
                                               defaultextension=".pdf",
                                               filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_save_path = file_path
            self.save_var.set(file_path)
    
    def load_images(self):
        # Supported image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        
        # Get images from folder
        self.image_files = []
        for file in os.listdir(self.image_folder):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                self.image_files.append(os.path.join(self.image_folder, file))
        
        # Sort by filename
        self.image_files.sort()
        
        # Initialize image status: all included by default
        self.image_status = {}
        for img_path in self.image_files:
            self.image_status[img_path] = True
        
        # Update image count display
        included_count = sum(1 for status in self.image_status.values() if status)
        self.image_count_var.set(f"Images detected: {len(self.image_files)} (Included: {included_count})")
        
        # Update listbox
        self.image_listbox.delete(0, tk.END)
        for img_path in self.image_files:
            img_name = os.path.basename(img_path)
            self.image_listbox.insert(tk.END, img_name)
            # Set initial background color to light green (included)
            index = self.image_files.index(img_path)
            self.image_listbox.itemconfig(index, {'bg': self.included_color})
    
    def on_listbox_click(self, event):
        # Get the index of the clicked item
        index = self.image_listbox.nearest(event.y)
        self.dragged_item = index
    
    def on_listbox_drag(self, event):
        # Get the index of the item under the cursor
        index = self.image_listbox.nearest(event.y)
        if index != self.dragged_item and index >= 0:
            # Swap items
            item = self.image_listbox.get(self.dragged_item)
            self.image_listbox.delete(self.dragged_item)
            self.image_listbox.insert(index, item)
            
            # Swap in the image_files list
            img = self.image_files[self.dragged_item]
            self.image_files.pop(self.dragged_item)
            self.image_files.insert(index, img)
            
            # Update the dragged item index
            self.dragged_item = index
            
            # Reapply colors after drag
            self.update_listbox_colors()
    
    def on_listbox_release(self, event):
        # Reset dragged item
        self.dragged_item = None
        # Ensure colors are correct after drag is complete
        self.update_listbox_colors()
    
    def update_listbox_colors(self):
        # Reapply colors to all listbox items based on their status
        for i, img_path in enumerate(self.image_files):
            status = self.image_status.get(img_path, True)
            if status:
                # Included - light green
                self.image_listbox.itemconfig(i, {'bg': self.included_color})
            else:
                # Excluded - light red
                self.image_listbox.itemconfig(i, {'bg': self.excluded_color})
    
    def on_listbox_select(self, event):
        # Enable delete button when an item is selected
        if self.image_listbox.curselection():
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)
    
    def create_rounded_frame(self, parent, radius):
        """Create a frame with rounded corners"""
        # Use a simpler approach with a regular frame
        # and a border to achieve a clean look
        frame = tk.Frame(parent, bg=self.frame_bg, 
                        bd=1, relief=tk.SOLID, 
                        highlightbackground=self.border_color,
                        highlightthickness=1)
        # Add some padding to create space inside the frame
        inner_frame = tk.Frame(frame, bg=self.frame_bg, padx=5, pady=5)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        return inner_frame
    
    def create_styled_button(self, parent, text, command, width=10, height=1, font_size=10, bold=False):
        """Create a styled button with hover and click effects"""
        # Create button with rounded corners
        button = tk.Button(parent, text=text, command=command, 
                         font=("Arial", font_size, "bold" if bold else "normal"),
                         width=width, height=height,
                         bg=self.button_bg, fg="white",
                         bd=0, relief=tk.FLAT,
                         cursor="hand2")
        
        # Add hover effect
        def on_enter(e):
            button.config(bg=self.button_hover)
            # Add subtle animation
            button.pack_configure(pady=(3, 7))
        
        def on_leave(e):
            button.config(bg=self.button_bg)
            # Reset animation
            button.pack_configure(pady=(5, 5))
        
        def on_press(e):
            button.config(bg=self.button_active)
            # Add press animation
            button.pack_configure(pady=(6, 4))
        
        def on_release(e):
            button.config(bg=self.button_hover)
            # Reset animation
            button.pack_configure(pady=(3, 7))
        
        # Bind events
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)
        
        return button
    
    def exclude_image(self):
        # Get selected item
        selected = self.image_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        img_path = self.image_files[index]
        
        # Toggle image status
        current_status = self.image_status.get(img_path, True)
        new_status = not current_status
        self.image_status[img_path] = new_status
        
        # Update listbox item color
        if new_status:
            # Included - light green
            self.image_listbox.itemconfig(index, {'bg': self.included_color})
        else:
            # Excluded - light red
            self.image_listbox.itemconfig(index, {'bg': self.excluded_color})
        
        # Update image count display
        included_count = sum(1 for status in self.image_status.values() if status)
        self.image_count_var.set(f"Images detected: {len(self.image_files)} (Included: {included_count})")
    
    def generate_pdf(self):
        # Check inputs
        if not self.image_folder:
            messagebox.showerror("Error", "Please select an image folder")
            return
        
        if not self.pdf_save_path:
            messagebox.showerror("Error", "Please select a PDF save path")
            return
        
        if len(self.image_files) == 0:
            messagebox.showerror("Error", "No images found in the selected folder")
            return
        
        # Filter included images
        included_images = [img_path for img_path in self.image_files if self.image_status.get(img_path, True)]
        
        if len(included_images) == 0:
            messagebox.showerror("Error", "No images selected for PDF generation")
            return
        
        try:
            # Convert images to PDF using the current order and only included images
            with open(self.pdf_save_path, "wb") as f:
                f.write(img2pdf.convert(included_images))
            
            messagebox.showinfo("Success", f"PDF generated successfully!\nSave path: {self.pdf_save_path}\nIncluded images: {len(included_images)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPdfApp(root)
    root.mainloop()