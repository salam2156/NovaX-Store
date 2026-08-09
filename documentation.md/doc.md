
Nova-Store/
└── Nova-Store-Documentation.md


---

Nova-Store — Full-Stack E-Commerce Project Documentation

1. Project Overview

Nova-Store is a full-stack e-commerce web application developed as an internship project.

The project provides a modern online shopping experience with product browsing, search, shopping cart functionality, customer accounts, checkout, orders, and contact functionality.

The application must be developed and improved using the existing project files.

The AI Agent must not rebuild the project from scratch.


---

2. Technology Stack

The existing technology stack must be preserved.

Frontend

HTML5

CSS3

JavaScript


Backend

Python

Flask


Database

SQLite


Database ORM

Flask-SQLAlchemy / SQLAlchemy


Deployment

The final version must be deployed to a publicly accessible URL.

The final application must not depend on:

localhost
127.0.0.1

The final URL should allow anyone with the link to open and view the website.


---

3. Main Development Rule

The AI Agent must work on the existing Nova-Store project.

Before making any changes, it must:

1. Inspect the complete project structure.


2. Read this documentation.


3. Inspect the existing HTML files.


4. Inspect CSS.


5. Inspect JavaScript.


6. Inspect Flask routes.


7. Inspect SQLAlchemy models.


8. Inspect the SQLite database structure.


9. Inspect existing tests.


10. Compare the actual implementation with this documentation.



The AI Agent must not assume that the documentation is more accurate than the actual code.

If the existing code differs from the documentation, inspect the code first and report the difference.


---

4. Do Not Rebuild the Project

The AI Agent must NOT:

Create a completely new project.

Replace Flask with another backend framework.

Replace SQLite without permission.

Replace HTML/CSS/JavaScript.

Delete existing features simply because they contain bugs.

Create unnecessary duplicate files.

Create a second Flask application.

Create a second database.

Create another CSS file when the shared stylesheet can be used.


The goal is to repair, improve and complete the existing Nova-Store project.


---

5. Project Design Style

Nova-Store must maintain a consistent modern e-commerce design.

The visual style should be:

Modern

Clean

Professional

Minimal

Responsive

User-friendly

Consistent across all pages


The design must feel like one complete website.

The AI Agent must not create a completely different visual style for individual pages.


---

6. Color System

The project should maintain a modern technology/e-commerce color palette.

Primary Dark Color

#0f172a

Used for:

Navbar

Footer

Dark sections

Main UI elements where appropriate


Primary Accent

#6366f1

Used for:

Primary buttons

Links

Interactive elements

Important UI highlights


Secondary Accent

#38bdf8

Used for:

Hover states

Small highlights

Technology-related accents


Success Color

#10b981

Used for:

Successful actions

Order confirmation

Positive status indicators


Main Background

#f8fafc

Used for:

Main page backgrounds

Product sections

Content areas


Text

Primary text:

#0f172a

Secondary text:

#64748b

The AI Agent should preserve the existing color system where possible and only adjust it when required for consistency.


---

7. Typography

The website must use a clean, modern and readable typography system.

Typography must remain consistent across:

Headings

Paragraphs

Buttons

Navigation

Product information

Forms

Footer


Avoid using many unrelated fonts.

The website should prioritize readability and professional presentation.


---

8. Shared CSS
[8/9/2026 12:26 AM] salam: The project must use:

static/style.css

as the main shared stylesheet.

Do not create separate CSS files for every page unless there is a strong technical reason.

All pages should inherit the same:

Colors

Typography

Buttons

Cards

Spacing

Navigation

Forms

Responsive behavior



---

9. Shared JavaScript

The project should use:

static/index.js

as the shared JavaScript file.

JavaScript functionality should be organized clearly.

Avoid duplicate functions.

Avoid registering the same event listener multiple times.


---

10. Navbar

All main pages should use a consistent navigation system.

The navigation should provide access to:

Home

Shop

About

Contact

Account

Cart


The navbar must remain responsive on mobile devices.

The active page should be visually distinguishable where appropriate.


---

11. Home Page

The Home page should act as the main landing page.

It should contain:

Navbar

Hero section

Store introduction

Featured products or shopping CTA

Benefits/features section where appropriate

Call-to-action button

Footer


The design should immediately communicate that Nova-Store is an e-commerce platform.


---

12. Shop Page

The Shop page is one of the most important parts of Nova-Store.

It must contain 15 products.

Required Product Count

15 products

All 15 products must use the same product-card design.

Do not create different card designs for individual products.


---

13. Product Cards

Every product card must have a consistent structure.

Recommended structure:

Product Image
Product Name
Short Description
Price
Action Button

Optional:

Category
Rating
Badge

All cards must have:

Consistent dimensions

Consistent image area

Consistent spacing

Consistent typography

Consistent button styling

Hover effect

Responsive behavior


Images must not break the layout.


---

14. Product Images

Each of the 15 products must have an appropriate product image.

The images should:

Have consistent visual proportions.

Fit inside the product image container.

Not stretch incorrectly.

Not break the card layout.

Work correctly on desktop and mobile.


The AI Agent must not use random unrelated images.

Product images should correspond logically to the product being displayed.


---

15. Search Bar

The Shop page must contain a working search bar.

The search bar should allow the user to type a product name and immediately find matching products.

Example:

User types:
"laptop"

↓

Products containing "laptop"
are displayed.

If the user types:

"iphone"

the matching iPhone product should be displayed.

The search should preferably be case-insensitive.

Example:

Laptop
laptop
LAPTOP

should produce the same results.


---

16. Instant Product Search

The search experience should be dynamic.

The user should not need to reload the page to search.

Expected behavior:

User types
     ↓
JavaScript detects input
     ↓
Products are filtered
     ↓
Matching products remain visible
     ↓
Non-matching products are hidden

The existing filterProducts() issue must be fixed.

There must be no:

ReferenceError: filterProducts is not defined


---

17. Search Empty State

If no product matches the search query, the website should display a clear message such as:

No products found.

The message must use the existing website design style.


---

18. Database-Driven Products

The final implementation should not depend on hardcoded product information inside shop.html.

The preferred architecture is:

SQLite
   ↓
Product Model
   ↓
Flask
   ↓
Jinja Template
   ↓
Shop Page

The 15 products should eventually be stored in the database.

The Shop route should retrieve the products using SQLAlchemy.


---

19. Shopping Cart

The cart should allow users to:

Add products.

Remove products.

Increase quantity.

Decrease quantity.

View cart count.

View total price.


The cart total must update correctly.

If quantity reaches zero, the product may be removed.

The cart interface must follow the same Nova-Store visual style.


---

20. Checkout
[8/9/2026 12:26 AM] salam: The Checkout page should collect the required customer information.

Potential fields include:

First name

Last name

Email

Address

City

Phone

Payment method

Order total


Every form field that must be submitted to Flask must have an appropriate:

name=""

attribute.

Frontend and backend field names must match.


---

21. Checkout Backend Flow

The final checkout flow must be:

Checkout Form
      ↓
POST Request
      ↓
Flask Route
      ↓
Validation
      ↓
SQLAlchemy
      ↓
SQLite
      ↓
Order Created
      ↓
Success Response

JavaScript must not simply display an alert and pretend that an order was created.


---

22. Contact Page

The Contact page should contain a professional contact form.

The form should connect to Flask.

The frontend must not prevent the submission unless JavaScript actually sends the request to the backend.


---

23. Account System

The Account page should eventually support:

Registration

Login

Logout

Customer session

Account information


Authentication must be implemented using Flask sessions.


---

24. Password Security

Passwords must never be stored in plaintext.

The final implementation must use secure password hashing.

The AI Agent must not introduce plaintext password storage.

Duplicate email registration must be handled safely.

It must not cause an HTTP 500 error.


---

25. Orders

Customers should eventually be able to:

Create orders.

View their orders.

View individual order details.


The following templates should be properly connected:

my_orders.html
order_detail.html


---

26. Static Files

All templates must correctly load static files using Flask.

Correct:

{{ url_for('static', filename='style.css') }}

and:

{{ url_for('static', filename='index.js') }}

Do not use incorrect relative paths such as:

style.css
index.js

when they cause Flask routes to return 404 errors.


---

27. Responsive Design

Nova-Store must work on:

Desktop

Laptop

Tablet

Mobile


The Shop grid should adapt according to screen size.

Example:

Desktop → multiple columns
Tablet  → fewer columns
Mobile  → one or two columns

The navbar and forms must also adapt to small screens.


---

28. Backend Structure

The Flask application should have one main application entry point.

The project must avoid unnecessary duplicate application files.

The application should eventually support:

Home
Shop
About
Contact
Checkout
Account
Orders
Order Details

through Flask routes.


---

29. Database Structure

The database should contain the required entities.

Customer

id
name
email
password_hash

Product

id
name
description
price
image
category

Order

id
customer_id
name
email
address
city
phone
payment_method
total
created_at
status

The exact fields should be confirmed against the existing project before modifying the database.

The AI Agent must not blindly replace the current schema.


---

30. Current Known Problems

The project scan identified the following problems:

B1

Missing account.html.

B2

Test suite contains an incorrect application path.

B3

Checkout does not properly reach the backend.

B4

Contact form does not properly reach the backend.

B5

CSS and JavaScript paths cause 404 errors on several pages.

B6

filterProducts() is missing.

B7

Authentication is incomplete.

B8

Passwords require secure hashing.

B9

Shop products are hardcoded instead of being database-driven.

B10

Order model does not match all Checkout fields.

B11

Order-related templates reference incomplete routes/functions.

B12

Duplicate application/database files create maintenance problems.


---

31. Planned Development Updates

The AI Agent should implement the following updates in order.

Phase 1 — Frontend Stability

1. Fix CSS paths.


2. Fix JavaScript paths.


3. Verify all pages load the shared CSS.


4. Verify JavaScript loads correctly.


5. Fix JavaScript console errors.


6. Implement filterProducts().




---

32. Phase 2 — Shop

1. Maintain exactly 15 products.


2. Make all product cards visually identical in structure.


3. Add appropriate product images.
[8/9/2026 12:26 AM] salam: 4. Implement instant search.


5. Implement filtering.


6. Add empty search state.


7. Connect products to SQLite.


8. Render products dynamically through Jinja.




---

33. Phase 3 — Cart

1. Add products to cart.


2. Update cart count.


3. Update quantities.


4. Remove products.


5. Calculate totals.


6. Verify cart behavior across the website.




---

34. Phase 4 — Checkout

1. Fix all form fields.


2. Add missing name attributes.


3. Connect frontend to Flask.


4. Validate submitted data.


5. Create Order records.


6. Store required order information.


7. Display successful checkout confirmation.


8. Prevent invalid orders.




---

35. Phase 5 — Contact

1. Connect Contact form to Flask.


2. Validate fields.


3. Handle invalid submissions.


4. Display appropriate success/error messages.




---

36. Phase 6 — Authentication

Implement:

Registration.

Login.

Logout.

Sessions.

Password hashing.

Duplicate-email handling.

Protected order pages.



---

37. Phase 7 — Orders

Implement:

Order creation.

Customer order history.

Individual order details.

Order status.

Correct database relationships.



---

38. Phase 8 — Project Cleanup

Remove or resolve:

Duplicate Flask application files.

Duplicate SQLite databases.

Unused code.

Duplicate JavaScript functions.

Broken routes.

Broken templates.

Unnecessary files.


Do not delete files without first verifying whether they are required.


---

39. Phase 9 — Testing

Tests should verify:

Flask startup.

Home route.

Shop route.

About route.

Contact route.

Checkout.

Registration.

Login.

Logout.

Product retrieval.

Order creation.

Database operations.


The test suite must actually run successfully.


---

40. Phase 10 — Final UI Review

Before deployment, verify:

All pages use the same design.

Navbar is consistent.

Footer is consistent.

Buttons are consistent.

Product cards are consistent.

15 products are displayed.

Product images work.

Search works instantly.

Cart works.

Checkout works.

Forms work.

Mobile layout works.

No broken images.

No CSS 404 errors.

No JavaScript errors.



---

41. Final Deployment

The final stage is to make Nova-Store publicly accessible.

The website must be deployed to a hosting platform that provides a public URL.

The final result should be:

User
  ↓
Public URL
  ↓
Nova-Store
  ↓
Flask Application
  ↓
Database

The final website must be accessible to anyone who has the link.

The project must not rely on:

localhost
127.0.0.1

for the final demonstration.

The deployment configuration must be compatible with Flask and the selected hosting platform.


---

42. Final Verification Before Deployment

Before publishing the website, perform a complete test.

Frontend

[ ] All pages load.

[ ] CSS works.

[ ] JavaScript works.

[ ] Images work.

[ ] Responsive design works.


Shop

[ ] Exactly 15 products.

[ ] All product cards have the same design.

[ ] Product images are correct.

[ ] Search works instantly.

[ ] Search is case-insensitive.

[ ] Empty search state works.

[ ] Products come from the database.


Cart

[ ] Add to cart works.

[ ] Quantity works.

[ ] Remove works.

[ ] Total works.


Backend

[ ] Flask routes work.

[ ] Forms reach Flask.

[ ] Validation works.

[ ] Database operations work.


Authentication

[ ] Registration works.

[ ] Passwords are hashed.

[ ] Login works.

[ ] Logout works.

[ ] Sessions work.


Orders

[ ] Checkout creates an order.

[ ] Order is stored.

[ ] Order history works.

[ ] Order details work.


Deployment

[ ] Public URL works.

[ ] Website opens without localhost.

[ ] Website is accessible from another device/network.

[ ] Static files work after deployment.

[ ] Database connection works.

[ ] No critical runtime errors.



---

43. AI Agent Final Rules

The AI Agent must always:

1. Read this documentation.


2. Inspect the existing project.


3. Work on existing files whenever possible.


4. Preserve the current technology stack.


5. Preserve the Nova-Store visual identity.


6. Keep the shared CSS and JavaScript architecture.
[8/9/2026 12:26 AM] salam: 7. Keep exactly 15 Shop products.


8. Keep all product cards visually consistent.


9. Implement functional instant product search.


10. Never invent missing functionality without checking the code.


11. Never delete working functionality without permission.


12. Never store plaintext passwords.


13. Test changes before claiming they work.


14. Report remaining issues.


15. Never claim deployment is complete until the public URL has actually been verified.




---

44. Final Project Goal

The final Nova-Store application should provide:

Modern UI
      +
15 Consistent Products
      +
Instant Search
      +
Shopping Cart
      +
Checkout
      +
Customer Authentication
      +
Order Management
      +
SQLite Database
      +
Flask Backend
      +
Responsive Design
      +
Secure Password Handling
      +
Testing
      +
Public Deployment
