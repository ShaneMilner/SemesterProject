# Randall Milner
# CS3080
# Semester Project
# Image Filter App


# tkinter is used to create the graphical user interface.
import tkinter as tk
from tkinter import filedialog, messagebox


# PIL/Pillow is used to open, display, edit, and save images.
from PIL import Image, ImageTk, ImageFilter, ImageOps


# OpenCV and NumPy are used for more advanced image processing.
import cv2
import numpy as np



# BaseFilter is the parent class for all image filters.
# It defines the structure that every filter class should follow.
class BaseFilter:
    def apply(self, image):
        # This method is meant to be overridden by child classes.
        raise NotImplementedError("Subclasses must implement apply method.")



# GrayscaleFilter inherits from BaseFilter.
# It converts the image to black and white.
class GrayscaleFilter(BaseFilter):
    def apply(self, image):
        return ImageOps.grayscale(image).convert("RGB")



# BlurFilter inherits from BaseFilter.
# It applies a Gaussian blur to smooth the image.
class BlurFilter(BaseFilter):
    def apply(self, image):
        return image.filter(ImageFilter.GaussianBlur(radius=4))



# EdgeFilter inherits from BaseFilter.
# It detects the edges/outlines in the image.
class EdgeFilter(BaseFilter):
    def apply(self, image):
        return image.filter(ImageFilter.FIND_EDGES)



# CartoonifyFilter inherits from BaseFilter.
# It creates a cartoon/poster style effect using OpenCV.
class CartoonifyFilter(BaseFilter):
    def apply(self, image):
        # Convert the PIL image into a NumPy array so OpenCV can process it.
        img_array = np.array(image.convert("RGB"))

        # Smooth the image while keeping some edge detail.
        color = cv2.bilateralFilter(
            img_array,
            d=15,
            sigmaColor=200,
            sigmaSpace=200
        )

        # Reshape image data into a list of pixels for color clustering.
        data = np.float32(color).reshape((-1, 3))

        # Criteria tells k-means when to stop processing.
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            20,
            1.0
        )

        # k controls how many main colors the image is reduced to.
        k = 8

        # k-means reduces the image colors to a smaller set of colors.
        _, labels, centers = cv2.kmeans(
            data,
            k,
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS
        )

        # Convert the color centers back to normal image values.
        centers = np.uint8(centers)

        # Replace every pixel with one of the simplified colors.
        posterized = centers[labels.flatten()]
        posterized = posterized.reshape(img_array.shape)

        # Convert the image to grayscale to prepare for edge detection.
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Median blur reduces noise before finding edges.
        gray = cv2.medianBlur(gray, 7)

        # Adaptive threshold creates bold black-and-white edge outlines.
        edges = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            5
        )

        # Convert edges back into RGB format.
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        # Combine simplified colors with the edge mask.
        cartoon = cv2.bitwise_and(posterized, edges)

        # Convert to HSV so saturation and brightness can be adjusted.
        hsv = cv2.cvtColor(cartoon, cv2.COLOR_RGB2HSV)

        # Increase color saturation.
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255)

        # Slightly increase brightness.
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)

        # Convert back to RGB format.
        cartoon = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        # Convert the NumPy array back into a PIL image.
        return Image.fromarray(cartoon)



# ImageFilterApp controls the main application window and user interaction.
class ImageFilterApp:
    def __init__(self, root):
        # Store the main tkinter window.
        self.root = root
        
        # Stores a history of all filters used so that, when saved, the filters are 
        # all applied to the newly created image instead of editing the original.
        self.filter_history = []

        # Set window title, size, and allow resizing.
        self.root.title("Image Filter App")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # Stores the original image loaded by the user.
        self.original_image = None

        # Stores the image currently being edited.
        self.current_image = None

        # Stores the tkinter-compatible image for display.
        self.display_image = None

        # Dictionary connects button names to filter objects.
        self.filters = {
            "Grayscale": GrayscaleFilter(),
            "Blur": BlurFilter(),
            "Edge Detection": EdgeFilter(),
            "Cartoonify": CartoonifyFilter()
        }

        # Build the app layout.
        self.create_widgets()


    # Creates all labels, frames, and buttons in the app.
    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Image Filter App",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=10)

        # Frame that holds the image display area.
        self.image_frame = tk.Frame(self.root, bg="lightgray")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Prevents the frame from resizing itself based only on its contents.
        self.image_frame.pack_propagate(False)

        # Label used to display the image.
        self.image_label = tk.Label(
            self.image_frame,
            text="No image selected",
            bg="lightgray"
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # When the frame changes size, resize the displayed image.
        self.image_frame.bind("<Configure>", self.resize_image)

        # Frame that holds all buttons.
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Open Image", command=self.open_image).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Grayscale", command=lambda: self.apply_filter("Grayscale")).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Blur", command=lambda: self.apply_filter("Blur")).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Edge Detection", command=lambda: self.apply_filter("Edge Detection")).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Cartoonify", command=lambda: self.apply_filter("Cartoonify")).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset_image).grid(row=0, column=5, padx=5)
        tk.Button(button_frame, text="Save Image", command=self.save_image).grid(row=0, column=6, padx=5)


    # Opens an image file from the user's computer.
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")
            ]
        )

        if file_path:
            full_image = Image.open(file_path).convert("RGB")

            # Keep full-resolution original for saving later
            self.original_image = full_image.copy()

            # Create a smaller working version for performance
            max_work_size = 900  # adjust for speed vs quality

            work_image = full_image.copy()
            work_image.thumbnail((max_work_size, max_work_size), Image.Resampling.LANCZOS)

            self.current_image = work_image

            # Display uses resized version anyway, so user won’t notice
            self.show_image(self.current_image)


    # Displays the current image in the app window.
    def show_image(self, image):
        if image is None:
            return

        # Get the current size of the image display frame.
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        # Get the full window height.
        window_height = self.root.winfo_height()

        # Reserve space for the title and buttons.
        max_height = window_height - 180

        # Default size used before tkinter fully calculates the frame size.
        if frame_width < 10 or frame_height < 10:
            frame_width = 750
            max_height = 450

        display = image.copy()

        # Resize image for display without changing the actual saved image.
        display.thumbnail((frame_width, max_height), Image.Resampling.LANCZOS)

        # Convert PIL image into a tkinter-compatible image.
        self.display_image = ImageTk.PhotoImage(display)

        # Place image inside the label.
        self.image_label.config(image=self.display_image, text="")


    # Automatically resizes the image when the window size changes.
    def resize_image(self, event):
        if self.current_image is not None:
            self.show_image(self.current_image)


    # Applies the selected filter to the current image.
    def apply_filter(self, filter_name):
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        selected_filter = self.filters[filter_name]

        # Apply filter to current image (for display)
        self.current_image = selected_filter.apply(self.current_image)

        # Save filter to history
        self.filter_history.append(filter_name)

        self.show_image(self.current_image)


    # Restores the image back to the original version.
    def reset_image(self):
        # Check if an image has been loaded
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        # Define the maximum size for the working image
        # This keeps processing fast while still looking good in the UI
        max_work_size = 900

        # Create a copy of the original image so it remains unchanged
        work_image = self.original_image.copy()

        # Resize the working image if it is too large
        # thumbnail() preserves aspect ratio while reducing resolution
        work_image.thumbnail((max_work_size, max_work_size), Image.Resampling.LANCZOS)

        # Set the resized image as the current working image
        # This ensures filters are applied to a smaller, faster version
        self.current_image = work_image

        # Clear the filter history since we are returning to the original state
        self.filter_history = []

        # Display the reset image in the UI
        self.show_image(self.current_image)


    # Saves the edited image to the user's computer.
    def save_image(self):
        if self.original_image is None:
            messagebox.showwarning("No Image", "There is no image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG Files", "*.jpg"),
                ("PNG Files", "*.png"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            # Start from original image
            image_to_save = self.original_image.copy()

            # Reapply ALL filters in order
            for filter_name in self.filter_history:
                selected_filter = self.filters[filter_name]
                image_to_save = selected_filter.apply(image_to_save)

            # Save new image
            if file_path.lower().endswith(".jpg"):
                image_to_save.save(file_path, quality=90, optimize=True)
            else:
                image_to_save.save(file_path, optimize=True)

            messagebox.showinfo("Saved", "New image saved successfully!")


# main creates the tkinter window and starts the app.
def main():
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()


# This makes sure the program only runs when this file is executed directly.
if __name__ == "__main__":
    main()