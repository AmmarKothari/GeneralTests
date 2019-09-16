from app import app
from gps_record import setup_recording

if __name__ == '__main__':
	setup_recording()
	app.run(debug=True)