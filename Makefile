# ---------------------------------------------------------
# [  INCLUDES  ]
# override to whatever works on your system

PIPENV := pipenv

include ./Makefile.in.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# override to whatever works on your system

WSGI_APPLICATION := main.wsgi:application
LOCAL_RUN := $(PYTHON) -m main.app

include ./Makefile.targets.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# keep your targets here
