from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('city_detail', args=[self.slug])

    class Meta:
        verbose_name_plural = "Cities"
        db_table = "stations_city"
        managed = False


class Stop(models.Model):

    STOP_PLATFORM = 0
    STATION = 1
    ENTRANCE_EXIT = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4
    AREA = 5

    LOCATION_TYPES = (
        (STOP_PLATFORM, "Stop or platform"),
        (STATION, "Station"),
        (ENTRANCE_EXIT, "Entrance/Exit"),
        (GENERIC_NODE, "Generic node"),
        (BOARDING_AREA, "Boarding area"),
        (AREA, "Area"),
    )

    CARDINAL_DIRECTIONS = (
        ("N", "North"),
        ("E", "East"),
        ("W", "West"),
        ("S", "South"),
    )

    WHEELCHAIR_BOARDING = (
        (0, "No info"),
        (1, "Yes"),
        (2, "No"),
    )

    VISUALLY_IMPAIRED_PATH = (
        (0,'No info for the stop'),
        (1, 'Yes'),
        (2, 'No'),
        (3, 'Only in some areas')
    )

    TODO = 0
    WORKING = 1
    COMPLETED = 2
    VALIDATED = 3

    STATUSES = (
        (TODO, "To do"),
        (WORKING, "Working"),
        (COMPLETED, "Completed"),
        (VALIDATED, "Validated"),
    )

    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="stops")
    code = models.CharField(verbose_name='Stop ID', max_length=20, blank=True)
    name = models.CharField(max_length=100)
    desc = models.TextField(verbose_name="Description", blank=True, null=True)
    lat = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    lon = models.FloatField(verbose_name="Longitude", blank=True, null=True)
    location_type = models.IntegerField(choices=LOCATION_TYPES, default=STATION)
    level = models.IntegerField(blank=True, null=True)
    parent_station = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    wheelchair_boarding = models.IntegerField(choices=WHEELCHAIR_BOARDING, default=0)
    visually_impaired_path = models.IntegerField(choices=VISUALLY_IMPAIRED_PATH, default=0)
    platform_code = models.CharField(max_length=20, blank=True)
    cardinal_direction = models.CharField(max_length=1, blank=True, choices=CARDINAL_DIRECTIONS )
    accessible_entrance = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    accessible_exit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    step_free_route_information_available = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    outside_station_unique_id = models.CharField(max_length=50, blank=True)
    blue_badge_car_parking = models.BooleanField(default=False)
    blue_badge_car_park_spaces = models.IntegerField(blank=True, null=True)
    taxi_ranks_outside_station = models.BooleanField(default=False)
    bus_stop_outside_station = models.BooleanField(default=False)
    train_station = models.BooleanField(default=False)
    image = models.ImageField(blank=True, upload_to='stops')
    status = models.IntegerField(choices=STATUSES, default=TODO)

    def __str__(self) -> str:
        return self.name

    @property
    def ancestors(self):
        ancestors = []
        current = self
        while current.parent_station:
            ancestors.append(current.parent_station)
            current = current.parent_station
        return ancestors


    def summary(self):
        from django.db.models import Count, Q
        totals = dict(self.lifts.aggregate(stairs=Count('type', filter=Q(type=Lift.STAIR)), lifts=Count('type', filter=Q(type=Lift.LIFT)), escalators=Count('type', filter=Q(type=Lift.ESCALATOR)), stairlifts=Count('type', filter=Q(type=Lift.STAIRLIFT))))
        totals.update(self.children.aggregate(stops=Count('id', filter=Q(location_type=Stop.STOP_PLATFORM)), entrances=Count('id', filter=Q(location_type=Stop.ENTRANCE_EXIT)), areas=Count('id', filter=Q(location_type=Stop.AREA) | Q(location_type=Stop.GENERIC_NODE))))
    
        return totals
    

    @property
    def url(self):
        if self.pk:
            return reverse('station_detail', args=[self.city.slug, self.pk])
        else:
            return reverse('home')

    class Meta:
        ordering=('location_type', '-level', 'name',)
        db_table = "stations_stop"
        managed = False
    



class Lift(models.Model):
    HANDRAIL = (
        (0, 'No'),
        (1, 'Right'),
        (2, 'Left'),
        (3, 'Both'),
    )

    PATHWAY_MODES = (
        (3, 'No (Moving walkway)'),
        (4, 'Yes (Escalator)'),
    )

    LIFT = 0
    STAIRLIFT = 1
    STAIR = 2
    ESCALATOR = 3

    LIFT_TYPES = (
        (LIFT, 'Lift'),
        (STAIRLIFT, 'Stairlift'),
        (STAIR, 'Stair'),
        (ESCALATOR, 'Escalator'),
    )

    STATUSES = (
        (None, 'Unknown'),
        (False, 'Not working'),
        (True, 'Working'),
    )

    type = models.IntegerField(choices=LIFT_TYPES)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="lifts")
    name = models.CharField(max_length=100)
    status = models.BooleanField(choices=STATUSES, null=True, blank=True, default=None)
    friendly_name = models.CharField(max_length=100, blank=True)
    from_area = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    intermediate_area1 = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    intermediate_area2 = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    to_area = models.ForeignKey(Stop, on_delete=models.CASCADE, blank=True, null=True)
    lift_width = models.PositiveIntegerField(blank=True, null=True, help_text='in millimeters')    #solo per lift
    lift_depth = models.PositiveIntegerField(blank=True, null=True, help_text='in millimeters')   #solo per lift
    visually_impaired_ok = models.BooleanField(default=False)
    assistance_required = models.BooleanField(default=False) #solo per stairlift

    number_of_steps = models.PositiveIntegerField(blank=True, null=True)    #solo per stair
    steps_height = models.PositiveIntegerField(default=0, help_text='in millimeters', blank=True, null=True) #solo per stair
    handrail = models.IntegerField(choices=HANDRAIL, default=0) #solo per stair
    handrail_height = models.PositiveIntegerField(help_text='in millimeters', blank=True, null=True) #solo per stair
    pathway_mode = models.IntegerField(choices=PATHWAY_MODES, default=0) #solo per escalator
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, upload_to='lifts')

    def __str__(self) -> str:
        return  self.name


    class Meta:
        ordering=('stop', 'type', 'name',)
        db_table = "stations_lift"
        managed = False


class Segnalazione(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lift = models.ForeignKey(Lift, on_delete=models.CASCADE)
    working = models.BooleanField(default=True)
    image = models.ImageField(blank=True, upload_to='segnalazioni')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Segnalazioni"
        ordering = ('-created',)

    def __str__(self):
        return f"{self.lift} - {self.working}"