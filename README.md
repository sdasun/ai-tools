# AI Tools

This is a simple developer workflow / productivity script that uses ChatGPT. This is just a proof of concept, feel free to modify and extend it to suit your needs.

## Setup Instructions

### 1. Create a Virtual Environment

Ensure you have Python 3.12 or later installed. Create a virtual environment by running:

```bash
python3.12 -m venv venv
```

Activate the virtual environment:

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  .\venv\Scripts\activate
  ```

### 2. Install Dependencies

Install the required dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Make a copy of the `.env.example` file and update the variables appropriately:

```bash
cp .env.example .env
```

Edit the `.env` file and set the following variables:

```env
GITLAB_API_TOKEN=glpat-xxxx
GITLAB_PROJECT_ID=10000
CHATGPT_API_KEY=sk-xxxx
CHATGPT_MODEL="gpt-4o-mini"
GITLAB_USERNAME=dasunxxxx
GITLAB_USER_ID=10000
GITLAB_MR_PREFIX=https://gitlab.com/xxx/xxxx/xxx/-/merge_requests/
```

Replace the placeholder values with your actual credentials and settings.

### 4. Run the Application

After setting up the environment variables, you can run the application:

```bash
python main.py
```

## License

This project is licensed under the MIT License.
