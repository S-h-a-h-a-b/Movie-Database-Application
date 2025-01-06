import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style, ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

class MovieDataApp:
    def __init__(self, root):
        self.style = Style(theme='flatly')
        self.root = root
        self.root.title("Movie Database")
        self.root.geometry("880x650")
        self.api_key = "c32f0d4901cfaa75c5ed7b553a8415f2"
        self.base_url = "https://api.themoviedb.org/3"
        self.img_url = "https://image.tmdb.org/t/p/w500"
        self.favs = []
        self.style.configure('TFrame', background='white')
        self.style.configure('Custom.TLabel', foreground='black', background='white')
        self.style.configure('MovieTitle.TLabel', font=('Helvetica', 20, 'bold'), foreground='black', background='white')
        self.style.configure('MovieOverview.TLabel', font=('Helvetica', 11), foreground='black', background='white')
        self.style.configure('TLabelframe', background='white')
        self.style.configure('TLabelframe.Label', background='white')
        self.style.configure('TNotebook', background='white')
        self.style.configure('TNotebook.Tab', background='white')
        self.style.configure('Vertical.TScrollbar', background='#EBF0F1', troughcolor='#EBF0F1')
        self.setup_ui()

    def setup_ui(self):
        self.main_cont = ttk.Frame(self.root, padding="10", style='TFrame')
        self.main_cont.pack(expand=True, fill='both')
        self.notebook = ttk.Notebook(self.main_cont)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        frames = {'search': ttk.Frame(self.notebook, padding="10", style='TFrame'), 'trending': ttk.Frame(self.notebook, padding="10", style='TFrame'), 'favorites': ttk.Frame(self.notebook, padding="10", style='TFrame')}
        for name, frame in frames.items():
            self.notebook.add(frame, text=name.capitalize())
            setattr(self, f"{name}_frame", frame)
        self.genres = self.fetch_data(f"{self.base_url}/genre/movie/list")['genres']
        self.genres = {genre['name']: genre['id'] for genre in self.genres}
        self.setup_search_frame()
        self.setup_trending_frame()
        self.setup_favorites_frame()
        ttk.Button(self.main_cont, text="Help", style='info.TButton', command=self.show_help).pack(side='right', padx=10, pady=5)

    def fetch_data(self, url, params=None):
        default_params = {'api_key': self.api_key}
        if params: default_params.update(params)
        try:
            response = requests.get(url, params=default_params)
            return response.json()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return {}

    def fetch_poster(self, movie):
        if movie.get('poster_path'):
            try:
                response = requests.get(f"{self.img_url}{movie['poster_path']}")
                img = Image.open(BytesIO(response.content))
                img = img.resize((150, 225), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception: return None
        return None

    def setup_search_frame(self):
        search_opts = ttk.LabelFrame(self.search_frame, text="Search Options", padding="15", style='info.TLabelframe')
        search_opts.pack(fill='x', padx=5, pady=5)
        inputs = [("Movie Title:", ttk.Entry, {'width': 40, 'style': 'info.TEntry'}, 'title_entry'), ("Year:", ttk.Combobox, {'width': 10, 'values': ["All Years"] + [str(year) for year in range(datetime.now().year, 1900, -1)], 'style': 'info.TCombobox'}, 'year_var'), ("Genre:", ttk.Combobox, {'width': 20, 'values': ["All Genres"] + list(self.genres.keys()), 'style': 'info.TCombobox'}, 'genre_var')]
        for row, (label, widget_class, widget_kwargs, attr_name) in enumerate(inputs):
            ttk.Label(search_opts, text=label, style='Custom.TLabel').grid(row=row, column=0, padx=5, pady=5, sticky='e')
            widget = widget_class(search_opts, **widget_kwargs)
            widget.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            setattr(self, attr_name, widget)
        ttk.Button(search_opts, text="Search", style='primary.TButton', command=self.search_movies).grid(row=len(inputs), column=0, columnspan=2, pady=10)
        self.setup_scroll_frame(self.search_frame, 'scrollable_frame')

    def setup_trending_frame(self):
        btn_frame = ttk.Frame(self.trending_frame, style='light.TFrame')
        btn_frame.pack(fill='x', padx=5, pady=5)
        for period, label in [('day', 'Daily'), ('week', 'Weekly')]:
            ttk.Button(btn_frame, text=f"{label} Trending", style='primary.TButton', command=lambda p=period: self.load_trending(p)).pack(side='left', padx=5)
        self.setup_scroll_frame(self.trending_frame, 'trending_results')

    def setup_favorites_frame(self):
        ctrl_frame = ttk.Frame(self.favorites_frame, style='TFrame')
        ctrl_frame.pack(fill='x', padx=5, pady=5)
        canvas = tk.Canvas(self.favorites_frame, background='white')
        scrollbar = ttk.Scrollbar(self.favorites_frame, orient="vertical", command=canvas.yview)
        self.favs_list = ttk.Frame(canvas, style='TFrame')
        self.favs_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.favs_list, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        def _on_wheel(event):
            if event.num == 5 or event.delta < 0: canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: canvas.yview_scroll(-1, "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)
        canvas.bind_all("<Button-4>", _on_wheel)
        canvas.bind_all("<Button-5>", _on_wheel)
        def _unbind_wheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        def _bind_wheel(event):
            canvas.bind_all("<MouseWheel>", _on_wheel)
            canvas.bind_all("<Button-4>", _on_wheel)
            canvas.bind_all("<Button-5>", _on_wheel)
        canvas.bind('<Enter>', _bind_wheel)
        canvas.bind('<Leave>', _unbind_wheel)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def config_canvas(event): canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind('<Configure>', config_canvas)

    def setup_scroll_frame(self, parent, attr_name):
        canvas = tk.Canvas(parent, background='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style='TFrame')
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        def _on_wheel(event):
            if event.num == 5 or event.delta < 0: canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: canvas.yview_scroll(-1, "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)
        canvas.bind_all("<Button-4>", _on_wheel)
        canvas.bind_all("<Button-5>", _on_wheel)
        def _unbind_wheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        def _bind_wheel(event):
            canvas.bind_all("<MouseWheel>", _on_wheel)
            canvas.bind_all("<Button-4>", _on_wheel)
            canvas.bind_all("<Button-5>", _on_wheel)
        canvas.bind('<Enter>', _bind_wheel)
        canvas.bind('<Leave>', _unbind_wheel)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        setattr(self, attr_name, scroll_frame)

    def create_mov_frame(self, parent, movie, show_remove=False):
        mov_frame = ttk.Frame(parent, style='TFrame', padding="10")
        mov_frame.pack(fill='x', padx=5, pady=5)
        if poster_img := self.fetch_poster(movie):
            poster_label = ttk.Label(mov_frame, image=poster_img, background='white')
            poster_label.image = poster_img
            poster_label.pack(side='left', padx=10)
        content_frame = ttk.Frame(mov_frame, style='TFrame')
        content_frame.pack(side='left', fill='x', expand=True)
        year = movie['release_date'][:4] if movie['release_date'] else 'N/A'
        ttk.Label(content_frame, text=f"{movie['title']} ({year})", style='MovieTitle.TLabel').pack(anchor='w')
        if movie['overview']:
            ttk.Label(content_frame, text=movie['overview'], wraplength=600, style='MovieOverview.TLabel').pack(anchor='w', pady=5)
        btn_frame = ttk.Frame(content_frame, style='TFrame')
        btn_frame.pack(fill='x', pady=5)
        if movie not in self.favs:
            ttk.Button(btn_frame, text="Add to Favorites", style='success.TButton', command=lambda: self.add_fav(movie)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="View Details", style='info.Outline.TButton', command=lambda: self.show_details(movie)).pack(side='left', padx=5)
        if show_remove:
            ttk.Button(btn_frame, text="Remove", style='danger.TButton', command=lambda: self.remove_fav(movie)).pack(side='left', padx=5)
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)

    def search_movies(self):
        query = self.title_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a movie title!")
            return
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        params = {'query': query, 'language': 'en-US', 'page': 1, 'include_adult': False}
        if year := self.year_var.get(): params['year'] = year
        if (genre := self.genre_var.get()) in self.genres: params['with_genres'] = self.genres[genre]
        data = self.fetch_data(f"{self.base_url}/search/movie", params)
        if results := data.get('results', []):
            if genre in self.genres:
                genre_id = self.genres[genre]
                results = [movie for movie in results if genre_id in movie.get('genre_ids', [])]
            self.display_results(results[:10], self.scrollable_frame)
        else:
            messagebox.showinfo("No Results", "No movies found matching your search criteria.")

    def load_trending(self, time_window):
        for widget in self.trending_results.winfo_children(): widget.destroy()
        data = self.fetch_data(f"{self.base_url}/trending/movie/{time_window}")
        if results := data.get('results', []): self.display_results(results[:10], self.trending_results)

    def display_results(self, movies, parent):
        if not movies:
            ttk.Label(parent, text="No movies found matching your criteria", font=('Helvetica', 12)).pack(pady=20)
            return
        for movie in movies: self.create_mov_frame(parent, movie)

    def add_fav(self, movie):
        if movie not in self.favs:
            self.favs.append(movie)
            messagebox.showinfo("Success", f"{movie['title']} added to favorites!")
            self.refresh_favs()
        else: messagebox.showinfo("Info", "This movie is already in your favorites!")

    def remove_fav(self, movie):
        self.favs.remove(movie)
        self.refresh_favs()
        messagebox.showinfo("Success", f"{movie['title']} removed from favorites!")

    def refresh_favs(self):
        for widget in self.favs_list.winfo_children(): widget.destroy()
        if not self.favs:
            ttk.Label(self.favs_list, text="No favorites added yet!", font=('Helvetica', 12)).pack(pady=20)
            return
        for movie in self.favs: self.create_mov_frame(self.favs_list, movie, show_remove=True)

    def show_details(self, movie):
        details = tk.Toplevel(self.root)
        details.title("Details")
        details.geometry("750x500")
        details.transient(self.root)
        details.grab_set()
        main_frame = ttk.Frame(details, padding="20", style='TFrame')
        main_frame.pack(fill='both', expand=True)
        details.configure(bg='white')
        left_frame = ttk.Frame(main_frame, style='TFrame')
        left_frame.pack(side='left', padx=(0, 20))
        if poster_img := self.fetch_poster(movie):
            poster_label = ttk.Label(left_frame, image=poster_img, background='white')
            poster_label.image = poster_img
            poster_label.pack()
        right_frame = ttk.Frame(main_frame, style='TFrame')
        right_frame.pack(side='left', fill='both', expand=True)
        ttk.Label(right_frame, text=movie['title'], style='MovieTitle.TLabel').pack(anchor='w', pady=(0, 20))
        info_items = [('Release Date', movie['release_date']), ('Rating', f"{movie['vote_average']}/10 ({movie.get('vote_count', 0)} votes)"), ('Popularity', f"{movie['popularity']:.1f}")]
        for label, value in info_items:
            if value:
                frame = ttk.Frame(right_frame)
                frame.pack(fill='x', pady=5)
                ttk.Label(frame, text=f"{label}:", style='Custom.TLabel', font=('Helvetica', 12, 'bold')).pack(side='left', padx=(0, 10))
                ttk.Label(frame, text=value, style='Custom.TLabel', font=('Helvetica', 12)).pack(side='left')
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=20)
        if movie['overview']:
            overview = tk.Text(right_frame, wrap='word', height=8, font=('Helvetica', 11), fg='black', bg='white')
            overview.insert('1.0', movie['overview'])
            overview.configure(state='disabled')
            overview.pack(fill='both', expand=True)
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        if movie not in self.favs:
            ttk.Button(btn_frame, text="Add to Favorites", style='success.TButton', command=lambda: self.add_fav(movie)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", style='secondary.TButton', command=details.destroy).pack(side='right', padx=5)

    def show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("Help")
        help_win.geometry("600x400")
        help_win.transient(self.root)
        help_win.grab_set()
        help_frame = ttk.Frame(help_win, padding="20")
        help_frame.pack(fill='both', expand=True)
        help_text = tk.Text(help_frame, wrap='word', width=60, height=15)
        help_text.pack(fill='both', expand=True)
        help_content = """Search Movies Tab:
• Enter a movie title in the search box
• Optionally select a year and/or genre filter
• Click Search to find movies
• View movie details or add to favorites

Trending Tab:
• View daily or weekly trending movies
• Add movies to favorites or view details

Favorites Tab:
• View your saved favorite movies
• Remove movies from favorites
• View detailed information about saved movies

General Tips:
• Movie posters are displayed when available
• Click "View Details" for more information about any movie"""
        help_text.insert('1.0', help_content)
        help_text.configure(state='disabled')
        ttk.Button(help_frame, text="Close", command=help_win.destroy).pack(pady=(20, 0))

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieDataApp(root)
    root.mainloop()