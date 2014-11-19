from flask import (
    render_template, url_for, flash,
    request, redirect, abort,
    send_from_directory
)

from flask.ext.login import (
    login_user, logout_user,
    login_required, current_user
)

from netui import app, db, login_manager
from netui.models import User, Network, APList
from netui.forms import (
    LoginForm, ChangePasswordForm,
    NetworkForm, APListForm,
    SQLiteFileForm,
    DummyForm
)

from sqlalchemy.exc import OperationalError
from os.path import abspath, dirname, join
from NetIO import (
    EtherReader, WiFiReader,
    WiFiWriter
)

NETWORK_DEVICE = 'lo'
WIFI_PREF_FILE = '/etc/wpa1.conf'


# Login_manager: load user info
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


# helper function: db recovery
def _check_if_db_is_valid():
    try:
        num_user = User.query.count()
        num_network = Network.query.count()
        num_aplist = APList.query.count()
        return True
    except OperationalError:
        db.create_all()
        return False
    return None


def _db_check_or_rebuild():
    if not _check_if_db_is_valid():
        # recreate a fresh new database if it doesn't exist
        db.create_all()
        flash('Fresh new database generated.')

        # Generate user 'admin:admin'
        user = User(username='admin')
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()

        # ...and fetch new data from system
        _resync_network_in_db()
        _resync_aplist_in_db()
    else:
        # Everything is fine!
        pass


def _resync_network_in_db():
    # Fetch real network info in system
    sysconf_dict = EtherReader.fetch(device=NETWORK_DEVICE)
    sysconf = Network(**sysconf_dict)

    # Resync data in 'network'
    Network.query.delete()
    db.session.add(sysconf)
    db.session.commit()
    #flash('Resync Network data complete')


def _resync_aplist_in_db():
    # Clean all data in 'ap_list'
    APList.query.delete()

    # Resync data from our wifi configuration
    wifi_dicts = WiFiReader.fetch(WIFI_PREF_FILE)
    for wifi_dict in wifi_dicts:
        ap_from_file = APList(**wifi_dict)
        db.session.add(ap_from_file)

    db.session.commit()
    #flash('Resync WiFi data complete')


def _apply_aplist_to_system():
    ap_list = APList.query.order_by(APList.priority.desc()).all()
    new_apconf = []
    for ap in ap_list:
        new_apconf.append(ap._output_dict())
    WiFiWriter.write(WIFI_PREF_FILE, new_apconf)
    flash('Writing new WiFi configurations into board...')


# default index page
# anonymous: please login
# already logged in => go to welcome page
@app.route("/login/", methods=["GET", "POST"])
def login():
    _db_check_or_rebuild()

    form = LoginForm()
    if form.validate_on_submit():
        auth_user = User.authenticate(
            form.username.data,
            form.password.data
        )
        if auth_user:
            login_user(auth_user)
            flash('You are signed in!')
            return redirect(url_for('welcome'))
        else:
            flash('Wrong username or password')
    return render_template('user/login.html', form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Change user's password
@app.route('/settings/', methods=['GET', 'POST'])
def account_settings():
    form = ChangePasswordForm(user=current_user)
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password is successfully changed.", 'success')
        return redirect(url_for('welcome'))
    return render_template('user/settings.html', form=form)


@app.route('/')
@app.route('/welcome/')
@login_required
def welcome():
    _db_check_or_rebuild()

    sysconf_dict = EtherReader.fetch(device=NETWORK_DEVICE)
    sysconf = Network(**sysconf_dict)

    dbconf = Network.query.filter_by(device=NETWORK_DEVICE).first()
    # This should not happen, just in case
    if dbconf is None:
        dbconf = sysconf

    aplist = APList.query.order_by(APList.priority.desc())

    return render_template(
        'welcome.html',
        sysconf=sysconf,
        dbconf=dbconf,
        aplist=aplist
    )


@app.route('/sync/<db_name>')
@login_required
def sync_db(db_name):
    if db_name == 'all':
        _resync_network_in_db()
        _resync_aplist_in_db()
    elif db_name == 'network':
        _resync_network_in_db()
    elif db_name == 'aplist':
        _resync_aplist_in_db()
    else:
        # do nothing
        pass
    flash('Database sync completed.')
    return redirect(url_for('welcome'))


@app.route('/wireless/<int:ap_id>/')
@login_required
def view_ap(ap_id):
    result = APList.query.filter_by(id=ap_id).first()
    if result is None:
        return abort(404)
    else:
        return render_template('view_ap.html', ap=result)


@app.route('/wireless/create/', methods=['GET', 'POST'])
@login_required
def create_ap():
    form = APListForm(security='WPA')
    if form.validate_on_submit():
        ap_list = APList(
            ssid=form.ssid.data,
            security=form.security.data,
            psk=form.psk.data,
            priority=form.priority.data,
        )
        db.session.add(ap_list)
        db.session.commit()
        flash('AP create request sent.')
        return redirect(url_for('welcome'))
    return render_template('aplist/create.html', form=form)


@app.route('/wireless/<int:ap_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_ap(ap_id):
    result = APList.query.filter_by(id=ap_id).first()
    form = APListForm(
        ssid=result.ssid,
        security=result.security,
        psk=result.psk,
        priority=result.priority
    )
    if form.validate_on_submit():
        result.ssid = form.ssid.data
        result.security = form.security.data
        result.psk = form.psk.data
        result.priority = form.priority.data

        db.session.commit()
        flash('AP modify request sent.')
        return redirect(url_for('welcome'))
    return render_template('aplist/edit.html', ap=result, form=form)


@app.route('/wireless/<int:ap_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_ap(ap_id):
    result = APList.query.filter_by(id=ap_id).first()
    form = DummyForm()

    if request.method == 'POST':
        db.session.delete(result)
        db.session.commit()
        flash('AP delete request sent.')
        return redirect(url_for('welcome'))
    return render_template('aplist/delete.html', ap=result, form=form)



@app.route('/network/', methods=['GET', 'POST'])
@login_required
def edit_network():
    dbconf = Network.query.filter_by(device=NETWORK_DEVICE).first()
    form = NetworkForm(
        ip_addr=dbconf.ip_addr,
        subnet_mask=dbconf.subnet_mask,
        gateway=dbconf.gateway,
        dns=dbconf.dns,
        dynamic=dbconf.dynamic
    )
    if form.validate_on_submit():
        dbconf.ip_addr = form.ip_addr.data
        dbconf.subnet_mask = form.subnet_mask.data
        dbconf.gateway = form.gateway.data
        dbconf.dns = form.dns.data
        dbconf.dynamic = form.dynamic.data

        db.session.commit()
        flash('Network modify request sent.')
        return redirect(url_for('welcome'))
    return render_template('network/edit.html', form=form)


@app.route('/export/', methods=['GET', 'POST'])
@login_required
def export_db():
    try:
        import shutil
        basename = dirname(__file__)
        shutil.copy(
            join(basename, app.config['DB_REL_PATH']),
            join(basename, app.config['UPLOAD_FOLDER'], 'netui.sqlite')
        )
    except IOError as e:
        flash(e.strerror)
    return render_template('misc/export.html')


@app.route('/downloads/<path:filename>')
@login_required
def download_file(filename):
    basename = dirname(__file__)
    return send_from_directory(
        join(basename, app.config['UPLOAD_FOLDER']),
        filename
        )


@app.route('/import/', methods=['GET', 'POST'])
@login_required
def import_db():
    from werkzeug import secure_filename
    form = SQLiteFileForm()

    if form.validate_on_submit():
        basename = dirname(__file__)
        filename = secure_filename(form.db_file.data.filename)

        new_db_path = join(basename, app.config['UPLOAD_FOLDER'], filename)
        old_db_path = join(basename, app.config['DB_REL_PATH'])
        backup_db_path = old_db_path + '.backup'

        import shutil
        try:
            form.db_file.data.save(new_db_path)
            shutil.copy(old_db_path, backup_db_path)
            shutil.copy(new_db_path, old_db_path)
        except IOError as e:
            flash(e.strerror)
            shutil.copy(backup_db_path, old_db_path)
            return redirect(url_for('welcome'))

        # Check the integrity of new database
        if not _check_if_db_is_valid():
            flash("Error: something goes wrong in the imported database.")
            shutil.copy(backup_db_path, old_db_path)
            return redirect(url_for('welcome'))

        flash('Import database successfully.')
        return redirect(url_for('welcome'))
    return render_template('misc/upload.html', form=form)


@app.route('/apply/')
@login_required
def apply_wifi():
    try:
        _apply_aplist_to_system()
    except IOError as e:
        flash(e.strerror)
        return redirect(url_for('welcome'))
    return redirect(url_for('apply_wifi_result'))


@app.route('/apply/result/', methods=['GET', 'POST'])
@login_required
def apply_wifi_result():
    form = DummyForm()
    if request.method == 'POST':
        return redirect(url_for('sync_db', db_name='aplist'))
    return render_template('misc/apply.html', form=form)


def _get_user_object_or_404(model, object_id, code=404):
    ''' get an object by id and owner user or raise an abort '''
    result = model.query.filter_by(id=object_id).first()
    return result or abort(code)
