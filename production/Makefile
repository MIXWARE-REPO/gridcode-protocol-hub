.PHONY: webasto cpms nuba all

webasto:
	./run/run_webasto.sh

cpms:
	./run/run_cpms.sh

nuba:
	NUBA_USER=$${NUBA_USER} NUBA_PASS=$${NUBA_PASS} ./run/run_nuba.sh

all: webasto cpms nuba
