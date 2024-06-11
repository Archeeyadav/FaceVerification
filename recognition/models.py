from django.db import models
import numpy as np
import base64

class Face(models.Model):
    image_url = models.URLField()
    encoding = models.TextField()

    def set_encoding(self, encoding):
        self.encoding = base64.b64encode(np.array(encoding)).decode('utf-8')

    def get_encoding(self):
        return np.frombuffer(base64.b64decode(self.encoding.encode('utf-8')), dtype=np.float64)
