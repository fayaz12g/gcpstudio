import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import customtkinter
import os
import json
import zipfile
import shutil
import tempfile
from PIL import Image, ImageTk
import requests
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play
import pygame

class GCPStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("GCP Studio")
        self.root.geometry('1200x600')

        self.temp_dir = None
        self.current_gcp_path = None
        self.opened_packs = {}
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Pack manager frame
        pack_manager_frame = ttk.Frame(main_frame, width=200)
        pack_manager_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.pack_tree = ttk.Treeview(pack_manager_frame, columns=('name',), show='tree')
        self.pack_tree.heading('#0', text='Packs')
        self.pack_tree.heading('name', text='Name')
        self.pack_tree.pack(fill=tk.BOTH, expand=True)

        download_button = ttk.Button(pack_manager_frame, text="Download Packs", command=self.download_packs)
        download_button.pack(pady=10)

        # Right side frame
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Pack info frame
        pack_info_frame = ttk.LabelFrame(right_frame, text="Pack Info", padding="10")
        pack_info_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pack_info_frame, text="Pack ID:").grid(row=0, column=0, sticky=tk.W)
        self.pack_id_entry = ttk.Entry(pack_info_frame)
        self.pack_id_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(pack_info_frame, text="Pack Name:").grid(row=1, column=0, sticky=tk.W)
        self.pack_name_entry = ttk.Entry(pack_info_frame)
        self.pack_name_entry.grid(row=1, column=1, sticky=tk.W)

        # Decks frame
        decks_frame = ttk.LabelFrame(right_frame, text="Decks", padding="10")
        decks_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.decks_tree = ttk.Treeview(decks_frame, columns=('Image', 'ID', 'Name', 'Color', 'Sound', 'Edit'), show='headings')
        self.decks_tree.heading('Image', text='Image')
        self.decks_tree.heading('ID', text='ID')
        self.decks_tree.heading('Name', text='Name')
        self.decks_tree.heading('Color', text='Color')
        self.decks_tree.heading('Sound', text='Sound')
        self.decks_tree.heading('Edit', text='Edit')
        self.decks_tree.pack(fill=tk.BOTH, expand=True)

        self.decks_tree.column('Image', width=50, anchor='center')
        self.decks_tree.column('Sound', width=50, anchor='center')
        self.decks_tree.column('Edit', width=50, anchor='center')

        # Buttons frame
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="Open GCP", command=self.open_gcp).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save GCP", command=self.save_gcp).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Add Deck", command=self.add_deck).pack(side=tk.LEFT, padx=5)

        # Bind pack tree selection
        self.pack_tree.bind('<<TreeviewSelect>>', self.on_pack_select)
        self.pack_tree.bind("<Button-3>", self.show_pack_context_menu)

    def show_pack_context_menu(self, event):
        selected_item = self.pack_tree.identify_row(event.y)
        if selected_item:
            self.pack_tree.selection_set(selected_item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Remove Pack", command=lambda: self.remove_pack(selected_item))
            menu.tk_popup(event.x_root, event.y_root)

    def remove_pack(self, pack_id):
        self.pack_tree.delete(pack_id)
        if pack_id in self.opened_packs:
            del self.opened_packs[pack_id]

            
    def download_packs(self):
        # Default packstore URL
        default_url = "https://raw.githubusercontent.com/fayaz12g/gcpstudio/main/packstore.json"
        
        # Ask for packstore URL
        packstore_url = simpledialog.askstring("Download Packs", "Enter packstore URL:", initialvalue=default_url)
        
        if not packstore_url:
            return

        try:
            # Fetch packstore.json
            response = requests.get(packstore_url)
            response.raise_for_status()
            packstore = response.json()

            # Create a new window for pack selection
            select_window = tk.Toplevel(self.root)
            select_window.title("Select Packs to Download")

            # Create a frame with scrollbar
            frame = ttk.Frame(select_window)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create checkbuttons for each pack
            pack_vars = {}
            for pack in packstore['packs']:
                var = tk.BooleanVar()
                ttk.Checkbutton(scrollable_frame, text=f"{pack['name']} ({pack['id']})", variable=var).pack(anchor="w")
                pack_vars[pack['id']] = var

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def select_all():
                for var in pack_vars.values():
                    var.set(True)

            def download_selected():
                selected_packs = [pack_id for pack_id, var in pack_vars.items() if var.get()]
                self.download_selected_packs(packstore, selected_packs)
                select_window.destroy()

            ttk.Button(select_window, text="Select All", command=select_all).pack(pady=5)
            ttk.Button(select_window, text="Download Selected", command=download_selected).pack(pady=5)

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch packstore: {str(e)}")

    def download_selected_packs(self, packstore, selected_packs):
        base_url = os.path.dirname(packstore['url'])
        app_data_dir = Path(os.getenv('APPDATA')) / 'GCP Studio'
        app_data_dir.mkdir(parents=True, exist_ok=True)

        for pack in packstore['packs']:
            if pack['id'] in selected_packs:
                pack_url = f"{base_url}/packs/{pack['id']}.gcp"
                try:
                    response = requests.get(pack_url)
                    response.raise_for_status()
                    pack_path = app_data_dir / f"{pack['id']}.gcp"
                    with open(pack_path, 'wb') as f:
                        f.write(response.content)
                    self.add_pack_to_tree(pack['id'], pack['name'], str(pack_path))
                except requests.RequestException as e:
                    messagebox.showerror("Error", f"Failed to download {pack['name']}: {str(e)}")

        messagebox.showinfo("Success", "Selected packs have been downloaded and added to the pack manager.")

    def add_pack_to_tree(self, pack_id, pack_name, pack_path):
        self.pack_tree.insert('', 'end', pack_id, text=pack_id, values=(pack_name,))
        self.opened_packs[pack_id] = pack_path

    def on_pack_select(self, event):
        selected_item = self.pack_tree.selection()[0]
        pack_path = self.opened_packs.get(selected_item)
        if pack_path:
            self.open_gcp(pack_path)


    def cleanup_temp_dir(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = None
        self.current_gcp_path = None

    def set_tag_colors(self):
        for item in self.decks_tree.get_children():
            deck_id = self.decks_tree.item(item, 'values')[1]
            color = self.decks_tree.item(item, 'values')[3]
            self.decks_tree.tag_configure(deck_id, background=color)
            
    def open_gcp(self, file_path=None):
        if file_path is None:
            file_path = filedialog.askopenfilename(title="Select GCP file", filetypes=[("GCP files", "*.gcp")])
        if not file_path:
            return

        self.current_gcp_path = file_path
        self.temp_dir = tempfile.mkdtemp()

        try:
            # Decompress the GCP file
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(self.temp_dir)

            # Ensure required directories exist
            for dir_name in ['deck', 'image', 'sound']:
                os.makedirs(os.path.join(self.temp_dir, dir_name), exist_ok=True)

            # Decompress deck.gcdp if it exists
            self.decompress_file(os.path.join(self.temp_dir, "deck.gcdp"), "deck", ".json")

            # Decompress image.gcip if it exists
            self.decompress_file(os.path.join(self.temp_dir, "image.gcip"), "image", ".png")

            # Decompress sound.gcsp if it exists
            self.decompress_file(os.path.join(self.temp_dir, "sound.gcsp"), "sound", ".m4a")

            # Load info.json
            info_path = os.path.join(self.temp_dir, "info.json")
            if not os.path.exists(info_path):
                raise FileNotFoundError("info.json not found in the GCP file")

            with open(info_path, 'r') as f:
                info = json.load(f)

            # Update UI with pack info
            self.pack_id_entry.delete(0, tk.END)
            self.pack_id_entry.insert(0, info.get('id', ''))
            self.pack_name_entry.delete(0, tk.END)
            self.pack_name_entry.insert(0, info.get('name', ''))

            # Add to pack manager tree if not already added
            pack_id = info.get('id', '')
            pack_name = info.get('name', '')
            if pack_id not in self.opened_packs:
                self.add_pack_to_tree(pack_id, pack_name, file_path)

            # Initialize the images dictionary
            self.decks_tree.images = {}

            # Clear and update decks tree
            self.decks_tree.delete(*self.decks_tree.get_children())
            for card in info.get('cards', []):
                deck = list(card.values())[0]
                image_path = os.path.join(self.temp_dir, "image", f"{deck['id']}.png")
                sound_path = os.path.join(self.temp_dir, "sound", f"{deck['id']}.m4a")
                
                item = self.decks_tree.insert('', 'end', values=('', deck['id'], deck['name'], deck['color'], '', 'Edit'), tags=(deck['id'],))
                self.update_tree_item_image(item, image_path)
                self.decks_tree.set(item, 'Sound', '▶' if os.path.exists(sound_path) else '')

            self.decks_tree.bind('<Double-1>', self.edit_deck)
            self.decks_tree.bind('<Button-3>', self.show_context_menu)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open GCP file: {str(e)}")
            self.cleanup_temp_dir()


    def decompress_file(self, file_path, target_dir, file_extension):
        if os.path.exists(file_path):
            target_dir_path = os.path.join(self.temp_dir, target_dir)
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(target_dir_path)
            
            # Rename and shift bits for decompressed files
            for file in os.listdir(target_dir_path):
                old_path = os.path.join(target_dir_path, file)
                file_name, file_ext = os.path.splitext(file)
                new_path = os.path.join(target_dir_path, file_name + file_extension)

                if file_ext in ['.gcd', '.gci', '.gcs']:
                    if file_ext == '.gcd':
                        self.shift_bits(old_path, shift_up=False)
                    os.rename(old_path, new_path)


    def play_sound(self, sound_path):
        if os.path.exists(sound_path):
            try:
                # Convert audio to WAV format
                sound = AudioSegment.from_file(sound_path)
                wav_path = tempfile.mktemp(suffix='.wav')
                sound.export(wav_path, format='wav')

                # Play the WAV file using pygame
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.play()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to play sound: {str(e)}")
        else:
            messagebox.showerror("Error", f"Sound file not found: {sound_path}")



    def show_context_menu(self, event):
        item = self.decks_tree.identify_row(event.y)
        if item:
            self.decks_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_deck(None))
            
            sound_menu = tk.Menu(menu, tearoff=0)
            sound_menu.add_command(label="Play Sound", command=lambda: self.play_sound(os.path.join(self.temp_dir, "sound", f"{self.decks_tree.item(item, 'values')[1]}.m4a")))
            sound_menu.add_command(label="Replace Sound", command=lambda: self.replace_sound(item))
            menu.add_cascade(label="Sound", menu=sound_menu)
            
            image_menu = tk.Menu(menu, tearoff=0)
            image_menu.add_command(label="View Image", command=lambda: self.view_image(item))
            image_menu.add_command(label="Replace Image", command=lambda: self.replace_image(item))
            menu.add_cascade(label="Image", menu=image_menu)
            
            menu.add_command(label="Rename ID", command=lambda: self.rename_id(item))
            menu.add_command(label="Rename Name", command=lambda: self.rename_name(item))
            menu.add_command(label="Change Color", command=lambda: self.change_color(item))
            
            menu.tk_popup(event.x_root, event.y_root)

    def view_image(self, item):
        deck_id = self.decks_tree.item(item, 'values')[1]
        image_path = os.path.join(self.temp_dir, "image", f"{deck_id}.png")
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img.show()
        else:
            messagebox.showerror("Error", "Image file not found.")

    def replace_image(self, item):
        deck_id = self.decks_tree.item(item, 'values')[1]
        new_image_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if new_image_path:
            dest_path = os.path.join(self.temp_dir, "image", f"{deck_id}.png")
            shutil.copy(new_image_path, dest_path)
            self.update_tree_item_image(item, dest_path)

    def replace_sound(self, item):
        deck_id = self.decks_tree.item(item, 'values')[1]
        new_sound_path = filedialog.askopenfilename(filetypes=[("M4A files", "*.m4a")])
        if new_sound_path:
            dest_path = os.path.join(self.temp_dir, "sound", f"{deck_id}.m4a")
            shutil.copy(new_sound_path, dest_path)
            self.decks_tree.set(item, 'Sound', '▶')

    def rename_id(self, item):
        old_id = self.decks_tree.item(item, 'values')[1]
        new_id = simpledialog.askstring("Rename ID", "Enter new ID:", initialvalue=old_id)
        if new_id:
            self.decks_tree.set(item, 'ID', new_id)
            self.rename_associated_files(old_id, new_id)

    def rename_name(self, item):
        old_name = self.decks_tree.item(item, 'values')[2]
        new_name = simpledialog.askstring("Rename Name", "Enter new name:", initialvalue=old_name)
        if new_name:
            self.decks_tree.set(item, 'Name', new_name)

    def change_color(self, item):
        old_color = self.decks_tree.item(item, 'values')[3]
        old_color = old_color.split('-')[0].strip()
        new_color = colorchooser.askcolor(color=old_color, title="Choose color")[1]
        if new_color:
            self.decks_tree.set(item, 'Color', new_color)

    def rename_associated_files(self, old_id, new_id):
        for dir_name in ['image', 'sound', 'deck']:
            old_path = os.path.join(self.temp_dir, dir_name, f"{old_id}{self.get_file_extension(dir_name)}")
            new_path = os.path.join(self.temp_dir, dir_name, f"{new_id}{self.get_file_extension(dir_name)}")
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

    def get_file_extension(self, dir_name):
        return {
            'image': '.png',
            'sound': '.m4a',
            'deck': '.json'
        }.get(dir_name, '')

    def update_tree_item_image(self, item, image_path):
        if os.path.exists(image_path):
            image = Image.open(image_path).resize((30, 30))
            photo = ImageTk.PhotoImage(image)
            self.decks_tree.set(item, 'Image', '')
            self.decks_tree.item(item, image=photo)
            self.decks_tree.images[item] = photo  # Store the image reference
        else:
            self.decks_tree.set(item, 'Image', 'No image')


    def save_gcp(self):
        # Ask for save location
        save_path = filedialog.asksaveasfilename(defaultextension=".gcp", filetypes=[("GCP files", "*.gcp")])
        if not save_path:
            return

        # Validate required fields
        if not self.pack_id_entry.get():
            self.show_field_error(self.pack_id_entry, "Pack ID is required")
            return
        if not self.pack_name_entry.get():
            self.show_field_error(self.pack_name_entry, "Pack Name is required")
            return

        # Create info.json
        info = {
            "id": self.pack_id_entry.get(),
            "name": self.pack_name_entry.get(),
            "cards": []
        }

        for item in self.decks_tree.get_children():
            values = self.decks_tree.item(item)['values']
            if not values[1] or not values[2] or not values[3]:
                messagebox.showerror("Error", f"Deck {values[1]} is missing required fields (ID, Name, or Color)")
                return
            info['cards'].append({values[3]: {"id": values[1], "name": values[2], "color": values[3]}})

        # Create temporary directory for packing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save info.json
            with open(os.path.join(temp_dir, "info.json"), 'w') as f:
                json.dump(info, f, indent=2)

            # Create deck, image, and sound directories
            os.makedirs(os.path.join(temp_dir, "deck"))
            os.makedirs(os.path.join(temp_dir, "image"))
            os.makedirs(os.path.join(temp_dir, "sound"))

            # Copy or create placeholder files
            for card in info['cards']:
                deck_id = list(card.values())[0]['id']
                
                # Deck JSON
                deck_path = os.path.join(temp_dir, "deck", f"{deck_id}.json")
                if self.temp_dir and os.path.exists(os.path.join(self.temp_dir, "deck", f"{deck_id}.json")):
                    shutil.copy(os.path.join(self.temp_dir, "deck", f"{deck_id}.json"), deck_path)
                else:
                    with open(deck_path, 'w') as f:
                        json.dump({"name": list(card.values())[0]['name'], "color": list(card.values())[0]['color'], "cards": []}, f, indent=2)

                # Image
                image_path = os.path.join(temp_dir, "image", f"{deck_id}.png")
                if self.temp_dir and os.path.exists(os.path.join(self.temp_dir, "image", f"{deck_id}.png")):
                    shutil.copy(os.path.join(self.temp_dir, "image", f"{deck_id}.png"), image_path)
                else:
                    Image.new('RGB', (1, 1), color='white').save(image_path)

                # Sound
                sound_path = os.path.join(temp_dir, "sound", f"{deck_id}.m4a")
                if self.temp_dir and os.path.exists(os.path.join(self.temp_dir, "sound", f"{deck_id}.m4a")):
                    shutil.copy(os.path.join(self.temp_dir, "sound", f"{deck_id}.m4a"), sound_path)
                else:
                    open(sound_path, 'wb').close()  # Create empty file

            # Compress the pack
            self.compress_pack(temp_dir, save_path)

        messagebox.showinfo("Success", f"Pack saved as {save_path}")

    def show_field_error(self, widget, message):
        error_label = ttk.Label(widget.master, text=message, foreground="red")
        error_label.grid(row=widget.grid_info()['row'], column=widget.grid_info()['column']+1)
        widget.master.after(3000, error_label.destroy)  # Remove error message after 3 seconds

    def add_deck(self):
        # Open a dialog to get deck details
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Deck")

        ttk.Label(dialog, text="Deck ID:").grid(row=0, column=0, sticky=tk.W)
        deck_id_entry = ttk.Entry(dialog)
        deck_id_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(dialog, text="Deck Name:").grid(row=1, column=0, sticky=tk.W)
        deck_name_entry = ttk.Entry(dialog)
        deck_name_entry.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(dialog, text="Deck Color:").grid(row=2, column=0, sticky=tk.W)
        deck_color_entry = ttk.Entry(dialog)
        deck_color_entry.grid(row=2, column=1, sticky=tk.W)

        image_path = tk.StringVar()
        ttk.Label(dialog, text="Deck Image:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(dialog, textvariable=image_path, state='readonly').grid(row=3, column=1, sticky=tk.W)
        ttk.Button(dialog, text="Browse", command=lambda: image_path.set(filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]))).grid(row=3, column=2)

        sound_path = tk.StringVar()
        ttk.Label(dialog, text="Deck Sound:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(dialog, textvariable=sound_path, state='readonly').grid(row=4, column=1, sticky=tk.W)
        ttk.Button(dialog, text="Browse", command=lambda: sound_path.set(filedialog.askopenfilename(filetypes=[("Audio files", "*.m4a")]))).grid(row=4, column=2)

        def save_deck():
            deck_id = deck_id_entry.get()
            deck_name = deck_name_entry.get()
            deck_color = deck_color_entry.get()

            if deck_id and deck_name and deck_color and image_path.get() and sound_path.get():
                # Save image
                img = Image.open(image_path.get())
                img.save(os.path.join(self.temp_dir, "image", f"{deck_id}.png"))

                # Save sound
                shutil.copy(sound_path.get(), os.path.join(self.temp_dir, "sound", f"{deck_id}.m4a"))

                # Add to treeview
                image = img.resize((30, 30))
                photo = ImageTk.PhotoImage(image)
                item = self.decks_tree.insert('', 'end', values=('', deck_id, deck_name, deck_color, '', 'Edit'))
                self.decks_tree.set(item, 'Image', '')
                self.decks_tree.item(item, image=photo)
                self.decks_tree.set(item, 'Sound', '▶')

                # Create empty deck JSON file
                deck_path = os.path.join(self.temp_dir, "deck", f"{deck_id}.json")
                with open(deck_path, 'w') as f:
                    json.dump({"name": deck_name, "color": deck_color, "cards": []}, f, indent=2)

                dialog.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")

        ttk.Button(dialog, text="Save", command=save_deck).grid(row=5, column=0, columnspan=3, pady=10)

    def edit_deck(self, event):
        item = self.decks_tree.selection()[0]
        deck_id = self.decks_tree.item(item, "values")[1]
        self.open_deck_editor(deck_id)

    def open_deck_editor(self, deck_id):
        # Open deck editing window
        deck_window = tk.Toplevel(self.root)
        deck_window.title(f"Editing Deck: {deck_id}")
        deck_window.geometry('800x600')

        # Load deck data
        deck_path = os.path.join(self.temp_dir, "deck", f"{deck_id}.json")
        with open(deck_path, 'r') as f:
            deck_data = json.load(f)

        # Deck info frame
        info_frame = ttk.Frame(deck_window)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text="Deck Name:").grid(row=0, column=0, sticky=tk.W)
        deck_name_entry = ttk.Entry(info_frame)
        deck_name_entry.grid(row=0, column=1, sticky=tk.W)
        deck_name_entry.insert(0, deck_data['name'])

        ttk.Label(info_frame, text="Deck Color:").grid(row=1, column=0, sticky=tk.W)
        deck_color_entry = ttk.Entry(info_frame)
        deck_color_entry.grid(row=1, column=1, sticky=tk.W)
        deck_color_entry.insert(0, deck_data['color'])

        ttk.Button(info_frame, text="Replace Image", command=lambda: self.replace_image(deck_id)).grid(row=0, column=2, padx=5)
        ttk.Button(info_frame, text="Replace Sound", command=lambda: self.replace_sound(deck_id)).grid(row=1, column=2, padx=5)

        # Create a frame for the cards
        cards_frame = ttk.Frame(deck_window)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a canvas and scrollbar
        canvas = tk.Canvas(cards_frame)
        scrollbar = ttk.Scrollbar(cards_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)


        # Function to add a new card
        def add_card(answer="", hints=["", "", ""]):
            card_frame = ttk.Frame(scrollable_frame)
            card_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(card_frame, text="Answer:").pack(side=tk.LEFT)
            answer_entry = ttk.Entry(card_frame)
            answer_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            answer_entry.insert(0, answer)

            hints_frame = ttk.Frame(scrollable_frame)
            hints_frame.pack(fill=tk.X, padx=5, pady=5)

            hint_entries = []
            for i, hint in enumerate(hints):
                ttk.Label(hints_frame, text=f"Hint {i+1}:").grid(row=i, column=0, sticky=tk.W)
                hint_entry = ttk.Entry(hints_frame)
                hint_entry.grid(row=i, column=1, sticky=tk.EW)
                hint_entry.insert(0, hint)
                hint_entries.append(hint_entry)

            hints_frame.grid_columnconfigure(1, weight=1)

            return answer_entry, hint_entries

        # Add existing cards
        card_widgets = []
        for card in deck_data['cards']:
            card_widgets.append(add_card(card['answer'], card['hints']))

        # Add button to add new cards
        ttk.Button(deck_window, text="Add Card", command=lambda: card_widgets.append(add_card())).pack(pady=10)

        # Save button
        def save_deck():
                deck_data['name'] = deck_name_entry.get()
                deck_data['color'] = deck_color_entry.get()
                deck_data['cards'] = []
                for answer_entry, hint_entries in card_widgets:
                    deck_data['cards'].append({
                        "answer": answer_entry.get(),
                        "hints": [hint.get() for hint in hint_entries]
                    })
                with open(deck_path, 'w') as f:
                    json.dump(deck_data, f, indent=2)
                
                # Update main treeview
                for item in self.decks_tree.get_children():
                    if self.decks_tree.item(item, "values")[1] == deck_id:
                        self.decks_tree.item(item, values=('', deck_id, deck_data['name'], deck_data['color'], self.decks_tree.item(item, "values")[4], 'Edit'))
                        break
                
                deck_window.destroy()

        ttk.Button(deck_window, text="Save Deck", command=save_deck).pack(pady=10)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def compress_pack(self, folder_path, output_path):
        # Create a temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the entire pack structure to the temp directory
            temp_pack_dir = os.path.join(temp_dir, os.path.basename(folder_path))
            shutil.copytree(folder_path, temp_pack_dir)
            
            # Process deck folder
            deck_path = os.path.join(temp_pack_dir, "deck")
            for file in os.listdir(deck_path):
                if file.endswith(".json"):
                    file_path = os.path.join(deck_path, file)
                    self.shift_bits(file_path, shift_up=True)
                    os.rename(file_path, file_path[:-5] + ".gcd")
            
            with zipfile.ZipFile(os.path.join(temp_pack_dir, "deck.gcdp"), 'w') as zipf:
                for root, _, files in os.walk(deck_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            
            # Process image folder
            image_path = os.path.join(temp_pack_dir, "image")
            for file in os.listdir(image_path):
                if file.endswith(".png"):
                    file_path = os.path.join(image_path, file)
                    os.rename(file_path, file_path[:-4] + ".gci")
            
            with zipfile.ZipFile(os.path.join(temp_pack_dir, "image.gcip"), 'w') as zipf:
                for root, _, files in os.walk(image_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)

            # Process sound folder
            sound_path = os.path.join(temp_pack_dir, "sound")
            for file in os.listdir(sound_path):
                if file.endswith(".m4a"):
                    file_path = os.path.join(sound_path, file)
                    os.rename(file_path, file_path[:-4] + ".gcs")
            
            with zipfile.ZipFile(os.path.join(temp_pack_dir, "sound.gcsp"), 'w') as zipf:
                for root, _, files in os.walk(sound_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            
            # Delete temporary deck and image and sound folders
            shutil.rmtree(deck_path)
            shutil.rmtree(image_path)
            shutil.rmtree(sound_path)
            
            # Create final ZIP archive
            with zipfile.ZipFile(output_path, 'w') as zipf:
                zipf.write(os.path.join(temp_pack_dir, "info.json"), "info.json")
                zipf.write(os.path.join(temp_pack_dir, "deck.gcdp"), "deck.gcdp")
                zipf.write(os.path.join(temp_pack_dir, "image.gcip"), "image.gcip")
                zipf.write(os.path.join(temp_pack_dir, "sound.gcsp"), "sound.gcsp")

    def shift_bits(self, file_path, shift_up=True):
        with open(file_path, 'rb') as file:
            data = bytearray(file.read())
        
        for i in range(len(data)):
            if shift_up:
                data[i] = (data[i] << 1) & 255
            else:
                data[i] = (data[i] >> 1) & 255
        
        with open(file_path, 'wb') as file:
            file.write(data)


if __name__ == "__main__":
    root = customtkinter.CTk()
    app = GCPStudio(root)
    root.mainloop()