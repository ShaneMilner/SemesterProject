# Randall Milner
# CS3080
# Semester Project
# Image Filter App





import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps
import cv2
import numpy as np


class BaseFilter:
    def apply(self, image):
        raise NotImplementedError("Subclasses must implement apply method.")


class GrayscaleFilter(BaseFilter):
    def apply(self, image):
        return ImageOps.grayscale(image).convert("RGB")


class BlurFilter(BaseFilter):
    def apply(self, image):
        return image.filter(ImageFilter.GaussianBlur(radius=4))


class EdgeFilter(BaseFilter):
    def apply(self, image):
        return image.filter(ImageFilter.FIND_EDGES)


class CartoonifyFilter(BaseFilter):
    def apply(self, image):
        img_array = np.array(image.convert("RGB"))

        # Smooth colors heavily
        color = cv2.bilateralFilter(img_array, d=15, sigmaColor=200, sigmaSpace=200)

        # Reduce number of colors for a poster/cartoon effect
        data = np.float32(color).reshape((-1, 3))
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            20,
            1.0
        )

        k = 8
        _, labels, centers = cv2.kmeans(
            data,
            k,
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS
        )

        centers = np.uint8(centers)
        posterized = centers[labels.flatten()]
        posterized = posterized.reshape(img_array.shape)

        # Create thick black edges
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 7)

        edges = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            5
        )

        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        cartoon = cv2.bitwise_and(posterized, edges)

        # Slightly boost brightness and saturation
        hsv = cv2.cvtColor(cartoon, cv2.COLOR_RGB2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)
        cartoon = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        return Image.fromarray(cartoon)


class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Filter App")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.original_image = None
        self.current_image = None
        self.display_image = None

        self.filters = {
            "Grayscale": GrayscaleFilter(),
            "Blur": BlurFilter(),
            "Edge Detection": EdgeFilter(),
            "Cartoonify": CartoonifyFilter()
        }

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Image Filter App",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=10)

        self.image_frame = tk.Frame(self.root, bg="lightgray")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_frame.pack_propagate(False)

        self.image_label = tk.Label(
            self.image_frame,
            text="No image selected",
            bg="lightgray"
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.image_frame.bind("<Configure>", self.resize_image)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Open Image", command=self.open_image).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Grayscale", command=lambda: self.apply_filter("Grayscale")).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Blur", command=lambda: self.apply_filter("Blur")).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Edge Detection", command=lambda: self.apply_filter("Edge Detection")).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Cartoonify", command=lambda: self.apply_filter("Cartoonify")).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset_image).grid(row=0, column=5, padx=5)
        tk.Button(button_frame, text="Save Image", command=self.save_image).grid(row=0, column=6, padx=5)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")
            ]
        )

        if file_path:
            self.original_image = Image.open(file_path).convert("RGB")
            self.current_image = self.original_image.copy()
            self.show_image(self.current_image)

    def show_image(self, image):
        if image is None:
            return

        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        window_height = self.root.winfo_height()

        # Reserve space for title + buttons (~150px)
        max_height = window_height - 180

        if frame_width < 10 or frame_height < 10:
            frame_width = 750
            max_height = 450

        display = image.copy()
        display.thumbnail((frame_width, max_height), Image.Resampling.LANCZOS)

        self.display_image = ImageTk.PhotoImage(display)
        self.image_label.config(image=self.display_image, text="")
    
    
    def resize_image(self, event):
        if self.current_image is not None:
            self.show_image(self.current_image)

    def apply_filter(self, filter_name):
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        selected_filter = self.filters[filter_name]
        self.current_image = selected_filter.apply(self.current_image)
        self.show_image(self.current_image)

    def reset_image(self):
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        self.current_image = self.original_image.copy()
        self.show_image(self.current_image)

    def save_image(self):
        if self.current_image is None:
            messagebox.showwarning("No Image", "There is no image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.current_image.save(file_path)
            messagebox.showinfo("Saved", "Image saved successfully!")


def main():
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()