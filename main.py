
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker (Трекер прочитанных книг)")
        self.books = []
        self.tree = None
        self.setup_ui()
        self.load_books()

    def setup_ui(self):
        # Поля ввода
        fields_frame = ttk.Frame(self.root)
        fields_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(fields_frame, text="Название:").grid(row=0, column=0, sticky='w')
        self.title_entry = ttk.Entry(fields_frame, width=20)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(fields_frame, text="Автор:").grid(row=0, column=2, sticky='w')
        self.author_entry = ttk.Entry(fields_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5)

        ttk.Label(fields_frame, text="Жанр:").grid(row=1, column=0, sticky='w')
        self.genre_entry = ttk.Entry(fields_frame, width=20)
        self.genre_entry.grid(row=1, column=1, padx=5)

        ttk.Label(fields_frame, text="Страниц:").grid(row=1, column=2, sticky='w')
        self.pages_entry = ttk.Entry(fields_frame, width=20)
        self.pages_entry.grid(row=1, column=3, padx=5)

        ttk.Button(fields_frame, text="Добавить книгу", command=self.add_book).grid(row=2, column=1, columnspan=2, pady=10)

        # Фильтры
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0)
        self.genre_filter = ttk.Combobox(filter_frame, width=15)
        self.genre_filter.grid(row=0, column=1, padx=5)
        self.genre_filter.bind('<<ComboboxSelected>>', self.apply_filters)

        ttk.Label(filter_frame, text="Страниц >").grid(row=0, column=2)
        self.pages_filter = ttk.Entry(filter_frame, width=10)
        self.pages_filter.insert(0, "200")
        self.pages_filter.grid(row=0, column=3, padx=5)
        ttk.Button(filter_frame, text="Фильтр", command=self.apply_filters).grid(row=0, column=4)
        ttk.Button(filter_frame, text="Сброс", command=self.reset_filters).grid(row=0, column=5, padx=5)

        ttk.Button(filter_frame, text="Сохранить", command=self.save_books).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="Загрузить", command=self.load_books).grid(row=0, column=7)

        # Таблица
        table_frame = ttk.Frame(self.root)
        table_frame.pack(pady=10, padx=10, fill='both', expand=True)

        columns = ('Название', 'Автор', 'Жанр', 'Страниц')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_text = self.pages_entry.get().strip()

        if not all([title, author, genre, pages_text]):
            messagebox.showerror("Ошибка", "Все поля обязательны!")
            return

        try:
            pages = int(pages_text)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Страниц должно быть положительным числом!")
            return

        book = {'title': title, 'author': author, 'genre': genre, 'pages': pages}
        self.books.append(book)
        self.update_tree()
        self.update_genre_filter()
        self.clear_entries()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def update_tree(self, filtered_books=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        books_to_show = filtered_books or self.books
        for book in books_to_show:
            self.tree.insert('', 'end', values=(book['title'], book['author'], book['genre'], book['pages']))

    def update_genre_filter(self):
        genres = sorted(set(book['genre'] for book in self.books))
        self.genre_filter['values'] = ['Все'] + genres
        self.genre_filter.set('Все')

    def apply_filters(self, event=None):
        genre = self.genre_filter.get()
        pages_text = self.pages_filter.get().strip()
        filtered = self.books[:]

        if genre != 'Все':
            filtered = [b for b in filtered if b['genre'] == genre]

        try:
            min_pages = int(pages_text) if pages_text else 0
            filtered = [b for b in filtered if b['pages'] > min_pages]
        except ValueError:
            pass

        self.update_tree(filtered)

    def reset_filters(self):
        self.genre_filter.set('Все')
        self.pages_filter.delete(0, tk.END)
        self.pages_filter.insert(0, "200")
        self.update_tree()

    def save_books(self):
        try:
            with open('books.json', 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены в books.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_books(self):
        try:
            if os.path.exists('books.json'):
                with open('books.json', 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
                self.update_tree()
                self.update_genre_filter()
                messagebox.showinfo("Успех", "Данные загружены")
            else:
                messagebox.showinfo("Инфо", "Файл books.json не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()