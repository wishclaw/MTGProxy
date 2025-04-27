import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class CardPDFCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Playing Card PDF Creator")
        self.root.geometry("600x500")
        
        # Variables
        self.input_folder = StringVar()
        self.output_pdf = StringVar()
        self.card_width = DoubleVar(value=2.5)
        self.card_height = DoubleVar(value=3.5)
        self.margin = DoubleVar(value=0.25)
        self.dpi = IntVar(value=300)
        self.progress = IntVar()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Input folder selection
        ttk.Label(main_frame, text="Card Images Folder:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky=EW, padx=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # Output PDF selection
        ttk.Label(main_frame, text="Output PDF File:").grid(row=1, column=0, sticky=W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_pdf, width=50).grid(row=1, column=1, sticky=EW, padx=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        # Card dimensions
        ttk.Label(main_frame, text="Card Dimensions (inches):").grid(row=2, column=0, sticky=W, pady=5)
        ttk.Spinbox(main_frame, textvariable=self.card_width, from_=1.0, to=5.0, increment=0.1, width=5).grid(row=2, column=1, sticky=W, padx=5)
        ttk.Label(main_frame, text="x").grid(row=2, column=1, sticky=N)
        ttk.Spinbox(main_frame, textvariable=self.card_height, from_=1.0, to=5.0, increment=0.1, width=5).grid(row=2, column=1, sticky=E, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=EW, pady=10)
        
        ttk.Label(settings_frame, text="Margin (inches):").grid(row=0, column=0, sticky=W)
        ttk.Spinbox(settings_frame, textvariable=self.margin, from_=0.1, to=1.0, increment=0.05, width=5).grid(row=0, column=1, sticky=W, padx=5)
        
        ttk.Label(settings_frame, text="DPI (quality):").grid(row=1, column=0, sticky=W)
        ttk.Spinbox(settings_frame, textvariable=self.dpi, from_=72, to=600, increment=50, width=5).grid(row=1, column=1, sticky=W, padx=5)
        
        # Preview button
        ttk.Button(main_frame, text="Preview Layout", command=self.preview_layout).grid(row=4, column=0, pady=10)
        
        # Create PDF button
        ttk.Button(main_frame, text="Create PDF", command=self.create_pdf).grid(row=4, column=1, pady=10, sticky=E)
        
        # Progress bar
        ttk.Progressbar(main_frame, variable=self.progress, maximum=100).grid(row=5, column=0, columnspan=3, sticky=EW, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky=W)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select folder containing card images")
        if folder:
            self.input_folder.set(folder)
            
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file:
            self.output_pdf.set(file)
    
    def preview_layout(self):
        if not self.validate_inputs():
            return
            
        try:
            # Calculate layout
            card_width_pt = self.card_width.get() * 72
            card_height_pt = self.card_height.get() * 72
            margin_pt = self.margin.get() * 72
            
            page_width, page_height = letter
            usable_width = page_width - 2 * margin_pt
            usable_height = page_height - 2 * margin_pt
            
            cards_per_row = int(usable_width // card_width_pt)
            cards_per_col = int(usable_height // card_height_pt)
            
            # Show preview window
            preview = Toplevel(self.root)
            preview.title("Layout Preview")
            
            # Create a canvas to show the layout
            canvas_width = 400
            canvas_height = int(canvas_width * (page_height/page_width))
            
            preview_canvas = Canvas(preview, width=canvas_width, height=canvas_height, bg="white")
            preview_canvas.pack(padx=10, pady=10)
            
            # Scale factor for display
            scale = canvas_width / page_width
            
            # Draw page outline
            preview_canvas.create_rectangle(
                0, 0, canvas_width, canvas_height,
                outline="black", width=2
            )
            
            # Draw card positions
            for row in range(cards_per_col):
                for col in range(cards_per_row):
                    x = margin_pt * scale + col * card_width_pt * scale
                    y = margin_pt * scale + row * card_height_pt * scale
                    
                    preview_canvas.create_rectangle(
                        x, y,
                        x + card_width_pt * scale,
                        y + card_height_pt * scale,
                        outline="blue", width=1, dash=(2,2)
                    )
            
            # Add info label
            ttk.Label(preview, text=f"Layout: {cards_per_row} cards wide × {cards_per_col} cards tall").pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not generate preview:\n{str(e)}")
    
    def validate_inputs(self):
        if not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return False
            
        if not self.output_pdf.get():
            messagebox.showerror("Error", "Please specify an output PDF file")
            return False
            
        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", "The input folder does not exist")
            return False
            
        return True
    
    def create_pdf(self):
        if not self.validate_inputs():
            return
            
        try:
            self.status_label.config(text="Working...", foreground="blue")
            self.root.update()
            
            # Convert inches to points (1 inch = 72 points)
            card_width_pt = self.card_width.get() * 72
            card_height_pt = self.card_height.get() * 72
            margin_pt = self.margin.get() * 72
            
            # Get list of image files
            image_files = [
                f for f in os.listdir(self.input_folder.get()) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
            ]
            
            if not image_files:
                messagebox.showerror("Error", "No image files found in the input folder")
                return
            
            # Calculate how many cards fit on a letter-sized page
            page_width, page_height = letter
            usable_width = page_width - 2 * margin_pt
            usable_height = page_height - 2 * margin_pt
            
            cards_per_row = int(usable_width // card_width_pt)
            cards_per_col = int(usable_height // card_height_pt)
            cards_per_page = cards_per_row * cards_per_col
            
            # Create PDF
            c = canvas.Canvas(self.output_pdf.get(), pagesize=letter)
            total_images = len(image_files)
            
            for i, image_file in enumerate(image_files):
                # Update progress
                self.progress.set(int((i+1)/total_images * 100))
                self.status_label.config(text=f"Processing {i+1} of {total_images}...")
                self.root.update()
                
                if i % cards_per_page == 0 and i > 0:
                    c.showPage()  # New page after each full page of cards
                
                # Calculate position on page
                page_pos = i % cards_per_page
                row = page_pos // cards_per_row
                col = page_pos % cards_per_row
                
                x = margin_pt + col * card_width_pt
                y = page_height - margin_pt - (row + 1) * card_height_pt  # PDF coordinates start at bottom
                
                # Open and resize image
                img_path = os.path.join(self.input_folder.get(), image_file)
                try:
                    img = Image.open(img_path)
                    img_reader = ImageReader(img)
                    
                    # Draw the image
                    c.drawImage(img_reader, x, y, width=card_width_pt, height=card_height_pt, preserveAspectRatio=True)
                    
                    # Add a border around each card
                    c.rect(x, y, card_width_pt, card_height_pt)
                    
                except Exception as e:
                    print(f"Error processing {image_file}: {str(e)}")
                    continue
            
            c.save()
            self.progress.set(100)
            self.status_label.config(text=f"Success! Created PDF with {total_images} cards", foreground="green")
            messagebox.showinfo("Success", f"PDF created successfully at:\n{self.output_pdf.get()}")
            
        except Exception as e:
            self.status_label.config(text="Error creating PDF", foreground="red")
            messagebox.showerror("Error", f"Failed to create PDF:\n{str(e)}")
        finally:
            self.progress.set(0)

if __name__ == "__main__":
    root = Tk()
    app = CardPDFCreator(root)
    root.mainloop()