# AntiGravity Workout Tracker

A premium workout tracking application tied to a Python backend.

## Features
- **Dashboard**: Select muscle groups and log workouts.
- **Logging**: Record logs with weight and reps for specific exercises.
- **History**: View past workout sessions with detailed breakdowns.
- **Admin**: Add or remove muscle groups and exercises.
- **Secure Auth**: JWT-based login system (Username: `GPU`, Password: `Gp119`).
- **Mobile Friendly**: optimized for touch and mobile viewports.
- **Design**: Dark mode with "Glassmorphism" aesthetics.

## Local Setup & Run

### Prerequisites
- Python 3.x

### Installation
1. **Clone the repo**:
   ```bash
   git clone https://github.com/guru-1432/AntiGravity.git
   cd AntiGravity/Workout_App
   ```

2. **Run the Setup & Start Script**:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

Or manually:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 seed.py  # Populates initial data
python3 main.py
```

Then open your browser to: **http://localhost:8000**

## deploying to AWS (Unix/Linux)

Run the following commands on your AWS instance:

1. **Update and Install Python/Git**:
   ```bash
   sudo yum update -y  # For Amazon Linux
   # OR sudo apt update && sudo apt install -y python3-venv git  # For Ubuntu
   sudo yum install -y git python3
   ```

2. **Clone and Setup**:
   ```bash
   git clone https://github.com/guru-1432/AntiGravity.git
   cd AntiGravity/Workout_App/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Initialize Database**:
   ```bash
   python3 seed.py
   ```

4. **Run the Server**:
   ```bash
   # Run in background with nohup so it stays alive after you disconnect
   nohup python3 main.py > app.log 2>&1 &
   ```

**Important**: Ensure your AWS Security Group allows Inbound Custom TCP traffic on port **8000**.
