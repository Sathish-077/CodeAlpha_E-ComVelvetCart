from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, UserProfile


class Command(BaseCommand):
    help = 'Seed the database with sample products and an admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            UserProfile.objects.get_or_create(user=admin)
            self.stdout.write('  ✓ Admin user created (admin / admin123)')

        # Create demo user
        if not User.objects.filter(username='demo').exists():
            demo = User.objects.create_user('demo', 'demo@example.com', 'demo123',
                                             first_name='Demo', last_name='User')
            UserProfile.objects.get_or_create(user=demo)
            self.stdout.write('  ✓ Demo user created (demo / demo123)')

        # Categories
        cats_data = [
            ('Electronics', 'electronics', 'Gadgets and devices'),
            ('Clothing', 'clothing', 'Fashion and apparel'),
            ('Books', 'books', 'Knowledge and stories'),
            ('Home & Garden', 'home-garden', 'For your living space'),
            ('Sports', 'sports', 'Gear and equipment'),
        ]
        cats = {}
        for name, slug, desc in cats_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})
            cats[slug] = cat

        # Products
        products = [
            # Electronics
            ('Wireless Headphones Pro', 'wireless-headphones-pro', cats['electronics'],
             'Premium noise-cancelling wireless headphones with 30-hour battery life and crystal-clear audio.', 2999, 25),
            ('Smart Watch Series X', 'smart-watch-series-x', cats['electronics'],
             'Feature-packed smartwatch with health monitoring, GPS, and 7-day battery.', 8499, 15),
            ('Bluetooth Speaker Mini', 'bluetooth-speaker-mini', cats['electronics'],
             'Compact yet powerful speaker with 360° sound and waterproof design.', 1499, 40),
            ('USB-C Hub 7-in-1', 'usb-c-hub-7in1', cats['electronics'],
             'Expand your connectivity with HDMI, USB-A, SD card, and more.', 999, 60),

            # Clothing
            ('Classic Cotton T-Shirt', 'classic-cotton-tshirt', cats['clothing'],
             'Soft 100% organic cotton tee in a relaxed fit. Timeless and versatile.', 399, 100),
            ('Slim Fit Chinos', 'slim-fit-chinos', cats['clothing'],
             'Modern slim-fit chinos in stretch fabric. Perfect for work or weekend.', 899, 50),
            ('Winter Puffer Jacket', 'winter-puffer-jacket', cats['clothing'],
             'Lightweight yet warm puffer jacket with water-resistant outer shell.', 2499, 30),

            # Books
            ('The Art of Code', 'the-art-of-code', cats['books'],
             'A deep dive into software craftsmanship, design patterns, and developer philosophy.', 499, 80),
            ('Mindful Leadership', 'mindful-leadership', cats['books'],
             'Transform your leadership style with mindfulness-based management techniques.', 349, 60),
            ('Python Mastery', 'python-mastery', cats['books'],
             'From beginner to expert: comprehensive Python programming guide with real projects.', 599, 45),

            # Home & Garden
            ('Ceramic Plant Pot Set', 'ceramic-plant-pot-set', cats['home-garden'],
             'Set of 3 minimalist ceramic pots with drainage holes. Perfect for indoor plants.', 799, 35),
            ('Bamboo Cutting Board', 'bamboo-cutting-board', cats['home-garden'],
             'Eco-friendly bamboo cutting board with juice groove and non-slip feet.', 449, 55),

            # Sports
            ('Yoga Mat Premium', 'yoga-mat-premium', cats['sports'],
             'Extra-thick 6mm non-slip yoga mat with alignment lines and carrying strap.', 699, 70),
            ('Resistance Band Set', 'resistance-band-set', cats['sports'],
             '5-piece latex resistance band set with carrying bag. Suitable for all fitness levels.', 499, 90),
        ]

        for name, slug, cat, desc, price, stock in products:
            obj, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name, 'category': cat,
                    'description': desc, 'price': price,
                    'stock': stock, 'available': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Product: {name}')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('   → Run: python manage.py runserver')
        self.stdout.write('   → Admin: http://127.0.0.1:8000/admin  (admin / admin123)')
        self.stdout.write('   → Shop:  http://127.0.0.1:8000/')
