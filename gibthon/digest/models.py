from django.db import models

class Manufacturer( models.Model ):
	name = models.CharField( max_length=100 )
	
	def __unicode__( self ):
		return self.name
	
	class Meta:
		ordering = [ 'name' ]
		

class Enzyme( models.Model ):
	name = models.CharField( max_length=20 )
	manufacturers = models.ManyToManyField( 'Manufacturer', through='BrandedEnzyme' )
	
	
	def __unicode__( self ):
		return self.name

class BrandedEnzyme( models.Model ):
	enzyme = models.ForeignKey( 'Enzyme' )
	manufacturer = models.ForeignKey( 'Manufacturer' )
	buffers = models.ManyToManyField( 'Buffer', through='EnzymeReactionBuffer' )
	
	def __unicode__( self ):
		return "%s (%s)"%( self.enzyme.name, self.manufacturer.name )
		
class EnzymeReactionBuffer( models.Model ):
	enzyme = models.ForeignKey( 'BrandedEnzyme' )
	buffer = models.ForeignKey( 'Buffer' )
	activity = models.PositiveIntegerField()
	
	def __unicode__( self ):
		return "%s (%s) - %s (%s)"%( self.enzyme.enzyme.name, self.enzyme.manufacturer.name, self.buffer.name, self.buffer.manufacturer.name )
	
	class Meta:
		ordering = [ 'enzyme__manufacturer__name', 'enzyme__enzyme__name', 'buffer__manufacturer__name', 'buffer__name' ]

class Buffer( models.Model ):
	name = models.CharField( max_length=20 )
	manufacturer = models.ForeignKey( 'Manufacturer', related_name='buffers' )
	groups = models.ManyToManyField( 'BufferGroup', related_name='buffers' )
	ingredients = models.ManyToManyField( 'Ingredient', through='BufferIngredient' )
	pH = models.DecimalField( max_digits=3, decimal_places=1 )
	
	def ingredient_list( self, ingredients ):
		concentrations = []
		for i in ingredients:
			try:
				ingredient = self.bufferingredient_set.filter( ingredient=i ).get()
			except BufferIngredient.DoesNotExist:
				concentrations.append( '-' )
			else:
				concentrations.append( ingredient.concentration )
		return concentrations
		
	def get_concentrations( self, ingredients ):
		self.concentrations = self.ingredient_list( ingredients )
		return self
	
	def __unicode__( self ):
		return "%s (%s)"%( self.name, self.manufacturer.name )
		
	class Meta:
		ordering = [ 'manufacturer__name', 'name' ]

class Ingredient( models.Model ):
	name = models.CharField( max_length=50 )
	order = models.PositiveSmallIntegerField()
	unit = models.CharField( max_length=15 )
	
	def __unicode__( self ):
		return self.name
		
	class Meta:
		ordering = [ 'order' ]
		
class BufferIngredient( models.Model ):
	buffer = models.ForeignKey( 'Buffer' )
	ingredient = models.ForeignKey( 'Ingredient' )
	concentration = models.DecimalField( max_digits=4, decimal_places=1)
	
	def __unicode__( self ):
		return "%s: %s"%( self.buffer.name, self.ingredient.name )
		
	class Meta:
		ordering = [ 'buffer__manufacturer__name', 'buffer__name', 'ingredient__order' ]
		
		
class BufferGroup( models.Model ):
	name = models.CharField( max_length=50 )
	order = models.PositiveIntegerField()
	
	def ingredients( self ):
		return Ingredient.objects.distinct().filter( buffer__groups=self )
	
	def get_filtered_buffers( self, manufacturers ):
		self.filtered_buffers = [ buffer.get_concentrations( self.ingredients() ) for buffer in self.buffers.filter( manufacturer__id__in=manufacturers ) ]
		return self
	
	def __unicode__( self ):
		return self.name
		
	class Meta:
		ordering = [ 'order' ]