# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from django.urls import reverse

class User(models.Model):
    uid = models.AutoField(primary_key=True)
    uname = models.CharField(max_length=50)
    email = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'user'


class Backbonetable(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20)  # Field name made lowercase.
    length = models.IntegerField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    sequence = models.TextField(db_column='Sequence')  # Field name made lowercase.
    ori = models.CharField(db_column='Ori', max_length=20)  # Field name made lowercase.
    marker = models.CharField(db_column='Marker', max_length=20)  # Field name made lowercase.
    species = models.CharField(db_column='Species', max_length=50, blank=True, null=True)  # Field name made lowercase.
    copynumber = models.CharField(db_column='CopyNumber', max_length=20, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=500, blank=True, null=True)  # Field name made lowercase.
    user = models.CharField(db_column='User', max_length=50)  # Field name made lowercase.
    tag = models.CharField(db_column="tag",max_length=50)
    class Meta:
        managed = True
        db_table = 'backbonetable'



class Parentplasmidtable(models.Model):
    ppid = models.AutoField(db_column='PPID', primary_key=True)  # Field name made lowercase.
    sonplasmidid = models.ForeignKey('Plasmidneed', on_delete=models.CASCADE, db_column='SonPlasmidID')  # Field name made lowercase.
    parentplasmidid = models.ForeignKey('Plasmidneed', on_delete=models.CASCADE, db_column='ParentPlasmidID', related_name='parentplasmidtable_parentplasmidid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'parentplasmidtable'

class Parentparttable(models.Model):
    ppid = models.AutoField(db_column='PPID', primary_key=True)  # Field name made lowercase.
    sonplasmidid = models.ForeignKey('Plasmidneed', on_delete=models.CASCADE, db_column='SonPlasmidID')  # Field name made lowercase.
    parentpartid = models.ForeignKey('PartTable', on_delete=models.CASCADE, db_column='parentpartid', related_name='parentparttable_parentpartid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'parentparttable'

class Parentbackbonetable(models.Model):
    pbid = models.AutoField(db_column='pbID', primary_key=True)  # Field name made lowercase.
    sonplasmidid = models.ForeignKey('Plasmidneed', on_delete=models.CASCADE, db_column='SonPlasmidID')  # Field name made lowercase.
    parentbackboneid = models.ForeignKey('backbonetable', on_delete=models.CASCADE, db_column='ParentbackboneID', related_name='parentbackbonetable_parentbackboneid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'parentbackbonetable'


class Partrputable(models.Model):
    prid = models.AutoField(db_column='PRID', primary_key=True)  # Field name made lowercase.
    partid = models.ForeignKey('Parttable', db_column='PartID',on_delete=models.CASCADE,related_name='Part')  # Field name made lowercase.
    rpu = models.FloatField(db_column='RPU')  # Field name made lowercase.
    teststrain = models.CharField(db_column='TestStrain', max_length=50, blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'partrputable'




class Parttable(models.Model):
    partid = models.AutoField(db_column='PartID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lengthinlevel0 = models.IntegerField(db_column='LengthInLevel0')  # Field name made lowercase.
    level0sequence = models.TextField(db_column='Level0Sequence', blank=True, null=True)  # Field name made lowercase.
    confirmedsequence = models.TextField(db_column='ConfirmedSequence', blank=True, null=True)  # Field name made lowercase.
    insertsequence = models.TextField(db_column='InsertSequence', blank=True, null=True)  # Field name made lowercase.
    sourceorganism = models.TextField(db_column='SourceOrganism', blank=True, null=True)  # Field name made lowercase.
    reference = models.TextField(db_column='Reference', blank=True, null=True)  # Field name made lowercase.
    note = models.TextField(db_column='Note', blank=True, null=True)  # Field name made lowercase.
    type = models.IntegerField(db_column='Type')  # Field name made lowercase.
    user = models.CharField(db_column='User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tag = models.CharField(db_column="tag",max_length = 50)


    class Meta:
        managed = True
        db_table = 'parttable'


class Plasmidneed(models.Model):
    plasmidid = models.AutoField(db_column='PlasmidID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20, blank=True, null=True)  # Field name made lowercase.
    oricloning = models.CharField(db_column='OriCloning', max_length=20)  # Field name made lowercase.
    orihost = models.CharField(db_column='OriHost', max_length=20)  # Field name made lowercase.
    markercloning = models.CharField(db_column='MarkerCloning', max_length=20)  # Field name made lowercase.
    markerhost = models.CharField(db_column='MarkerHost', max_length=20)  # Field name made lowercase.
    level = models.CharField(db_column='Level', max_length=10)  # Field name made lowercase.
    length = models.IntegerField(db_column='Length')  # Field name made lowercase.
    sequenceconfirm = models.TextField(db_column='SequenceConfirm')  # Field name made lowercase.
    plate = models.CharField(db_column='Plate', max_length=100, blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State',blank=True,null=True)  # Field name made lowercase.
    user = models.CharField(db_column='User', max_length=20)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=500, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=500, blank=True, null=True)  # Field name made lowercase.
    CustomParentInfo = models.TextField(db_column='CustomParentInformation',blank=True,null=True)
    tag = models.CharField(db_column="tag",max_length=50)
    
    class Meta:
        managed = True
        db_table = 'plasmidneed'




class Straintable(models.Model):
    strainid = models.AutoField(db_column='StrainID', primary_key=True)  # Field name made lowercase.
    strainname = models.CharField(db_column='StrainName', max_length=20)  # Field name made lowercase.
    background = models.CharField(db_column='Background', max_length=20)  # Field name made lowercase.
    marker = models.CharField(db_column='Marker', max_length=30)  # Field name made lowercase.
    store = models.CharField(db_column='Store', max_length=100)  # Field name made lowercase.
    genotype = models.CharField(max_length=100)
    type = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'straintable'




class TbBackboneUserfileaddress(models.Model):
    ufid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    backboneid = models.ForeignKey(Backbonetable,on_delete=models.CASCADE , db_column='backboneid', blank=True, null=True)
    fileaddress = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tb_backbone_userfileaddress'


class TbPartUserfileaddress(models.Model):
    ufid = models.AutoField(primary_key=True)
    userid = models.ForeignKey('User', on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    partid = models.ForeignKey('Parttable', on_delete=models.CASCADE, db_column='partid', blank=True, null=True)
    fileaddress = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tb_part_userfileaddress'


class TbPlasmidUserfileaddress(models.Model):
    ufid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    plasmidid = models.ForeignKey(Plasmidneed, on_delete=models.CASCADE, db_column='plasmidid', blank=True, null=True)
    fileaddress = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tb_plasmid_userfileaddress'

class Testdatatable(models.Model):
    testdataid = models.AutoField(db_column='TestDataID', primary_key=True)  # Field name made lowercase.
    testdataname = models.CharField(db_column='TestDataName', max_length=20)  # Field name made lowercase.
    purpose = models.TextField(db_column='Purpose', blank=True, null=True)  # Field name made lowercase.
    standardstrain = models.CharField(db_column='StandardStrain', max_length=30, blank=True, null=True)  # Field name made lowercase.
    positivecontrol = models.CharField(db_column='PositiveControl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dataaddress = models.TextField(db_column='DataAddress', blank=True, null=True)  # Field name made lowercase.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    strain = models.CharField(db_column='Strain', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'testdatatable'



class Dbdtable(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20)  # Field name made lowercase.
    i0 = models.FloatField(db_column='I0')  # Field name made lowercase.
    kd = models.FloatField()

    class Meta:
        managed = True
        db_table = 'dbdtable'


class Lbddimertable(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20)  # Field name made lowercase.
    k1 = models.FloatField()
    k2 = models.FloatField()
    k3 = models.FloatField()
    i = models.FloatField(db_column='I')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'lbddimertable'


class Lbdnrtable(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=20)  # Field name made lowercase.
    k1 = models.FloatField()
    k2 = models.FloatField()
    k3 = models.FloatField()
    kx1 = models.FloatField()
    kx2 = models.FloatField()

    class Meta:
        managed = True
        db_table = 'lbdnrtable'



# class UploadedFile(models.Model):
#     title = models.CharField(max_length=100, verbose_name="文件标题")
#     file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="文件")
#     description = models.TextField(blank=True, verbose_name="文件描述")
#     uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
#     file_size = models.BigIntegerField(default=0, verbose_name="文件大小")
    
#     class Meta:
#         verbose_name = "上传文件"
#         verbose_name_plural = "上传文件"
#         ordering = ['-uploaded_at']
    
#     def __str__(self):
#         return self.title
    
#     def get_absolute_url(self):
#         return reverse('file_download', kwargs={'pk': self.pk})
    
#     def save(self, *args, **kwargs):
#         # 保存前计算文件大小
#         if self.file:
#             self.file_size = self.file.size
#         super().save(*args, **kwargs)
class Partscartable(models.Model):
    partscarid = models.AutoField(db_column='PartScarID', primary_key=True)  # Field name made lowercase.
    # userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    partid = models.ForeignKey(Parttable,on_delete=models.CASCADE,db_column = 'part_id')
    bsmbi = models.CharField(db_column='BsmBI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bsai = models.CharField(db_column = "BsaI",max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bbsi = models.CharField(db_column = 'BbsI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    aari = models.CharField(db_column = 'AarI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    sapi = models.CharField(db_column = "SapI",max_length=100,blank=False,null=False,default='Enzyme Not Available')

    class Meta:
        managed = True
        db_table = 'Partscartable'


class Backbonescartable(models.Model):
    backbonescarid = models.AutoField(db_column='BackboneScarID', primary_key=True)  # Field name made lowercase.
    # userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    backboneid = models.ForeignKey(Backbonetable,on_delete=models.CASCADE,db_column = 'BackboneID')
    # k1 = models.FloatField()
    # k2 = models.FloatField()
    # k3 = models.FloatField()
    # i = models.FloatField(db_column='I')  # Field name made lowercase.
    bsmbi = models.CharField(db_column='BsmBI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bsai = models.CharField(db_column = "BsaI",max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bbsi = models.CharField(db_column = 'BbsI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    aari = models.CharField(db_column = 'AarI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    sapi = models.CharField(db_column = "SapI",max_length=100,blank=False,null=False,default='Enzyme Not Available')

    class Meta:
        managed = True
        db_table = 'Backbonescartable'

class Plasmidscartable(models.Model):
    plasmidscarid = models.AutoField(db_column='PlasmidScarID', primary_key=True)  # Field name made lowercase.
    # userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid', blank=True, null=True)
    plasmidid = models.ForeignKey(Plasmidneed,on_delete=models.CASCADE,db_column = 'PlasmidID')
    bsmbi = models.CharField(db_column='BsmBI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bsai = models.CharField(db_column = "BsaI",max_length=100,blank=False,null=False,default='Enzyme Not Available')
    bbsi = models.CharField(db_column = 'BbsI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    aari = models.CharField(db_column = 'AarI',max_length=100,blank=False,null=False,default='Enzyme Not Available')
    sapi = models.CharField(db_column = "SapI",max_length=100,blank=False,null=False,default='Enzyme Not Available')

    class Meta:
        managed = True
        db_table = 'Plasmidscartable'


class Plasmid_Culture_Functions(models.Model):
    pcfid = models.AutoField(primary_key=True)
    plasmid_id = models.ForeignKey('Plasmidneed', models.CASCADE,db_column = "plasmid_id")
    function_content = models.CharField(max_length=100)
    function_type = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'plasmid_culture_functions'


class Backbone_Culture_Functions(models.Model):
    bcfid = models.AutoField(primary_key=True)
    backbone_id = models.ForeignKey('Backbonetable', models.CASCADE, db_column="backbone_id")
    function_content = models.CharField(max_length=50)
    function_type = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'backbone_culture_functions'
