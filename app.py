from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.travel_agency_db
packages_collection = db.packages
bookings_collection = db.bookings


@app.route('/')
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    packages = list(packages_collection.find({"is_deleted": {"$ne": True}}))  # Exclude deleted packages
    return render_template("index.html", packages=packages)


@app.route('/book/<package_id>', methods=['GET', 'POST'])
def book(package_id):
    package = packages_collection.find_one({"_id": ObjectId(package_id)})

    if not package:
        flash("Package not found!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        phone_number = request.form.get('phone_number')
        travelers = int(request.form.get('travelers'))
        booking_start_date = request.form.get('start_date')
        booking_end_date = request.form.get('end_date')

        # Validate that the selected dates are within the available date range
        if not (package['start_date'] <= booking_start_date <= package['end_date'] and
                package['start_date'] <= booking_end_date <= package['end_date']):
            flash("Selected dates are outside the available range!", "danger")
            return redirect(url_for('book', package_id=package_id))

        # Validate traveler count
        if travelers > package['availability']:
            flash("Not enough availability for the selected package!", "danger")
            return redirect(url_for('book', package_id=package_id))

        total_price = travelers * package['price']

        booking = {
            "package_id": package_id,
            "package_name": package['name'],
            "customer_name": customer_name,
            "customer_email": customer_email,
            "phone_number": phone_number,
            "travelers": travelers,
            "start_date": booking_start_date,
            "end_date": booking_end_date,
            "total_price": total_price
        }
        bookings_collection.insert_one(booking)

        # Update availability
        packages_collection.update_one(
            {"_id": ObjectId(package_id)},
            {"$inc": {"availability": -travelers}}
        )

        flash("Booking successful!", "success")
        return redirect(url_for('invoice', booking_id=booking['_id']))

    return render_template("book.html", package=package)


@app.route("/invoice/<booking_id>")
def invoice(booking_id):
    try:
        booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    except:
        flash("Invalid booking ID!", "error")
        return redirect(url_for("index"))

    if not booking:
        flash("Booking not found!", "error")
        return redirect(url_for("index"))

    package = packages_collection.find_one({"_id": booking["package_id"]})
    return render_template("invoice.html", booking=booking, package=package)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    packages = list(packages_collection.find())  # Fetch all packages from the database
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        image_url = request.form["image_url"]
        availability = int(request.form["availability"])
        package = {
            "name": name,
            "description": description,
            "price": price,
            "start_date": start_date,  # Store start_date
            "end_date": end_date,      # Store end_date
            "image_url": image_url,
            "availability": availability
        }
        packages_collection.insert_one(package)
        flash("Package added successfully!", "success")
        return redirect(url_for("admin"))

    return render_template("admin.html", packages=packages)


@app.route("/admin/update_package/<package_id>", methods=["GET", "POST"])
def update_package(package_id):
    package = packages_collection.find_one({"_id": ObjectId(package_id)})

    if not package:
        flash("Package not found!", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        # Get the updated data from the form
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        image_url = request.form["image_url"]
        availability = int(request.form["availability"])

        # Update the package in the database
        packages_collection.update_one(
            {"_id": ObjectId(package_id)},
            {"$set": {
                "name": name,
                "description": description,
                "price": price,
                "start_date": start_date,
                "end_date": end_date,
                "image_url": image_url,
                "availability": availability
            }}
        )

        flash("Package updated successfully!", "success")
        return redirect(url_for("admin"))

    # If it's a GET request, render the form with existing package data
    return render_template("update_package.html", package=package)




@app.route("/admin/delete/<package_id>", methods=["POST"])
def delete_package(package_id):
    print(f"Delete request received for package: {package_id}")
    
    # Delete the package completely from the database
    packages_collection.delete_one({"_id": ObjectId(package_id)})
    
    flash("Package deleted successfully!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/add_package", methods=["POST"])
def add_package():
    name = request.form["name"]
    description = request.form["description"]
    price = float(request.form["price"])
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    image_url = request.form["image_url"]
    availability = int(request.form["availability"])

    package = {
        "name": name,
        "description": description,
        "price": price,
        "start_date": start_date,
        "end_date": end_date,
        "image_url": image_url,
        "availability": availability
    }

    packages_collection.insert_one(package)

    # Return the updated list of packages as JSON
    packages = list(packages_collection.find({"is_deleted": {"$ne": True}}))
    return jsonify(packages=[{
        "name": package["name"],
        "description": package["description"],
        "price": package["price"],
        "start_date": package["start_date"],
        "end_date": package["end_date"],
        "availability": package["availability"],
        "_id": str(package["_id"])
    } for package in packages])

@app.route("/admin/bookings")
def view_bookings():
    bookings = list(bookings_collection.find())
    return render_template("bookings.html", bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True)
