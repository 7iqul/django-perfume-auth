from django.core.management.base import BaseCommand

from myapp.models import Perfume


class Command(BaseCommand):
    help = 'Add sample perfumes to a fresh Ambre catalog.'

    def handle(self, *args, **options):
        samples = [
            ('Cedar Veil', '120.00', 'Dry cedar with soft amber and musk.'),
            ('Citrus Dawn', '95.00', 'Bright bergamot with a fresh neroli finish.'),
            ('Midnight Oud', '160.00', 'Dark oud softened by rose and warm resin.'),
        ]
        created_count = 0
        for name, price, description in samples:
            _, created = Perfume.objects.get_or_create(
                brand='Ambre', name=name,
                defaults={'price': price, 'size_ml': 50, 'description': description},
            )
            created_count += created
        self.stdout.write(f'Added {created_count} sample perfume(s).')
