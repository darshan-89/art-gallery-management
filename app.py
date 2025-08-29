from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",          # change if needed
        password="",          # put your MySQL password if you set one
        database="art_gallery"
    )

# -------------------------------
# Home Route
# -------------------------------
@app.route('/')
def home():
    return redirect(url_for("artists"))

# -------------------------------
# Artist Routes
# -------------------------------
@app.route("/artists")
def artists():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM artists ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    return render_template("home.html", artists=data)

@app.route("/add_artist", methods=["GET", "POST"])
def add_artist():
    if request.method == "POST":
        name = request.form["name"]
        contact = request.form.get("contact") or None
        bio = request.form.get("bio") or None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO artists (name, contact, bio) VALUES (%s, %s, %s)",
            (name, contact, bio)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("artists"))

    return render_template("add_artist.html")

@app.route("/edit_artist/<int:id>", methods=["GET", "POST"])
def edit_artist(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM artists WHERE id = %s", (id,))
    artist = cursor.fetchone()

    if request.method == "POST":
        name = request.form["name"]
        contact = request.form.get("contact") or None
        bio = request.form.get("bio") or None

        cursor.execute(
            "UPDATE artists SET name=%s, contact=%s, bio=%s WHERE id=%s",
            (name, contact, bio, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("artists"))

    conn.close()
    return render_template("edit_artist.html", artist=artist)

@app.route("/delete_artist/<int:id>")
def delete_artist(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM artists WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("artists"))

# -------------------------------
# Artwork Routes
# -------------------------------
@app.route("/artworks")
def artworks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.title, a.description, a.price, a.image_url,
               r.name AS artist_name
        FROM artworks a
        JOIN artists r ON a.artist_id = r.id
        ORDER BY a.id DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return render_template("artworks.html", artworks=data)

@app.route("/buy_artwork/<int:id>")
def buy_artwork(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM artworks WHERE id = %s", (id,))
    artwork = cursor.fetchone()
    conn.close()

    if not artwork:
        return "Artwork not found", 404

    return render_template("purchase_success.html", artwork=artwork)

@app.route("/add_artwork", methods=["GET", "POST"])
def add_artwork():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # fetch artists for dropdown
    cursor.execute("SELECT id, name FROM artists ORDER BY name")
    artists = cursor.fetchall()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description") or None
        image_url = request.form.get("image_url") or None

        # safely handle price
        price_raw = request.form.get("price") or None
        price = float(price_raw) if price_raw not in (None, "",) else None

        artist_id = int(request.form["artist_id"])

        cur2 = conn.cursor()
        cur2.execute(
            "INSERT INTO artworks (title, description, price, image_url, artist_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (title, description, price, image_url, artist_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("artworks"))

    conn.close()
    return render_template("add_artwork.html", artists=artists)
@app.route("/edit_artwork/<int:id>", methods=["GET", "POST"])
def edit_artwork(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # fetch artwork
    cursor.execute("SELECT * FROM artworks WHERE id = %s", (id,))
    artwork = cursor.fetchone()

    # fetch artists for dropdown
    cursor.execute("SELECT id, name FROM artists ORDER BY name")
    artists = cursor.fetchall()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description") or None
        image_url = request.form.get("image_url") or None
        price_raw = request.form.get("price") or None
        price = float(price_raw) if price_raw not in (None, "",) else None
        artist_id = int(request.form["artist_id"])

        cursor.execute(
            "UPDATE artworks SET title=%s, description=%s, price=%s, image_url=%s, artist_id=%s WHERE id=%s",
            (title, description, price, image_url, artist_id, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("artworks"))

    conn.close()
    return render_template("edit_artwork.html", artwork=artwork, artists=artists)


@app.route("/delete_artwork/<int:id>")
def delete_artwork(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM artworks WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("artworks"))
# -------------------------------
# Run the App
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8080)