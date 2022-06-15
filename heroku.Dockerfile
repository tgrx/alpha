# syntax=docker/dockerfile:1

FROM alexandersidorov/alpha:latest

ENTRYPOINT ["make", "run-prod"]
