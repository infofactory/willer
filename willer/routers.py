

class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'voxpop':
            return 'voxpop'
        return None

    def db_for_write(self, model, **hints):
        return 'default'
