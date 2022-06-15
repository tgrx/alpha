# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 alexandersidorov/alpha:2022.06.15

ENTRYPOINT ["make", "run-prod"]
