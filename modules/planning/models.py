from django.db import models
from django.db.models.fields import SmallIntegerField
from ..app.models import TablasConfiguracion, Publico


class Perfil(models.Model):

    idperfil = models.SmallAutoField(primary_key=True)
    deescripcion = models.TextField()
    desc_corta = models.TextField()
    fk_rama = models.ForeignKey(TablasConfiguracion, on_delete=models.CASCADE, default=None, null=True)
    
    def __str__(self):

        return self.deescripcion

    def filtering(username, id=None):

        if(id):

            return Perfil.objects.exclude(idperfil=id).filter(deescripcion__iexact=username).exists()
        else:

            return Perfil.objects.filter(deescripcion__iexact=username).exists()
            
    class Meta:

        ordering = ['-idperfil']

class CompetenciasReq(models.Model):

    idcompetenciasreq = models.AutoField(primary_key=True)
    desc_competencia = models.TextField()
    fk_perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, default=None, null=True)
    fk_tipo_competencia = models.ForeignKey(TablasConfiguracion, on_delete=models.CASCADE, default=None, null=True)
    fk_nivel = models.ForeignKey(TablasConfiguracion, related_name='competencias_nivel', on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):

        return self.desc_competencia

    def filtering(username, id=None):

        if(id):

            return CompetenciasReq.objects.exclude(idcompetenciasreq=id).filter(desc_competencia__iexact=username).exists()

        else:

            return CompetenciasReq.objects.filter(desc_competencia__iexact=username).exists()

    class Meta:

        ordering = ['-idcompetenciasreq']

class CompetenciasAdq(models.Model):
    
    idcompetencias_adq = models.AutoField(primary_key=True)
    periodo = models.CharField(max_length=15)
    experiencia = models.SmallIntegerField()
    fk_publico = models.ForeignKey(Publico, on_delete=models.CASCADE, default=None, null=True)
    fk_competencia = models.ForeignKey(CompetenciasReq, on_delete=models.CASCADE, default=None, null=True, related_name="competencia")
    fk_nivel = models.ForeignKey(TablasConfiguracion, on_delete=models.CASCADE, default=None, null=True, related_name="nivel")
    fk_tipo_duracion = models.ForeignKey(TablasConfiguracion, on_delete=models.CASCADE, default=None, null=True)

    class Meta:

        ordering = ['-idcompetencias_adq']