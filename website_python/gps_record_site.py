from app import app
import gps_record

if __name__ == '__main__':
	gps_record.setup_recording()
	app.run(debug=True)