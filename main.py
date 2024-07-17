import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import base64
import json
from datetime import datetime
import os

class TAMFile:
    def __init__(self, text="", media=None, metadata=None):
        self.text = text
        self.media = media if media else []
        self.metadata = metadata if metadata else {
            "version": "1.0",
            "author": "",
            "creation_date": datetime.now().isoformat()
        }

    def add_media(self, media_name, media_path, description=""):
        with open(media_path, "rb") as media_file:
            encoded_media = base64.b64encode(media_file.read()).decode('utf-8')
            extension = os.path.splitext(media_path)[1]
            media_item = {
                "name": media_name,
                "description": description,
                "data": encoded_media,
                "timestamp": datetime.now().isoformat(),
                "extension": extension
            }
            self.media.append(media_item)

    def save(self, file_path):
        tam_content = {
            "metadata": self.metadata,
            "text": self.text,
            "media": self.media
        }
        with open(file_path, "w") as tam_file:
            json.dump(tam_content, tam_file)

    @classmethod
    def load(cls, file_path):
        with open(file_path, "r") as tam_file:
            tam_content = json.load(tam_file)
            text = tam_content.get("text", "")
            media = tam_content.get("media", [])
            metadata = tam_content.get("metadata", {})
            return cls(text, media, metadata)

    def extract_media(self, media_name, output_path):
        for media_item in self.media:
            if media_item["name"] == media_name:
                output_path_with_extension = output_path + media_item["extension"]
                with open(output_path_with_extension, "wb") as media_file:
                    media_file.write(base64.b64decode(media_item["data"]))
                return
        print(f"No media found with name: {media_name}")

class TAMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TAM File Creator")

        self.text_label = tk.Label(root, text="Text:")
        self.text_label.pack()
        self.text_entry = tk.Text(root, height=10)
        self.text_entry.pack()

        self.author_label = tk.Label(root, text="Author:")
        self.author_label.pack()
        self.author_entry = tk.Entry(root)
        self.author_entry.pack()

        self.media_frame = tk.Frame(root)
        self.media_frame.pack()
        
        self.media_label = tk.Label(self.media_frame, text="Media Files:")
        self.media_label.pack(side=tk.LEFT)

        self.media_listbox = tk.Listbox(self.media_frame, width=50)
        self.media_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.media_button = tk.Button(root, text="Add Media", command=self.add_media)
        self.media_button.pack()

        self.save_button = tk.Button(root, text="Save TAM File", command=self.save_tam_file)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="Load TAM File", command=self.load_tam_file)
        self.load_button.pack()

        self.media_list = []

    def add_media(self):
        media_path = filedialog.askopenfilename()
        if media_path:
            media_name = simpledialog.askstring("Media Name", "Enter a name for the media:")
            if media_name:
                description = simpledialog.askstring("Description", "Enter a description for the media:")
                extension = os.path.splitext(media_path)[1]
                self.media_list.append((media_name, media_path, description, extension))
                self.update_media_listbox()

    def update_media_listbox(self):
        self.media_listbox.delete(0, tk.END)
        for media in self.media_list:
            media_name, media_path, description, extension = media
            self.media_listbox.insert(tk.END, f"{media_name} ({os.path.basename(media_path)}) - {description}")

    def save_tam_file(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        author = self.author_entry.get().strip()
        tam = TAMFile(text=text, metadata={"author": author})

        for media_name, media_path, description, extension in self.media_list:
            tam.add_media(media_name, media_path, description)

        file_path = filedialog.asksaveasfilename(defaultextension=".tam", filetypes=[("TAM files", "*.tam")])
        if file_path:
            tam.save(file_path)
            messagebox.showinfo("TAM File Saved", f"TAM file saved to '{file_path}' successfully.")

    def load_tam_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".tam", filetypes=[("TAM files", "*.tam")])
        if file_path:
            tam = TAMFile.load(file_path)
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.insert(tk.END, tam.text)
            self.author_entry.delete(0, tk.END)
            self.author_entry.insert(0, tam.metadata.get("author", ""))

            self.media_listbox.delete(0, tk.END)
            self.media_list = []
            for media in tam.media:
                media_name = media["name"]
                description = media["description"]
                extension = media["extension"]
                self.media_list.append((media_name, "", description, extension))
            self.update_media_listbox()

            self.extract_media_button = tk.Button(self.root, text="Extract Media", command=lambda: self.extract_media(tam))
            self.extract_media_button.pack()

    def extract_media(self, tam):
        selected_media = self.media_listbox.get(tk.ACTIVE)
        if selected_media:
            media_name = selected_media.split(' ')[0]
            media_extension = ""
            for media in tam.media:
                if media["name"] == media_name:
                    media_extension = media["extension"]
                    break
            initialfile = media_name + media_extension
            output_path = filedialog.asksaveasfilename(defaultextension=media_extension, initialfile=initialfile)
            if output_path:
                tam.extract_media(media_name, output_path)
                messagebox.showinfo("Media Extracted", f"Media '{media_name}' extracted to '{output_path}' successfully.")
        else:
            messagebox.showwarning("No Media Selected", "Please select a media file to extract.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = TAMGUI(root)
    root.mainloop()
