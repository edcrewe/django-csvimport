# Dont use signals because it gets recursive
# but use this for override saves

#from django.db.models.signals import pre_save
def save_csvimport(props={}, instance=None):
    """ To avoid circular imports do saves here """
#    from csvimport.models import CSVImport
#    if not instance:
#        csvimport = CSVImport()
    for key in props.keys():
        csvimport.__setattr__(key, value)
    csvimport.save()
    return csvimport.id

