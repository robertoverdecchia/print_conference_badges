import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

def create_badges(csv_file, png_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Constants for the badges
    badges_per_page = 8
    badges_per_row = 2
    badge_width, badge_height = A4[0] / badges_per_row, A4[1] / (badges_per_page / badges_per_row)

    # Load the background image and resize it to the badge size
    bg_image = Image.open(png_file)
    bg_image = bg_image.resize((int(badge_width), int(badge_height)))

    # Create a new PDF file
    c = canvas.Canvas("output.pdf", pagesize=A4)

    for i, (index, row) in enumerate(df.iterrows()):
        # Calculate the position of the badge on the page
        x = (i % badges_per_row) * badge_width
        y = A4[1] - ((i // badges_per_row % (badges_per_page // badges_per_row) + 1) * badge_height)

        # Draw the background image
        c.drawInlineImage(bg_image, x, y, width=badge_width, height=badge_height)

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
