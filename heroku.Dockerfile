# syntax=docker/dockerfile:1

FROM alexandersidorov/alpha:2022.06.15

ENTRYPOINT ["make", "run-prod"]
