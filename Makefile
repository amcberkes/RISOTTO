all: sim 

sim: 
	g++ -std=c++14 -O2 run_simulation.cc cheby.cc simulate_system.cc common.cc -o bin/sim

debug: debug_sim debug_snc_lolp debug_snc_eue

debug_sim: 
	g++ -std=c++14 -O0 -ggdb -D DEBUG run_simulation.cc cheby.cc simulate_system.cc common.cc -o bin/debug/sim

clean: 
	rm bin/sim bin/snc_lolp bin/snc_eue bin/debug/sim bin/debug/snc_lolp bin/debug/snc_eue
