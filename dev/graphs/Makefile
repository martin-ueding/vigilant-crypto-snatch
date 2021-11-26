puml = $(wildcard *.puml)
svg = $(puml:%.puml=%.svg)

all: $(svg)

%.svg: %.puml
	java -jar ~/.local/lib/plantuml.1.2021.14.jar -tsvg $<

vigilant_crypto_snatch.svg: $(puml)