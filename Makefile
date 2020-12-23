# ---------------------------------------------------------
# [  INCLUDES  ]
# override to whatever works on your system

PIPENV := pipenv

include ./Makefile.in.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# override to whatever works on your system

APPLICATION := main.asgi:application
LOCAL_RUN := $(RUN) uvicorn \
			--host 0.0.0.0 \
			--lifespan off \
			--log-level debug \
			--port 8000 \
			--reload \
			--workers 1 \
			--ws none \
			$(APPLICATION)

include ./Makefile.targets.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# keep your targets here
