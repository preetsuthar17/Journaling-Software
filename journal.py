import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


opened_tabs = {}
entries_displayed = {}


def create_table_if_not_exists():
    connection = sqlite3.connect('diary_entries.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT,
            entry_text TEXT
        )
    ''')
    connection.commit()
    connection.close()

def save_entry():
    current_date_time = datetime.datetime.now()
    entry_date = current_date_time.strftime('%Y-%m-%d %H:%M:%S')
    entry_text = text_entry.get('1.0', 'end-1c')
    
    connection = sqlite3.connect('diary_entries.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO entries (entry_date, entry_text) VALUES (?, ?)', (entry_date, entry_text))
    connection.commit()
    connection.close()
    
    update_entries_tab()

    text_entry.delete('1.0', tk.END)

def read_entries():
    connection = sqlite3.connect('diary_entries.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM entries')
    entries = cursor.fetchall()
    connection.close()
    return entries

def delete_entry(entry_id):
    connection = sqlite3.connect('diary_entries.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    connection.commit()
    connection.close()

def wipe_database():
    result = messagebox.askyesno("Wipe Database", "Are you sure you want to wipe the entire database?")
    if result:
        connection = sqlite3.connect('diary_entries.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM entries')
        connection.commit()
        connection.close()
        
        update_entries_tab()

def update_entries_tab():
    entries_tab = None
    for tab in notebook.tabs():
        if notebook.tab(tab, "text") == "Entries":
            entries_tab = tab
            break
    
    if entries_tab:
        entries_listbox = entries_displayed.get(entries_tab)
        if entries_listbox:
            entries_listbox.delete(0, tk.END)
            entries = read_entries()
            for entry in entries:
                entries_listbox.insert(tk.END, entry[1])
                entries_displayed[entry[0]] = entry[1]

def show_entries_tab():
    entries_tab = ttk.Frame(notebook)
    entries_listbox = tk.Listbox(entries_tab)
    entries_listbox.pack(fill=tk.BOTH, expand=True)
    
    entries = read_entries()
    for entry in entries:
        entries_listbox.insert(tk.END, entry[1])
    
    def on_entry_select(event):
        selected_index = entries_listbox.curselection()
        if selected_index:
            selected_entry = entries[selected_index[0]]
            show_entry_content(selected_entry)
    
    entries_listbox.bind("<<ListboxSelect>>", on_entry_select)
    entries_displayed[entries_tab] = entries_listbox 
    notebook.add(entries_tab, text="Entries")

def show_entry_content(selected_entry):
    if selected_entry[0] in opened_tabs:
        notebook.select(opened_tabs[selected_entry[0]])
        return
    
    content_tab = ttk.Frame(notebook)
    
    content_text = tk.Text(content_tab, wrap=tk.WORD)
    content_text.pack(fill=tk.BOTH, expand=True)
    content_text.insert(tk.END, selected_entry[2])
    
    close_button = tk.Button(content_tab, text='Close', command=lambda: close_content_tab(content_tab, selected_entry[0]))
    close_button.pack()
    
    delete_button = tk.Button(content_tab, text='Delete', command=lambda entry_id=selected_entry[0]: delete_selected_entry(entry_id))
    delete_button.pack()
    
    opened_tabs[selected_entry[0]] = notebook.add(content_tab, text=selected_entry[1])

def close_content_tab(content_tab, entry_id):
    notebook.forget(content_tab)
    del opened_tabs[entry_id]

def delete_selected_entry(entry_id):
    if entry_id in opened_tabs:
        tab_to_close = opened_tabs[entry_id]
        notebook.forget(tab_to_close)
        del opened_tabs[entry_id]
    
    delete_entry(entry_id)
    update_entries_tab()

def close_active_tab():
    selected_tab = notebook.select()
    if selected_tab:
        notebook.forget(selected_tab)
        
def on_text_click(event):
    if text_entry.get('1.0', 'end-1c') == 'Write your entry here...':
        text_entry.delete('1.0', tk.END) 
        text_entry.config(fg='black')    

root = tk.Tk()
root.title('Personal Journal')
root.configure(padx=10, pady=10)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

text_entry = tk.Text(root, height=10, width=150)
text_entry.insert('1.0', 'Write your entry here...') 
text_entry.config(fg='grey') 
text_entry.bind('<FocusIn>', on_text_click)
text_entry.pack()

save_button = tk.Button(root, text='Save',  command=save_entry)
save_button.pack()

read_button = tk.Button(root, text='Read Journal',  command=show_entries_tab)
read_button.pack()

wipe_button = tk.Button(root, text='Wipe Journal',  command=wipe_database)
wipe_button.pack()

close_tab_button = tk.Button(root, text='Close Tab',  command=close_active_tab)
close_tab_button.pack()

create_table_if_not_exists()

root.mainloop()
