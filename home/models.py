from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Willer(models.Model):
    nickname = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nickname


class Answer(models.Model):
    STATIONS = (
        ('T', 'Train'),
        ('M', 'Metro')
    )

    LEVELS = (
        ('1', 'Only ground'),
        ('2', 'Different levels')
    )

    STATUS = (
        ('1', 'Don’t know'),
        ('2', 'It’s working'),
        ('3', 'Out of order')
    )

    willer = models.ForeignKey(Willer, on_delete=models.CASCADE, related_name="answers")

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    station = models.CharField(max_length=1, choices=STATIONS, blank=True)
    levels = models.CharField(max_length=1, choices=LEVELS, blank=True)
    lift = models.CharField(max_length=1, choices=STATUS, blank=True)
    stairs_lift = models.CharField(max_length=1, choices=STATUS, blank=True)
    up_escalator = models.CharField(max_length=1, choices=STATUS, blank=True)
    down_escalator = models.CharField(max_length=1, choices=STATUS, blank=True)

    zone = models.CharField(max_length=100, blank=True)
    no_stairs_needed = models.BooleanField(null=True)
    step_free = models.BooleanField(null=True)

    lift_image = models.ImageField(upload_to='images', blank=True)
    stairs_lift_image = models.ImageField(upload_to='images', blank=True)
    up_escalator_image = models.ImageField(upload_to='images', blank=True)
    down_escalator_image = models.ImageField(upload_to='images', blank=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rilevazione old'
        verbose_name_plural = 'Rilevazioni old'
        ordering = ('-updated',)


class Text(models.Model):
    code = models.CharField(max_length=100, unique=True)
    text = models.TextField(blank=True)
    rich_text = RichTextField(blank=True)
    

    def __str__(self):
        return self.code
    

    def get_text(self):
        from django.utils.safestring import mark_safe
        return self.text or mark_safe(self.rich_text) or self.code
    
    def get_text_short(self):
        from django.utils.safestring import mark_safe
        return self.text[:100] or mark_safe(self.rich_text[:100]) or self.code

    class Meta:
        verbose_name = 'Testo'
        verbose_name_plural = 'Testi'
        ordering = ('text',)


class Translation(models.Model):
    label = models.CharField(max_length=500, unique=True)
    label_it = models.CharField(max_length=500, blank=True)
    label_en = models.CharField(max_length=500, blank=True)


    def __str__(self):
        return self.label
        
    class Meta:
        verbose_name = 'Traduzione old'
        verbose_name_plural = 'Traduzioni old'
        ordering = ('label',)


class Luogo(models.Model):
    name = models.CharField(max_length=100)
    place_id = models.CharField(max_length=100, blank=True, help_text="Google Place ID")
    address = models.CharField(max_length=200, blank=True)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Luogo'
        verbose_name_plural = 'Luoghi'
        ordering = ('name',)


class Categoria(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=1, blank=True, default='R')
    ordine = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        ordering = ('ordine',)




class Area(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True, related_name="aree")
    nome = models.CharField(max_length=50)
    ordine = models.IntegerField(default=1)

    def __str__(self):
        return self.nome + ' (' + (self.categoria and self.categoria.name or '') + ')'
    
    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Aree'
        ordering = ('categoria', 'ordine',)



class Esigenza(models.Model):
    nome = models.CharField(max_length=50)
    ordine = models.IntegerField(default=1)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Esigenza'
        verbose_name_plural = 'Esigenze'
        ordering = ('ordine',)


class Domanda(models.Model):
    QUESTION_TYPES = (
        ('radio', 'Radio'),
        ('checkbox', 'Checkbox'),
        ('text', 'Text'),
        ('number', 'Number'),
        ('textarea', 'Textarea'),
        ('image', 'Foto'),
        ('vote', 'Valutazione 1-4'),
    )

    esigenza = models.ManyToManyField(Esigenza, related_name="domande", blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="domande")
    domanda = models.CharField(max_length=500)
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='radio')
    ordine = models.IntegerField(default=0)

    def __str__(self):
        return self.domanda

    class Meta:
        verbose_name = 'Domanda'
        verbose_name_plural = 'Domande'
        ordering = ('area', 'ordine',)


class Risposta(models.Model):
    domanda = models.ForeignKey(Domanda, on_delete=models.CASCADE, related_name="risposte")
    risposta = models.CharField(max_length=500)
    ordine = models.IntegerField(default=1)

    def __str__(self):
        return self.risposta

    class Meta:
        verbose_name = 'Risposta'
        verbose_name_plural = 'Risposte'
        ordering = ('ordine',)



class Rilevazione(models.Model):
    luogo = models.ForeignKey(Luogo, on_delete=models.CASCADE, related_name="rilevazioni")
    domanda = models.ForeignKey(Domanda, on_delete=models.CASCADE, related_name="rilevazioni")
    risposta = models.ForeignKey(Risposta, on_delete=models.CASCADE, related_name="rilevazioni", blank=True, null=True)
    value = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='images', blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rilevazioni", blank=True, null=True)
    ip_address = models.CharField(max_length=100, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.luogo.name
    

    @property
    def risposta_text(self):
        if self.risposta:
            return self.risposta.risposta
        else:
            return self.value

    class Meta:
        verbose_name = 'Rilevazione'
        verbose_name_plural = 'Rilevazioni'
        ordering = ('-data',)