from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import io, os, csv
import qrcode

app = Flask(__name__)
app.secret_key = "secret"

DEFAULT_TABLE_COUNT = 10
GUESTS_PER_TABLE = 6

QR_FOLDER = "static/qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)


# --------------------------------------------
# ASSIGN TABLES – 6 guests per table
# --------------------------------------------
def assign_tables(guest_names):
    tables = {}
    table_number = 1
    seat = 0

    for name in guest_names:
        if table_number not in tables:
            tables[table_number] = []

        tables[table_number].append(name)
        seat += 1

        if seat == GUESTS_PER_TABLE:
            table_number += 1
            seat = 0

    # Save for view_table route
    with open("last_assignment.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for tnum, names in tables.items():
            writer.writerow([tnum] + names)

    return tables


# --------------------------------------------
# QR CODE GENERATION
# --------------------------------------------
def generate_qr_for_table(table_number):
    url = f"https://your-render-app-url/table/{table_number}"  # Replace with actual Render URL
    img = qrcode.make(url)
    img_path = os.path.join(QR_FOLDER, f"table_{table_number}.png")
    img.save(img_path)
    return img_path


# --------------------------------------------
# HOME PAGE
# --------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        names_text = request.form.get('names')
        file = request.files.get('file')
        names = []

        # File upload
        if file and file.filename:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            for line in stream:
                line = line.strip()
                if line:
                    names.append(line)

        # Pasted text
        elif names_text:
            for line in names_text.splitlines():
                line = line.strip()
                if line:
                    names.append(line)

        else:
            flash('Please paste names or upload a CSV.', 'warning')
            return redirect(url_for('index'))

        # Must be exactly 60 names
        if len(names) != DEFAULT_TABLE_COUNT * GUESTS_PER_TABLE:
            flash(
                f"You provided {len(names)} names — must be exactly {DEFAULT_TABLE_COUNT * GUESTS_PER_TABLE} (10 tables × 6).",
                "danger"
            )
            return redirect(url_for('index'))

        # Assign tables
        tables = assign_tables(names)

        # Generate QR codes
        for t in tables.keys():
            generate_qr_for_table(t)

        return render_template('tables.html', tables=tables)

    return render_template('index.html')


# --------------------------------------------
# VIEW INDIVIDUAL TABLE
# --------------------------------------------
@app.route('/table/<int:table_number>')
def view_table(table_number):
    assignment_file = 'last_assignment.csv'

    # If no assignment yet
    if not os.path.exists(assignment_file):
        return render_template(
            'table.html',
            table_number=table_number,
            guests=None,
            qr_path=url_for('static', filename=f'qr_codes/table_{table_number}.png')
        )

    tables = {}
    with open(assignment_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            tnum = int(row[0])
            names = [n for n in row[1:] if n]
            tables[tnum] = names

    guests = tables.get(table_number)
    qr_path = url_for('static', filename=f'qr_codes/table_{table_number}.png')

    return render_template('table.html',
                           table_number=table_number,
                           guests=guests,
                           qr_path=qr_path)


# --------------------------------------------
# DOWNLOAD SAMPLE CSV
# --------------------------------------------
#@app.route('/download-sample')
#def download_sample():
#   return send_from_directory(directory='.', filename='guests_sample.csv', as_attachment=True)
@app.route('/download-sample')
def download_sample():
    return send_from_directory(
        '.',
        'guests_sample.csv',
        as_attachment=True
    )




# --------------------------------------------
# RUN APP
# --------------------------------------------
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000)),
        debug=True
    )
