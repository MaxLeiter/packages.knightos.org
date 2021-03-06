from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text
from sqlalchemy.orm import relationship, backref
from .database import Base

from datetime import datetime
import bcrypt

package_dependencies = Table('package_dependencies', Base.metadata,
    Column('package_id', Integer, ForeignKey('package.id')),
    Column('dependency_id', Integer, ForeignKey('package.id')),
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String(128), nullable = False, index = True)
    email = Column(String(256), nullable = False, index = True)
    admin = Column(Boolean())
    password = Column(String)
    created = Column(DateTime)
    confirmation = Column(String(128))
    passwordReset = Column(String(128))
    passwordResetExpiry = Column(DateTime)
    packages = relationship('Package', order_by='Package.created')

    def set_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.admin = False
        self.created = datetime.now()

    def __repr__(self):
        return '<User %r>' % self.username

    # Flask.Login stuff
    # We don't use most of these features
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username

class Package(Base):
    __tablename__ = 'package'
    # packages.knightos.org data
    id = Column(Integer, primary_key = True)
    updated = Column(DateTime)
    created = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('package', order_by=id))
    approved = Column(Boolean)
    contents = Column(Unicode(2048))
    pkgrel = Column(Integer)
    downloads = Column(Integer)
    # From package metadata
    name = Column(String(128), nullable = False)
    repo = Column(String(128), nullable = False)
    version = Column(String(128), nullable = False)
    description = Column(Unicode(1024))
    author = Column(Unicode(1024))
    maintainer = Column(Unicode(1024))
    infourl = Column(Unicode(1024))
    copyright = Column(Unicode(1024))
    capabilities = Column(Unicode(2048))
    dependencies = relationship('Package', 
        secondary=package_dependencies,
        primaryjoin=id==package_dependencies.c.package_id,
        secondaryjoin=id==package_dependencies.c.dependency_id,
        backref='package.id')

    def __init__(self):
        self.created = datetime.now()
        self.updated = datetime.now()
        self.approved = False

    def __repr__(self):
        return '{0}/{1}'.format(self.repo, self.name)
