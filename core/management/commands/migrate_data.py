import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, Category, Project, DigitalAsset, Fabric, Payment, OrderTracking, Design

class Command(BaseCommand):
    help = 'Migrate data from legacy CSV files to the new database schema'

    def handle(self, *args, **kwargs):
        # Specify the paths to your legacy CSV files
        user_profile_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/user_profiles.csv'
        category_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/categories.csv'
        project_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/projects.csv'
        digital_asset_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/digital_assets.csv'
        fabric_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/fabrics.csv'
        payment_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/payments.csv'
        order_tracking_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/order_tracking.csv'
        design_file = 'c:/Users/dell/CascadeProjects/ubiglu_afro_mutation/data/designs.csv'

        # Migrate User Profiles
        with open(user_profile_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_instance, created = User.objects.get_or_create(username=row['user'])
                if created:
                    user_instance.set_password('defaultpassword')  # Set a default password
                    user_instance.save()
                    self.stdout.write(self.style.SUCCESS(f'Created new user: {user_instance.username}'))
                
                user_profile, profile_created = UserProfile.objects.get_or_create(user=user_instance)
                if profile_created:
                    user_profile.profile_image = row['profile_image']
                    user_profile.bio = row['bio']
                    user_profile.website = row['website']
                    user_profile.location = row['location']
                    user_profile.skills = row['skills']
                    user_profile.interests = row['interests']
                    user_profile.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated user profile for: {user_instance.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User profile for {user_instance.username} already exists. Skipping creation.'))

        # Migrate Categories
        with open(category_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category, created = Category.objects.get_or_create(
                    slug=row['slug'],  # Use slug to check for existing category
                    defaults={
                        'name': row['name'],
                        'description': row['description'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new category: {category.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Category {category.name} already exists. Skipping creation.'))

        # Migrate Projects
        with open(project_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    owner_instance = User.objects.get(username=row['owner'])
                    category_instance = Category.objects.get(slug=row['category'])
                    project = Project(
                        title=row['title'],
                        description=row['description'],
                        owner=owner_instance,
                        category=category_instance,
                        price=row['price'],
                        total_sales=row['total_sales'],
                        total_earnings=row['total_earnings'],
                        status=row['status'],
                        image=row['image'],
                    )
                    project.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated project: {project.title}'))
                except (User.DoesNotExist, Category.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating project {row["title"]}: {str(e)}'))

        # Migrate Digital Assets
        with open(digital_asset_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_instance = User.objects.get(username=row['user'])
                    category_instance = Category.objects.get(slug=row['category'])
                    digital_asset = DigitalAsset(
                        title=row['title'],
                        description=row['description'],
                        user=user_instance,
                        category=category_instance,
                        file=row['file'],
                        file_type=row['file_type'],
                        tags=row['tags'],
                    )
                    digital_asset.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated digital asset: {digital_asset.title}'))
                except (User.DoesNotExist, Category.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating digital asset {row["title"]}: {str(e)}'))

        # Migrate Fabrics
        with open(fabric_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    project_instance = Project.objects.get(title=row['project'])
                    category_instance = Category.objects.get(slug=row['category'])
                    fabric = Fabric(
                        name=row['name'],
                        description=row['description'],
                        image=row['image'],
                        project=project_instance,
                        category=category_instance,
                        price=row['price'],
                        weight=row['weight'],
                        color=row['color'],
                        texture=row['texture'],
                    )
                    fabric.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated fabric: {fabric.name}'))
                except (Project.DoesNotExist, Category.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating fabric {row["name"]}: {str(e)}'))

        # Migrate Payments
        with open(payment_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_instance = User.objects.get(username=row['user'])
                    payment = Payment(
                        user=user_instance,
                        amount=row['amount'],
                        transaction_id=row['transaction_id'],
                        payment_date=row['payment_date'],
                        payment_method=row['payment_method'],
                        status=row['status'],
                    )
                    payment.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated payment for: {user_instance.username}'))
                except User.DoesNotExist as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating payment for user {row["user"]}: {str(e)}'))

        # Migrate Order Tracking
        with open(order_tracking_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_instance = User.objects.get(username=row['user'])
                    order_tracking = OrderTracking(
                        user=user_instance,
                        status=row['status'],
                        shipping_details=row['shipping_details'],
                        progress=row['progress'],
                    )
                    order_tracking.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated order tracking for: {user_instance.username}'))
                except User.DoesNotExist as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating order tracking for user {row["user"]}: {str(e)}'))

        # Migrate Designs
        with open(design_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_instance = User.objects.get(username=row['user'])
                    design = Design(
                        user=user_instance,
                        name=row['name'],
                        description=row['description'],
                        measurements=row['measurements'],
                        style_options=row['style_options'],
                        thumbnail=row['thumbnail'],
                    )
                    design.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully migrated design: {design.name}'))
                except User.DoesNotExist as e:
                    self.stdout.write(self.style.ERROR(f'Error migrating design for user {row["user"]}: {str(e)}'))