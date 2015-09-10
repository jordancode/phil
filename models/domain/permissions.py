class Permissions:

	PERMISSION_MASK_OWNER = 0b1
	PERMISSION_MASK_READ = 0b10
	PERMISSION_MASK_WRITE = 0b100
	
	_owner = False
	_read = False
	_write = False
	
	@classmethod
	def from_bitmap(cls, bitmap):
		return Permissions(
						bool(bitmap & Permissions.PERMISSION_MASK_READ),
						bool(bitmap & Permissions.PERMISSION_MASK_WRITE),	
						bool(bitmap & Permissions.PERMISSION_MASK_OWNER)
						)
	
	
	def __init__(self, read = False, write = False, owner = False):
		self._read = read
		self._write = write
		self._owner = owner
	
	
	def is_owner(self):
		return self._owner
	
	def can_read(self):
		return self._read
	
	def can_write(self):
		return self._write
	
	def to_dict(self):
		return self.to_bitmap()
	
	def to_bitmap(self):
		return ((self._owner  * Permissions.PERMISSION_MASK_OWNER) | 
			(self._read * Permissions.PERMISSION_MASK_READ)	 | 
			(self._write * Permissions.PERMISSION_MASK_WRITE))
	

	def verify_is_owner(self):
		if not self.is_owner():
			raise PermissionError()
		
	def verify_can_read(self):
		if not self.can_read():
			raise PermissionError()

	def verify_can_write(self):
		if not self.can_write():
			raise PermissionError()


class PermissionsError(Exception):
	def __init(self):
		super().__init__("You don't have permissions to do this")