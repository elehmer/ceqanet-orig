State Template 2013 v3.0 – Responsive Design


Instructions
________________________________________
Step 1

Extract the zip file to your web root directory (usually htdocs or wwwroot).
Make sure your web server is configured to process SSI. It might be configured to process only files with certain file extensions such
as .stm. In that case, you'll need to either name your pages with a .stm extension or configure your server to process .html as well.

________________________________________
Step 2 - Navigation type

Select your navigation type: Mega Drop-Down, Mini Nav, or Single Level Nav.
Open /templates/*.dwt and update line 43.

________________________________________
Step 3 - Color scheme

Select a color scheme.
Open head_css_js.html and update line 24.

________________________________________
Step 4 - Google Analytics

Open header.*.html (the file you chose in step 2).
Insert your Google Analytics ID at line 6.

________________________________________
Step 5 - Header images

Replace the sample /images/template2013/header_organization.png with your own logo and organization name.

Replace /images/template2013/*/header_background.jpg with your own image.

________________________________________
Step 6 - Search engine

Create a search engine results page (SERP) or customize the sample serp.html.

Open header.*.html and enter your search engine ID at lines 28 and 57.

Open serp.html and enter your search engine ID at line 60.

If you change the filename or location of your SERP, you'll need to update scripts.js, line 6, with your new path.

________________________________________
Step 7 - Fix navigation item width for IE 7

Open /css/600.css.  Update line 98. Set the width to 100% divided by the number of your navigation items. Round down.

________________________________________
Step 8 - Icons (optional)

Replace the "favorites" icons with your own:

/images/template2013/apple-touch-icon-*.png
/favicon.ico

________________________________________
Step 9 - Content

The .html files contain examples of the new content styles.
There are 5 containers (container_style_*), 3 list styles (list_style_*), several icons that may be added to headings (add_icon_*),
and a style for creating two columns (half_width_column).

________________________________________


Problems?
---------
Please report any compatibility issues, bugs, or suggestions to info@eservices.ca.gov. These will be addressed in future versions.

