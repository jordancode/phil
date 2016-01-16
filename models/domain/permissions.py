from werkzeug.exceptions import Forbidden
from asyncore import read
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
	
	def can_share(self):
		return self._owner
	
	def has_mask(self, permissions_mask):
		if permissions_mask.read is not None:
			if self.can_read() != permissions_mask.read:
				return False
	
		if permissions_mask.write is not None:
			if self.can_write() != permissions_mask.write:
				return False
		
		if permissions_mask.owner is not None:
			if self.is_owner() != permissions_mask.owner:
				return False
		
		return True
	
	def _recursive_to_dict(self, seen_refs, for_client = False):
		return self.to_bitmap()
	
	def to_bitmap(self):
		return ((self._owner  * Permissions.PERMISSION_MASK_OWNER) | 
			(self._read * Permissions.PERMISSION_MASK_READ)	 | 
			(self._write * Permissions.PERMISSION_MASK_WRITE))
	

	def verify_is_owner(self):
		if not self.is_owner():
			raise PermissionsError()
		
	def verify_can_read(self):
		if not self.can_read():
			raise PermissionsError()

	def verify_can_write(self):
		if not self.can_write():
			raise PermissionsError()
	
	def verify_can_share(self):
		if not self.can_share():
			raise PermissionsError()
	
class PermissionsMask:
	
	_owner = None
	_read = None
	_write = None
	
	def __init__(self, read = None, write = None, owner = None):
		self._read = read
		self._write = write
		self._owner = owner
	
	@property
	def read(self):
		return self._read
	
	@property
	def write(self):
		return self._write
	
	@property
	def owner(self):
		return self._owner
	
	#returns the bitmap of permissions that must be set to True
	def to_required_bitmap(self):
		bm = 0b0
		if self.owner:
			bm = bm | Permissions.PERMISSION_MASK_OWNER
		if self.read:
			bm = bm | Permissions.PERMISSION_MASK_READ
		if self.write:
			bm = bm | Permissions.PERMISSION_MASK_WRITE
		
		return bm
		
		
	#returns the bitmap of permissions that must be set to False
	def to_missing_bitmap(self): 
		bm = 0b0
		if self.owner == False:
			bm = bm | Permissions.PERMISSION_MASK_OWNER
		if self.read == False:
			bm = bm | Permissions.PERMISSION_MASK_READ
		if self.write == False:
			bm = bm | Permissions.PERMISSION_MASK_WRITE
		
		return bm
	

class PermissionsError(Forbidden):
	def __init(self):
		super().__init__("You don't have permissions to do this")