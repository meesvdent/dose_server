from django.db import models
from rdkit import Chem
from rdkit.Chem import Draw
from django.core.files import File


# Create your models here.
from django.utils import timezone


class CompoundType(models.Model):
    type = models.CharField(max_length=200)
    description = models.TextField()
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.type


class Compound(models.Model):
    compound = models.CharField(max_length=200)
    mol_mass = models.FloatField()
    t_half = models.FloatField()
    k_abs = models.FloatField()
    dv = models.FloatField()
    compound_type = models.ManyToManyField(CompoundType, related_name='compound')
    description = models.TextField()
    photo = models.ImageField(upload_to="compound_structures", null=True, blank=True)
    color = models.CharField(max_length=200)
    smiles = models.CharField(max_length=2000, null=True)
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.compound

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.smiles and not self.photo:
            url = draw_compound_structure(smiles=self.smiles, name=self.compound, width=300, height=300)

            self.photo.save(self.compound+".png", File(open(url, 'rb')))
            print("saved in model")
            self.save()


def draw_compound_structure(smiles, name, width, height):
    mol = Chem.MolFromSmiles(smiles)

    #png = Draw.MolsToGridImage([mol])
    path = "media/compound_structures/" + name + ".png"
    print(path + "  saved!")
    Draw.MolToFile(mol, path, size=(width, height))
    return path


