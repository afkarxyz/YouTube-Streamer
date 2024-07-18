import customtkinter as ctk
import pygetwindow as gw
import subprocess
import time
import os
from tkinter import messagebox, filedialog
from collections import defaultdict

# Constants
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov']
WINDOW_WIDTH, WINDOW_HEIGHT = 480, 350
MAX_WINDOWS = 10

class YouTubeStreamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Streamer")
        self.geometry("450x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self._setup_ui()

        self.generated_files = []
        self.base_path = ""
        self.files = defaultdict(list)

    def _setup_ui(self):
        """Set up the user interface components."""
        self._setup_icon()
        self._setup_theme()
        self._setup_input_fields()
        self._setup_buttons()
        self._setup_output_area()

    def _setup_icon(self):
        """Set up the application icon."""
        icon_path = os.path.join(os.path.dirname(__file__), "live.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print("Warning: Icon file 'live.ico' not found.")

    def _setup_theme(self):
        """Set up the application theme."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _setup_input_fields(self):
        """Set up input fields for the application."""
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nsew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Location browse
        self._create_location_field()

        # Rename field
        self._create_rename_field()

        # Loop count field
        self._create_loop_count_field()

    def _create_location_field(self):
        """Create the location input field and browse button."""
        self.location_label = ctk.CTkLabel(self.input_frame, text="Location")
        self.location_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.location_entry = ctk.CTkEntry(self.input_frame, width=220)
        self.location_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ctk.CTkButton(self.input_frame, text="Browse", command=self.browse_location, width=80,
                                           fg_color="#4A4D50", hover_color="#343638")
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

    def _create_rename_field(self):
        """Create the rename input field."""
        self.rename_label = ctk.CTkLabel(self.input_frame, text="Rename")
        self.rename_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rename_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Streamer")
        self.rename_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    def _create_loop_count_field(self):
        """Create the loop count input field."""
        self.loop_count_label = ctk.CTkLabel(self.input_frame, text="Loop")
        self.loop_count_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.loop_count_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Unlimited")
        self.loop_count_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    def _setup_buttons(self):
        """Set up the main action buttons."""
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)

        self.inner_button_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.inner_button_frame.grid(row=0, column=0)

        self.generate_button = ctk.CTkButton(self.inner_button_frame, text="Generate", command=self.generate_batch_files, width=80)
        self.generate_button.grid(row=0, column=0, padx=5, pady=5)

        self.run_button = ctk.CTkButton(self.inner_button_frame, text="Run", command=self.open_and_arrange, width=80, fg_color="#27ae60", hover_color="#1e8449")
        self.run_button.grid(row=0, column=1, padx=5, pady=5)

        self.reset_button = ctk.CTkButton(self.inner_button_frame, text="Reset", command=self.reset, width=80, fg_color="#e74c3c", hover_color="#c0392b")
        self.reset_button.grid(row=0, column=2, padx=5, pady=5)

    def _setup_output_area(self):
        """Set up the output text area."""
        self.output_text = ctk.CTkTextbox(self, width=460, height=200)
        self.output_text.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="nsew")
        
        placeholder_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"])
        self.output_text.configure(text_color=placeholder_color)

    def browse_location(self):
        """Open a file dialog to select a folder and update the location entry."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.base_path = folder_path
            self.location_entry.delete(0, ctk.END)
            self.location_entry.insert(0, folder_path)
            self.find_all_files(folder_path)

    def find_all_files(self, path):
        """Find all files in the given path and categorize them by extension."""
        self.files = defaultdict(list)
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                self.files[file_ext].append(file_path)

        self.display_found_files()

    def display_found_files(self):
        """Display information about the found files in the output area."""
        total_files = sum(len(files) for files in self.files.values())
        self.output_text.insert(ctk.END, f"Found {total_files} file(s) in total.\n")

        self._display_specific_file_types()
        self._display_video_files()
        self._display_other_files()

    def _display_specific_file_types(self):
        """Display information about specific file types."""
        for ext in ['.exe', '.bat', '.txt']:
            if ext in self.files:
                files = [os.path.basename(f) for f in self.files[ext]]
                self.output_text.insert(ctk.END, f"Found {len(files)} {ext} file(s): {', '.join(files)}\n")

    def _display_video_files(self):
        """Display information about video files."""
        video_files = sum(len(self.files[ext]) for ext in VIDEO_EXTENSIONS if ext in self.files)
        if video_files:
            self.output_text.insert(ctk.END, f"Found {video_files} video file(s)\n")

    def _display_other_files(self):
        """Display information about other file types."""
        other_files = sum(len(files) for ext, files in self.files.items() 
                          if ext not in ['.exe', '.bat', '.txt'] + VIDEO_EXTENSIONS)
        if other_files:
            self.output_text.insert(ctk.END, f"Found {other_files} other file(s)\n")

    def generate_batch_files(self):
        """Generate batch files based on the input parameters."""
        if not self._validate_input():
            return False

        rename_prefix = self.rename_entry.get() or "Streamer"
        loop_count = self.loop_count_entry.get()

        txt_file = self._find_txt_file()
        ffmpeg_path = self._find_ffmpeg()

        if not txt_file or not ffmpeg_path:
            return False

        loop_option = "-stream_loop -1" if not loop_count else f"-stream_loop {loop_count}"

        self._create_batch_files(txt_file, ffmpeg_path, rename_prefix, loop_option)

        return bool(self.generated_files)

    def _validate_input(self):
        """Validate user input before generating batch files."""
        if not self.base_path:
            self.output_text.insert(ctk.END, "Error: Please select a folder first.\n")
            messagebox.showerror("Error", "Please select a folder first.")
            return False
        return True

    def _find_txt_file(self):
        """Find the first .txt file in the selected directory."""
        txt_files = self.files.get('.txt', [])
        if not txt_files:
            error_message = "Error: No .txt file found in the selected directory."
            self.output_text.insert(ctk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)
            return None
        return txt_files[0]

    def _find_ffmpeg(self):
        """Find the ffmpeg executable in the selected directory or its subdirectories."""
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower() == "ffmpeg.exe":
                    return os.path.join(root, file)
        
        error_message = "Error: ffmpeg.exe not found in the selected directory or its subdirectories."
        self.output_text.insert(ctk.END, error_message + "\n")
        messagebox.showerror("Error", error_message)
        return None

    def _create_batch_files(self, txt_file, ffmpeg_path, rename_prefix, loop_option):
        """Create batch files based on the provided parameters."""
        with open(txt_file, 'r') as f:
            stream_keys = f.readlines()

        self.generated_files = []
        all_files = [file for files in self.files.values() for file in files if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS]
        
        for i, key in enumerate(stream_keys, 1):
            if i <= len(all_files):
                file = all_files[i-1]
                outfile = f"{rename_prefix} {i}.bat"
                self._write_batch_file(outfile, ffmpeg_path, loop_option, file, key.strip())
            else:
                self.output_text.insert(ctk.END, f"Error: Video file for {rename_prefix} {i} not found\n")

        self._display_generation_result()

    def _write_batch_file(self, outfile, ffmpeg_path, loop_option, video_file, stream_key):
        """Write a single batch file."""
        try:
            with open(os.path.join(self.base_path, outfile), 'w') as f:
                f.write(f'"{ffmpeg_path}" {loop_option} -re -i "{video_file}" -c copy -f flv -flvflags no_duration_filesize rtmp://a.rtmp.youtube.com/live2/{stream_key}')
            self.generated_files.append(os.path.join(self.base_path, outfile))
            self.output_text.insert(ctk.END, f"Generated: {outfile}\n")
        except IOError as e:
            self.output_text.insert(ctk.END, f"Error writing file {outfile}: {str(e)}\n")

    def _display_generation_result(self):
        """Display the result of batch file generation."""
        if self.generated_files:
            message = f"\nSuccessfully generated {len(self.generated_files)} batch files."
            self.output_text.insert(ctk.END, message + "\n")
            messagebox.showinfo("Success", message)
        else:
            error_message = "Failed to generate batch files. Check the output for details."
            self.output_text.insert(ctk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)

    def find_bat_files(self):
        """Find all .bat files in the selected directory."""
        if not self.base_path:
            self.output_text.insert(ctk.END, "Error: Please select a folder first.\n")
            messagebox.showerror("Error", "Please select a folder first.")
            return []

        bat_files = self.files.get('.bat', [])
        
        if not bat_files:
            self.output_text.insert(ctk.END, "No .bat files found in the selected directory.\n")
        else:
            self.output_text.insert(ctk.END, f"Found {len(bat_files)} .bat file(s).\n")
        
        return bat_files

    def open_and_arrange(self):
        """Open CMD windows for each batch file and arrange them on the screen."""
        bat_files = self.find_bat_files()
        if not bat_files:
            if not self.generated_files:
                messagebox.showerror("Error", "No batch files found. Please generate batch files first or select a folder with existing .bat files.")
                return
            else:
                bat_files = self.generated_files
        
        num_files = min(len(bat_files), MAX_WINDOWS)

        self._open_cmd_windows(bat_files[:num_files])
        self._arrange_cmd_windows(num_files)

        self.output_text.insert(ctk.END, f"\nOpened and arranged {num_files} window(s).\n")

    def _open_cmd_windows(self, bat_files):
        """Open CMD windows for each batch file."""
        for file in bat_files:
            try:
                subprocess.Popen(f'start cmd /K "{file}"', shell=True)
                time.sleep(1)  # Add a 1-second delay between opening each CMD window
            except subprocess.SubprocessError as e:
                self.output_text.insert(ctk.END, f"Error opening {file}: {str(e)}\n")

        # Additional delay to ensure all windows are open
        time.sleep(1)

    def _arrange_cmd_windows(self, num_windows):
        """Arrange the opened CMD windows in a grid."""
        cmd_windows = gw.getWindowsWithTitle("cmd.exe")

        for i, window in enumerate(cmd_windows[:num_windows]):
            try:
                row = i // 4
                col = i % 4
                x = col * WINDOW_WIDTH
                y = row * WINDOW_HEIGHT
                window.resizeTo(WINDOW_WIDTH, WINDOW_HEIGHT)
                window.moveTo(x, y)
                time.sleep(0.5)  # Add a small delay between arranging each window
            except Exception as e:
                self.output_text.insert(ctk.END, f"Error arranging window {i+1}: {str(e)}\n")

    def reset(self):
        """Reset all input fields and clear the output area."""
        self.location_entry.delete(0, ctk.END)
        self.base_path = ""
        self.rename_entry.delete(0, ctk.END)
        self.rename_entry.configure(placeholder_text="Streamer")
        self.loop_count_entry.delete(0, ctk.END)
        self.loop_count_entry.configure(placeholder_text="Unlimited")
        self.output_text.delete('1.0', ctk.END)
        self.generated_files = []
        self.files = defaultdict(list)
        
        self.output_text.insert(ctk.END, "All fields have been reset.\n")

    def run(self):
        """Main method to run the application."""
        bat_files = self.find_bat_files()
        if bat_files:
            self.open_and_arrange()
        elif not self.generated_files:
            response = messagebox.askyesno("No Batch Files", "No batch files found. Do you want to generate them?")
            if response:
                if self.generate_batch_files():
                    self.open_and_arrange()
            else:
                self.output_text.insert(ctk.END, "Operation cancelled.\n")
        else:
            self.open_and_arrange()

if __name__ == "__main__":
    app = YouTubeStreamerApp()
    app.mainloop()