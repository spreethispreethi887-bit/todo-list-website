import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3 as sql
from PIL import Image, ImageTk
from datetime import datetime

# Function to add tasks to the list with a deadline
def add_task():
    task_string = task_field.get()
    deadline_string = deadline_field.get()
    if len(task_string) == 0 or len(deadline_string) == 0:
        messagebox.showinfo('Error', 'Task or Deadline field is empty.')
    else:
        try:
            deadline = datetime.strptime(deadline_string, "%Y-%m-%d %H:%M")  # Parse the deadline
            tasks.append((task_string, deadline, False))  # Store the task, deadline, and completion status
            the_cursor.execute('insert into tasks values (?, ?, ?)', (task_string, deadline_string, False))
            task_field.delete(0, 'end')
            deadline_field.delete(0, 'end')

            # Check for deadline alerts
            check_deadline_alerts()
        except ValueError:
            messagebox.showinfo('Error', 'Invalid deadline format. Use YYYY-MM-DD HH:MM')

# Function to check deadlines and show alert if any deadlines are missed
def check_deadline_alerts():
    current_time = datetime.now()
    for task, deadline, completed in tasks:
        if current_time > deadline and not completed:
            messagebox.showwarning("Deadline Alert", f"Task '{task}' is past the deadline!")

# Function to mark a task as completed
def mark_task_completed():
    if not tasks:
        messagebox.showinfo("Error", "No tasks available to complete.")
        return

    # Create a popup window for selecting the task to mark as completed
    complete_popup = tk.Toplevel()
    complete_popup.title("Mark Task Completed")
    complete_popup.geometry("300x250")

    instruction_label = ttk.Label(complete_popup, text="Select a task to mark as completed:", font=("Consolas", 11))
    instruction_label.pack(pady=10)

    # Create a listbox to display tasks
    complete_listbox = tk.Listbox(complete_popup, width=40, height=10, selectmode='SINGLE')
    complete_listbox.pack(pady=5)

    # Populate the listbox with tasks
    for index, (task, deadline, completed) in enumerate(tasks):
        status = "(Completed)" if completed else ""
        complete_listbox.insert(tk.END, f"{index + 1}. {task} - Deadline: {deadline.strftime('%Y-%m-%d %H:%M')} {status}")

    # Function to perform task completion
    def perform_completion():
        try:
            selected_index = complete_listbox.curselection()[0]
            task_to_complete = tasks[selected_index][0]
            tasks[selected_index] = (task_to_complete, tasks[selected_index][1], True)  # Update completion status
            the_cursor.execute('UPDATE tasks SET completed = ? WHERE title = ?', (True, task_to_complete))
            messagebox.showinfo("Task Completed", f"Task '{task_to_complete}' has been marked as completed.")
            complete_popup.destroy()  # Close the popup window
        except IndexError:
            messagebox.showinfo("Error", "Please select a task to complete.")

    # Add Complete Button
    complete_button = ttk.Button(complete_popup, text="Complete Selected Task", command=perform_completion)
    complete_button.pack(pady=10)

# Updated function to delete a selected task using a popup with a listbox
def delete_task_popup():
    if not tasks:
        messagebox.showinfo("Error", "No tasks to delete.")
        return

    # Create a popup window (Toplevel)
    delete_popup = tk.Toplevel()
    delete_popup.title("Delete Task")
    delete_popup.geometry("300x250")

    # Label for instructions
    instruction_label = ttk.Label(delete_popup, text="Select a task to delete:", font=("Consolas", 11))
    instruction_label.pack(pady=10)

    # Create a listbox to display tasks
    delete_listbox = tk.Listbox(delete_popup, width=40, height=10, selectmode='SINGLE')
    delete_listbox.pack(pady=5)

    # Populate the listbox with tasks
    for index, (task, deadline, completed) in enumerate(tasks):
        status = "(Completed)" if completed else ""
        delete_listbox.insert(tk.END, f"{index + 1}. {task} - Deadline: {deadline.strftime('%Y-%m-%d %H:%M')} {status}")

    # Function to perform task deletion
    def perform_deletion():
        try:
            selected_index = delete_listbox.curselection()[0]
            task_to_delete = tasks[selected_index][0]
            tasks.pop(selected_index)  # Remove task from the list
            the_cursor.execute('DELETE FROM tasks WHERE title = ?', (task_to_delete,))
            messagebox.showinfo("Task Deleted", f"Task '{task_to_delete}' has been deleted.")
            delete_popup.destroy()  # Close the popup window
        except IndexError:
            messagebox.showinfo("Error", "Please select a task to delete.")

    # Add Delete Button
    delete_button = ttk.Button(delete_popup, text="Delete Selected Task", command=perform_deletion)
    delete_button.pack(pady=10)

# Function to delete all tasks
def delete_all_tasks():
    message_box = messagebox.askyesno('Delete All', 'Are you sure you want to delete all tasks?')
    if message_box:
        tasks.clear()  # Clear the list
        the_cursor.execute('DELETE FROM tasks')  # Clear the database
        messagebox.showinfo("Deleted", "All tasks have been deleted.")

# Function to show tasks in a table format popup window
def show_tasks_table():
    if not tasks:
        messagebox.showinfo("Tasks", "No tasks available.")
    else:
        # Create a popup window (Toplevel)
        table_popup = tk.Toplevel()
        table_popup.title("Task List")
        table_popup.geometry("300x250")

        # Create headers for the table
        task_num_label = ttk.Label(table_popup, text="Task No.", font=("Consolas", 10, "bold"))
        task_desc_label = ttk.Label(table_popup, text="Task Description", font=("Consolas", 10, "bold"))

        task_num_label.grid(row=0, column=0, padx=10, pady=5)
        task_desc_label.grid(row=0, column=1, padx=10, pady=5)

        # Populate the table with tasks
        for index, (task, deadline, completed) in enumerate(tasks):
            task_num = ttk.Label(table_popup, text=f"{index + 1}", font=("Consolas", 10))
            status = "(Completed)" if completed else ""
            task_desc = ttk.Label(table_popup, text=f"{task})- Deadline: {deadline.strftime('%Y-%m-%d %H:%M')} {status}", font=("Consolas", 10))
            task_num.grid(row=index + 1, column=0, padx=10, pady=5)
            task_desc.grid(row=index + 1, column=1, padx=10, pady=5)

# Function to retrieve tasks from the database
def retrieve_database():
    tasks.clear()
    for row in the_cursor.execute('select title, deadline, completed from tasks'):
        task = row[0]
        deadline = datetime.strptime(row[1], "%Y-%m-%d %H:%M")
        completed = bool(row[2])  # Convert to boolean
        tasks.append((task, deadline, completed))

# Function to close the application
def close():
    the_connection.commit()
    the_cursor.close()
    guiWindow.destroy()

# Function to update the time label
def update_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format current date and time
    time_label.config(text=current_time)  # Update the time label
    guiWindow.after(1000, update_time)  # Update every second

# Main function
if __name__ == "__main__":
    # Initialize window
    guiWindow = tk.Tk()
    guiWindow.title("To-Do List Manager")
    guiWindow.geometry("500x450")
    guiWindow.resizable(0, 0)

    # Connect to database
    the_connection = sql.connect('listOfTasks.db')
    the_cursor = the_connection.cursor()
    # Drop the table if it exists
    the_cursor.execute('DROP TABLE IF EXISTS tasks')
    # Create the new table with the deadline and completed columns
    the_cursor.execute('CREATE TABLE tasks (title TEXT, deadline TEXT, completed BOOLEAN)')

    tasks = []

    # Load background image
    background_image = Image.open("C:\\Users\\User\\Desktop\\team project\\bw.png")  # Specify the path to your image
    background_image = background_image.resize((500, 450), Image.LANCZOS)  # Resize to fit the window
    bg_image = ImageTk.PhotoImage(background_image)

    # Create a canvas to place the background image
    canvas = tk.Canvas(guiWindow, width=500, height=450)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)

    # Define frames for widgets (on the canvas)
    header_frame = tk.Frame(guiWindow)
    functions_frame = tk.Frame(guiWindow)

    # Place frames on the canvas
    canvas.create_window(250, 50, window=header_frame)  # Center header
    canvas.create_window(250, 250, window=functions_frame)  # Center for buttons

    # Header Label
    header_label = ttk.Label(
        header_frame,
        text="The To-Do List",
        font=("Brush Script MT", 30),
    )
    header_label.pack(padx=0, pady=0)

    # Current Time Label
    time_label = ttk.Label(
        header_frame,
        text="",
        font=("Consolas", 12),
    )
    time_label.pack(pady=0)

    # Task Entry Label and Field
    task_label = ttk.Label(
        functions_frame,
        text="Enter the Task:",
        font=("Consolas", 11, "bold"),
    )
    task_label.pack(pady=0)

    task_field = ttk.Entry(
        functions_frame,
        font=("Consolas",12),
        width=18
    )
    task_field.pack(pady=0)

    # Deadline Entry Label and Field
    deadline_label = ttk.Label(
        functions_frame,
        text="Enter the Deadline (YYYY-MM-DD HH:MM):",
        font=("Consolas", 11,"bold"),
    )
    deadline_label.pack(pady=0)

    deadline_field = ttk.Entry(
        functions_frame,
        font=("Consolas",12),
        width=18
    )
    deadline_field.pack(pady=0)

    # Buttons
    add_button = ttk.Button(functions_frame, text="Add Task", width=24, command=add_task)
    show_table_button = ttk.Button(functions_frame, text="Show Task List", width=24, command=show_tasks_table)  # Button to show tasks in table format
    mark_completed_button = ttk.Button(functions_frame, text="Mark Task Completed", width=24, command=mark_task_completed)  # New button for marking task as completed
    del_button = ttk.Button(functions_frame, text="Delete Task", width=24, command=delete_task_popup)
    del_all_button = ttk.Button(functions_frame, text="Delete All Tasks", width=24, command=delete_all_tasks)
    exit_button = ttk.Button(functions_frame, text="Exit", width=24, command=close)

    add_button.pack(pady=5)
    show_table_button.pack(pady=5)  # Positioned right after the Add Task button
    mark_completed_button.pack(pady=5)  # Position the new button here
    del_button.pack(pady=5)
    del_all_button.pack(pady=5)
    exit_button.pack(pady=5)

    # Retrieve tasks from the database
    retrieve_database()

    # Start updating time
    update_time()

    guiWindow.mainloop()
