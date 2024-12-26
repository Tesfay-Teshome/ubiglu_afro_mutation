import csv
import os

# Define the directory where the CSV files will be created
data_dir = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/'
os.makedirs(data_dir, exist_ok=True)

# Sample data for each CSV

# User Profiles
user_profiles = [
    ['user', 'profile_image', 'bio', 'website', 'location', 'skills', 'interests'],
    ['user1', '/path/to/image1.jpg', 'Bio for user1', 'www.user1.com', 'Location1', 'Skill1', 'Interest1'],
    ['user2', '/path/to/image2.jpg', 'Bio for user2', 'www.user2.com', 'Location2', 'Skill2', 'Interest2'],
]

# Categories
categories = [
    ['name', 'description', 'slug'],
    ['Category1', 'Description for category1', 'category1'],
    ['Category2', 'Description for category2', 'category2'],
]

# Projects
projects = [
    ['title', 'description', 'owner', 'category', 'price', 'total_sales', 'total_earnings', 'status', 'image'],
    ['Project1', 'Description for project1', 'user1', 'category1', '100.00', '10', '1000.00', 'draft', '/path/to/image.jpg'],
    ['Project2', 'Description for project2', 'user2', 'category2', '200.00', '5', '500.00', 'in_progress', '/path/to/image2.jpg'],
]

# Digital Assets
digital_assets = [
    ['title', 'description', 'user', 'category', 'file', 'file_type', 'tags'],
    ['Asset1', 'Description for asset1', 'user1', 'category1', '/path/to/file1.jpg', 'image', 'tag1,tag2'],
    ['Asset2', 'Description for asset2', 'user2', 'category2', '/path/to/file2.mp4', 'video', 'tag3,tag4'],
]

# Fabrics
fabrics = [
    ['name', 'description', 'image', 'project', 'category', 'price', 'weight', 'color', 'texture'],
    ['Fabric1', 'Description for fabric1', '/path/to/fabric1.jpg', 'Project1', 'category1', '50.00', '200.00', 'Red', 'Smooth'],
    ['Fabric2', 'Description for fabric2', '/path/to/fabric2.jpg', 'Project2', 'category2', '75.00', '300.00', 'Blue', 'Rough'],
]

# Payments
payments = [
    ['user', 'amount', 'transaction_id', 'payment_date', 'payment_method', 'status'],
    ['user1', '100.00', 'TX12345', '2024-01-01', 'Credit Card', 'Completed'],
    ['user2', '150.00', 'TX12346', '2024-01-02', 'PayPal', 'Pending'],
]

# Order Tracking
order_tracking = [
    ['user', 'status', 'shipping_details', 'progress'],
    ['user1', 'Shipped', '{"address": "123 Main St"}', '50.0'],
    ['user2', 'In Transit', '{"address": "456 Elm St"}', '75.0'],
]

# Designs
designs = [
    ['user', 'name', 'description', 'measurements', 'style_options', 'thumbnail'],
    ['user1', 'Design1', 'Description for design1', '{"chest": "38"}', '{"style": "casual"}', '/path/to/thumbnail1.jpg'],
    ['user2', 'Design2', 'Description for design2', '{"waist": "30"}', '{"style": "formal"}', '/path/to/thumbnail2.jpg'],
]

# Create CSV files
def create_csv(filename, data):
    with open(os.path.join(data_dir, filename), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Create all CSV files
create_csv('user_profiles.csv', user_profiles)
create_csv('categories.csv', categories)
create_csv('projects.csv', projects)
create_csv('digital_assets.csv', digital_assets)
create_csv('fabrics.csv', fabrics)
create_csv('payments.csv', payments)
create_csv('order_tracking.csv', order_tracking)
create_csv('designs.csv', designs)