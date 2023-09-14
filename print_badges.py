import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightgrey
from PIL import Image

def cm_to_points(cm):
    # Convert centimeters to points
    return cm * 28.3465

def create_badges(csv_file, png_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Constants for the badges
    badges_per_page = 8
    badges_per_row = 2
    badge_width, badge_height = cm_to_points(8.9), cm_to_points(5.4)  # Adjusted badge size

    # Load the background image
    bg_image = Image.open(png_file)

    # Create a new PDF file
    c = canvas.Canvas("output.pdf", pagesize=(badges_per_row * badge_width, (badges_per_page // badges_per_row) * badge_height))

    for i, (index, row) in enumerate(df.iterrows()):
        # Calculate the position of the badge on the page
        x = (i % badges_per_row) * badge_width
        y = c._pagesize[1] - ((i // badges_per_row % (badges_per_page // badges_per_row) + 1) * badge_height)

        # Draw the background image without resizing
        c.drawInlineImage(bg_image, x, y, width=badge_width, height=badge_height)

        # Draw the border
        c.setStrokeColor(lightgrey)
        c.rect(x, y, badge_width, badge_height)

        # Draw the text with increased size
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(x + badge_width / 2, y + badge_height / 2 + 10, f"{row['name']} {row['surname']}")
        c.setFont("Helvetica", 14)
        c.drawCentredString(x + badge_width / 2, y + badge_height / 2 - 10, row['affiliation'])

        # If we have reached the maximum number of badges per page, start a new page
        if (i + 1) % badges_per_page == 0:
            c.showPage()

    # Save the PDF file
    c.save()

# Call the function with your files
create_badges("input.csv", "background.png")
