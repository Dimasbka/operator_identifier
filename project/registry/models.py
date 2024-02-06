from django.db import models
import re





class Operator(  models.Model ):
	name	 = models.CharField( verbose_name="Оператор",  max_length=255 )
	inn		 = models.BigIntegerField( verbose_name="ИНН", default=0)

	class Meta:
		verbose_name		 = "Оператор"
		verbose_name_plural	 = "Операторы"

	def __str__( self ):
		return self.name


class Region(  models.Model ):
	name	 = models.CharField( verbose_name="Регион",  max_length=1500 )

	class Meta:
		verbose_name		 = "Регион"
		verbose_name_plural	 = "Регионы"

	def __str__( self ):
		return self.name


class Range(  models.Model ):
	operator = models.ForeignKey( Operator,verbose_name=u"Оператор", on_delete=models.CASCADE)
	region = models.ForeignKey( Region, verbose_name=u"Регион", on_delete=models.CASCADE)
	abc_def	 = models.IntegerField( verbose_name="АВС/DEF", default=0 )
	sn_from	 = models.IntegerField( verbose_name="От", default=0)
	sn_to	 = models.IntegerField( verbose_name="До", default=0)
	capacity = models.IntegerField( verbose_name="Емкость", default=0)

	class Meta:
		verbose_name		 = "Диапазон"
		verbose_name_plural	 = "Диапазоны"
		unique_together		 = ( ( 'abc_def', 'sn_from','sn_to' ), )

	def __str__( self ):
		return f'{self.abc_def} [{self.sn_from}:{self.sn_to}] - {self.operator}'



class OperatorProvider():
    error = ''
    status = 200

    def is_valid_number(self,phone_number:str):
        return re.match(r"^7[0-9]{10,12}$",phone_number) != None


    def get_data(self,phone_number:str):
        if not self.is_valid_number(phone_number):
            self.error='Неверный формат номера'
            self.status=400
            return False

        abc_def	=int(phone_number[1:4])
        sn = int(phone_number[4:])

        range_obj = Range.objects.filter(
			abc_def=abc_def,
			sn_from__lte=sn,
			sn_to__gte=sn,
        ).order_by(
			"-capacity",
		).select_related(
			'operator','region'
		).first()

        if range_obj == None:
            self.error = 'Номер не найден'
            self.status=404
            return False
    

        return {
			'phone_numder':phone_number,
			'operator':range_obj.operator.name,
			'region':range_obj.region.name,
        }

