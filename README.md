# Chat Web Application in Jinja

## Overview
The Chat Web Application in Jinja is a web-based platform where users can create chatrooms and communicate with each other. It utilizes Flask for the server-side application, Jinja for templating, and WebSockets for real-time communication. The application supports user authentication, friend management, and article posting with comments.

## Features
- **User Authentication:** Sign up, log in, and log out functionalities.
- **Chatrooms:** Create and join chatrooms to communicate with friends in real-time.
- **Friend Management:** Send, approve, reject, and remove friend requests.
- **Articles and Comments:** Users can post articles and comments.
- **Admin Controls:** Mute and unmute users, manage user roles.

## Getting Started

### Prerequisites
- Python 3.x
- SQLite (for database)
- Node.js (for dependency management if needed)

### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/ap539813/Chat-Web-Application-in-Jinja
    cd Chat-Web-Application-in-Jinja
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Generate encryption keys:
    ```sh
    python -c "from encryption import get_encryption_key; get_encryption_key()"
    ```

5. Run the application:
    ```sh
    python app.py
    ```

## File Structure
- **app.py:** Contains the main Flask application and request handlers.
- **db.py:** Contains the logic to interface with the SQL database.
- **encryption.py:** Handles encryption key generation and management.
- **models.py:** Defines SQLAlchemy models for the database.
- **socket_routes.py:** Contains all the routes related to socket.io.
- **templates/:** Contains Jinja templates for the web pages.
- **static/css/:** Contains CSS stylesheets.
- **static/js/:** Contains JavaScript files.

## Running the Application
To run the application, navigate to the project directory and execute the following command:
```sh
python app.py
```
The application will be available at `https://localhost:443`.

## Usage
### User Authentication
- **Sign Up:** Navigate to `/signup` and create a new account.
- **Login:** Navigate to `/login` and enter your credentials.
- **Logout:** Click the logout button in the navigation bar.

### Chatrooms
- **Join Chatroom:** Enter a friend’s username and click "Chat" to join a room.
- **Send Message:** Type a message and press "Enter" or click "Send".

### Friend Management
- **Send Friend Request:** Enter a username and click "Send Friend Request".
- **Approve/Reject Requests:** Manage incoming friend requests from the Friend Requests section.

### Articles and Comments
- **Post Article:** Navigate to the Articles section and submit a new article.
- **Comment:** Add comments to articles.

## Dependencies
- Flask
- Flask-SocketIO
- SQLAlchemy
- cryptography
- Jinja2

Check `requirements.txt` for the full list of dependencies.

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -am 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.
