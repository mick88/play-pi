from play_pi.management.commands.sync_gplay import Command as SyncCommand


class Command(SyncCommand):
    def handle(self, *args, **options):
        self.stdout.write('init_play command is deprecated. Please use sync_gplay.')
        super(Command, self).handle(*args, **options)