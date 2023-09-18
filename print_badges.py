import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import lightgrey
from PIL import Image
import tempfile

def cm_to_points(cm):
    # Convert centimeters to points
    return cm * 28.3465

def create_badges(csv_file, png_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Constants for the badges
    badges_per_page = 10
    badges_per_row = 2
    badge_width, badge_height = cm_to_points(6.9), cm_to_points(4.2)  # Adjusted badge size

    # Define the page size with 1cm left and right margins
    page_width = badges_per_row * badge_width + cm_to_points(2)  # 1cm left and right margins
    page_height = (badges_per_page // badges_per_row) * badge_height

    # Create a new PDF file with the specified page size
    c = canvas.Canvas("output.pdf", pagesize=(page_width, page_height))

    for i, (index, row) in enumerate(df.iterrows()):
        # Calculate the position of the badge on the page, considering margins
        x = cm_to_points(1) + (i % badges_per_row) * badge_width
        y = page_height - ((i // badges_per_row % (badges_per_page // badges_per_row) + 1) * badge_height)

        # Save the background image as a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_image:
            bg_image = Image.open(png_file)
            bg_image.save(temp_image, format="PNG")

            # Draw the background image without resizing
            c.drawImage(temp_image.name, x, y, width=badge_width, height=badge_height)

        # Draw the border
        c.setStrokeColor(lightgrey)
        c.rect(x, y, badge_width, badge_height)

        # Draw the text with increased size and adjust if necessary to fit within margins
        name_surname = f"{row['name']} {row['surname']}"
        font_size = 18
        c.setFont("Helvetica-Bold", font_size)
        while c.stringWidth(name_surname, "Helvetica-Bold", font_size) > badge_width - cm_to_points(0.8):  # Leave 4mm space on both sides
            font_size -= 1
            c.setFont("Helvetica-Bold", font_size)
        c.drawCentredString(x + badge_width / 2, y + badge_height / 2 + 10, name_surname)

        affiliation = row['affiliation']
        font_size_affiliation = 14
        c.setFont("Helvetica", font_size_affiliation)
        while c.stringWidth(affiliation, "Helvetica", font_size_affiliation) > badge_width - cm_to_points(0.8):  # Leave 4mm space on both sides
            font_size_affiliation -= 1
            c.setFont("Helvetica", font_size_affiliation)
        c.drawCentredString(x + badge_width / 2, y + badge_height / 2 - 10, affiliation)

        # If we have reached the maximum number of badges per page, start a new page
        if (i + 1) % badges_per_page == 0:
            c.showPage()

    # Save the PDF file
    c.save()

# Call the function with your files
create_badges("input.csv", "background.png")
