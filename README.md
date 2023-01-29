# Du It!
#### Video Demo: https://youtu.be/_LK3Bt1pypw
#### Description: Du It! is a simple to-do list which allows users to log in and create to-do tasks inside their respective lists. It has a list of buttons on the left side to display the respective list of tasks on the right side. In the table of tasks, there are columns for the title of the task, its due date, whether it is completed and a button for deletion of the task. There is also a settings page for users to edit their profile or delete their account.

##### Login page (login.html): User is automatically redirected to this page if he/she has not logged in. The program rejects any missing inputs or invalid username and password combination with an alert on top of the form.

##### Register page (register.html): Users without an account can create an account on this page. Similar to the login page, the program rejects any missing inputs, if the passwords do not match or if the username is already taken with an alert on top of the form. After registering the account, the user is directed to the homepage.

##### Layout (layout.html): The layout has a few links, "Du It!" redirects it to the homepage, "Add list" lets users create a new list to store their tasks under, "Add task" to add another task to an existing list. "Settings" is a dropdown menu which lets users change their username, password or delete their account. About gives information about the project and logout logs the user out.

##### Homepage (index.html, list.html): If the user has no current list(s), the homepage has a message of "Create a list to get started!", prompting the user to create a list. (index.html) If the user has one or more lists, they are displayed on the left hand side as buttons. The buttons display the respective list of tasks and there is also a counter for uncompleted task situated in the header. If the task has been completed, the user can click on the button with a checkbox icon to indicate it in the server and there will be a strikethrough on the respective task. Alternatively, the user can delete the task from the list. If the deleted task is the last task, the list itself is also deleted. (list.html)

##### Add list (addlist.html): Allows user to add a list and a task under that list. The system will reject the form if name of list, name of task or due date of task is not inputted with an alert.

##### Add task (addtask.html): Allows user to add a task under an existing list. The system will reject the form if a list is not selected or if name of task or due date is not inputted. If the user does not have an existing list, he/she will not be able to add a task.

##### Settings (edituser.html, editpass.html, delete.html): Allows user to change their username or password. To ensure it is the user doing so, there is also an input for the user's password. The system will reject any missing fields or if the password is incorrect with an alert. If all is successful, the system will return a success alert depending on whether the username or password is changed. The user can also delete their account and there will be a prompt asking for the user's confirmation. If the user confirms, all user data are deleted from the database and the user is redirected to the login page.

##### About (about.html): Has information on the project and an inspirational quote.