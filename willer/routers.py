

class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'voxpop':
            return 'voxpop'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'voxpop':# and model.name == 'segnalazione':
            return 'voxpop'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    # def allow_migrate(self, db, app_label, model_name=None, **hints):
    #     if app_label == 'voxpop':
    #         return db == 'voxpop'
    #     return None
