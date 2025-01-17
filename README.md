# Starships Backend

## **Overview**

This backend application serves as a central system to manage and expose data related to Star Wars starships. The
application synchronizes data from an external Star Wars API, stores it in a local relational database, and exposes
endpoints for querying and managing the data.

---

## **Features**

### **1. Synchronization from External API**

- The backend periodically synchronizes data from the external **[Star Wars API](https://swapi.tech/)**.
- Only new or updated records are fetched and stored locally.
- Unused or outdated records are removed to keep the database clean.

### **2. Exposed APIs**

The backend provides a set of RESTful APIs for querying starships and their manufacturers, including:

- **Authentication Endpoint:** Secure access using JWT.
- **Manufacturers Endpoint:** List and filter manufacturers.
- **Starships Endpoint:**
    - Paginated list of starships.
    - Filter by manufacturer.
    - Retrieve detailed information for a specific starship.

### **3. Relational Database**

- Starships and their manufacturers are stored in a SQLite database for simplicity.
- Data relationships are maintained between starships and manufacturers.

### **4. Periodic Synchronization**

- Background jobs handle periodic synchronization of data using **Flask Scheduler**.

---

## **Technologies Used**

- **Python** (v3.x)
- **Flask**
- **SQLAlchemy** (ORM)
- **Flask-Migrate** (for database migrations)
- **Flask-JWT-Extended** (for authentication)
- **SQLite** (database)
- **Flask-Scheduler** (for background jobs)

---

## **Setup Instructions**

### **1. Prerequisites**

- Python 3.x installed.
- A virtual environment tool (e.g., `venv` or `virtualenv`).

### **2. Clone the Repository**

```bash
$ git clone <repository-url>
$ cd <repository-folder>
```

### **3. Set Up the Environment**

1. Create a virtual environment:
    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2. Install dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```

### **4. Environment Variables**

Create a `.env` file in the root directory with the following variables:

```env
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///starships.db
JWT_SECRET_KEY=your_jwt_secret_key
```

### **5. Initialize the Database**

1. Run database migrations:
    ```bash
    $ flask db upgrade
    ```
2. Populate the database with synchronized data:
    ```bash
    $ flask shell
    >>> from app.sync.sync_job import SyncJob
    >>> SyncJob.sync_starships()
    >>> exit()
    ```

### **6. Start the Application**

Run the Flask development server:

```bash
$ flask run
```

The application will be available at `http://127.0.0.1:5000`.

---

## **API Documentation**

### **1. Authentication**

- **Endpoint:** `/api/authenticate`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin"
  }
  ```
- **Response:**
  ```json
  {
    "token": "<JWT_TOKEN>"
  }
  ```

### **2. Manufacturers**

- **Endpoint:** `/api/manufacturers`
- **Method:** `GET`
- **Query Parameters:**
    - `name`: (optional) Filters manufacturers by name.
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "Kuat Drive Yards"
    },
    {
      "id": 2,
      "name": "Corellian Engineering Corporation"
    }
  ]
  ```

### **3. Starships List**

- **Endpoint:** `/api/starships`
- **Method:** `GET`
- **Query Parameters:**
    - `manufacturer_id`: (optional) Filters starships by manufacturer ID.
    - `page`: (optional) Page number for pagination (default: 1).
    - `limit`: (optional) Number of items per page (default: 10).
- **Response:**
  ```json
  {
    "starships": [
      {
        "id": 1,
        "name": "Millennium Falcon",
        "model": "YT-1300 light freighter",
        "class": "Light Freighter",
        "length": "34.75",
        "manufacturer": ["Corellian Engineering Corporation"]
      }
    ],
    "total_items": 1
  }
  ```

### **4. Starship Details**

- **Endpoint:** `/api/starships/<starship_id>`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "id": 1,
    "name": "Millennium Falcon",
    "model": "YT-1300 light freighter",
    "starship_class": "Light Freighter",
    "cost_in_credits": "100000",
    "length": "34.75",
    "crew": "4",
    "passengers": "6",
    "max_atmosphering_speed": "1050",
    "hyperdrive_rating": "0.5",
    "MGLT": "75",
    "cargo_capacity": "100000",
    "consumables": "2 months",
    "created_at": "2023-01-01T00:00:00Z",
    "edited_at": "2023-01-01T00:00:00Z",
    "url": "https://swapi.tech/api/starships/1/",
    "manufacturers": ["Corellian Engineering Corporation"]
  }
  ```

---

## **Periodic Synchronization**

### **Background Job**

The application uses **Flask Scheduler** to periodically synchronize data from the external API.

- Synchronization logic fetches paginated data from the API.
- Only updates records if the `edited` timestamp is newer than the last synchronization.

To enable automatic synchronization, ensure the scheduler is initialized when the app starts.

---

## **Contributing**

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

---

## **License**

This project is licensed under the MIT License.
