import os
import sys

CCFLAGS=["-O3 -Wno-long-long -Wreturn-type -g -fPIC"]
CXXFLAGS=CCFLAGS+["-ftemplate-depth-100 -g -fPIC"]

if sys.platform=='darwin':
    FORCE_HASH_MAP=True

if os.environ.has_key('SAGE_DEBUG'):
    CPPDEFINES=[]
    CCFLAGS=[" -pg"] + CCFLAGS
    CXXFLAGS=[" -pg"] + CXXFLAGS
    LINKFLAGS=[" -pg"]

if os.environ['SAGE64'] == "yes":
    print "64 bit OSX build"
    CCFLAGS=[" -m64"] + CCFLAGS
    CXXFLAGS=[" -m64"] + CXXFLAGS
    LINKFLAGS=[" -m64"]

CPPPATH=[os.environ['BOOSTINCDIR']]+[os.environ['SAGE_LOCAL']+"/include"]
PYPREFIX=os.environ['PYTHONHOME']
PBP=os.environ['PYTHONHOME']+'/bin/python'

HAVE_DOXYGEN=False
HAVE_PYDOC=False
HAVE_L2H=False
HAVE_HEVEA=False
HAVE_TEX4HT=False
HAVE_PYTHON_EXTENSION=False
EXTERNAL_PYTHON_EXTENSION=True

try:
  CC = os.environ['CC']
except:
  pass

try:
  CXX = os.environ['CXX']
except:
  pass