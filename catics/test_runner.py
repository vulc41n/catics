from django.conf import settings
from django.test.runner import DiscoverRunner


class DetectableTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        settings.TEST_MODE = True
        super(DetectableTestRunner, self).__init__(*args, **kwargs)
