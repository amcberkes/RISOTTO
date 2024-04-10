all: sim 

sim: 
	g++ -std=c++14 -O2 -I/opt/homebrew/Cellar/asio/1.28.1/include run_simulation.cc cheby.cc simulate_system.cc common.cc ev.cc -o bin/sim -lpthread

debug: debug_sim 

debug_sim: 
	g++ -std=c++14 -O0 -ggdb -D DEBUG -I/opt/homebrew/Cellar/asio/1.28.1/include run_simulation.cc cheby.cc simulate_system.cc common.cc ev.cc -o bin/debug/sim -lpthread

clean: 
	rm -f bin/sim bin/debug/sim
