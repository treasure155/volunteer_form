from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from email_validator import validate_email, EmailNotValidError
import smtplib
import os
from config import MONGO_URI, GMAIL_USER, GMAIL_PASS

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")  # Use an environment variable for security

def send_email(to_email, name):
    """Send notification email to the volunteer."""
    subject = "Thank You for Volunteering!"
    message = f"""Dear {name},

Thank you for your interest in volunteering with TechAlpha. Your support means a lot to us!

If you have any questions, feel free to reach out:
📍 Address: TechAlpha Hub, 139 Etinan-Uyo Road, Etinan, Akwa Ibom State
📞 Phone: +2347066155981, +2348130790321
📧 Email: admin@techalphahub.com

Best Regards,  
TechAlpha Team
"""

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        email_message = f"Subject: {subject}\nContent-Type: text/plain; charset=utf-8\n\n{message}".encode("utf-8")
        server.sendmail(GMAIL_USER, to_email, email_message)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        occupation = request.form.get("occupation", "").strip()
        interest = request.form.get("interest", "").strip()
        comment = request.form.get("comment", "").strip()

        try:
            validate_email(email)  # Validate email format

            # Insert into MongoDB
            mongo.db.volunteers.insert_one({
                "name": name,
                "email": email,
                "address": address,
                "phone": phone,
                "occupation": occupation,
                "interest": interest,
                "comment": comment
            })

            send_email(email, name)  # Send confirmation email
            flash("Thank you for signing up as a volunteer!", "success")
            return redirect(url_for("success"))
        
        except EmailNotValidError:
            flash("Invalid email address. Please enter a valid email.", "danger")
        
        except Exception as e:
            print(f"Database error: {e}")
            flash("Something went wrong. Please try again.", "danger")

    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
