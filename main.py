import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# Directory containing known face images
known_faces_dir = '/Users/Nitin/Desktop/Diploma/Major Project 0/Data'

# Load known faces
known_faces = []
known_names = []
for filename in os.listdir(known_faces_dir):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(filename.split('.')[0])

# Function to capture image
def capture_image():
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow('Press Space to capture', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    cam.release()
    cv2.destroyAllWindows()
    return frame if ret else None

# Function to recognize face
def recognize_face(captured_image):
    face_encodings = face_recognition.face_encodings(captured_image)
    if len(face_encodings) == 0:
        print("No faces detected in the image.")
        return None
    captured_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]
    return None

# Function to mark attendance
def mark_attendance(student_name, file='attendance.xlsx'):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    try:
        df = pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)
    df.to_excel(file, index=False)

# Function to show attendance
def show_attendance(file='attendance.xlsx'):
    try:
        df = pd.read_excel(file)
        messagebox.showinfo("Attendance", df.to_string(index=False))
    except FileNotFoundError:
        messagebox.showinfo("Attendance", "No attendance records found.")

# Function to capture and mark attendance
def capture_and_mark():
    image = capture_image()
    if image is None:
        messagebox.showerror("Error", "Failed to capture image.")
        return
    student_name = recognize_face(image)
    if student_name is None:
        messagebox.showerror("Error", "Student not recognized!")
        return
    mark_attendance(student_name)
    messagebox.showinfo("Success", f"Attendance marked for {student_name}")

# Function to add a new face
def add_new_face():
    image = capture_image()
    if image is None:
        messagebox.showerror("Error", "Failed to capture image.")
        return
    name = simpledialog.askstring("Input", "Enter the name of the person:", parent=root)
    if not name:
        messagebox.showerror("Error", "Name cannot be empty!")
        return
    face_encodings = face_recognition.face_encodings(image)
    if len(face_encodings) == 0:
        messagebox.showerror("Error", "No face detected!")
        return
    encoding = face_encodings[0]
    known_faces.append(encoding)
    known_names.append(name)
    # Save the image
    cv2.imwrite(f"{known_faces_dir}/{name}.jpg", image)
    messagebox.showinfo("Success", f"New face added for {name}")

# Main GUI application
def main():
    global root
    root = tk.Tk()
    root.title("Face Recognition Attendance System")

    # Center the window
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Configure grid layout
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Add buttons with styling
    capture_button = tk.Button(root, text="Capture Image", command=capture_and_mark, font=("Helvetica", 14), bg="#4CAF50", fg="white")
    capture_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    show_button = tk.Button(root, text="Show Attendance", command=show_attendance, font=("Helvetica", 14), bg="#2196F3", fg="white")
    show_button.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    add_face_button = tk.Button(root, text="Add New Face", command=add_new_face, font=("Helvetica", 14), bg="#FF5722", fg="white")
    add_face_button.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()
