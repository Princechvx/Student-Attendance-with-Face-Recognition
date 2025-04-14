import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# Directory containing known face images - using os.path for cross-platform compatibility
known_faces_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Diploma', 'Student Attendance with Face Recognition', 'known_faces_dir')

# Create directory if it doesn't exist
if not os.path.exists(known_faces_dir):
    os.makedirs(known_faces_dir)
    print(f"Created directory: {known_faces_dir}")

# Load known faces
known_faces = []
known_names = []

# Check if directory is empty
if os.path.exists(known_faces_dir) and os.listdir(known_faces_dir):
    for filename in os.listdir(known_faces_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            try:
                image_path = os.path.join(known_faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    encoding = encodings[0]
                    known_faces.append(encoding)
                    known_names.append(filename.split('.')[0])
                    print(f"Loaded face: {filename}")
                else:
                    print(f"No face found in {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
else:
    print(f"No face images found in {known_faces_dir}")

# Function to capture image
def capture_image():
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("Error: Could not open camera")
            return None
            
        captured_frame = None
        while True:
            ret, frame = cam.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            cv2.imshow('Press Space to capture, ESC to cancel', frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):
                captured_frame = frame.copy()  # Make a copy of the current frame
                print("Image captured!")
                break
            elif key == 27:  # ESC key to cancel
                print("Capture canceled")
                break
                
        cam.release()
        cv2.destroyAllWindows()
        return captured_frame
        
    except Exception as e:
        print(f"Error capturing image: {e}")
        if 'cam' in locals() and cam.isOpened():
            cam.release()
        cv2.destroyAllWindows()
        return None

# Function to recognize face
def recognize_face(captured_image):
    try:
        face_encodings = face_recognition.face_encodings(captured_image)
        if len(face_encodings) == 0:
            print("No faces detected in the image.")
            return None
        captured_encoding = face_encodings[0]
        
        if not known_faces:
            print("No known faces to compare with.")
            return None
            
        matches = face_recognition.compare_faces(known_faces, captured_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            return known_names[first_match_index]
        return None
    except Exception as e:
        print(f"Error recognizing face: {e}")
        return None

# Function to mark attendance
def mark_attendance(student_name, file='attendance.xlsx'):
    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # Check if student already marked attendance today
        try:
            df = pd.read_excel(file)
            today_records = df[(df['Name'] == student_name) & (df['Date'] == current_date)]
            if not today_records.empty:
                return False, "Already marked attendance today"
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Name", "Date", "Time"])
            
        new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
        df = pd.concat([df, new_record_df], ignore_index=True)
        df.to_excel(file, index=False)
        return True, "Attendance marked successfully"
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False, str(e)

# Function to show attendance
def show_attendance(file='attendance.xlsx'):
    try:
        if not os.path.exists(file):
            messagebox.showinfo("Attendance", "No attendance records found.")
            return
            
        df = pd.read_excel(file)
        if df.empty:
            messagebox.showinfo("Attendance", "No attendance records found.")
            return
            
        # Format the display to show today's attendance first
        today = datetime.now().strftime("%Y-%m-%d")
        today_df = df[df['Date'] == today]
        other_df = df[df['Date'] != today]
        
        display_df = pd.concat([today_df, other_df])
        
        # Create a formatted string for display
        attendance_str = "Today's Attendance:\n"
        attendance_str += "=" * 40 + "\n"
        if not today_df.empty:
            attendance_str += today_df.to_string(index=False) + "\n\n"
        else:
            attendance_str += "No attendance marked today\n\n"
            
        attendance_str += "Previous Records:\n"
        attendance_str += "=" * 40 + "\n"
        if not other_df.empty:
            attendance_str += other_df.to_string(index=False)
        else:
            attendance_str += "No previous records"
            
        messagebox.showinfo("Attendance Records", attendance_str)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show attendance: {e}")

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
        
    success, message = mark_attendance(student_name)
    if success:
        messagebox.showinfo("Success", f"Attendance marked for {student_name}")
    else:
        messagebox.showinfo("Info", f"{student_name}: {message}")

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
        
    # Validate name (no special characters that could cause file system issues)
    import re
    if not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
        messagebox.showerror("Error", "Name contains invalid characters!")
        return
        
    face_encodings = face_recognition.face_encodings(image)
    if len(face_encodings) == 0:
        messagebox.showerror("Error", "No face detected!")
        return
        
    # Check if directory exists, create if it doesn't
    if not os.path.exists(known_faces_dir):
        try:
            os.makedirs(known_faces_dir)
            print(f"Created directory: {known_faces_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directory: {e}")
            return
            
    # Save the image
    try:
        image_path = os.path.join(known_faces_dir, f"{name}.jpg")
        cv2.imwrite(image_path, image)
        
        # Add to known faces and names
        encoding = face_encodings[0]
        known_faces.append(encoding)
        known_names.append(name)
        
        messagebox.showinfo("Success", f"New face added for {name}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save image: {e}")

# Main GUI application
def main():
    global root
    root = tk.Tk()
    root.title("Face Recognition Attendance System")

    # Center the window
    window_width = 500
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Configure grid layout
    for i in range(4):
        root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Add status label
    status_text = f"System Ready - {len(known_names)} faces loaded"
    status_label = tk.Label(root, text=status_text, font=("Helvetica", 10), fg="#555555")
    status_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

    # Add buttons with styling
    capture_button = tk.Button(root, text="Mark Attendance", command=capture_and_mark, 
                              font=("Helvetica", 14), bg="#4CAF50", fg="white")
    capture_button.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    show_button = tk.Button(root, text="Show Attendance Records", command=show_attendance, 
                           font=("Helvetica", 14), bg="#2196F3", fg="white")
    show_button.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    add_face_button = tk.Button(root, text="Register New Face", command=add_new_face, 
                               font=("Helvetica", 14), bg="#FF5722", fg="white")
    add_face_button.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

    # Display the known faces directory path
    path_label = tk.Label(root, text=f"Database: {known_faces_dir}", 
                         font=("Helvetica", 8), fg="#888888")
    path_label.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

    root.mainloop()

if __name__ == "__main__":
    main()
