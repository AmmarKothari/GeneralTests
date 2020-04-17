import app
import app.forms as af
import flask
import gps_record

points_recorded = 1

class test_routes(object):
	def __init__(self):
		self.i = 0

	@app.app.route('/index', methods=['GET', 'POST'])
	def index(self):
		print('Home page requested')
		return('Home page in gps test class')

@app.app.route('/')
def redirect_to_index():
	print('Going to index')
	print(flask.url_for('index'))
	return flask.redirect(flask.url_for('index'))

# @app.app.route('/index', methods=['GET', 'POST'])
# def index():
# 	print('Home page requested')
# 	form = af.LoginForm()
# 	if form.validate_on_submit():
# 		print('Recording point')
# 		flask.flash('Recording point: {}'.format('N/A'))
# 		# flask.flash('Recording point: {}'.format(points_recorded))
# 		# points_recorded += 1
# 		return flask.redirect(flask.url_for('index'))
# 	return flask.render_template('index.html', points=gps_record.load_lle_points(gps_record.mock_points), form=form)

@app.app.route('/record_point')
def record_point():
	print('Recording point')
	gps_record.record_lle_point()
	return flask.redirect(flask.url_for('index'))

@app.app.route('/get_rtk_fix_status', methods=['POST'])
def get_rtk_fix_status():
	return flask.jsonify({'text': gps_record.fix_status()})